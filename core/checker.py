"""通用檢查器：這段文字是不是合法的受限語言。

規則（所有語言共用）：
  1. 每個單位都要在詞表內，或是可以由詞表推導（屈折、字首字尾）。
  2. 表外的詞必須是「外來語」：第一次出現時要���括號說明，說明本身也要用受限語言寫。
  3. 禁用詞（spec.replace）要改用替代說法。
  4. 描述必須符合該語言的描述模板，並且以類頭結尾。
  5. 數字用阿拉伯數字；標點與單位符號另外處理。

用法：
    from core.checker import Checker
    c = Checker(spec)
    errors = c.check('...')
"""
from __future__ import annotations

import re

from . import korean, morph
from .tokenizer import get as get_tokenizer


PAREN = re.compile(r'\(([^()]*)\)')
FULLPAREN = re.compile(r'（([^（）]*)）')
SPEAKER = re.compile(r'^\s*[^\s:：]{1,12}[:：]\s*')

# 國際單位符號：到處都可以用，不必說明
UNITS = {'km', 'kg', 'g', 'm', 'cm', 'mm', 'ml', 'l', 'kmh', 'kph', 'mph',
         'c', 'f', '°c', '°f', 'hz', 'kb', 'mb', 'gb', 'tb', 'usd', 'eur', 'jpy',
         'rmb', 'nt', 'kw', 'v', 'w', 'sec', 'min', 'hr'}


class Error:
    __slots__ = ('kind', 'msg', 'token')

    def __init__(self, kind, msg, token=''):
        self.kind = kind
        self.msg = msg
        self.token = token

    def __str__(self):
        return f'{self.kind}：{self.msg}'

    def __repr__(self):
        return f'<Error {self.kind} {self.msg}>'


