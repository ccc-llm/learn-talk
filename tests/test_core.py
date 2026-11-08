#!/usr/bin/env python3
"""核心引擎的測試（不需要網路）。

用法：python tests/test_core.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.lexicon import Lexicon  # noqa: E402

FAILS: list[str] = []


def ok(cond, msg):
    if cond:
        print(f'✅ {msg}')
    else:
        print(f'❌ {msg}')
        FAILS.append(msg)


def test_spec():
    print('\n== 規格載入 ==')
    langs = spec_mod.all_langs()
    ok(len(langs) == 5, f'有 5 個語言（{len(langs)}）')
    for d in langs:
        s = spec_mod.Spec(d)
        ok(len(s.words) > 0, f'{s.name}：{len(s.words)} 單位，{len(s.core)} 核心')
        ok(bool(s.categories), f'{s.name}：有 {len(s.categories)} 個類別')
        ok(bool(s.heads), f'{s.name}：有 {len(s.heads)} 個類頭')


def test_checker():
    print('\n== 檢查器 ==')
    cases = [
        ('chinese', '我家有一個 dog（會看家的小東西）。', True),
        ('chinese', '我昨天去醫院看病。', False),      # 院 不在字表
        ('chinese', '我昨天去看病的地方。', True),
        ('english', 'I went to the park yesterday.', True),
        ('english', 'I went to the hospital yesterday.', True),   # hospital 在詞表內
        ('english', 'I quantised the widgets yesterday.', False),  # 表外的詞
        ('english', 'I went to a place where doctors help sick people.', True),
        ('french', 'J\'ai mangé une pomme.', True),
        ('french', 'Je vais au marché demain.', True),
        ('french', 'I mangé une pomme.', False),
        ('japanese', '私は学生です。', True),
        ('japanese', '昨日学校に書きました。', True),
        ('japanese', '昨日学校に書いて。', False),      # て形
        ('korean', '제가 학생이에요.', True),
        ('korean', '어제 친구를 만났어요.', True),
        ('korean', '밥을 먹어요.', True),
    ]
    for lang, text, want_ok in cases:
        s = spec_mod.load(lang)
        c = Checker(s)
        errs = c.check(text)
        got = not errs
        ok(got == want_ok,
           f'{s.name}：{text[:26]!r} → {"✅ 通過" if got else "❌ " + str(errs[0])}')


def test_lexicon():
    print('\n== 詞典 ==')
    for d in spec_mod.all_langs():
        s = spec_mod.Spec(d)
        lex = Lexicon(s.dir / 'lexicon.tsv')
        c = Checker(s)
        problems = lex.validate(c)
        ok(not problems, f'{s.name}：詞典 {len(lex)} 列全部通過' +
           (f'（{len(problems)} 個問題）' if problems else ''))


def test_spec_md():
    print('\n== spec.md 與 prompts 一致 ==')
    import re
    for d in spec_mod.all_langs():
        s = spec_mod.Spec(d)
        p = s.dir / 'spec.md'
        if not p.exists():
            ok(False, f'{s.name}：spec.md 不存在')
            continue
        text = p.read_text(encoding='utf-8')
        m = re.search(r'## 附錄：完整詞表.*?```text\n(.*?)```', text, re.S)
        ok(m is not None, f'{s.name}：spec.md 有附錄詞表')
        if not m:
            continue
        words = set()
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if s.unit_kind == 'char':
                words.update(line)
            else:
                words.add(line.lower())
        ok(words == set(s.words), f'{s.name}：附錄詞表與 data/words.tsv 一致')
        sysmd = s.dir / 'prompts' / 'system.md'
        if sysmd.exists():
            t = sysmd.read_text(encoding='utf-8')
            m2 = re.search(r'## 1\. 詞表.*?```text\n(.*?)```', t, re.S)
            pw = set()
            if m2:
                for line in m2.group(1).splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if s.unit_kind == 'char':
                        pw.update(line)
                    else:
                        pw.add(line.lower())
            ok(pw == set(s.words), f'{s.name}：prompts/system.md 的詞表一致')


def main():
    test_spec()
    test_checker()
    test_lexicon()
    test_spec_md()
    print()
    if FAILS:
        print(f'❌ {len(FAILS)} 個測試失敗')
        sys.exit(1)
    print('✅ 全部通過')


if __name__ == '__main__':
    main()
