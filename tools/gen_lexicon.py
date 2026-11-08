#!/usr/bin/env python3
"""用 LLM 產生受限語言的詞典候選（每個詞的受限說法）。

用法：
    python tools/gen_lexicon.py --lang fr --words common_fr.txt
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.llm import LLM  # noqa: E402

LANG_NAME = {'fr': 'Mini-French', 'ja': 'Mini-Japanese', 'ko': 'Mini-Korean'}


def load_system(lang: str) -> str:
    """把該語言的完整規格（詞表、類頭、描述模板）放進系統提示詞。"""
    from core import spec as spec_mod
    s = spec_mod.load(lang)
    lang = getattr(s, 'code', lang)
    spec_text = (s.dir / 'spec.md').read_text(encoding='utf-8')
    return f"""你正在為外國人設計一套受限語言：{s.name}。
只用下面這份規格裡的詞表就能說日常生活的話。

{spec_text}

詞表外的一般概念用「描述」說出來，描述要由詞表內的詞組成，並且以類頭結尾。
類頭：{'、'.join(s.heads)}

描述的公式（依這個語言的慣例）：
{chr(10).join('- ' + t for t in s.desc_templates)}

說不出「是哪一個」的（人名、地名、物種、品牌）用外來語：寫原文，說明放在後面的括號裡。

要求：
1. 只能用詞表內的詞。**不要改寫詞表裡的詞**（表裡是「麺」就寫「麺」，不要寫成「麵條」）。
2. 描述要用這個語言允許的句型（規格裡的「描述模板」），不要用其他語言的句型。
   - 日文：不用て形，用「…をする人」「…の場所」
   - 韓文：只用 해요體，描述用「…하는 사람」「…하는 곳」，助詞用「을/를」「이/가」依收音正確選擇。
   - 法文：描述用「un lieu où…」「une personne qui…」
3. 輸出一行一個詞，格式：原文<TAB>受限說法<TAB>方式<TAB>說明
3. 方式只能是：本詞／描述／外來語
4. 說明欄：外來語必填（用受限語言寫），本詞與描述留空。
5. 不要輸出其他文字，不要解釋，直接給那一行。"""


SYSTEM = load_system('fr')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default='fr')
    ap.add_argument('--words', required=True)
    ap.add_argument('--out', default=None)
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()

    ALIAS = {'fr': 'mini-french', 'ja': 'mini-japanese', 'ko': 'mini-korean'}
    lang_dir = ROOT / 'langs' / ALIAS.get(a.lang, f'mini-{a.lang}')
    words = [w.strip() for w in Path(a.words).read_text(encoding='utf-8').splitlines() if w.strip()]
    if a.limit:
        words = words[:a.limit]
    llm = LLM(provider=a.provider)
    system = load_system(a.lang)

    def one(w):
        prompt = (f'「{w}」用 Mini-French 怎麼說？\n'
                  f'依序試三層：本詞（詞表內直接用）／描述（用詞表內的詞描述）／外來語（原文＋括號說明）。\n'
                  f'輸出一行，格式：原文<TAB>受限說法<TAB>方式<TAB>說明')
        try:
            return llm.chat(prompt, system=system, max_tokens=4000).split('\n')[0].strip()
        except Exception as e:      # noqa: BLE001
            return f'ERROR {e}'

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, words))

    rows = ['原文\t受限說法\t方式\t說明']
    bad = 0
    for w, r in zip(words, results):
        if r.startswith('ERROR'):
            bad += 1
            continue
        parts = [p.strip() for p in r.split('\t')]
        if len(parts) < 3:
            parts = [p.strip() for p in r.split('|')]
        if len(parts) < 3:
            bad += 1
            continue
        src = parts[0] or w
        mini, way = parts[1], parts[2]
        note = parts[3] if len(parts) > 3 else ''
        if way not in ('本詞', '描述', '外來語'):
            bad += 1
            continue
        rows.append(f'{src}\t{mini}\t{way}\t{note}')
    out = Path(a.out) if a.out else lang_dir / 'lexicon_candidate.tsv'
    out.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'✅ {len(rows) - 1} 列（{bad} 個失敗）→ {out}')


if __name__ == '__main__':
    main()
