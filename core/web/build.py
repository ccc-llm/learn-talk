#!/usr/bin/env python3
"""產生網頁需要的 data.js：把每個語言的詞表、類頭、描述模板帶到前端。

用法：python core/web/build.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402


def build():
    out = {}
    for d in spec_mod.all_langs():
        s = spec_mod.Spec(d)
        words = []
        for cat in s.categories:
            for w in sorted(s.by_category().get(cat, []),
                            key=lambda x: (x.level != 'C', x.unit)):
                words.append({
                    'w': w.unit,
                    'lv': w.level,
                    'pos': w.pos,
                    'g': w.gloss,
                    'cat': cat,
                    'ex': w.example,
                })
        out[s.code] = {
            'name': s.name,
            'native': s.native,
            'unit': s.unit_kind,
            'script': s.script,
            'romanization': s.romanization,
            'target': s.target_reader,
            'words': words,
            'heads': s.heads,
            'desc': s.desc_templates,
            'replace': s.replace,
            'rules': [{'id': r.rid, 'text': r.text, 'ex': r.example} for r in s.rules],
        }
    path = ROOT / 'core' / 'web' / 'data.js'
    path.write_text('const LANGS = ' + json.dumps(out, ensure_ascii=False) + ';\n',
                    encoding='utf-8')
    total = sum(len(v['words']) for v in out.values())
    print(f'✅ {path}（{len(out)} 個語言、{total} 個詞）')


if __name__ == '__main__':
    build()
