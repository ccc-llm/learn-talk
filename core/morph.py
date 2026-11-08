"""形態：哪些寫法算「同一個單位」。

設計原則：**能從資料推的就從資料推，資料推不出來的就直接列出來。**

    words.tsv 的 forms 欄   → 直接可寫的形式（例如日文 たべます たべました たべません たべたい）
    irregular.tsv          → 不規則形式（英文 went、goose；法文 allé）
    affix.tsv              → 允許的字首字尾（英文 un-、-er；法文 -eux）

拉丁語系（英、法）的規則屈折由 core 提供；日、韓的活用形直接寫在 forms 欄。
"""
from __future__ import annotations

import re


# ── 拉丁語系的規則屈折（英文）─────────────────────────────────────────────────
DOUBLE_V = {
    'cut', 'stop', 'plan', 'sit', 'run', 'swim', 'drop', 'beg', 'hug', 'rub', 'jog',
    'fit', 'get', 'put', 'let', 'set', 'bet', 'shut', 'ship', 'shop', 'skip', 'step',
    'stir', 'tap', 'wrap', 'grab', 'occur', 'prefer', 'refer', 'admit', 'permit',
    'commit', 'regret', 'forget', 'begin', 'control', 'pat', 'chat', 'clap', 'plot',
    'spot', 'strap', 'tug', 'ban', 'eject', 'equip', 'hand', 'win',
}
DOUBLE_ADJ = {'big', 'hot', 'sad', 'wet', 'fat', 'mad', 'dim', 'grim', 'flat', 'thin', 'slim'}
VERB_O_ES = {'go', 'do', 'echo'}
O_ES = {'cargo', 'domino', 'echo', 'embargo', 'hero', 'torpedo', 'veto', 'volcano'}

IRREG_PARADIGM = {
    'be': 'be / am / is / are / was / were / been / being',
    'have': 'have / has / had',
    'do': 'do / does / did',
    'will': 'will / would',
    'can': 'can / could',
    'shall': 'shall / should',
    'may': 'may / might',
    'must': 'must',
    'need': 'need',
    'let': 'let',
}


def plural(w: str) -> str:
    if w.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return w + 'es'
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'ies'
    if w.endswith('o') and w in O_ES:
        return w + 'es'
    return w + 's'


def third(w: str) -> str:
    if w.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return w + 'es'
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'ies'
    if w.endswith('o') and w in VERB_O_ES:
        return w + 'es'
    return w + 's'


def ing(w: str) -> str:
    if w.endswith('ie'):
        return w[:-2] + 'ying'
    if w.endswith('e') and not w.endswith(('ee', 'ye', 'oe')):
        return w[:-1] + 'ing'
    if w in DOUBLE_V:
        return w + w[-1] + 'ing'
    return w + 'ing'


def ed(w: str) -> str:
    if w.endswith('e'):
        return w + 'd'
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'ied'
    if w in DOUBLE_V:
        return w + w[-1] + 'ed'
    return w + 'ed'


def compar(w: str) -> tuple[str, str]:
    if len(w) <= 6 and not w.endswith(('ful', 'ous', 'ing')):
        if w.endswith('e'):
            return w + 'r', w + 'st'
        if w.endswith('y') and w[-2:-1] not in 'aeiou':
            return w[:-1] + 'ier', w[:-1] + 'iest'
        if w in DOUBLE_ADJ:
            return w + w[-1] + 'er', w + w[-1] + 'est'
        return w + 'er', w + 'est'
    return 'more ' + w, 'most ' + w


def english_forms(w: str, pos: str, irr: list[str]) -> set[str]:
    """英文：屈折形式。"""
    out = {w}
    kinds = pos.split('/')
    if 'v' in kinds:
        out.add(third(w))
        out.add(ing(w))
        out.update(irr if irr else [ed(w)])
    if 'n' in kinds:
        out.add(plural(w))
        out.update(irr)
    if 'adj' in kinds:
        if irr:
            out.update(irr)
        else:
            c, s = compar(w)
            out.update((c, s))
    if w in IRREG_PARADIGM:
        out.update(x.strip() for x in IRREG_PARADIGM[w].split(' / '))
    return out


# ── 法文：規則的過去分詞與第三人稱單數 ────────────────────────────────────────

def french_past_participle(w: str) -> str:
    """規則的過去分詞。

    -er  : parler → parlé（去掉 r 加 é）
    -ir  : finir → fini（第二組，去掉 ir 加 i）
    -re  : vendre → vendu（去掉 re 加 u）
    其他不規則形式列在 irregular.tsv。
    """
    if w.endswith('er'):
        return w[:-1] + 'é'
    if w.endswith('ir') and len(w) > 4 and w[-3] in 'nt':
        return w[:-2] + 'i'
    if w.endswith('re'):
        return w[:-2] + 'u'
    return w


