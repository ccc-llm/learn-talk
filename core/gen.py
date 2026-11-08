"""生成程式：用 LLM 產生受限語言的語料、翻譯與詞典，並自動用 checker 把關。

三種用途：
  1. gen corpus    產生語料（給 mini-lm 用），不通過檢查的丟掉
  2. gen rewrite   把一般文章改寫成受限語言，統計一次通過率
  3. gen lexicon   從常用詞表產生受限說法候選

用法：
    python -m core.gen corpus   --lang zh --topics topics.txt --out corpus/
    python -m core.gen rewrite  --lang zh --file article.txt
    python -m core.gen lexicon  --lang zh --words common_words.txt
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
import re
from pathlib import Path

from . import spec as spec_mod
from .checker import Checker
from .llm import LLM

ROOT = Path(__file__).resolve().parent.parent


def load_prompt(lang_dir: Path) -> str:
    p = lang_dir / 'prompts' / 'system.md'
    if not p.exists():
        return ''
    text = p.read_text(encoding='utf-8')
    m = re.search(r'\n---\n(.*?)(?:\n---\n|$)', text, re.S)
    return m.group(1).strip() if m else text


# ── 1. 語料生成 ───────────────────────────────────────────────────────────────

def gen_corpus(spec, llm: LLM, topics: list[str], out_dir: Path,
               n_per_topic: int = 20, workers: int = 3) -> dict:
    system = load_prompt(spec.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checker = Checker(spec)

    def make(topic):
        prompt = (f'請寫 {n_per_topic} 句關於「{topic}」的 {spec.name}。\n'
                  f'每句一行，不要編號，不要解說。\n'
                  f'只能使用 {spec.name} 詞表內的字詞；詞表外的專有名詞用外來語並在第一次出現時加括號說明。')
        return llm.chat_lines(prompt, system=system)

    results = llm.batch(topics, make, workers=workers)
    kept: list[str] = []
    dropped: list[tuple[str, str]] = []
    for topic, lines in zip(topics, results):
        if not isinstance(lines, list):
            dropped.append((topic, str(lines)))
            continue
        for line in lines:
            errs = checker.check(line)
            if errs:
                dropped.append((line, '; '.join(str(e) for e in errs[:3])))
            else:
                kept.append(line)
    (out_dir / 'corpus.txt').write_text('\n'.join(kept) + '\n', encoding='utf-8')
    (out_dir / 'dropped.json').write_text(
        json.dumps(dropped, ensure_ascii=False, indent=2), encoding='utf-8')
    total = len(kept) + len(dropped)
    rate = len(kept) / total if total else 0
    print(f'語料：{len(kept)}/{total} 句通過（{rate:.0%}），輸出到 {out_dir}')
    if dropped:
        print('最常見的問題（前 10 句）：')
        for s, why in dropped[:10]:
            print(f'  ❌ {s}　→　{why}')
    return {'kept': len(kept), 'total': total, 'rate': rate}


# ── 2. 改寫測試 ───────────────────────────────────────────────────────────────

def gen_rewrite(spec, llm: LLM, texts: list[str], workers: int = 3,
                rounds: int = 3) -> dict:
    """把一般文章改寫成受限語言。

    rounds > 1 時會做「自我修正」：把檢查器報的錯回饋給模型，讓它改。
    """
    system = load_prompt(spec.dir)
    checker = Checker(spec)

    def make(t):
        prompt = (f'請把下面這段一般文字改寫成 {spec.name}。\n'
                  f'意思不能變，只能用 {spec.name} 詞表內的字詞。\n'
                  f'直接輸出改寫後的文字，不要解說。\n\n'
                  f'{t}')
        return llm.chat(prompt, system=system, max_tokens=4000)

    def fix(t, out, errs):
        """把錯誤回饋給模型，讓它改。"""
        bad = '\n'.join(f'- {e}' for e in errs[:12])
        prompt = (f'你剛才改寫的 {spec.name} 有錯：\n\n'
                  f'{out}\n\n'
                  f'檢查器報的錯：\n{bad}\n\n'
                  f'請只輸出改好的 {spec.name} 全文，不要解說。\n'
                  f'改的時候要遵守規格裡的語法規則：'
                  f'不要用表外的詞、不要用禁用的說法、'
                  f'外來語第一次出現時要加括號說明。')
        return llm.chat(prompt, system=system, max_tokens=4000)

    def work(t):
        out = make(t)
        defined = set()
        errs = checker.check(out, defined)
        history = [len(errs)]
        for _ in range(max(0, rounds - 1)):
            if not errs:
                break
            try:
                out = fix(t, out, errs)
            except Exception:      # noqa: BLE001
                break
            errs = checker.check(out, defined)
            history.append(len(errs))
        return {'source': t, 'output': out,
                'errors': [str(e) for e in errs[:20]], 'history': history}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        details = list(ex.map(work, texts))
    ok = sum(1 for d in details if not d['errors'])
    rate = ok / len(texts) if texts else 0
    print(f'改寫：{ok}/{len(texts)} 段一次通過（{rate:.0%}）')
    for d in details:
        print(f'  錯誤數：{d["history"]}')
    return {'ok': ok, 'total': len(texts), 'rate': rate, 'details': details}


# ── 3. 詞典生成 ───────────────────────────────────────────────────────────────

def gen_lexicon(spec, llm: LLM, words: list[str], workers: int = 3) -> list[dict]:
    system = load_prompt(spec.dir)

    def make(w):
        prompt = (f'「{w}」用 {spec.name} 怎麼說？\n'
                  f'依序試三層：本詞（詞表內直接用）／描述（用詞表內的字描述）／外來語（原文＋括號說明）。\n'
                  f'用一行回答，格式：方式｜受限說法｜說明\n'
                  f'方式只能是：本詞／描述／外來語。不要多餘的話。')
        return llm.chat(prompt, system=system)

    results = llm.batch(words, make, workers=workers)
    out = []
    for w, r in zip(words, results):
        if not isinstance(r, str):
            continue
        parts = [p.strip() for p in r.split('\n')[0].split('｜')]
        if len(parts) < 2:
            parts = [p.strip() for p in re.split(r'\||\t', r.split('\n')[0])]
        if len(parts) < 2:
            continue
        way = parts[0]
        mini = parts[1]
        note = parts[2] if len(parts) > 2 else ''
        if way not in ('本詞', '描述', '外來語'):
            continue
        out.append({'原文': w, '受限說法': mini, '方式': way, '說明': note})
    print(f'詞典候選：{len(out)}/{len(words)}')
    return out


def main():
    ap = argparse.ArgumentParser(description='用 LLM 產生受限語言的資料')
    ap.add_argument('task', choices=['corpus', 'rewrite', 'lexicon'])
    ap.add_argument('--lang', required=True)
    ap.add_argument('--provider', default='nvidia', choices=['nvidia', 'minimax'])
    ap.add_argument('--model', default=None)
    ap.add_argument('--topics', default=None)
    ap.add_argument('--file', default=None)
    ap.add_argument('--words', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--n', type=int, default=20)
    ap.add_argument('--workers', type=int, default=3)
    a = ap.parse_args()

    spec = spec_mod.load(a.lang)
    llm = LLM(provider=a.provider, model=a.model)

    if a.task == 'corpus':
        topics = Path(a.topics).read_text(encoding='utf-8').split('\n') if a.topics else [
            '自我介紹', '買東西', '問路', '看醫生', '天氣', '家庭', '工作', '旅行', '食物', '學習']
        topics = [t.strip() for t in topics if t.strip()]
        out = Path(a.out) if a.out else spec.dir / 'corpus'
        gen_corpus(spec, llm, topics, out, n_per_topic=a.n, workers=a.workers)
    elif a.task == 'rewrite':
        texts = Path(a.file).read_text(encoding='utf-8').split('\n\n') if a.file else []
        texts = [t.strip() for t in texts if t.strip()]
        r = gen_rewrite(spec, llm, texts, workers=a.workers)
        out = Path(a.out) if a.out else spec.dir / 'rewrite_test.json'
        out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        words = Path(a.words).read_text(encoding='utf-8').split('\n') if a.words else []
        words = [w.strip() for w in words if w.strip()]
        rows = gen_lexicon(spec, llm, words, workers=a.workers)
        out = Path(a.out) if a.out else spec.dir / 'lexicon_candidate.tsv'
        out.write_text('原文\t受限說法\t方式\t說明\n' + '\n'.join(
            '\t'.join([r['原文'], r['受限說法'], r['方式'], r['說明']]) for r in rows) + '\n',
            encoding='utf-8')
    print(llm.stats())


if __name__ == '__main__':
    main()
