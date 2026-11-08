"""韓文的活用與助詞。

Mini-Korean 的設計：
* **只用 해요體**：現在＝해요／過去＝았어요·었어요／未來＝(으)ㄹ 거예요
* **助詞只有八個**：은/는(이/가)、을/를、에、에서、도、의、하고、부터
* **助詞跟前面的詞走**：有收音（받침）用 은・을，沒有收音用 이・를。
* 不用敬語（하십시오체）、不用半語。
"""

# ── 韓文字母 ─────────────────────────────────────────────────────────────────
CHOSEONG = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
JUNGSEONG = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
JONGSEONG = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'

# ── 不規則動詞：詞幹 → (해요 形, 過去式) ─────────────────────────────────────
IRREGULAR: dict[str, tuple[str, str]] = {
    '가': ('가요', '갔어요'),
    '오': ('와요', '왔어요'),
    '보': ('봐요', '봤어요'),
    '하': ('해요', '했어요'),
    '들': ('들어요', '들었어요'),
    '같': ('같아요', '같았어요'),
    '곧': ('곧아요', '곧았어요'),
    '싫': ('싫어요', '싫었어요'),
    '나': ('나요', '났어요'),
    '자': ('자요', '잤어요'),
    '살': ('살아요', '살았어요'),
    '알': ('알아요', '알았어요'),
    '길': ('길어요', '길었어요'),
    '물': ('물어요', '물었어요'),
    '설': ('설어요', '설었어요'),
    '열': ('열어요', '열었어요'),
    '끄': ('끄나요', '끄냈어요'),
    '맵': ('매워요', '매웠어요'),
    '아프': ('아파요', '아팠어요'),
    '기쁘': ('기뻐요', '기뻐서요'),
    '어렵': ('어려워요', '어려웠어요'),
    '예쁘': ('예뻐요', '예뻬서요'),
    '귀찮': ('귀찮아요', '귀찮았어요'),
    '재미있': ('재미있어요', '재미있었어요'),
    '바쁘': ('바빠요', '바빴어요'),
    '깨끗하': ('깨끗해요', '깨끗했어요'),
    '바라': ('바라요', '바라봤어요'),
}

# 母音 a / o 結尾 → 아요
VOWEL_A = set('ㅏㅑㅐㅒㅣ')

# ── 助詞 ─────────────────────────────────────────────────────────────────────
# 依收音變化的助詞：{'助詞': {'consonant': '有收音時', 'vowel': '無收音時'}}
PARTICLES = {
    '은': {'consonant': '은', 'vowel': '는'},      # 主題
    '는': {'consonant': '은', 'vowel': '는'},
    '이': {'consonant': '이', 'vowel': '가'},      # 主格
    '가': {'consonant': '이', 'vowel': '가'},
    '을': {'consonant': '을', 'vowel': '를'},      # 賓語
    '를': {'consonant': '을', 'vowel': '를'},
    '에': {'consonant': '에', 'vowel': '에'},      # 目的地／時間點／對象
    '에서': {'consonant': '에서', 'vowel': '에서'},
    '도': {'consonant': '도', 'vowel': '도'},      # 也
    '의': {'consonant': '의', 'vowel': '의'},      # 的
    '하고': {'consonant': '하고', 'vowel': '하고'},
    '부터': {'consonant': '부터', 'vowel': '부터'},
    '까지': {'consonant': '까지', 'vowel': '까지'},
    '만': {'consonant': '만', 'vowel': '만'},
    '에게': {'consonant': '에게', 'vowel': '에게'},
    '한테': {'consonant': '한테', 'vowel': '한테'},
}
FIXED_PARTICLES = {'에', '에서', '도', '의', '하고', '부터', '까지', '만', '에게', '한테'}
# 有收音時用這些、無收音時用那些
PAIR_PAIRS = {('은', '는'), ('이', '가'), ('을', '를')}


def has_batchim(word: str) -> bool:
    """最後一個音節有沒有收音（받침）。"""
    if not word:
        return False
    code = ord(word[-1]) - 0xAC00
    if not (0 <= code < 0xD7A4):
        return False
    return code % 28 != 0


