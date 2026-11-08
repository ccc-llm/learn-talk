"""詞典（lexicon.tsv）與反向翻譯。

lexicon.tsv 欄位：原文 / 受限語言說法 / 方式（本詞|描述|外來語）/ 說明
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

FIELDS = ['原文', '受限說法', '方式', '說明']
WAYS = ('本詞', '描述', '外來語')


class Lexicon:
    def __init__(self, path: Path):
        self.path = path
        self.rows: list[dict] = []
        if path.exists():
            with open(path, encoding='utf-8') as f:
                self.rows = list(csv.DictReader(f, delimiter='\t'))

    def __len__(self):
        return len(self.rows)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, delimiter='\t')
            w.writeheader()
            for r in self.rows:
                w.writerow({k: r.get(k, '') for k in FIELDS})

    def add(self, source: str, mini: str, way: str, note: str = ''):
        self.rows.append({'原文': source, '受限說法': mini, '方式': way, '說明': note})

    def validate(self, checker) -> list[str]:
        """每一列的受限說法都要通過檢查。回傳問題清單。"""
        problems = []
        seen = set()
        for i, r in enumerate(self.rows, 2):
            src = r['原文'].strip()
            mini = r['受限說法'].strip()
            way = r['方式'].strip()
            if not src:
                continue
            if src in seen:
                problems.append(f'第 {i} 行：{src} 重複')
            seen.add(src)
            if way not in WAYS:
                problems.append(f'第 {i} 行：方式必須是 {"／".join(WAYS)}')
                continue
            if way == '本詞':
                if checker.spec.unit_kind == 'char':
                    # 漢字語言：「本詞」＝每個字都在字表內
                    bad = [ch for ch in mini if not ('\u4e00' <= ch <= '\u9fff') or ch.lower() not in checker.spec.vocab]
                    if bad:
                        problems.append(f'第 {i} 行：{src} 標成本詞，但 {mini} 用了字表外的字 {"".join(bad)}')
                else:
                    # 拉丁語言：允許冠詞前綴（un docteur / la rivière）
                    head = mini
                    for art in ('le ', 'la ', 'les ', 'un ', 'une ', 'des ', 'du ', "de l'", "d'"):
                        if head.lower().startswith(art):
                            head = head[len(art):]
                            break
                    if head.lower() not in checker.spec.vocab and head.lower() not in checker.accepted:
                        problems.append(f'第 {i} 行：{src} 標成本詞，但 {mini} 不在詞表內')
                continue
            if way == '外來語':
                if not r['說明'].strip():
                    problems.append(f'第 {i} 行：{src} 是外來語，必須有說明')
                    continue
                errs = checker.check(r['說明'], allow_bare_loanword=True)
                for e in errs:
                    problems.append(f'第 {i} 行（{src} 的說明）{e}')
                continue
            errs = checker.check(mini, allow_bare_loanword=True)
            for e in errs:
                problems.append(f'第 {i} 行（{src}）{e}　→　{mini}')
        return problems


SKIP = {'a', 'an', 'the', 'is', 'are', 'be', 'of', 'in', 'on', 'and', 'or', 'not',
        'very', 'some', 'more', 'most', 'one', 'two', 'many', 'much', 'few', 'it',
        'he', 'she', 'they', 'we', 'you', 'i'}


class Reverser:
    """受限語言 → 一般語言：用詞典把描述／外來語換回去。"""

    def __init__(self, lexicon: Lexicon, spec):
        self.spec = spec
        table: dict[str, str] = {}
        for r in lexicon.rows:
            mini = r['受限說法'].strip()
            src = r['原文'].strip()
            if not mini or not src or mini.lower() in SKIP or mini == src:
                continue
            table.setdefault(mini.lower(), src)
        rows = sorted(table.items(), key=lambda kv: -len(kv[0]))
        self.regex = re.compile('|'.join(re.escape(k) for k, _ in rows)) if rows else None
        self.table = table

    def to_source(self, text: str) -> str:
        if not self.regex:
            return text
        notes = []

        def stash(m):
            notes.append(m.group(1))
            return f'\x00{len(notes) - 1}\x00'

        text = re.sub(r'\(([^()]*)\)', stash, text)
        text = self.regex.sub(lambda m: self.table.get(m.group(0).lower(), m.group(0)), text)
        for i, n in enumerate(notes):
            text = text.replace(f'\x00{i}\x00', f' ({n})')
        return text
