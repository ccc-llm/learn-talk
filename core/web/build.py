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
from core.romaji import hangul_romanize, kana_to_romaji  # noqa: E402
from core.web.voices import BROWSER_LANG, TTS_VOICES  # noqa: E402

import re  # noqa: E402


def rom_map(s, words) -> dict:
    """每個「字」的羅馬字（中文拼音、日文羅馬字、韓文 RR），給前端標 ruby。"""
    if s.script == 'latin':
        return {}
    if s.code == 'chinese':
        return {w['w']: w['ip'] for w in words if w['ip']}
    chars = sorted(set(''.join(w['w'] for w in words)))
    if s.code == 'japanese':
        readings: dict[str, str] = {}
        rp = s.dir / 'data' / 'readings.tsv'
        if rp.exists():
            for line in rp.read_text(encoding='utf-8').splitlines():
                if '\t' in line:
                    k, r = line.split('\t', 1)
                    readings[k] = r.strip()
        return {c: (readings.get(c, '') if re.match(r'[\u4e00-\u9fff]', c)
                    else kana_to_romaji(c)) for c in chars}
    if s.code == 'korean':
        return {c: hangul_romanize(c) for c in chars}
    return {}


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
                    'ip': w.ipa,
                })
        out[s.code] = {
            'name': s.name,
            'native': s.native,
            'unit': s.unit_kind,
            'script': s.script,
            'romanization': s.romanization,
            'target': s.target_reader,
            'browserLang': BROWSER_LANG.get(s.code, 'en-US'),
            'tts': TTS_VOICES.get(s.code, {}),
            'rom': rom_map(s, words),
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
