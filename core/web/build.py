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
from core.romaji import hangul_romanize, kana_table, kana_to_romaji  # noqa: E402
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


def extra_rom(s, lex) -> dict:
    """字表以外的讀音，讓「任意文字」也能標 ruby。

    - 中文：詞典「原文」欄會用到的漢字（逆向翻譯的對譯就是這些字）
    - 日文：完整的假名表（五十音→羅馬字）
    """
    if s.code == 'chinese':
        chars = set()
        for row in lex:
            chars |= set(re.findall(r'[\u4e00-\u9fff]', row.get('o', '')))
        if not chars:
            return {}
        try:
            from pypinyin import Style, pinyin
        except ImportError:
            return {}
        out = {}
        for ch in sorted(chars):
            out[ch] = ''.join(x[0] for x in pinyin(ch, style=Style.TONE))
        return out
    if s.code == 'japanese':
        return kana_table()
    return {}


def lexicon_data(s) -> tuple[list, dict]:
    """詞典列（靜態版查詞典、lookup_word 用）與反向對照表（受限說法 → 原文）。"""
    lex, rev = [], {}
    lp = s.dir / 'lexicon.tsv'
    if lp.exists():
        lines = lp.read_text(encoding='utf-8').splitlines()
        if lines and lines[0].split('\t')[:2] == ['原文', '受限說法']:
            for line in lines[1:]:
                col = line.split('\t')
                if len(col) >= 4:
                    row = {'o': col[0], 'm': col[1], 'w': col[2], 'n': col[3]}
                    lex.append(row)
                    rev[col[1].lower()] = col[0]
    return lex, rev


def system_prompt(s) -> str:
    """prompts/system.md 的 --- 主體（嚴格模式提示）。"""
    p = s.dir / 'prompts' / 'system.md'
    if not p.exists():
        return ''
    text = p.read_text(encoding='utf-8')
    m = re.search(r'\n---\n(.*?)(?:\n---\n|$)', text, re.S)
    return (m.group(1) if m else text).strip()


def fast_prompt(s, by=None) -> str:
    """快速模式提示：字表＋外來語規則，不用工具。"""
    by = by or s.by_category()
    lines = [f'你是{s.name}老師。當我和你對話時，你必須用{s.name}回答。', '',
             f'# {s.name}字表', '']
    for cat in s.categories:
        ws = by.get(cat, [])
        units = (''.join(w.unit for w in ws) if s.unit_kind == 'char'
                 else '、'.join(w.unit for w in ws))
        lines += [f'## {cat}', units, '']
    lines += ['# 規則',
              '- 只有字表內的字（詞）可以直接用。',
              '- 字表外的通用概念：用「描述＋類頭」說明。',
              '- 專名、品牌、物種：用外來語（原文寫出），第一次出現時加括號說明。',
              '- 數字用阿拉伯數字。',
              '- 不用檢查工具，直接回答。']
    return '\n'.join(lines)


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
        lex, rev = lexicon_data(s)
        rom = rom_map(s, words)
        for ch, r in extra_rom(s, lex).items():
            rom.setdefault(ch, r)
        out[s.code] = {
            'name': s.name,
            'native': s.native,
            'unit': s.unit_kind,
            'script': s.script,
            'romanization': s.romanization,
            'target': s.target_reader,
            'browserLang': BROWSER_LANG.get(s.code, 'en-US'),
            'tts': TTS_VOICES.get(s.code, {}),
            'rom': rom,
            'rev': rev,
            'lex': lex,
            'sys': system_prompt(s),
            'fast': fast_prompt(s, s.by_category()),
            'words': words,
            'heads': s.heads,
            'desc': s.desc_templates,
            'replace': s.replace,
            'rules': [{'id': r.rid, 'text': r.text, 'ex': r.example} for r in s.rules],
        }
    payload = 'const LANGS = ' + json.dumps(out, ensure_ascii=False) + ';\n'
    total = sum(len(v['words']) for v in out.values())
    for path in (ROOT / 'core' / 'web' / 'data.js',
                 ROOT / 'core' / 'staticweb' / 'data.js'):
        path.write_text(payload, encoding='utf-8')
        print(f'✅ {path}（{len(out)} 個語言、{total} 個詞）')


if __name__ == '__main__':
    build()
