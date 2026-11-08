#!/usr/bin/env python3
"""把 LLM 產生的候選詞表校訂成正式詞表。

每個語言在 tools/curated/<lang>.py 裡定義：
    CORE    核心層詞（必學）
    DROP    刪掉（太難寫、太抽象、能用其他詞說出來）
    EXTRA   候選裡沒有但一定要有的詞

用法：python tools/curate.py --lang fr
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ALIAS = {'fr': 'mini-french', 'french': 'mini-french',
         'ja': 'mini-japanese', 'japanese': 'mini-japanese',
         'ko': 'mini-korean', 'korean': 'mini-korean',
         'en': 'mini-english', 'english': 'mini-english',
         'zh': 'mini-chinese', 'chinese': 'mini-chinese'}

CATS = ['pron', 'gram', 'num', 'time', 'place', 'nature', 'verb', 'adj',
        'noun', 'social', 'abstr']
CAT_NAMES = {
    'pron': '代詞・指示', 'gram': '語法（功能詞）', 'num': '數量・比例',
    'time': '時間', 'place': '方位・地點', 'nature': '自然・天氣',
    'verb': '動作', 'adj': '性質', 'noun': '事物', 'social': '社交・人',
    'abstr': '抽象概念',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    ap.add_argument('--provider', default='minimax')
    a = ap.parse_args()

    mod_name = ALIAS.get(a.lang, a.lang).replace('mini-', '')
    mod = importlib.import_module(f'tools.curated.{mod_name}')
    core = {w.lower() for w in mod.CORE}
    drop = {w.lower() for w in mod.DROP}
    extra = mod.EXTRA          # [(word, pos, gloss, category)]
    fixes = getattr(mod, 'FIXES', {})   # {word: (pos, gloss)}

    lang_dir = ROOT / 'langs' / ALIAS.get(a.lang, f'mini-{a.lang}')
    data = lang_dir / 'data'

    # 收集候選
    cand: dict[str, list[tuple[str, str]]] = {}
    for f in CATS:
        p = data / f'_cand_{f}.tsv'
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            c = line.split('\t')
            while len(c) < 3:
                c.append('')
            w, pos, gloss = c[0].strip(), c[1].strip(), c[2].strip()
            if not w:
                continue
            cand.setdefault(f, []).append((w, pos, gloss))

    rows = ['unit\tlevel\tpos\tgloss\tcategory\texample\tipa\tstem']
    seen: set[str] = set()
    n_c = n_e = 0
    ko_forms = {}
    kof = lang_dir / 'data' / 'ko_forms.tsv'
    if kof.exists():
        for line in kof.read_text(encoding='utf-8').splitlines()[1:]:
            c = [x.strip() for x in line.split('\t')]
            if len(c) >= 5:
                ko_forms[c[0]] = c[1:5]

    def add(w, pos, gloss, cat):
        nonlocal n_c, n_e
        k = w.lower()
        if k in seen or k in drop:
            return
        seen.add(k)
        level = 'C' if k in core else 'E'
        if level == 'C':
            n_c += 1
        else:
            n_e += 1
        stem = '|'.join(ko_forms[w]) if ko_forms.get(w) else ''
        rows.append(f'{w}\t{level}\t{pos}\t{gloss}\t{CAT_NAMES[cat]}\t\t\t{stem}')

    for f in CATS:
        for w, pos, gloss in cand.get(f, []):
            if pos in fixes:
                pos, gloss = fixes[pos]
            # 日文：動詞只留「ます形」，原形由 core/japanese.py 推導
            if a.lang in ('ja', 'japanese') and pos.startswith('v') and not w.endswith('ます'):
                continue
            add(w, pos, gloss, f)
    for item in extra:
        w, pos, gloss, cat = item[0], item[1], item[2], item[3]
        stem = item[4] if len(item) > 4 else ''
        k = w.lower()
        if k in seen or k in drop:
            continue
        seen.add(k)
        level = 'C' if k in core else 'E'
        if level == 'C':
            n_c += 1
        else:
            n_e += 1
        rows.append(f'{w}\t{level}\t{pos}\t{gloss}\t{CAT_NAMES[cat]}\t\t\t{stem}')

    (data / 'words.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'✅ {lang_dir.name} 詞表：核心 {n_c} ＋ 擴充 {n_e} ＝ {n_c + n_e} 詞')


if __name__ == '__main__':
    main()
