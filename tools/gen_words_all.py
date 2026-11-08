#!/usr/bin/env python3
"""批次產生一個語言所有類別的詞表候選（平行呼叫）。

用法：
    python tools/gen_words_all.py --lang japanese --n 90
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.llm import LLM  # noqa: E402
from tools.gen_words import CATEGORY_HINT  # noqa: E402

ORDER = ['pron', 'gram', 'num', 'time', 'place', 'nature', 'verb', 'adj',
         'noun', 'social', 'abstr']

# 每種語言的寫作規則
LANG_RULES = {
    'french': """這是法文（Mini-French）：
- 名詞用小寫；動詞用原形（infinitif）；形容詞用陽性單數。
- 詞性用：n（名詞）、v（動詞）、adj（形容詞）、adv（副詞）、det（限定詞）、pron（代詞）、num（數詞）、gram（功能詞）。
- 不要有重音符以外的裝飾，維持正確的法文拼寫（含重音符，例如 é、è、ê）。""",
    'japanese': """這是日文（Mini-Japanese）：
- **名詞用漢字**（例如 人、水、店），但只收最常用、最簡單的漢字。
- **動詞與形容詞用平假名**（例如 たべる、大きい），不用漢字寫。
- 片假名只用於外來語（コーヒー），一般詞不用。
- 詞性用：n（名詞）、v（動詞）、adj（形容詞）、adv（副詞）、det（限定詞）、pron（代詞）、num（數詞）、gram（功能詞／助詞）。
- 動詞一律用「ます形」（たべます、のみます），不要用辶書形。""",
    'korean': """這是韓文（Mini-Korean）：
- 用諺文（한글），不用漢字。
- 動詞用「해요體」原形（먹어요、가요、해요）。
- 名詞直接用（학교、물）。
- 詞性用：n（名詞）、v（動詞）、adj（形容詞）、adv（副詞）、det（限定詞）、pron（代詞）、num（數詞）、gram（功能詞／助詞）。
- 一個詞裡不要有空格。""",
}

SYSTEM_TMPL = """你是一位語言學家，正在為外國人設計一套受限的{lang}（受限語言）。
受限語言的詞表要能表達日常生活，選詞原則是：
1. 選「表達力強、能構詞」的詞，不看詞頻。
2. 一個概念一個詞，去掉同義詞。
3. 能用其他詞輕鬆說出來的不收（醫院 → 「看病的地方」這類描述）。
4. 盡量避免難寫、容易唸錯的詞。

{rules}

你只要輸出詞表，不要解說。每行一個詞，格式：
詞<TAB>詞性<TAB>中文意思
不要輸出表頭以外的任何文字。"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default='french')
    ap.add_argument('--n', type=int, default=90)
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--cats', default=','.join(ORDER))
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()

    lang_dir = ROOT / 'langs' / f'mini-{a.lang}'
    (lang_dir / 'data').mkdir(parents=True, exist_ok=True)
    llm = LLM(provider=a.provider)
    system = SYSTEM_TMPL.format(lang=a.lang, rules=LANG_RULES.get(a.lang, ''))

    def one(cat):
        hint = CATEGORY_HINT.get(cat, cat)
        prompt = (f'請給 {a.lang} 的「{cat}」類別出 {a.n} 個詞。\n'
                  f'這一類是：{hint}。\n'
                  f'每行一個：詞<TAB>詞性<TAB>中文意思\n'
                  f'不要重複，不要輸出其他文字。')
        try:
            return cat, llm.chat_lines(prompt, system=system, max_tokens=6000)
        except Exception as e:      # noqa: BLE001
            return cat, [f'ERROR {e}']

    cats = a.cats.split(',')
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, cats))

    for cat, lines in results:
        rows = ['unit\tpos\tgloss']
        seen = set()
        for l in lines:
            if l.startswith('ERROR'):
                print(f'❌ {cat}: {l}')
                continue
            parts = l.split('\t')
            if len(parts) < 2:
                parts = l.split('|')
            if len(parts) < 2:
                continue
            w = parts[0].strip()
            pos = parts[1].strip().split('/')[0].strip()
            gloss = parts[2].strip() if len(parts) > 2 else ''
            if not w or ' ' in w or w.lower() in seen:
                continue
            seen.add(w.lower())
            rows.append(f'{w}\t{pos}\t{gloss}')
        out = lang_dir / 'data' / f'_cand_{cat}.tsv'
        out.write_text('\n'.join(rows) + '\n', encoding='utf-8')
        print(f'✅ {cat}: {len(rows) - 1} 個 → {out.name}')
    print(llm.stats())


if __name__ == '__main__':
    main()
