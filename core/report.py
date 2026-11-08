"""自我檢查報告：詞表有沒有重複、各處的詞表是否一致、例句是否通過。"""
from __future__ import annotations

import re

from .checker import Checker
from .lexicon import Lexicon


def _appendix_block(text: str) -> list[str]:
    m = re.search(r'## 附錄：完整詞表.*?```text\n(.*?)```', text, re.S)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines() if l.strip() and not l.startswith('#')]


def _snippets(text: str):
    """抓 spec.md 裡面所有必須是受限語言的片段。"""
    lines = text.splitlines()
    header = None
    for no, line in enumerate(lines, 1):
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            if header is None:
                header = cells
            else:
                for name, cell in zip(header, cells):
                    if name in ('例子', '例句', '受限說法'):
                        yield no, re.sub(r'（.*?）', '', cell)
        else:
            header = None


def report(spec) -> bool:
    ok = True
    c = Checker(spec)
    print(f'== {spec.name} ==')
    print(f'詞表：{len(spec.words)} 單位（核心 {len(spec.core)} ＋ 擴充 {len(spec.words) - len(spec.core)}）')

    spec_md = spec.dir / 'spec.md'
    if spec_md.exists():
        text = spec_md.read_text(encoding='utf-8')
        ap = _appendix_block(text)
        # 漢字語言：同一類的字接在同一行，要拆開比對
        if spec.unit_kind == 'char':
            ap = list(''.join(ap))
        dup = sorted({w for w in ap if ap.count(w) > 1})
        if dup:
            print(f'❌ spec.md 詞表有重複：{", ".join(dup)}')
            ok = False
        else:
            print(f'✅ spec.md 附錄詞表 {len(ap)} 單位，不重複')
        if {w.lower() for w in ap} != {k.lower() for k in spec.words}:
            extra = sorted({w for w in ap if w.lower() not in {k.lower() for k in spec.words}})
            lack = sorted({k for k in spec.words if k.lower() not in {w.lower() for w in ap}})
            print(f'❌ spec.md 與 data/words.tsv 不一致：多 {extra[:10]}　少 {lack[:10]}')
            ok = False
        else:
            print('✅ spec.md 與 data/words.tsv 一致')
        n = 0
        for no, s in _snippets(text):
            if not s.strip():
                continue
            n += 1
            for e in c.check(s):
                print(f'❌ spec.md:{no} {e}　→　{s[:80]}')
                ok = False
        print(f'✅ 檢查了 {n} 段例句')
    else:
        print('⚠️  沒有 spec.md（先跑 python -m core.cli build）')

    sysmd = spec.dir / 'prompts' / 'system.md'
    if sysmd.exists():
        t = sysmd.read_text(encoding='utf-8')
        s = spec
        m = re.search(r'## 1\. 詞表.*?```text\n(.*?)```', t, re.S)
        if m:
            pw = set()
            for line in m.group(1).splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # 漢字語言：同一類的字接在同一行，要拆開
                if s.unit_kind == 'char':
                    pw.update(line)
                else:
                    pw.add(line.lower())
            if pw != set(spec.words):
                print('❌ prompts/system.md 的詞表和 data/words.tsv 不一樣，請重新 build')
                ok = False
            else:
                print('✅ prompts/system.md 的詞表一致')

    lex = Lexicon(spec.dir / 'lexicon.tsv')
    if len(lex):
        problems = lex.validate(c)
        if problems:
            ok = False
            for p in problems[:20]:
                print(f'❌ {p}')
        print(f'{"❌" if problems else "✅"} 詞典 {len(lex)} 列')

    print('✅ 全部通過' if ok else '❌ 有錯誤')
    return ok
