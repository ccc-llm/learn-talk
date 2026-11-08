"""共用的語言規格資料結構與載入器。

每個語言的資料放在 langs/<lang>/ 底下：

    meta.json          語言的中文名、程式碼、寫作單位（char/word）、script
    data/words.tsv     詞表：unit / level / pos / gloss / category
    data/heads.tsv     類頭（描述的最後一個詞）
    data/desc.tsv      描述模板
    data/replace.tsv   禁用詞 → 替代說法
    data/irregular.tsv 不規則形式
    data/affix.tsv     允許的字首字尾
    data/gram.tsv      語法規則
    data/proper.tsv    常見專有名詞（免說明）

詞表是唯一的權威來源：spec.md、prompts/system.md、lexicon.tsv、網頁都由它產生或被它檢查。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS_DIR = ROOT / 'langs'

# 資料檔第一行的欄位標題
_HEADER_TOKENS = {'unit', 'word', 'head', 'template', 'affix', 'lemma', 'rid', '原文'}


@dataclass
class Word:
    unit: str          # 書寫單位：中文是「字」，其他是「詞」
    level: str         # C = 核心層，E = 擴充層
    pos: str           # 詞性：n / v / adj / adv / det / pron / num / gram / ...
    gloss: str         # 中文解釋
    category: str      # 大類（代詞、時間、動作…）
    forms: list[str] = field(default_factory=list)   # 可直接寫出的其他形式
    example: str = ''  # 例子（會被檢查程式驗證）
    ipa: str = ''      # 音標
    stem: str = ''     # 詞幹（韓文動詞／形容詞用）

    @property
    def key(self) -> str:
        return self.unit.lower()


@dataclass
class Rule:
    rid: str
    kind: str          # grammar / replace / desc
    text: str
    example: str = ''
    note: str = ''


class Spec:
    """一個語言的完整規格。"""

    def __init__(self, lang_dir: Path):
        self.dir = lang_dir
        self.code = lang_dir.name.replace('mini-', '')
        meta_path = lang_dir / 'meta.json'
        meta = json.loads(meta_path.read_text(encoding='utf-8')) if meta_path.exists() else {}
        self.name: str = meta.get('name', lang_dir.name)
        self.native: str = meta.get('native', '')
        self.unit_kind: str = meta.get('unit', 'word')       # char / word
        self.script: str = meta.get('script', 'latin')       # han / latin / kana / hangul
        self.romanization: str = meta.get('romanization', '')
        self.target_reader: str = meta.get('target_reader', '')

        self.words: dict[str, Word] = {}
        self.categories: list[str] = []
        self.heads: list[str] = []
        self.desc_templates: list[str] = []
        self.replace: dict[str, str] = {}
        self.irregular: dict[str, list[str]] = {}
        self.affixes: list[dict] = []
        self.rules: list[Rule] = []
        self.proper: set[str] = set()
        self._common_outside: list[str] | None = None
        self._load()

    # ── 載入 ────────────────────────────────────────────────────────────────
    def _tsv(self, name) -> list[list[str]]:
        p = self.dir / 'data' / name
        if not p.exists():
            return []
        out = []
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            out.append([c.strip() for c in line.split('\t')])
        # 每個資料檔的第一行都是欄位標題
        if out and _HEADER_TOKENS & set(out[0][:1]):
            out = out[1:]
        return out

    def _load(self):
        for row in self._tsv('words.tsv'):
            unit, level, pos, gloss, cat = (row + [''] * 5)[:5]
            w = Word(unit, level or 'C', pos, gloss, cat or '其他')
            if len(row) > 5:
                w.example = row[5]
            if len(row) > 6:
                w.ipa = row[6]
            if len(row) > 7:
                w.stem = row[7]
            self.words[w.key] = w
            if w.category and w.category not in self.categories:
                self.categories.append(w.category)
        for row in self._tsv('heads.tsv'):
            self.heads.append(row[0])
        for row in self._tsv('desc.tsv'):
            self.desc_templates.append(row[0])
        for row in self._tsv('replace.tsv'):
            if len(row) >= 2:
                self.replace[row[0].lower()] = row[1]
        for row in self._tsv('irregular.tsv'):
            if len(row) >= 2:
                self.irregular[row[0].lower()] = [f.lower() for f in row[1].split() if f]
        for row in self._tsv('affix.tsv'):
            self.affixes.append({'affix': row[0], 'kind': row[1] if len(row) > 1 else '',
                                 'meaning': row[2] if len(row) > 2 else ''})
        for row in self._tsv('gram.tsv'):
            self.rules.append(Rule(row[0], 'grammar', row[1] if len(row) > 1 else '',
                                   row[2] if len(row) > 2 else '', row[3] if len(row) > 3 else ''))
        for row in self._tsv('proper.tsv'):
            if row[0]:
                self.proper.add(row[0].lower())
        # 韓文：動詞／形容詞的形式表（unit, present, past, future, topic）
        self.ko_forms: dict[str, list[str]] = {}
        for row in self._tsv('ko_forms.tsv'):
            if len(row) >= 5:
                unit = row[0].strip()
                self.ko_forms[unit] = [r.strip() for r in row[1:5]]
        # 日文：動詞的形式表（unit, て, た, ない, たい, ます）
        self.ja_forms: dict[str, list[str]] = {}
        for row in self._tsv('ja_forms.tsv'):
            if len(row) >= 6:
                unit = row[0].strip()
                self.ja_forms[unit] = [r.strip() for r in row[1:6]]
        self.ja_adj_forms: dict[str, list[str]] = {}
        for row in self._tsv('ja_adj_forms.tsv'):
            if len(row) >= 4:
                unit = row[0].strip()
                self.ja_adj_forms[unit] = [r.strip() for r in row[1:4]]

    # ── 查詢 ────────────────────────────────────────────────────────────────
    @property
    def vocab(self) -> set[str]:
        return set(self.words)

    @property
    def core(self) -> set[str]:
        return {k for k, w in self.words.items() if w.level == 'C'}

    @property
    def forbidden(self) -> list[str]:
        """這個語言「不要用」的結構（寫進 LLM 系統提示詞）。"""
        p = self.dir / 'data' / 'forbidden.txt'
        if not p.exists():
            return []
        return [w.strip() for w in p.read_text(encoding='utf-8').splitlines()
                if w.strip() and not w.startswith('#')]

    @property
    def common_outside(self) -> list[str]:
        """詞表外最常見的詞（提醒模型不要不小心寫出來）。"""
        if self._common_outside is not None:
            return self._common_outside
        p = self.dir / 'data' / 'common_outside.txt'
        out: list[str] = []
        if p.exists():
            out = [w.strip() for w in p.read_text(encoding='utf-8').splitlines()
                   if w.strip() and not w.startswith('#')]
        self._common_outside = out
        return out

    def in_vocab(self, unit: str) -> bool:
        return unit.lower() in self.words

    def category_of(self, unit: str) -> str:
        w = self.words.get(unit.lower())
        return w.category if w else ''

    def gloss(self, unit: str) -> str:
        w = self.words.get(unit.lower())
        return w.gloss if w else ''

    def by_category(self) -> dict[str, list[Word]]:
        out: dict[str, list[Word]] = {}
        for w in self.words.values():
            out.setdefault(w.category, []).append(w)
        return out

    # ── 產生規格文件 ───────────────────────────────────────────────────────
    def appendix_block(self) -> str:
        """權威詞表（```text 區塊的內容）。

        漢字語言：同一類的字接在同一行（比較好讀、比較省 token）。
        詞語言：一行一個詞。
        """
        lines = []
        for cat in self.categories:
            ws = self.by_category().get(cat, [])
            if not ws:
                continue
            ws = sorted(ws, key=lambda w: (w.level != 'C', w.unit))
            lines.append(f'# {cat}')
            if self.unit_kind == 'char':
                lines.append(''.join(w.unit for w in ws))
            else:
                lines.extend(w.unit for w in ws)
        return '\n'.join(lines)

    def word_table_rows(self) -> list[str]:
        rows = []
        has_ex = any(w.example for w in self.words.values())
        for cat in self.categories:
            for w in sorted(self.by_category().get(cat, []), key=lambda w: (w.level != 'C', w.unit)):
                base = f'| {w.unit} | {w.level} | {w.pos} | {w.gloss} | {w.category} |'
                if has_ex:
                    base += f' {w.example} |'
                rows.append(base)
        return rows


ALIAS = {
    'zh': 'mini-chinese', 'cn': 'mini-chinese', 'chinese': 'mini-chinese',
    'en': 'mini-english', 'english': 'mini-english',
    'fr': 'mini-french', 'french': 'mini-french',
    'ja': 'mini-japanese', 'jp': 'mini-japanese', 'japanese': 'mini-japanese',
    'ko': 'mini-korean', 'kr': 'mini-korean', 'korean': 'mini-korean',
}


def load(lang: str) -> Spec:
    """lang 可以是 'zh'、'chinese'、'mini-chinese'。"""
    cands = [ALIAS.get(lang, f'mini-{lang}'), lang]
    for c in cands:
        d = LANGS_DIR / c
        if d.exists():
            return Spec(d)
    known = sorted(p.name for p in LANGS_DIR.iterdir() if p.is_dir()) if LANGS_DIR.exists() else []
    raise SystemExit(f'找不到語言「{lang}」。已有：{", ".join(known) or "（無）"}')


def all_langs() -> list[Path]:
    if not LANGS_DIR.exists():
        return []
    return sorted(p for p in LANGS_DIR.iterdir() if (p / 'meta.json').exists())
