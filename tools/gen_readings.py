#!/usr/bin/env python3
"""填上日韓詞表的羅馬字（ipa 欄），並用 LLM 產生日文漢字讀音表。

- 韓文：每個詞的 ipa ← RR 羅馬字（程式推導）
- 日文：純假名詞的 ipa ← Hepburn 羅馬字（程式推導）
- 日文漢字：每個漢字一個常用讀音 → langs/mini-japanese/data/readings.tsv
  （已存在的漢字不重查，可重複執行補齐）

用法：python tools/gen_readings.py        # 需要 NVIDIA_API_KEY（.env）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.romaji import hangul_romanize, is_kana_only, kana_to_romaji  # noqa: E402


def fill_tsv(path: Path, want_korean: bool):
    rows = [l.split('\t') for l in path.read_text(encoding='utf-8').splitlines()]
    head, data = rows[0], rows[1:]
    filled = 0
    for row in data:
        if len(row) >= 7 and not row[6]:
            row[6] = (hangul_romanize(row[0]) if want_korean
                      else kana_to_romaji(row[0]) if is_kana_only(row[0])
                      else '')
            if row[6]:
                filled += 1
    path.write_text('\n'.join('\t'.join(r) for r in [head] + data) + '\n',
                    encoding='utf-8')
    print(f'  {path.name}: 填了 {filled} 個')


def kanji_of(units: list[str]) -> set[str]:
    chars = set(''.join(units))
    return {c for c in chars if re.match(r'[\u4e00-\u9fff]', c)}


def gen_japanese_readings():
    path = ROOT / 'langs' / 'mini-japanese' / 'data' / 'words.tsv'
    units = [l.split('\t')[0]
             for l in path.read_text(encoding='utf-8').splitlines()[1:]]
    kanji = sorted(kanji_of(units))
    out = ROOT / 'langs' / 'mini-japanese' / 'data' / 'readings.tsv'
    have: dict[str, str] = {}
    if out.exists():
        for line in out.read_text(encoding='utf-8').splitlines():
            if '\t' in line:
                k, r = line.split('\t', 1)
                have[k] = r.strip()
    todo = [k for k in kanji
            if not re.fullmatch(r'[a-zāīūēō\-]{2,10}', have.get(k, ''))]
    print(f'日文漢字：共 {len(kanji)}，已有讀音 {len(kanji) - len(todo)}，待查 {len(todo)}')
    if todo:
        from core.llm import LLM
        llm = LLM(provider='nvidia', temperature=0.2, max_tokens=4096)
        chunks = [todo[i:i + 75] for i in range(0, len(todo), 75)]

        def ask(chunk):
            listing = '　'.join(chunk)
            return llm.chat(
                '下面每個日文漢字，各給一個最常用的讀音，用平文式羅馬字（Hepburn）。\n'
                '每行一個，格式：漢字 羅馬字\n'
                '規則：一行只有漢字和一個讀音，讀音全小寫、最長 8 個字母，'
                '讀音後面不准再寫任何字或說明。\n\n' + listing)

        import re as _re
        results = llm.batch(chunks, ask, workers=3)
        line_re = _re.compile(r'^([\u4e00-\u9fff])[\t:： ]+([a-zāīūēō\-]{1,10})(?:\s|$)')
        for r in results:
            if not isinstance(r, str):
                continue
            for line in r.splitlines():
                m = line_re.match(line.strip().lstrip('-*0123456789. '))
                if m and m.group(1) in todo:
                    have[m.group(1)] = m.group(2)
        out.write_text('\n'.join(f'{k}\t{have[k]}' for k in sorted(have)) + '\n',
                       encoding='utf-8')
        got = sum(1 for k in kanji if have.get(k))
        print(f'  readings.tsv：{got}/{len(kanji)} 個漢字有讀音')


def main():
    print('韓文：')
    fill_tsv(ROOT / 'langs' / 'mini-korean' / 'data' / 'words.tsv', want_korean=True)
    print('日文：')
    fill_tsv(ROOT / 'langs' / 'mini-japanese' / 'data' / 'words.tsv', want_korean=False)
    gen_japanese_readings()


if __name__ == '__main__':
    main()
