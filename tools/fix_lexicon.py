#!/usr/bin/env python3
"""清理詞典：刪掉不合格的列、嘗試修一些常見問題。

用法：python tools/fix_lexicon.py --lang japanese
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.lexicon import Lexicon  # noqa: E402

ALIAS = {'japanese': 'mini-japanese', 'ja': 'mini-japanese',
         'french': 'mini-french', 'fr': 'mini-french',
         'korean': 'mini-korean', 'ko': 'mini-korean',
         'english': 'mini-english', 'en': 'mini-english',
         'chinese': 'mini-chinese', 'zh': 'mini-chinese'}

# 明顯是壞掉的原文（模型產生時走鐘）
BAD_SOURCE = re.compile(r'^(Use:|Pe\?|ERROR|待|以下|以下は|抱歉|无法|無法|请|請|第\d+)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    a = ap.parse_args()

    s = spec_mod.load(ALIAS.get(a.lang, a.lang))
    checker = Checker(s)
    path = s.dir / 'lexicon.tsv'
    lex = Lexicon(path)

    keep = []
    dropped = 0
    for r in lex.rows:
        src = r['原文'].strip()
        mini = r['受限說法'].strip()
        way = r['方式'].strip()
        note = r['說明'].strip()
        if not src or BAD_SOURCE.match(src):
            dropped += 1
            continue
        if way == '本詞':
            head = mini
            for art in ('の',):
                if head.startswith(art):
                    head = head[len(art):]
                    break
            if head not in s.vocab and head.lower() not in s.vocab:
                dropped += 1
                continue
        elif way == '外來語':
            if not note:
                dropped += 1
                continue
            if checker.check(note, allow_bare_loanword=True):
                dropped += 1
                continue
        else:
            if checker.check(mini, allow_bare_loanword=True):
                dropped += 1
                continue
        keep.append(r)

    lex.rows = keep
    lex.save()
    print(f'✅ 保留 {len(keep)} 列，刪掉 {dropped} 列')


if __name__ == '__main__':
    main()
