#!/usr/bin/env python3
"""learn-talk 的跨語言命令列工具。

用法：
    python -m core.cli list                        # 列出所有語言
    python -m core.cli check zh "我想喝茶。"        # 檢查一段文字
    python -m core.cli check-en zh file.txt        # 檢查檔案
    python -m core.cli lexicon zh                  # 檢查詞典
    python -m core.cli reverse zh "看病的地方"      # 反向翻譯
    python -m core.cli build zh                    # 產生 spec.md 與 prompts/system.md
    python -m core.cli report zh                   # 自我檢查報告
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import spec as spec_mod
from .checker import Checker
from .lexicon import Lexicon, Reverser


def cmd_list(a):
    langs = spec_mod.all_langs()
    if not langs:
        print('（還沒有任何語言）')
        return
    for d in langs:
        s = spec_mod.Spec(d)
        print(f'{d.name:22} {s.code:6} {len(s.words):5} 單位  {s.unit_kind:5} {d}')


def cmd_check(a):
    s = spec_mod.load(a.lang)
    c = Checker(s)
    if a.file:
        bad = total = 0
        for p in a.file:
            defined = set()
            for no, line in enumerate(Path(p).read_text(encoding='utf-8').splitlines(), 1):
                if not line.strip():
                    continue
                total += 1
                errs = c.check(line, defined)
                if errs:
                    bad += 1
                    if bad <= 30:
                        for e in errs:
                            print(f'❌ {p}:{no} {e}　→　{line.strip()[:70]}')
        print(f'檢查了 {len(a.file)} 個檔案、{total} 行：' + ('✅ 全部在字表內' if not bad else f'❌ {bad} 行有問題'))
        return 1 if bad else 0
    errs = c.check(' '.join(a.text))
    if not errs:
        print('✅ 全部在字表內')
        return 0
    for e in errs:
        print(f'❌ {e}')
    return 1


def cmd_lexicon(a):
    s = spec_mod.load(a.lang)
    c = Checker(s)
    lex = Lexicon(s.dir / 'lexicon.tsv')
    problems = lex.validate(c)
    stat = {}
    for r in lex.rows:
        stat[r['方式']] = stat.get(r['方式'], 0) + 1
    print(f'{s.name} 詞典：{len(lex)} 列　' + '　'.join(f'{k} {v}' for k, v in sorted(stat.items())))
    if problems:
        for p in problems[:40]:
            print(f'❌ {p}')
        print(f'❌ {len(problems)} 個問題')
        return 1
    print('✅ 全部通過')
    return 0


def cmd_reverse(a):
    s = spec_mod.load(a.lang)
    lex = Lexicon(s.dir / 'lexicon.tsv')
    rev = Reverser(lex, s)
    print(rev.to_source(' '.join(a.text)))
    return 0


def cmd_build(a):
    from .build import build
    s = spec_mod.load(a.lang)
    build(s)
    print(f'✅ 已產生 {s.dir / "spec.md"} 與 {s.dir / "prompts" / "system.md"}')
    return 0


def cmd_report(a):
    from .report import report
    s = spec_mod.load(a.lang)
    report(s)
    return 0


def main():
    ap = argparse.ArgumentParser(description='learn-talk 工具')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('list')

    p = sub.add_parser('check')
    p.add_argument('lang')
    p.add_argument('text', nargs='*')
    p.add_argument('--file', nargs='*', default=[])

    p = sub.add_parser('lexicon')
    p.add_argument('lang')

    p = sub.add_parser('reverse')
    p.add_argument('lang')
    p.add_argument('text', nargs='*')

    p = sub.add_parser('build')
    p.add_argument('lang')

    p = sub.add_parser('report')
    p.add_argument('lang')

    a = ap.parse_args()
    fn = {'list': cmd_list, 'check': cmd_check, 'lexicon': cmd_lexicon,
          'reverse': cmd_reverse, 'build': cmd_build, 'report': cmd_report}[a.cmd]
    sys.exit(fn(a) or 0)


if __name__ == '__main__':
    main()
