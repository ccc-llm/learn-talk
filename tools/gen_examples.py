#!/usr/bin/env python3
"""用 LLM 為詞表裡的每個詞造一個例句，並用 checker 驗證；通過的寫進 words.tsv 的 example 欄。

用法：
    python tools/gen_examples.py --lang fr --cats verb,noun
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.llm import LLM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    ap.add_argument('--cats', default='')
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()

    s = spec_mod.load(a.lang)
    checker = Checker(s)
    llm = LLM(provider=a.provider)

    spec_text = (s.dir / 'spec.md').read_text(encoding='utf-8')
    system = f"""你正在為受限語言 {s.name} 造例句。
只能用下面規格裡的詞表。每一行輸出一句例句，不要解釋，不要編號。

{spec_text}
"""

    cats = [c for c in a.cats.split(',') if c] or s.categories
    targets = []
    for c in cats:
        targets.extend(w.unit for w in s.by_category().get(c, []) if w.level == 'C')
    if a.limit:
        targets = targets[:a.limit]

    def one(w):
        prompt = (f'請為「{w}」造一句最短的 {s.name} 例句。\n'
                  f'只能一行，不要解釋。')
        try:
            return llm.chat(prompt, system=system, max_tokens=600).split('\n')[0].strip()
        except Exception as e:      # noqa: BLE001
            return ''

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, targets))

    ok = 0
    for w, ex_text in zip(targets, results):
        ex_text = ex_text.strip().strip('「」"')
        if not ex_text:
            continue
        errs = checker.check(ex_text)
        if errs:
            continue
        s.words[w.lower()].example = ex_text
        ok += 1

    # 寫回 words.tsv
    rows = ['unit\tlevel\tpos\tgloss\tcategory\texample\tipa']
    for cat in s.categories:
        for w in sorted(s.by_category().get(cat, []), key=lambda x: (x.level != 'C', x.unit)):
            rows.append(f'{w.unit}\t{w.level}\t{w.pos}\t{w.gloss}\t{cat}\t{w.example}\t{w.ipa}')
    (s.dir / 'data' / 'words.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'✅ {ok}/{len(targets)} 個例句通過檢查')


if __name__ == '__main__':
    main()