class Checker:
    def __init__(self, spec):
        self.spec = spec
        self.accepted = morph.accepted_forms(spec)
        self.tok = get_tokenizer(spec.script, spec.vocab | self.accepted)
        self.tok = get_tokenizer(spec.script, spec.vocab | self.accepted)
        self.heads = {h.lower() for h in spec.heads}
        # 切分用的「詞」集合：詞表 + 可接受形式 + 詞表外但常見的詞幹
        # （日文要能切出「大きく」這種形容詞的連用形，所以要包含原形）
        self.segmentable = spec.vocab | self.accepted

    # ── 對外 ────────────────────────────────────────────────────────────────
    def check(self, text: str, defined=None, in_paren=False, allow_bare_loanword=False):
        """回傳 [Error]。

        allow_bare_loanword：允許沒有括號說明的外來語（用於詞典的描述欄、說明欄，
        那些欄位本身就是「解釋」，不需要再自我說明）。
        """
        spec = self.spec
        if defined is None:
            defined = set()
        errors: list[Error] = []
        text = text.strip()
        if not text:
            return errors

        # 括號：說明本身要檢查，但裡面的外來語不用再說明
        paren_spans = [(m.start(), m.end()) for m in PAREN.finditer(text)]
        paren_spans += [(m.start(), m.end()) for m in FULLPAREN.finditer(text)]

        def in_paren_at(pos):
            return any(a <= pos < b for a, b in paren_spans)

        # 多字禁用詞先抓，抓到後整段跳過
        phrase_spans = []
        for phrase in sorted((p for p in spec.replace if ' ' in p or any('　' <= c <= '鿿' for c in p)),
                             key=len, reverse=True):
            for m in re.finditer(re.escape(phrase), text, re.I):
                errors.append(Error('禁用詞', f'「{m.group(0)}」是禁用詞，改用「{spec.replace[phrase.lower()]}」',
                                    m.group(0)))
                phrase_spans.append((m.start(), m.end()))

        # 括號前的專有名詞 → 已說明
        for m in re.finditer(r'([A-Za-z\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af][\w\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]*(?:\s+[A-Za-z\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]+)*)\s*[（(]', text):
            for w in m.group(1).split():
                defined.add(w.lower())

        for pos, tok, kind in self.tok.tokens(text):
            par = in_paren_at(pos)
            if any(a <= pos < b for a, b in phrase_spans):
                continue
            if tok[0].isdigit():
                continue
            if not tok[0].isalnum():
                continue

            low = tok.lower()
            if low in UNITS:
                continue
            # 非漢字語言：漢字是外來語（例如用中文解釋的句子），不檢查
            if spec.script != 'han' and re.match(r'[\u4e00-\u9fff]', tok):
                continue
            # 中文：每個漢字一個單位；漢字之外的拉丁字母＝外來語
            if spec.unit_kind == 'char':
                if low in spec.vocab:
                    continue
                if re.match(r'[A-Za-z]', tok):
                    pass          # 外來語，往下走
                else:
                    errors.append(Error('未知詞', f'「{tok}」不在字表內（用描述或外來語）', tok))
                    continue

            if low in spec.vocab or low in self.accepted:
                # 日文：て・た・ない・たい 形式不合規，要特別提示
                if spec.script == 'kana':
                    bad = self._ja_bad_form(low)
                    if bad:
                        errors.append(Error('禁用詞', bad, tok))
                        continue
                continue

            ok, why = morph.contraction_ok(tok, spec, self.accepted)
            if ok:
                continue
            if why:
                errors.append(Error('未知詞', why, tok))
                continue
            if morph.derivable(spec, low, self.accepted):
                continue

            # 韓文：助詞接在詞幹後面（학교에서），先拆助詞再檢查
            if spec.script == 'hangul':
                # 先拆繫詞（학생이에요 → 학생 + 이에요）
                stem0, copula = korean.strip_copula(tok)
                if copula:
                    if stem0.lower() in spec.vocab or stem0.lower() in self.accepted:
                        continue
                    errors.append(Error('未知詞', f'「{stem0}」不在詞表內（用描述或外來語）', tok))
                    continue
                stem, particle = korean.strip_particle(tok)
                if particle:
                    if stem.lower() in spec.vocab or stem.lower() in self.accepted:
                        if not korean.correct_particle(stem, particle):
                            want = korean.particle_for(stem, particle)
                            errors.append(Error('助詞', f'「{tok}」的助詞用錯了：'
                                                    f'{stem} 後面應該用 '
                                                    f'「{want}」', tok))
                        continue
                    # 動詞詞幹 + 助詞
                    for key, w in spec.words.items():
                        if w.stem and w.stem == stem and 'v' in w.pos:
                            if not korean.correct_particle(stem, particle):
                                errors.append(Error('助詞', f'「{tok}」的助詞用錯了', tok))
                            continue
                    errors.append(Error('未知詞', f'「{stem}」不在詞表內（用描述或外來語）', tok))
                    continue

            # 禁用詞
            if low in spec.replace:
                errors.append(Error('禁用詞', f'「{tok}」是禁用詞，改用「{spec.replace[low]}」', tok))
                continue
            # 日文：て形（〜て）不合規，提示改成「〜ます」
            if spec.script == 'kana' and tok.endswith('て') and len(tok) > 1:
                errors.append(Error('禁用詞',
                                    f'「{tok}」是て形，Mini-Japanese 不用て形，'
                                    f'改用「{tok[:-1]}ます」', tok))
                continue

            # 外來語：第一次出現必須有括號說明
            nxt = text[pos + len(tok):].lstrip()
            if nxt[:1] in ('(', '（'):
                defined.add(low)
                continue
            if low in defined:
                continue
            if par:
                continue
            if allow_bare_loanword and self._is_loanword(tok):
                continue
            if self._is_loanword(tok):
                errors.append(Error('外來語', f'「{tok}」是外來語，第一次出現時必須有括號說明', tok))
                continue
            errors.append(Error('未知詞', f'「{tok}」不在詞表內（用描述或外來語）', tok))

        return errors

    # ── 外來語判定 ──────────────────────────────────────────────────────────
    def _ja_bad_form(self, low: str) -> str:
        """日文：這個形式不合規（て／た／ない／たい 形），回傳說明。"""
        forms = getattr(self.spec, 'ja_forms', {})
        for unit, fs in forms.items():
            # fs = [て, た, ない, たい, ます]
            masu = fs[4]
            if low == fs[0]:
                return f'「{low}」是て形，Mini-Japanese 不用て形，請用「{masu}」'
            if low == fs[1]:
                return f'「{low}」是た形，Mini-Japanese 不用た形，請用「{masu}ました」'
            if low == fs[2]:
                return f'「{low}」是「ない」形，Mini-Japanese 否定用「ません」，請改寫成「{masu}ません」'
            if low == fs[3]:
                return f'「{low}」是「たい」形，Mini-Japanese 不用「たい」，請改寫成「{masu}」'
        return ''
    def _is_loanword(self, tok: str) -> bool:
        """表外的詞，看起來像專有名詞／片假名／非本語字母 → 外來語。"""
        spec = self.spec
        low = tok.lower()
        if low in spec.proper:
            return True
        if spec.script in ('latin',):
            # 拉丁語言：表外且大寫開頭 → 專有名詞
            return tok[0].isupper()
        if spec.script == 'han':
            # 中文：漢字表外的拉丁字母一定是外來語
            return True
        if spec.script == 'kana':
            # 日本語：片假名 = 外來語；表外的漢字 = 未知詞（不是外來語）
            return bool(re.match(r'[\u30a1-\u30f6]', tok))
        if spec.script == 'hangul':
            return False
        return False

    # ── 描述檢查 ────────────────────────────────────────────────────────────
    def check_description(self, phrase: str) -> list[Error]:
        """一句描述是否合格：每個詞都在表內，最後是類頭。"""
        errors = []
        for tok, kind in self.tok.tokens(phrase):
            if kind in ('number', 'punct'):
                continue
            low = tok.lower()
            if low in spec_head(self.spec) or low in self.spec.vocab or low in self.accepted:
                continue
            errors.append(Error('描述', f'描述裡的「{tok}」不在詞表內', tok))
        if self.heads:
            last = phrase.strip().split()[-1] if phrase.strip().split() else ''
            if last and last.lower() not in self.heads:
                errors.append(Error('描述', f'描述要以類頭結尾（{last} 不是類頭）', last))
        return errors


def spec_head(spec):
    return {h.lower() for h in spec.heads}
