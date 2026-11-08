#!/usr/bin/env python3
"""只補課本裡缺掉的章節（已存在的���會重寫）。

用法：
    python tools/gen_book_fill.py --lang english --provider nvidia
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.gen_book as gb  # noqa: E402
from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.llm import LLM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    ap.add_argument('--provider', default='nvidia')
    ap.add_argument('--workers', type=int, default=3)
    a = ap.parse_args()

    s = spec_mod.load(a.lang)
    checker = Checker(s)
    name = gb.BOOK_NAME.get(s.code, s.name)
    n = len(s.words)
    llm = LLM(provider=a.provider)
    system = gb.build_system(s, checker)
    out_dir = ROOT / 'books' / s.code
    out_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    for num, title, brief in gb.CHAPTERS:
        prefix = num + '-'
        if any(p.name.startswith(prefix) for p in out_dir.glob(prefix + '*.md')):
            continue
        missing.append((num, title, brief))
    print(f'缺 {len(missing)} 章：{[m[0] for m in missing]}')
    if not missing:
        return

    from concurrent.futures import ThreadPoolExecutor

    def one(ch):
        num, title, brief = ch
        t = title.replace('{name}', name).replace('{n}', str(n))
        prompt = (f'請寫「{num} {t}」這一章。\n'
                  f'這一章的重點：{brief}\n\n'
                  f'要求：\n'
                  f'- 開頭用一段話說明這一章要學什麼。\n'
                  f'- 中間分成 2–4 個小節（用 ## 標題），每節有說明、表格或例句。\n'
                  f'- 至少 5 個完整例句（用 {name} 寫），必要時用表格對照。\n'
                  f'- 最後給 3–5 題練習與答案。\n'
                  f'- 全文用 markdown。')
        try:
            text = llm.chat(prompt, system=system, max_tokens=8192)
        except Exception as e:      # noqa: BLE001
            return num, t, f'ERROR {e}'
        for _ in range(2):
            if num in ('A', 'B', 'C'):
                break
            errs = gb.find_errors(text, checker, s)
            if not errs:
                break
            bad = '\n'.join(f'- {e}' for e in errs[:15])
            fix_prompt = (f'你寫的「{num} {t}」這一章裡，以下例句不合規則：\n\n{bad}\n\n'
                          f'請把整章重寫一次，把這些例句改對。'
                          f'其他內容可以保留。\n'
                          f'只輸出改好的 markdown 章節，不要解說。')
            try:
                text = llm.chat(fix_prompt, system=system, max_tokens=8192)
            except Exception:      # noqa: BLE001
                break
        return num, t, text

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, missing))

    bad = 0
    for num, title, text in results:
        if text.startswith('ERROR'):
            print(f'❌ {num} {title}：{text[:90]}')
            bad += 1
            continue
        if num not in ('A', 'B', 'C'):
            errs = gb.find_errors(text, checker, s)
            for e in errs[:5]:
                print(f'❌ {num} {title}：{e}')
            bad += len(errs)
        fn = out_dir / f'{num}-{title.replace("/", "／")}.md'
        fn.write_text(f'# {num} {title}\n\n{text}\n', encoding='utf-8')
    print(f'✅ 補了 {len(results) - bad} 章（{bad} 個問題）')
    print(llm.stats())


if __name__ == '__main__':
    main()