def french_third(w: str) -> str:
    if w.endswith(('s', 'x', 'z')):
        return w
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'i'
    return w + 's'


def french_forms(w: str, pos: str, irr: list[str]) -> set[str]:
    from . import french
    out = {w}
    kinds = pos.split('/')
    if 'v' in kinds:
        out.update(french.conjugation(w))
        out.add(french.past_participle(w, irr or None))
        out.update(irr)
    if 'n' in kinds:
        if irr:
            out.update(irr)
        else:
            if w.endswith(('s', 'x', 'z')):
                out.add(w)
            elif w.endswith('al'):
                out.add(w[:-2] + 'aux')
            else:
                out.add(w + 's')
    if 'adj' in kinds:
        if irr:
            out.update(irr)
        else:
            out.update(french_adj_forms(w))
    return out


# 法文形容詞的陰性與複數：依字尾變化

# 不規則的陰性形式
FRENCH_ADJ_IRREGULAR = {
    'beau': 'belle', 'nouveau': 'nouvelle', 'vieux': 'vieille',
    'blond': 'blonde', 'blanc': 'blanche', 'gris': 'grise',
    'public': 'publique', 'magic': 'magique', 'gros': 'grosse',
}


def french_adj_forms(w: str) -> set[str]:
    """形容詞 → 陰性／複數形式。

    long → longue、beau → belle、premier → première、neuf → neuve
    """
    out = {w}
    fem = w
    if w in FRENCH_ADJ_IRREGULAR:
        fem = FRENCH_ADJ_IRREGULAR[w]
    elif w.endswith('eux'):                 # heureux → heureuse
        fem = w[:-3] + 'euse'
    elif w.endswith('eau'):                 # nouveau → nouvelle
        fem = w[:-3] + 'elle'
    elif w.endswith('el') or w.endswith('eil'):   # réel → réelle
        fem = w[:-2] + 'elle'
    elif w.endswith('g'):                   # long → longue
        fem = w[:-1] + 'gue'
    elif w.endswith('on'):                  # bon → bonne
        fem = w[:-2] + 'onne'
    elif w.endswith('en'):                  # ancien → ancienne
        fem = w[:-2] + 'enne'
    elif w.endswith('er'):                  # premier → première
        fem = w[:-2] + 'ère'
    elif w.endswith('f'):                   # neuf → neuve
        fem = w[:-1] + 've'
    elif w.endswith('e'):
        fem = w
    else:
        fem = w + 'e'
    out.add(fem)
    # 複數
    if w.endswith('s') or w.endswith('x') or w.endswith('z'):
        out.add(w)
    elif w.endswith('eau'):
        out.add(w[:-1] + 'x')
    elif w.endswith('al'):
        out.add(w[:-2] + 'aux')
    else:
        out.add(w + 's')
    # 陰性複數
    out.add(fem if fem.endswith('s') else fem + 's')
    return out


# ── 法文的省音縮約（elision）──────────────────────────────────────────────────
# J'ai = je + ai ; l'école = le/la + école ; d'accord = de + accord …
FRENCH_ELISION = {
    'j': 'je', 'l': 'le', 'd': 'de', 'n': 'ne', 'qu': 'que', 'c': 'ce',
    's': 'se', 'm': 'me', 't': 'te',
}


def french_elision_ok(token: str, spec, accepted: set[str]) -> tuple[bool, str]:
    """法文縮約：J'ai / l'ami / d'accord 是否成立。"""
    t = token.lower().replace('’', "'")
    if "'" not in t:
        return False, ''
    head, _, tail = t.partition("'")
    if not tail:
        return False, ''
    if head not in FRENCH_ELISION:
        return False, ''
    # 已經是縮約形式的詞（例如 l'on）
    if head == 'l' and tail == 'on':
        return True, ''
    if tail in spec.vocab or tail in accepted:
        return True, ''
    return False, f'{token} 的後半 {tail} 不在詞表內'


# ── 通用：由 spec 產生可接受形式 ──────────────────────────────────────────────