def jamo(ch: str) -> tuple[str, str, str]:
    """回傳 (初聲, 中聲, 終聲)。"""
    code = ord(ch) - 0xAC00
    if not (0 <= code < 0xD7A4):
        return '', '', ''
    cho = CHOSEONG[code // 588]
    jung = JUNGSEONG[(code % 588) // 28]
    jong = JONGSEONG[code % 28] if code % 28 else ''
    return cho, jung, jong


def last_vowel(word: str) -> str:
    if not word:
        return ''
    return jamo(word[-1])[1]


def last_batchim(word: str) -> str:
    if not word:
        return ''
    return jamo(word[-1])[2]


def stem_of(form: str) -> str:
    """把 해요 形（或過去式）反推成詞幹（어간）。

    만나요 → 만나、먹어요 → 먹、좋아요 → 좋다 的 어간「좋」、공부해요 → 공부하
    """
    # 過去式 → 回到現在式
    for suf, repl in (('았어요', '아요'), ('었어요', '어요')):
        if form.endswith(suf):
            form = form[:-len(suf)] + repl
            break
    # 不規則：해요 形 → 詞幹
    for stem, (now, _) in IRREGULAR.items():
        if form == now:
            return stem
    if not form.endswith('요'):
        return form
    base = form[:-1]                       # 去掉 요
    if base.endswith('해'):
        return base[:-1] + '하'            # 공부해 → 공부하
    if base.endswith(('아', '어')) and len(base) >= 2:
        if has_batchim(base[:-1]):
            return base[:-1]               # 좋아요 → 좋、먹어요 → 먹
    return base                            # 만나요 → 만나、사요 → 사


def compose(cho: str, jung: str, jong: str) -> str:
    """組成一個韓文音節。"""
    c = CHOSEONG.index(cho) if cho in CHOSEONG else 0
    j = JUNGSEONG.index(jung) if jung in JUNGSEONG else 0
    k = JONGSEONG.index(jong) if jong in JONGSEONG else 0
    return chr(0xAC00 + c * 588 + j * 28 + k)


# 母音合併：어간的母音 + 어 的母音
VOWEL_MERGE = {
    # 어간母音 + 어 → 合併後
    ('ㅏ', 'ㅣ'): 'ㅐ',   # 하 + 어 → 해
    ('ㅏ', 'ㅓ'): 'ㅐ',   # 가 + 어 → 가
    ('ㅏ', 'ㅐ'): 'ㅘ',   # 사 + 어 → 사
    ('ㅗ', 'ㅓ'): 'ㅕ',   # 보 + 어 → 봤
    ('ㅗ', 'ㅐ'): 'ㅘ',   # 오 + 어 → 왔
    ('ㅜ', 'ㅓ'): 'ㅝ',
    ('ㅡ', 'ㅓ'): 'ㅓ',
    ('ㅣ', 'ㅓ'): 'ㅣ',
}


def contract(stem: str) -> str:
    """把「어간 + 어」的合併結果算出來（用於過去式）。

    가 + 어 → 갔、만나 + 어 → 만났、하 + 어 → 했、보 + 어 → 봤、오 + 어 → 왔
    """
    if not stem:
        return stem
    cho, jung, jong = jamo(stem[-1])
    if jong:
        # 有收音：不合併，直接加 았어요／었어요
        return stem
    merged = VOWEL_MERGE.get((jung, 'ㅓ'))
    if merged is None:
        return stem
    # ㅆ 的形成：ㄷ → ㅆ
    return stem[:-1] + compose(cho, merged, 'ㅆ')


def _last_syl(stem: str) -> tuple[str, str, str]:
    return jamo(stem[-1])


def _syllable(cho: str, jung: str, jong: str = '') -> str:
    return compose(cho, jung, jong)


def _present(stem: str) -> str:
    """詞幹 → 해요 形（現在）。

    規則：
        母音結尾 ㅏ/ㅗ  → 어간 + 요        （만나요、사요）
        母音結尾 ㅣ     → ㅣ 收縮（마시→마셔요）
        母音結尾 ㅡ     → ㅡ 收縮（쓰→써요）
        母音結尾 ㅕ     → 어간 + 요        （켜요）
        收音 + ㅏ/ㅗ    → 어간 + 아요      （좋아요、살아요）
        收音 + 其他     → 어간 + 어요      （먹어요、있어요）
    """
    if stem in IRREGULAR:
        return IRREGULAR[stem][0]
    if not stem:
        return stem
    cho, jung, jong = _last_syl(stem)
    if not jong:
        if jung in VOWEL_A:
            return stem + '요'
        if jung == 'ㅣ':
            return stem[:-1] + _syllable(cho, 'ㅕ') + '요'
        if jung == 'ㅡ':
            return stem[:-1] + _syllable(cho, 'ㅓ') + '요'
        if jung == 'ㅕ':
            return stem + '요'
        return stem + '어요'
    if jung in VOWEL_A:
        return stem + '아요'
    return stem + '어요'


def _past(stem: str) -> str:
    """詞幹 → 過去式。

    規則：
        母音結尾 ㅏ/ㅗ  → 어간 + ㅆ + 어요     （갔어요、만났어요）
        母音結尾 ㅣ     → ㅣ 收縮 + ㅆ         （기다렸요）
        母音結尾 ㅡ     → ㅡ 收縮 + ㅆ         （썼요）
        母音結尾 其他   → 어간 + 었어요       （배었어요）
        收音 + ㅏ/ㅗ    → 어간 + 았어요       （좋았어요）
        收音 + 其他     → 어간 + 었어요       （먹었어요）
    """
    if stem in IRREGULAR:
        return IRREGULAR[stem][1]
    if not stem:
        return stem
    cho, jung, jong = _last_syl(stem)
    if not jong:
        if jung in VOWEL_A:
            # ㅆ 附在最後一個音節
            return stem[:-1] + _syllable(cho, jung, 'ㅆ') + '어요'
        if jung == 'ㅣ':
            return stem[:-1] + _syllable(cho, 'ㅕ', 'ㅆ') + '요'
        if jung == 'ㅡ':
            return stem[:-1] + _syllable(cho, 'ㅓ', 'ㅆ') + '요'
        return stem + '었어요'
    if jung in VOWEL_A:
        return stem + '았어요'
    return stem + '었어요'


def _future(stem: str) -> str:
    """詞幹 → 未來（으）ㄹ 거예요。"""
    if not stem:
        return stem
    if has_batchim(stem):
        return stem + '을 거예요'
    return stem + 'ㄹ 거예요'


def verb_topic_form(stem: str) -> str:
    """動詞的名詞化：〜는（먹는 = 吃的）。

    描述用：「운전하는 사람」＝開車的人。
    """
    if stem in IRREGULAR:
        base = {'가': '가', '오': '와', '보': '보', '하': '하', '들': '들',
                '같': '같', '싫': '싫', '나': '나', '자': '자'}.get(stem, stem)
        return base + '는'
    base = stem
    if base.endswith('하'):
        base = base[:-1] + '하'
    return base + '는'


def verb_forms(stem: str) -> set[str]:
    """詞幹 → 可以寫出來的形式。

    只用 해요體：
        現在：가요／먹어요／해요
        過去：갔어요／먹었어요／했어요
        未來：갈 거예요／먹을 거예요／할 거예요
        名詞化：먹는（描述用）
    """
    out = {_present(stem), _past(stem), _future(stem), verb_topic_form(stem)}
    if stem:
        out.add(stem)
    return out


def adj_forms(stem: str) -> set[str]:
    """形容詞詞幹 → 해요體 與 冠形詞形（修飾名詞時用）。

        좋아요／좋았어요／좋을 거예요／좋은（書）／좋아（快速的）
    """
    now = _present(stem)
    out = {now, _past(stem), _future(now)}
    if stem:
        out.add(stem)
    # 冠形詞形：形容詞 + 冠形詞形助詞（좋은／좋은 書）
    if has_batchim(stem):
        out.add(stem + '은')
    else:
        out.add(stem + 'ㄴ')
    return out


def strip_particle(word: str) -> tuple[str, str]:
    """把詞尾的助詞拆下來。回傳 (詞幹, 助詞)。

    韓文是黏著語：학교에서 → 學校 + 에서。
    """
    forms = set(PARTICLES) | set(FIXED_PARTICLES)
    for p in sorted(forms, key=len, reverse=True):
        if word.endswith(p) and len(word) > len(p):
            return word[:-len(p)], p
    return word, ''


# ── 繫詞（이다）───────────────────────────────────────────────────────────────
# 「학생이에요」「학생예요」＝是學生。
COPULA = ('이에요', '예요')


def strip_copula(word: str) -> tuple[str, str]:
    """把句尾的繫詞拆下來。回傳 (詞幹, 繫詞)。"""
    for c in COPULA:
        if word.endswith(c) and len(word) > len(c):
            stem = word[:-len(c)]
            if c == '이에요' and not has_batchim(stem):
                continue
            return stem, c
    return word, ''


def particle_for(stem: str, particle: str) -> str:
    """這個詞幹後面應該用哪個助詞。"""
    for con, vow in PAIR_PAIRS:
        if particle in (con, vow):
            return con if has_batchim(stem) else vow
    return particle


def correct_particle(stem: str, particle: str) -> bool:
    """助詞用對了嗎（有收音用 은/을，沒有收音用 이/를）。"""
    if particle in FIXED_PARTICLES:
        return True
    for con, vow in PAIR_PAIRS:
        if particle == con:
            return has_batchim(stem)
        if particle == vow:
            return not has_batchim(stem)
    return True
