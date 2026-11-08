"""覆蓋率測試：抽一批常用詞，看有多少能用本詞／描述／外來語說出來。

用法：
    python -m core.coverage --lang zh --sample data/coverage_sample.txt
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

from . import spec as spec_mod
from .checker import Checker
from .lexicon import Lexicon


def main():
    ap = argparse.ArgumentParser(description='覆蓋率測試')
    ap.add_argument('--lang', required=True)
    ap.add_argument('--sample', default=None, help='抽樣詞表（一行一個詞）')
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=42)
    a = ap.parse_args()

    spec = spec_mod.load(a.lang)
    checker = Checker(spec)
    lex = Lexicon(spec.dir / 'lexicon.tsv')
    known = {r['原文'] for r in lex.rows}

    if a.sample:
        words = [l.strip() for l in Path(a.sample).read_text(encoding='utf-8').splitlines()
                 if l.strip() and not l.startswith('#')]
    else:
        words = [w for w in known]
    words = [w for w in words if w not in known] or words
    random.seed(a.seed)
    if len(words) > a.n:
        words = random.sample(words, a.n)

    stat = {'本詞': 0, '描述': 0, '外來語': 0, '說不好': 0}
    bad = []
    for w in words:
        if w.lower() in spec.vocab:
            stat['本詞'] += 1
            continue
        hit = None
        for r in lex.rows:
            if r['原文'] == w and r['方式'] in ('描述', '外來語'):
                hit = r
                break
        if hit is None:
            stat['說不好'] += 1
            bad.append(w)
        else:
            stat[hit['方式']] += 1
    total = len(words) or 1
    print(f'{spec.name} 覆蓋率測試（{len(words)} 個詞）')
    for k, v in stat.items():
        print(f'  {k}：{v}（{v / total:.0%}）')
    if bad:
        print('說不好的詞：' + '、'.join(bad[:40]))
    out = spec.dir / 'coverage.tsv'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('原文\t方式\n' + '\n'.join(
        f'{w}\t{"本詞" if w.lower() in spec.vocab else ""}' for w in words) + '\n',
        encoding='utf-8')


if __name__ == '__main__':
    main()