def accepted_forms(spec) -> set[str]:
    """這個語言所有可以直接寫出來的形式。"""
    out: set[str] = set()
    irr = spec.irregular
    for key, w in spec.words.items():
        out.add(w.unit.lower())
        out.update(f.lower() for f in w.forms)
        if spec.script == 'latin':
            lang = spec.code
            if lang in ('en', 'english'):
                out.update(english_forms(key, w.pos, irr.get(key, [])))
            elif lang in ('fr', 'french'):
                out.update(french_forms(key, w.pos, irr.get(key, [])))
        elif spec.script == 'kana':
            from . import japanese
            kinds = w.pos.split('/')
            ja_forms = getattr(spec, 'ja_forms', {})
            if 'v' in kinds:
                out.update(japanese.verb_forms(w.unit))
                out.update(japanese.verb_extra(w.unit))
                # 形式表：て・た・ない・たい（這些形式不合規，只用來偵錯）
                for unit, forms in ja_forms.items():
                    if forms[4] == w.unit:
                        out.update(forms)
                        # 辞書形（描述用：〜をする人）
                        out.add(unit)
                        break
                # ます形 → 字典形（用來切分「考える」這種寫法）
                plain = japanese.plain_of(w.unit)
                if plain != w.unit:
                    out.add(plain)
            if 'adj' in kinds:
                out.update(japanese.adj_forms(w.unit))
                for unit, forms in getattr(spec, 'ja_adj_forms', {}).items():
                    if forms[2] == w.unit:
                        out.update(forms)
                        out.add(unit)
                        break
        elif spec.script == 'hangul':
            from . import korean
            kinds = w.pos.split('/')
            stem = w.stem or korean.stem_of(w.unit)
            # 形式表優先（韓文活用不規則多，直接列）
            forms = getattr(spec, 'ko_forms', {})
            if w.unit in forms:
                out.update(forms[w.unit])
            if w.stem:
                out.update(f for f in w.stem.split('|') if f)
            elif 'v' in kinds:
                out.update(korean.verb_forms(stem))
            if 'adj' in kinds:
                out.update(korean.adj_forms(stem))
            # 助詞（附在詞幹後面）
            if w.pos.startswith('p'):
                out.add(w.unit)
        for f in irr.get(key, []):
            out.add(f.lower())
    return out


def derivable(spec, unit: str, accepted: set[str]) -> bool:
    """是不是「表內詞 ＋ 允許的字首字尾」。"""
    unit = unit.lower()
    for a in spec.affixes:
        aff = a['affix'].strip('`').lower()
        if a['kind'] == 'prefix':
            stem = aff.rstrip('-')
            if unit.startswith(stem) and len(unit) > len(stem):
                rest = unit[len(stem):]
                if rest in spec.vocab or rest in accepted:
                    return True
        else:
            suf = aff.lstrip('-')
            if unit.endswith(suf) and len(unit) > len(suf):
                rest = unit[:-len(suf)]
                if rest in spec.vocab or rest in accepted:
                    return True
    return False


CONTRACTION_MAP = {
    "n't": None, "'ll": 'will', "'ve": 'have', "'re": 'are', "'m": 'am', "'d": 'would',
    "'s": None,
}
NOT_STEMS = {'wo': 'will', 'ca': 'can', 'sha': 'shall', 'mu': 'must', 'ne': 'need',
             'ai': 'is', 'ar': 'are', 'we': 'were', 'ha': 'has', 'do': 'does'}


def contraction_ok(token: str, spec, accepted: set[str]) -> tuple[bool, str]:
    """縮寫／縮約是不是表內的詞。回傳 (ok, 說明)。"""
    t = token.lower().replace('’', "'")
    if t in spec.vocab or t in accepted:
        return True, ''
    if t == 'cannot':
        return True, ''
    if spec.code in ('fr', 'french') and "'" in t:
        ok, why = french_elision_ok(t, spec, accepted)
        if ok or why:
            return ok, why
    if t.endswith("n't"):
        stem = NOT_STEMS.get(t[:-3], t[:-3])
        if stem in spec.vocab or stem in accepted:
            return True, ''
        return False, f'{token} 的原形 {stem} 不在表內'
    if t.endswith("'s"):
        base = t[:-2]
        if base in spec.vocab or base in accepted:
            return True, ''
        return False, f'{token} 的原形 {base} 不在表內'
    for suf, repl in (("'ll", 'will'), ("'ve", 'have'), ("'re", 'are'), ("'m", 'am')):
        if t.endswith(suf):
            base = t[:-len(suf)]
            if base in spec.vocab or base in accepted:
                return True, ''
            return False, f'{token} 的原形 {base} 不在表內'
    if t.endswith("'d"):
        base = t[:-3]
        if base in spec.vocab or base in accepted:
            return True, ''
        return False, f'{token} 的原形 {base} 不在表內'
    return False, ''
