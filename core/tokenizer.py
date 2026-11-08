"""切分器：把文字切成「單位」（中文＝字，其他＝詞）。

每種語言的切分規則不一樣，所以這裡是策略模式：
    CJK  ：每個漢字是一個單位（中文）
    Latin ：空白切詞， contractions 與連字號保留
    Kana  ：假名 run 或單字漢字（日本語）
    Hangul：韓文以空白分詞（語節），助詞另外處理
"""
from __future__ import annotations

import re

HAN = r'\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\u31f0-\u31ff\uac00-\ud7af'


class Tokenizer:
    """base：Latin 語言（英、法）。"""

    script = 'latin'
    unit_kind = 'word'

    TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*|"
                       r"\d+(?:[.,]\d+)*(?:st|nd|rd|th)?|"
                       r"[\u4e00-\u9fff\u3400-\u4dbf]+|[^\s\w]")

    def tokens(self, text: str):
        """yield (start, surface, kind)。kind: word / number / punct / foreign"""
        for m in self.TOKEN.finditer(text):
            s = m.group(0)
            if s[0].isdigit():
                yield m.start(), s, 'number'
            elif re.match(r'[\u4e00-\u9fff\u3400-\u4dbf]', s):
                # 拉丁語言裡的漢字 = 外來語
                yield m.start(), s, 'foreign'
            elif re.match(r'[^\w]', s):
                yield m.start(), s, 'punct'
            else:
                yield m.start(), s, 'word'


class CJKTokenizer(Tokenizer):
    """中文：每個漢字一個單位；漢字之外的拉丁字母＝外來語。"""
    script = 'han'
    unit_kind = 'char'

    TOKEN = re.compile(r"[0-9]+(?:[.,][0-9]*)*%?|"
                       r"[A-Za-z]+(?:['’][A-Za-z]+)*|"
                       r"[\u4e00-\u9fff\u3400-\u4dbf]|"
                       r"[^\s]")


class KanaTokenizer(Tokenizer):
    """日本語：沒有空格，靠詞表做最長匹配切分。

    詞表裡的詞可能是混寫的（例如 勉強します），所以切分要對整段文字做，
    不能只處理純漢字或純假名的片段。
    """
    script = 'kana'
    unit_kind = 'word'

    def __init__(self, vocab=None):
        # vocab 包含詞表與所有可接受的形式（屈折），切分時用最長匹配
        self.vocab = vocab or set()

    def tokens(self, text: str):
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch.isdigit():
                m = re.match(r'\d+(?:[.,]\d+)*', text[i:])
                s = m.group(0)
                yield i, s, 'number'
                i += len(s)
                continue
            if re.match(r'[A-Za-z]', ch):
                m = re.match(r"[A-Za-z]+(?:['’][A-Za-z]+)*", text[i:])
                s = m.group(0)
                yield i, s, 'foreign'
                i += len(s)
                continue
            if not re.match(r'[\w\u3040-\u30ff]', ch):
                yield i, ch, 'punct'
                i += 1
                continue
            # 片假名：外來語，整段切出
            if re.match(r'[\u30a1-\u30f6\u30fc]', ch):
                m = re.match(r'[\u30a1-\u30f6\u30fc]+', text[i:])
                s = m.group(0)
                yield i, s, 'foreign'
                i += len(s)
                continue
            # 疊字符號「々」接在前一個字後面
            if ch == '々' and i > 0:
                yield i, '々', 'word'
                i += 1
                continue
            # 最長匹配
            matched = False
            for L in range(min(10, n - i), 0, -1):
                piece = text[i:i + L]
                if piece in self.vocab:
                    yield i, piece, 'word'
                    i += L
                    matched = True
                    break
            if not matched:
                yield i, ch, 'word'
                i += 1


class HangulTokenizer(Tokenizer):
    """韓文：以空白切詞（語節），每個語節是一個單位。

    韓文是黏著語：助詞接在詞幹後面（학교에서）。切分只切空白，
    詞幹與助詞的拆解交給 checker（core/korean.py）。
    """
    script = 'hangul'
    unit_kind = 'word'

    TOKEN = re.compile(r"[0-9]+(?:[.,][0-9]*)*%?|"
                       r"[\uac00-\ud7af]+|"
                       r"[A-Za-z]+(?:['’][A-Za-z]+)*|"
                       r"[^\s]")


def get(script: str, vocab=None) -> Tokenizer:
    if script == 'han':
        return CJKTokenizer()
    if script == 'kana':
        return KanaTokenizer(vocab)
    if script == 'hangul':
        return HangulTokenizer()
    return Tokenizer()
