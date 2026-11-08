#!/usr/bin/env python3
"""把 mini-lang 的 Mini-English 規格遷移成 learn-talk 的 langs/mini-english/。

用法：python tools/migrate_english.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path('/Users/Shared/ccc/project/mini-lang/mini-english')
DST = ROOT / 'langs' / 'mini-english'

CATS = [
    ('pron', '代詞・指示'), ('gram', '語法（功能詞）'), ('num', '數量・比例'),
    ('time', '時間'), ('place', '方位・地點'), ('nature', '自然・天氣'),
    ('verb', '動作'), ('adj', '性質'), ('noun', '事物'), ('social', '社交・人'),
    ('abstr', '抽象概念'),
]


def main():
    if not SRC.exists():
        sys.exit(f'找不到來源：{SRC}')
    data = SRC / 'data'
    doc_text = (SRC / 'mini-english.md').read_text(encoding='utf-8')
    (DST / 'data').mkdir(parents=True, exist_ok=True)
    (DST / 'prompts').mkdir(parents=True, exist_ok=True)

    (DST / 'meta.json').write_text(json.dumps({
        'name': 'Mini-English',
        'native': '簡易英文',
        'unit': 'word',
        'script': 'latin',
        'romanization': 'ipa',
        'target_reader': '母語不是英文的外國人',
        'source': 'mini-lang/mini-english',
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    # 詞表
    extra = parse_word_tables(doc_text)
    rows = ['unit\tlevel\tpos\tgloss\tcategory\texample\tipa']
    seen = set()
    for f, cat in CATS:
        p = data / f'{f}.tsv'
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            c = [x.strip() for x in line.split('\t')]
            while len(c) < 4:
                c.append('')
            w, level, pos, zh = c[0], c[1] or 'C', c[2], c[3]
            if not w or w.lower() in seen:
                continue
            seen.add(w.lower())
            ex, ipa = extra.get(w.lower(), ('', ''))
            rows.append(f'{w}\t{level}\t{pos}\t{zh}\t{cat}\t{ex}\t{ipa}')
    (DST / 'data' / 'words.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'詞表 {len(rows) - 1} 詞')

    # 類頭
    heads = []
    p = data / 'head.tsv'
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            if line.strip():
                heads.append(line.split('\t')[0].strip())
    (DST / 'data' / 'heads.tsv').write_text(
        'head\tgloss\n' + '\n'.join(f'{h}\t' for h in heads) + '\n', encoding='utf-8')
    print(f'類頭 {len(heads)} 個')

    # 描述模板
    desc = ['a place where ...', 'a person who ...', 'a thing that ...',
            'a kind of ...', 'the place where ... happens', 'a thing for ...']
    (DST / 'data' / 'desc.tsv').write_text(
        'template\tgloss\n' + '\n'.join(f'{d}\t' for d in desc) + '\n', encoding='utf-8')

    # 禁用詞
    rep = []
    p = data / 'replace.tsv'
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            c = [x.strip() for x in line.split('\t')]
            if len(c) >= 2:
                rep.append((c[0], c[1]))
    (DST / 'data' / 'replace.tsv').write_text(
        'word\treplace\n' + '\n'.join(f'{k}\t{v}' for k, v in rep) + '\n', encoding='utf-8')
    print(f'禁用詞 {len(rep)} 條')

    # 不規則形式
    irr = []
    p = data / 'irregular.tsv'
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            c = [x.strip() for x in line.split('\t')]
            if len(c) >= 2:
                irr.append((c[0], ' '.join(c[1:])))
    (DST / 'data' / 'irregular.tsv').write_text(
        'lemma\tforms\n' + '\n'.join(f'{k}\t{v}' for k, v in irr) + '\n', encoding='utf-8')
    print(f'不規則形式 {len(irr)} 條')

    # 字首字尾
    aff = []
    p = data / 'affix.tsv'
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            c = [x.strip() for x in line.split('\t')]
            if len(c) >= 3:
                aff.append((c[0], c[1], c[2]))
    (DST / 'data' / 'affix.tsv').write_text(
        'affix\tkind\tmeaning\n' + '\n'.join(f'{a}\t{b}\t{c}' for a, b, c in aff) + '\n',
        encoding='utf-8')

    # 語法規則：從 mini-english.md 的規則表抓
    doc = doc_text
    rules = parse_grammar(doc)
    g = ['rid\ttext\texample\tnote']
    for rid, text, ex in rules:
        g.append(f'{rid}\t{text}\t{ex}\t')
    (DST / 'data' / 'gram.tsv').write_text('\n'.join(g) + '\n', encoding='utf-8')
    print(f'語法規則 {len(rules)} 條')

    # 專有名詞
    proper = []
    p = SRC / 'web' / 'crosscheck.py'
    if p.exists():
        t = p.read_text(encoding='utf-8')
        m = re.search(r'PROPER\s*=\s*\{(.*?)\}', t, re.S)
        if m:
            proper = [x.strip().strip("'\"") for x in m.group(1).replace('\n', '').split(',')
                      if x.strip()]
    if not proper:
        proper = ['paris', 'china', 'japan', 'korea', 'taiwan', 'india', 'england',
                  'france', 'germany', 'italy', 'spain', 'russia', 'canada', 'australia',
                  'brazil', 'mexico', 'london', 'tokyo', 'beijing', 'shanghai',
                  'hong kong', 'taipei', 'seoul', 'new york', 'osaka', 'kyoto',
                  'europe', 'asia', 'africa', 'america', 'english', 'french', 'german',
                  'spanish', 'italian', 'russian', 'british']
    (DST / 'data' / 'proper.tsv').write_text(
        'word\tgloss\n' + '\n'.join(f'{p_}\t' for p_ in proper) + '\n', encoding='utf-8')

    # 詞典
    lex = (SRC / 'lexicon.tsv').read_text(encoding='utf-8').splitlines()
    out = ['原文\t受限說法\t方式\t說明']
    for line in lex[1:]:
        if not line.strip():
            continue
        c = [x.strip() for x in line.split('\t')]
        while len(c) < 4:
            c.append('')
        eng, mini, way, note = c[0], c[1], c[2], c[3]
        way = {'本詞': '本詞', '描述': '描述', '外來詞': '外來語'}.get(way, '描述')
        out.append(f'{eng}\t{mini}\t{way}\t{note}')
    (DST / 'lexicon.tsv').write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'詞典 {len(out) - 1} 列')


def parse_word_tables(doc: str) -> dict:
    """從 mini-english.md 第 2 節的表格抓 (例子, IPA)。"""
    out: dict[str, tuple[str, str]] = {}
    sec = doc[doc.index('## 2. 詞表'):doc.index('## 3.')]
    header = None
    for line in sec.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if all(re.fullmatch(r':?-+:?', c) for c in cells):
            continue
        if header is None:
            header = cells
            continue
        if '詞' not in header or 'IPA' not in header:
            continue
        row = dict(zip(header, cells))
        w = row.get('詞', '').strip()
        if not w:
            continue
        ipa = row.get('IPA', '').strip().strip('/')
        ex = row.get('例子', '').strip()
        if ex.startswith('（') and ex.endswith('）'):
            ex = ''
        out[w.lower()] = (ex, ipa)
    return out


def parse_grammar(doc: str):
    """抓 mini-english.md 裡「### 規則 N　標題」與其例句。"""
    rules = []
    start = doc.find('## 5. 語法')
    end = doc.find('## 6. ')
    if start < 0:
        start, end = 0, len(doc)
    sec = doc[start:end]
    parts = re.split(r'\n###\s*規則\s*(\d+)', sec)
    for i in range(1, len(parts) - 1, 2):
        rid = parts[i]
        body = parts[i + 1]
        title = body.split('\n', 1)[0].strip()
        ex = ''
        m = re.search(r'```en\n(.*?)```', body, re.S)
        if m:
            ex = ' / '.join(x.strip() for x in m.group(1).splitlines() if x.strip())
        rules.append((rid, title, ex))
    return rules


if __name__ == '__main__':
    main()
