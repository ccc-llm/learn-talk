"""羅馬字推導：日文假名→Hepburn 羅馬字、韓文諺文→RR（國語羅馬字）。

漢字讀音無法推導，由 tools/gen_readings.py 用 LLM 產生，
存進 langs/mini-japanese/data/readings.tsv。
"""
from __future__ import annotations

# ── 日文：假名 → Hepburn 羅馬字 ─────────────────────────────────────────────
_KANA = {
    'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
    'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
    'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
    'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
    'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
    'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
    'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
    'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
    'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
    'わ': 'wa', 'を': 'wo', 'ん': 'n',
    'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
    'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
    'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
    'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
    'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
    'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
    'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
    'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
    'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
    'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
    'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
    'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
    'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
    'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
    'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
    'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo',
}

# 單獨出現時的讀法
_KANA['ぁ'] = 'a'
_KANA['ぃ'] = 'i'
_KANA['ぅ'] = 'u'
_KANA['ぇ'] = 'e'
_KANA['ぉ'] = 'o'
_KANA['ゃ'] = 'ya'
_KANA['ゅ'] = 'yu'
_KANA['ょ'] = 'yo'
_KANA['っ'] = 'tsu'
_KANA['ッ'] = 'tsu'
_KANA['ー'] = ''        # 長音符：延續前面的母音，單獨不標
_KANA['々'] = ''        # 疊字符號
_KANA['ヶ'] = 'ka'      # 計量記號（ヶ月＝かげつ）
_KANA['ヵ'] = 'ka'

# 最後統一產生片假名對應：平假名（U+3041–U+309F）平移 0x60
for _k, _v in list(_KANA.items()):
    if len(_k) == 1 and 0x3041 <= ord(_k) <= 0x309F:
        _KANA[chr(ord(_k) + 0x60)] = _v


def kana_to_romaji(text: str) -> str:
    """把假名（含濁音、拗音、促音）轉成 Hepburn 羅馬字。"""
    out = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i + 2] in _KANA:
            out.append(_KANA[text[i:i + 2]])
            i += 2
            continue
        ch = text[i]
        if ch in ('っ', 'ッ'):
            # 促音：重複下一個子音（sh→ss 例外），單獨時標 tsu
            nxt = ''
            j = i + 1
            if j < len(text):
                if j + 1 < len(text) and text[j:j + 2] in _KANA:
                    nxt = _KANA[text[j:j + 2]]
                elif text[j] in _KANA:
                    nxt = _KANA[text[j]]
            if nxt:
                out.append(nxt[0])
            else:
                out.append('tsu')
            i += 1
            continue
        out.append(_KANA.get(ch, ch if not ('\u3040' <= ch <= '\u30ff') else ''))
        i += 1
    return ''.join(out)


def is_kana_only(text: str) -> bool:
    return all('\u3040' <= c <= '\u30ff' for c in text)


# ── 韓文：諺文 → RR（國語羅馬字）────────────────────────────────────────────
_CHO = ['g', 'kk', 'n', 'd', 'tt', 'r', 'm', 'b', 'pp', 's', 'ss', '',
        'j', 'jj', 'ch', 'k', 't', 'p', 'h']
_JUNG = ['a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae',
         'oe', 'yo', 'u', 'wo', 'we', 'wi', 'yu', 'eu', 'ui', 'i']
_JONG = ['', 'k', 'k', 'k', 'n', 'n', 'n', 't', 'l', 'l', 'l', 'l', 'l',
         'l', 'l', 'l', 'm', 'p', 'p', 't', 't', 'ng', 't', 't', 'k', 't',
         'p', 't']


def hangul_romanize(text: str) -> str:
    """把韓文音節轉成 RR 羅馬字（不處理連音變化）。"""
    out = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            idx = code - 0xAC00
            out.append(_CHO[idx // 588] + _JUNG[(idx % 588) // 28] + _JONG[idx % 28])
        else:
            out.append(ch)
    return ''.join(out)


def is_hangul_only(text: str) -> bool:
    return all(0xAC00 <= ord(c) <= 0xD7A3 or c in ' ' for c in text)
