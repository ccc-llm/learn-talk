/* learn-talk 網頁：翻譯器／檢查器／唸出來／詞典／詞表／語法／LLM 專家 */

let LANG = 'chinese';
let chatHistory = [];

// ── 介面語言（i18n）─────────────────────────────────────────────────────────
const UI_LANGS = ['zh-Hant', 'en', 'fr', 'ja', 'ko'];
let UILANG = 'zh-Hant';
try { if (UI_LANGS.includes(localStorage.getItem('lt-ui-lang'))) UILANG = localStorage.getItem('lt-ui-lang'); } catch (e) { /* 沒有儲存空間也能用 */ }
let romajiOn = true;
try { romajiOn = localStorage.getItem('lt-romaji') !== '0'; } catch (e) { /* 忽略 */ }
let showThink = true;
try { showThink = localStorage.getItem('lt-think') !== '0'; } catch (e) { /* 忽略 */ }

const I18N = {
  'zh-Hant': {
    sub: '用很少的字詞學會說話：Mini-Chinese／Mini-English／Mini-French／Mini-Japanese／Mini-Korean',
    uiLang: '介面語言', learnLang: '學習語言',
    tabTranslate: '翻譯器', tabCheck: '檢查器', tabSpeak: '唸出來', tabLexicon: '詞典',
    tabWords: '詞表', tabRules: '語法', tabExpert: 'LLM 專家',
    trInLabel: '受限語言（Mini-X）', trOutLabel: '一般語言',
    trInPh: '例如：昨天我和朋友一起去買東西。',
    trOutPh: '反向翻譯的結果會出現在這裡',
    btnCheck: '檢查', btnSpeak: '🔊 唸出來', btnReverse: '反向翻譯',
    ckLabel: '貼一段文字，看它是不是合法的受限語言',
    ckInPh: '把 Mini-X 的文字貼在這裡', btnFile: '讀檔案',
    spTitle: '唸出來（文字轉語音）',
    spHint: '兩種方式：<b>瀏覽器語音</b>（免金鑰、離線可用）與<b>伺服器語音</b>（edge-tts，音色較自然，需要本機有 edge-tts）。',
    spTextLabel: '要唸的文字', spInPh: '貼上任何段落',
    spBrowser: '🔊 瀏覽器唸', spServer: '🔊 伺服器唸（mp3）', spStop: '⏹ 停止', spRate: '速度',
    spPinyin: '中文拼音',
    lxLabel: '查一個詞，看它在受限語言怎麼說',
    lxPh: '輸入詞（中／英／法／日／韓）', btnLookup: '查',
    lxNotFound: '詞典裡沒有這個詞。試試用「描述」或「外來語」。',
    wdPh: '搜尋', wdAllCat: '全部類別', wdAll: '全部', wdCore: '核心層', wdExt: '擴充層',
    btnSpeakRow: '🔊 唸這一列', nItems: '{n} 個',
    exClear: '清除對話', exInPh: '問問題，或請它把中文翻成 Mini-X', btnSend: '送出',
    units: '單位', charUnit: '以「字」為單位', wordUnit: '以「詞」為單位',
    coreLbl: '核心', extLbl: '擴充', audience: '對象',
    checkOk: '✅ 全部在字表內，語法也正確。', checkErr: '❌ 有 {n} 個問題：',
    rulesTitle: '{name} 的語法規則（{n} 條）', ruleEx: '例',
    you: '你', expert: '專家', thinking: '思考中…', error: '錯誤', noReply: '（沒有回應）',
    voicesNone: '（未設定）',
    noSpeech: '這個瀏覽器不支援語音朗讀。',
    miniNames: { chinese: '簡易中文', english: '簡易英文', french: '簡易法文', japanese: '簡易日文', korean: '簡易韓文' },
    miniTargets: { chinese: '母語不是中文的外國人', english: '母語不是英文的外國人', french: '母語不是法文的外國人', japanese: '母語不是日文的外國人', korean: '母語不是韓文的外國人' },
    modeFast: '快速（不檢查，直接回答）', romajiLabel: '標拼音', thinkLabel: '顯示思考', thinkSummary: '思考過程', modeStrict: '嚴格（自動檢查字表，較慢）', tabCharset: '字集', copyBtn: '複製', csCopied: '已複製', ttsFail: '伺服器語音失敗：{msg}\n（請確認有安裝 edge-tts）',
  },
  en: {
    sub: 'Learn to speak with very few words: Mini-Chinese / Mini-English / Mini-French / Mini-Japanese / Mini-Korean',
    uiLang: 'Interface', learnLang: 'Language to learn',
    tabTranslate: 'Translator', tabCheck: 'Checker', tabSpeak: 'Read aloud', tabLexicon: 'Lexicon',
    tabWords: 'Word list', tabRules: 'Grammar', tabExpert: 'LLM expert',
    trInLabel: 'Mini language (Mini-X)', trOutLabel: 'Plain language',
    trInPh: 'e.g. Yesterday I went shopping with a friend.',
    trOutPh: 'The back-translation will appear here',
    btnCheck: 'Check', btnSpeak: '🔊 Read aloud', btnReverse: 'Back-translate',
    ckLabel: 'Paste some text to see whether it is valid Mini language',
    ckInPh: 'Paste Mini-X text here', btnFile: 'Open file',
    spTitle: 'Read aloud (text to speech)',
    spHint: 'Two ways: <b>browser speech</b> (no key, works offline) and <b>server speech</b> (edge-tts, more natural voices, needs edge-tts installed).',
    spTextLabel: 'Text to read', spInPh: 'Paste any paragraph',
    spBrowser: '🔊 Browser', spServer: '🔊 Server (mp3)', spStop: '⏹ Stop', spRate: 'Speed',
    spPinyin: 'Chinese pinyin',
    lxLabel: 'Look up how a word is said in the Mini language',
    lxPh: 'Enter a word (zh/en/fr/ja/ko)', btnLookup: 'Look up',
    lxNotFound: 'Not in the lexicon. Try a "description" or a "loanword".',
    wdPh: 'Search', wdAllCat: 'All categories', wdAll: 'All', wdCore: 'Core', wdExt: 'Extended',
    btnSpeakRow: '🔊 Read this row', nItems: '{n}',
    exClear: 'Clear chat', exInPh: 'Ask a question, or ask it to translate into Mini-X', btnSend: 'Send',
    units: 'units', charUnit: 'unit: characters', wordUnit: 'unit: words',
    coreLbl: 'Core', extLbl: 'Ext.', audience: 'For',
    checkOk: '✅ Every word is in the word list and the grammar is correct.',
    checkErr: '❌ {n} problem(s):',
    rulesTitle: '{name} grammar rules ({n})', ruleEx: 'e.g.',
    you: 'You', expert: 'Expert', thinking: 'Thinking…', error: 'Error', noReply: '(no reply)',
    voicesNone: '(not set)',
    noSpeech: 'This browser does not support speech synthesis.',
    miniNames: { chinese: 'Simple Chinese', english: 'Simple English', french: 'Simple French', japanese: 'Simple Japanese', korean: 'Simple Korean' },
    miniTargets: { chinese: 'Non-native speakers of Chinese', english: 'Non-native speakers of English', french: 'Non-native speakers of French', japanese: 'Non-native speakers of Japanese', korean: 'Non-native speakers of Korean' },
    modeFast: 'Fast (no checking, direct answer)', romajiLabel: 'Romanization', thinkLabel: 'Show thinking', thinkSummary: 'Thinking', modeStrict: 'Strict (checks the word list, slower)', tabCharset: 'Character set', copyBtn: 'Copy', csCopied: 'Copied', ttsFail: 'Server speech failed: {msg}\n(make sure edge-tts is installed)',
  },
  fr: {
    sub: 'Apprenez à parler avec très peu de mots : Mini-Chinois / Mini-Anglais / Mini-Français / Mini-Japonais / Mini-Coréen',
    uiLang: 'Interface', learnLang: 'Langue à apprendre',
    tabTranslate: 'Traducteur', tabCheck: 'Vérificateur', tabSpeak: 'Écouter', tabLexicon: 'Dictionnaire',
    tabWords: 'Liste de mots', tabRules: 'Grammaire', tabExpert: 'Expert LLM',
    trInLabel: 'Langue Mini (Mini-X)', trOutLabel: 'Langue ordinaire',
    trInPh: 'ex. Hier je suis allé faire les courses avec un ami.',
    trOutPh: 'La rétro-traduction apparaîtra ici',
    btnCheck: 'Vérifier', btnSpeak: '🔊 Écouter', btnReverse: 'Rétro-traduire',
    ckLabel: 'Collez un texte pour vérifier s’il est en langue Mini valide',
    ckInPh: 'Collez ici du texte en Mini-X', btnFile: 'Ouvrir un fichier',
    spTitle: 'Écouter (synthèse vocale)',
    spHint: 'Deux méthodes : <b>voix du navigateur</b> (sans clé, hors ligne) et <b>voix du serveur</b> (edge-tts, plus naturelle, nécessite edge-tts).',
    spTextLabel: 'Texte à lire', spInPh: 'Collez n’importe quel paragraphe',
    spBrowser: '🔊 Navigateur', spServer: '🔊 Serveur (mp3)', spStop: '⏹ Arrêter', spRate: 'Vitesse',
    spPinyin: 'Pinyin du chinois',
    lxLabel: 'Chercher comment un mot se dit en langue Mini',
    lxPh: 'Saisir un mot (zh/en/fr/ja/ko)', btnLookup: 'Chercher',
    lxNotFound: 'Absent du dictionnaire. Essayez une « description » ou un « emprunt ».',
    wdPh: 'Rechercher', wdAllCat: 'Toutes catégories', wdAll: 'Tous', wdCore: 'Noyau', wdExt: 'Extension',
    btnSpeakRow: '🔊 Lire cette ligne', nItems: '{n}',
    exClear: 'Effacer la conversation', exInPh: 'Posez une question, ou demandez une traduction en Mini-X', btnSend: 'Envoyer',
    units: 'unités', charUnit: 'unité : caractères', wordUnit: 'unité : mots',
    coreLbl: 'Noyau', extLbl: 'Ext.', audience: 'Pour',
    checkOk: '✅ Tous les mots sont dans la liste et la grammaire est correcte.',
    checkErr: '❌ {n} problème(s) :',
    rulesTitle: 'Règles de grammaire de {name} ({n})', ruleEx: 'ex.',
    you: 'Vous', expert: 'Expert', thinking: 'Réflexion…', error: 'Erreur', noReply: '(pas de réponse)',
    voicesNone: '(non défini)',
    noSpeech: 'Ce navigateur ne prend pas en charge la synthèse vocale.',
    miniNames: { chinese: 'Chinois simplifié', english: 'Anglais simplifié', french: 'Français simplifié', japanese: 'Japonais simplifié', korean: 'Coréen simplifié' },
    miniTargets: { chinese: 'Personnes dont la langue maternelle n\'est pas le chinois', english: 'Personnes dont la langue maternelle n\'est pas l\'anglais', french: 'Personnes dont la langue maternelle n\'est pas le français', japanese: 'Personnes dont la langue maternelle n\'est pas le japonais', korean: 'Personnes dont la langue maternelle n\'est pas le coréen' },
    modeFast: 'Rapide (sans vérification, réponse directe)', romajiLabel: 'Romanisation', thinkLabel: 'Afficher la réflexion', thinkSummary: 'Réflexion', modeStrict: 'Strict (vérifie la liste de mots, plus lent)', tabCharset: 'Ensemble de caractères', copyBtn: 'Copier', csCopied: 'Copié', ttsFail: 'Échec de la voix serveur : {msg}\n(vérifiez que edge-tts est installé)',
  },
  ja: {
    sub: '少ない語彙で話せるようになる：ミニ中国語／ミニ英語／ミニフランス語／ミニ日本語／ミニ韓国語',
    uiLang: '表示言語', learnLang: '学習言語',
    tabTranslate: '翻訳', tabCheck: 'チェッカー', tabSpeak: '読み上げ', tabLexicon: '辞書',
    tabWords: '単語表', tabRules: '文法', tabExpert: 'LLM エキスパート',
    trInLabel: 'ミニ言語（Mini-X）', trOutLabel: '普通の言語',
    trInPh: '例：昨日友達と買い物に行きました。',
    trOutPh: '逆翻訳の結果がここに表示されます',
    btnCheck: 'チェック', btnSpeak: '🔊 読み上げ', btnReverse: '逆翻訳',
    ckLabel: 'テキストを貼り付けて、正しいミニ言語かどうか確認します',
    ckInPh: 'ここに Mini-X のテキストを貼り付け', btnFile: 'ファイルを開く',
    spTitle: '読み上げ（音声合成）',
    spHint: '2 つの方法：<b>ブラウザ音声</b>（キー不要、オフライン可）と<b>サーバー音声</b>（edge-tts、より自然、要 edge-tts インストール）。',
    spTextLabel: '読み上げるテキスト', spInPh: '任意の段落を貼り付け',
    spBrowser: '🔊 ブラウザ', spServer: '🔊 サーバー (mp3)', spStop: '⏹ 停止', spRate: '速度',
    spPinyin: '中国語ピンイン',
    lxLabel: 'ある語がミニ言語でどう言われるか検索します',
    lxPh: '語を入力（中／英／仏／日／韓）', btnLookup: '検索',
    lxNotFound: '辞書にありません。「説明」か「外来語」を試してください。',
    wdPh: '検索', wdAllCat: '全カテゴリ', wdAll: 'すべて', wdCore: '基礎層', wdExt: '拡張層',
    btnSpeakRow: '🔊 この行を読む', nItems: '{n} 件',
    exClear: '会話を消す', exInPh: '質問するか、Mini-X への翻訳を頼む', btnSend: '送信',
    units: '単位', charUnit: '単位：「字」', wordUnit: '単位：「語」',
    coreLbl: '基礎', extLbl: '拡張', audience: '対象',
    checkOk: '✅ すべて語表内で、文法も正しいです。',
    checkErr: '❌ {n} 件の問題：',
    rulesTitle: '{name} の文法規則（{n} 条）', ruleEx: '例',
    you: 'あなた', expert: 'エキスパート', thinking: '考え中…', error: 'エラー', noReply: '（応答なし）',
    voicesNone: '（未設定）',
    noSpeech: 'このブラウザは音声合成に対応していません。',
    miniNames: { chinese: 'やさしい中国語', english: 'やさしい英語', french: 'やさしいフランス語', japanese: 'やさしい日本語', korean: 'やさしい韓国語' },
    miniTargets: { chinese: '中国語を母語としない学習者', english: '英語を母語としない学習者', french: 'フランス語を母語としない学習者', japanese: '日本語を母語としない学習者', korean: '韓国語を母語としない学習者' },
    modeFast: '高速（チェックなし、直接回答）', romajiLabel: 'ローマ字', thinkLabel: '思考を表示', thinkSummary: '思考過程', modeStrict: '厳密（語表を自動チェック、やや遅い）', tabCharset: '文字セット', copyBtn: 'コピー', csCopied: 'コピーしました', ttsFail: 'サーバー音声に失敗：{msg}\n（edge-tts がインストールされているか確認してください）',
  },
  ko: {
    sub: '적은 단어로 말하기를 배웁니다: 미니 중국어／미니 영어／미니 프랑스어／미니 일본어／미니 한국어',
    uiLang: '인터페이스 언어', learnLang: '학습 언어',
    tabTranslate: '번역기', tabCheck: '검사기', tabSpeak: '읽어 주기', tabLexicon: '사전',
    tabWords: '단어 목록', tabRules: '문법', tabExpert: 'LLM 전문가',
    trInLabel: '미니 언어(Mini-X)', trOutLabel: '일반 언어',
    trInPh: '예: 어제 친구와 쇼핑을 갔어요.',
    trOutPh: '역번역 결과가 여기에 표시됩니다',
    btnCheck: '검사', btnSpeak: '🔊 읽어 주기', btnReverse: '역번역',
    ckLabel: '텍스트를 붙여넣어 올바른 미니 언어인지 확인합니다',
    ckInPh: '여기에 Mini-X 텍스트를 붙여넣기', btnFile: '파일 열기',
    spTitle: '읽어 주기(음성 합성)',
    spHint: '두 가지 방식: <b>브라우저 음성</b>(키 불필요, 오프라인 가능)과 <b>서버 음성</b>(edge-tts, 더 자연스러움, edge-tts 필요).',
    spTextLabel: '읽을 텍스트', spInPh: '아무 문단이나 붙여넣기',
    spBrowser: '🔊 브라우저', spServer: '🔊 서버 (mp3)', spStop: '⏹ 정지', spRate: '속도',
    spPinyin: '중국어 병음',
    lxLabel: '단어가 미니 언어로 어떻게 말해지는지 찾아봅니다',
    lxPh: '단어 입력(중/영/불/일/한)', btnLookup: '찾기',
    lxNotFound: '사전에 없습니다. ‘설명’ 또는 ‘외래어’ 방식을 시도해 보세요.',
    wdPh: '검색', wdAllCat: '전체 분류', wdAll: '전체', wdCore: '핵심층', wdExt: '확장층',
    btnSpeakRow: '🔊 이 항목 읽기', nItems: '{n}개',
    exClear: '대화 지우기', exInPh: '질문하거나 Mini-X로 번역을 요청하세요', btnSend: '보내기',
    units: '단위', charUnit: "단위: '자'", wordUnit: "단위: '어'",
    coreLbl: '핵심', extLbl: '확장', audience: '대상',
    checkOk: '✅ 모든 단어가 단어 목록 안에 있고 문법도 맞습니다.',
    checkErr: '❌ {n}개의 문제:',
    rulesTitle: '{name} 문법 규칙({n}개)', ruleEx: '예',
    you: '나', expert: '전문가', thinking: '생각 중…', error: '오류', noReply: '(응답 없음)',
    voicesNone: '(미설정)',
    noSpeech: '이 브라우저는 음성 합성을 지원하지 않습니다.',
    miniNames: { chinese: '쉬운 중국어', english: '쉬운 영어', french: '쉬운 프랑스어', japanese: '쉬운 일본어', korean: '쉬운 한국어' },
    miniTargets: { chinese: '모국어가 중국어가 아닌 학습자', english: '모국어가 영어가 아닌 학습자', french: '모국어가 프랑스어가 아닌 학습자', japanese: '모국어가 일본어가 아닌 학습자', korean: '모국어가 한국어가 아닌 학습자' },
    modeFast: '빠름(검사 없이 바로 응답)', romajiLabel: '로마자', thinkLabel: '생각 보기', thinkSummary: '생각 과정', modeStrict: '엄격(단어 목록 자동 검사, 느림)', tabCharset: '글자 집합', copyBtn: '복사', csCopied: '복사됨', ttsFail: '서버 음성 실패: {msg}\n(edge-tts 설치를 확인하세요)',
  },
};

const t = (key) => (I18N[UILANG] && I18N[UILANG][key]) || I18N['zh-Hant'][key] || key;
const tf = (key, vars) => Object.entries(vars || {}).reduce(
  (s, [k, v]) => s.replaceAll('{' + k + '}', String(v)), t(key));

function applyUI() {
  document.documentElement.lang = UILANG;
  $$('[data-i18n]').forEach((el) => { el.innerHTML = t(el.dataset.i18n); });
  $$('[data-i18n-ph]').forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
  const to = $('#tr-out');
  if (to) to.dataset.ph = t('trOutPh');
}

// ── 輸出的 ruby 標音 ────────────────────────────────────────────────────────
let trOutText = '';

function withRuby(text) {
  const rom = (LANGS[LANG] || {}).rom || {};
  let out = '';
  for (const ch of String(text)) {
    const r = romajiOn ? rom[ch] : '';
    out += r ? `<ruby>${escapeHtml(ch)}<rt>${escapeHtml(r)}</rt></ruby>` : escapeHtml(ch);
  }
  return out;
}

function renderTrOut() {
  const el = $('#tr-out');
  el.innerHTML = withRuby(trOutText);
}

// ── 初始化 ─────────────────────────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

function init() {
  // 介面語言
  const ui = $('#uilang');
  ui.value = UILANG;
  ui.addEventListener('change', () => {
    UILANG = ui.value;
    try { localStorage.setItem('lt-ui-lang', UILANG); } catch (e) { /* 忽略 */ }
    applyUI();
    onLangChange();
  });

  // 學習語言（Mini-X）
  const sel = $('#lang');
  Object.keys(LANGS).forEach((code) => {
    const o = document.createElement('option');
    o.value = code;
    o.textContent = `${LANGS[code].name}（${LANGS[code].words.length} ${t('units')}）`;
    sel.appendChild(o);
  });
  sel.value = 'chinese';
  sel.addEventListener('change', () => { LANG = sel.value; onLangChange(); });

  // 分頁
  $$('.tab').forEach((tb) => tb.addEventListener('click', () => {
    $$('.tab').forEach((x) => x.classList.remove('active'));
    $$('.panel').forEach((x) => x.classList.remove('active'));
    tb.classList.add('active');
    $('#tab-' + tb.dataset.tab).classList.add('active');
  }));

  $('#tr-check').addEventListener('click', checkTranslate);
  $('#tr-rev').addEventListener('click', reverseTranslate);
  $('#tr-copy').addEventListener('click', async (e) => {
    const text = trOutText || $('#tr-out').textContent || '';
    if (!text) return;
    await copyText(text);
    flashCopy(e.target, t('csCopied'));
  });
  $('#tr-speak').addEventListener('click', () => speak($('#tr-in').value));
  $('#tr-out-speak').addEventListener('click', () => speak(trOutText || $('#tr-out').textContent));

  $('#ck-go').addEventListener('click', checkOnly);
  $('#ck-file').addEventListener('click', () => $('#ck-file-input').click());
  $('#ck-file-input').addEventListener('change', (e) => {
    const f = e.target.files[0];
    if (!f) return;
    f.text().then((tx) => { $('#ck-in').value = tx; checkOnly(); });
  });
  $('#ck-speak').addEventListener('click', () => speak($('#ck-in').value));

  $('#sp-browser').addEventListener('click', speakBrowser);
  $('#sp-server').addEventListener('click', speakServer);
  $('#sp-stop').addEventListener('click', stopSpeak);
  $('#sp-in').addEventListener('input', updatePinyin);

  $('#lx-go').addEventListener('click', lookup);
  $('#lx-q').addEventListener('keydown', (e) => { if (e.key === 'Enter') lookup(); });

  $('#wd-q').addEventListener('input', renderWords);
  $('#wd-cat').addEventListener('change', renderWords);
  $('#wd-lv').addEventListener('change', renderWords);
  $('#wd-speak').addEventListener('click', () => {
    const card = $('#wd-result').querySelector('.wordcard');
    if (card) speak(card.dataset.word);
  });

  const em = $('#ex-mode');
  try { const m = localStorage.getItem('lt-expert-mode'); if (m === 'fast' || m === 'strict') em.value = m; } catch (e) { /* 忽略 */ }
  em.addEventListener('change', () => { try { localStorage.setItem('lt-expert-mode', em.value); } catch (e) { /* 忽略 */ } });

  $$('.rom-toggle').forEach((cb) => {
    cb.checked = romajiOn;
    cb.addEventListener('change', () => {
      romajiOn = cb.checked;
      $$('.rom-toggle').forEach((x) => { x.checked = romajiOn; });
      try { localStorage.setItem('lt-romaji', romajiOn ? '1' : '0'); } catch (e) { /* 忽略 */ }
      renderTrOut();
      rebuildChat();
    });
  });
  const tt = $('#think-toggle');
  tt.checked = showThink;
  tt.addEventListener('change', () => {
    showThink = tt.checked;
    try { localStorage.setItem('lt-think', showThink ? '1' : '0'); } catch (e) { /* 忽略 */ }
    rebuildChat();
  });

  $('#ex-go').addEventListener('click', askExpert);
  $('#cs-copy').addEventListener('click', async (e) => {
    try {
      await navigator.clipboard.writeText(charsetText());
      e.target.textContent = t('csCopied');
      setTimeout(() => { e.target.textContent = t('csCopy'); }, 1500);
    } catch (err) { /* 忽略 */ }
  });
  $('#ex-in').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) askExpert();
  });
  $('#ex-clear').addEventListener('click', () => { chatHistory = []; chatLog.length = 0; $('#ex-chat').innerHTML = ''; });
  $('#ex-chat').addEventListener('click', async (e) => {
    const btn = e.target.closest('.msgcopy');
    if (!btn) return;
    const msg = btn.closest('.msg');
    const idx = Array.prototype.indexOf.call(msg.parentNode.children, msg);
    const item = chatLog[idx];
    if (!item) return;
    if (await copyText(item.body)) flashCopy(btn, t('csCopied'));
  });

  applyUI();
  onLangChange();
}

function onLangChange() {
  const L = LANGS[LANG];
  const name = (I18N[UILANG].miniNames || {})[LANG] || L.native;
  const target = (I18N[UILANG].miniTargets || {})[LANG] || L.target;
  $('#langinfo').textContent =
    `${name}　${L.unit === 'char' ? t('charUnit') : t('wordUnit')}` +
    `　${t('coreLbl')} ${L.words.filter(w => w.lv === 'C').length} ＋ ${t('extLbl')} ${L.words.filter(w => w.lv === 'E').length}` +
    `　${t('audience')}：${target}`;

  // 類別選單
  const cats = [...new Set(L.words.map(w => w.cat))];
  $('#wd-cat').innerHTML = `<option value="">${t('wdAllCat')}</option>` +
    cats.map(c => `<option value="${c}">${c}</option>`).join('');

  renderWords();
  renderCharSet();
  renderRules();
  $('#sp-voices').textContent =
    `${L.browserLang}　｜　${Object.entries(L.tts || {}).flatMap(([loc, vs]) => vs.map(v => loc + ' / ' + v)).join('　') || t('voicesNone')}`;
  updatePinyin();
  trOutText = '';
  renderTrOut();
  rebuildChat();
}

// ── 翻譯器 ─────────────────────────────────────────────────────────────────
async function checkTranslate() {
  const text = $('#tr-in').value;
  if (!text.trim()) return;
  const r = await post('/api/check', { lang: LANG, text });
  showCheck(r, '#tr-result');
}

async function reverseTranslate() {
  const text = $('#tr-in').value;
  if (!text.trim()) return;
  if (UILANG !== 'zh-Hant') $('#tr-result').innerHTML = `<span class="hint">${t('thinking')}</span>`;
  trOutText = '';
  renderTrOut();
  let last = 0;
  const paint = () => {
    if (Date.now() - last > 120) { renderTrOut(); last = Date.now(); }
  };
  try {
    const resp = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang: LANG, text, ui: UILANG }),
    });
    if (!resp.ok || !resp.body) {
      const j = await resp.json().catch(() => ({}));
      throw new Error(j.error || ('HTTP ' + resp.status));
    }
    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = '', rewrite = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split('\n\n');
      buf = parts.pop();
      for (const ev of parts) {
        if (!ev.startsWith('data:')) continue;
        let j;
        try { j = JSON.parse(ev.slice(5)); } catch (e) { continue; }
        if (j.type === 'base') {
          // 規則翻譯先上畫面；LLM 改寫一開始就把它換掉
          if (!rewrite) { trOutText = j.text; paint(); }
        } else if (j.type === 'content') {
          if (!rewrite) trOutText = '';
          rewrite += j.text;
          trOutText = rewrite;
          paint();
        } else if (j.type === 'error') {
          trOutText = (trOutText ? trOutText + '\n' : '') + '⚠ ' + j.text;
        }
      }
    }
  } catch (e) {
    trOutText = '⚠ ' + (e.message || e);
  }
  renderTrOut();
  $('#tr-result').innerHTML = '';
}

// ── 檢查器 ─────────────────────────────────────────────────────────────────
async function checkOnly() {
  const text = $('#ck-in').value;
  if (!text.trim()) return;
  const r = await post('/api/check', { lang: LANG, text });
  showCheck(r, '#ck-result');
}

function showCheck(r, sel) {
  const box = $(sel);
  if (r.ok) {
    box.innerHTML = `<div class="ok">${t('checkOk')}</div>`;
    return;
  }
  const items = r.errors.map(e =>
    `<li><b>${e.kind}</b>：${escapeHtml(e.msg)}` +
    (e.token ? `　<span class="hint">（${escapeHtml(e.token)}）</span>` : '') + '</li>').join('');
  box.innerHTML = `<div class="err">${tf('checkErr', { n: r.errors.length })}</div><ul>${items}</ul>`;
}

// ── 唸出來 ─────────────────────────────────────────────────────────────────
let voicesCache = [];

function loadVoices() {
  if (!('speechSynthesis' in window)) return [];
  voicesCache = speechSynthesis.getVoices();
  return voicesCache;
}
if ('speechSynthesis' in window) {
  loadVoices();
  speechSynthesis.onvoiceschanged = loadVoices;
}

// 各語言偏好的優質語音（依序遞減；命中越多越好）
const VOICE_PREF = {
  'zh-CN': ['Tingting', 'Ting-Ting', 'Microsoft Xiaoxiao', 'Microsoft Yunxi',
            'Sinji', 'Meijia', 'Google 國語', 'Google Chinese'],
  'zh-TW': ['Meijia', 'Sinji', 'Microsoft Yunxi', 'Google 國語'],
  'en-US': ['Samantha', 'Aria', 'Microsoft Aria', 'Microsoft Jenny', 'Microsoft Guy',
            'Alex', 'Allison', 'Google US English'],
  'en-GB': ['Daniel', 'Microsoft Libby', 'Serena', 'Google UK English'],
  'fr-FR': ['Thomas', 'Microsoft Denys', 'Amelie', 'Google français', 'Google French'],
  'ja-JP': ['Kyoko', 'O-ren', 'Microsoft Haruka', 'Google 日本語', 'Google Japanese'],
  'ko-KR': ['Yuna', 'Microsoft Heami', 'Google 한국의', 'Google Korean'],
};
// 各語言的朗讀語速（稍慢一點比較清楚）
const RATE = {
  'zh-CN': 0.88, 'zh-TW': 0.88, 'en-US': 0.96, 'en-GB': 0.96,
  'fr-FR': 0.96, 'ja-JP': 0.94, 'ko-KR': 0.94,
};

function pickVoice() {
  const L = LANGS[LANG];
  const want = L.browserLang || 'en-US';
  const vs = loadVoices();
  if (!vs.length) return null;
  const base = want.split('-')[0];
  const pref = VOICE_PREF[want] || [];
  const scored = vs.map((v) => {
    const lang = (v.lang || '').replace('_', '-');
    let sc = -1;
    if (lang === want) sc = 100;
    else if (lang.split('-')[0] === base) sc = 40;
    if (sc < 0) return null;
    if (v.localService) sc += 25;                       // 系統語音通常較自然
    const name = `${v.name || ''} ${v.voiceURI || ''}`;
    const idx = pref.findIndex((p) => name.toLowerCase().includes(p.toLowerCase()));
    if (idx >= 0) sc += 60 - idx * 4;                    // 偏好清單越前面越加分
    if (/natural|neural|enhanced|premium/i.test(name)) sc += 20;
    if (/microsoft/i.test(name)) sc += 8;
    if (/google/i.test(name)) sc += 4;
    if (v.default) sc += 2;
    return { v, sc };
  }).filter(Boolean).sort((a, b) => b.sc - a.sc);
  return scored.length ? scored[0].v : null;
}

// 逐句朗讀：長句在部分瀏覽器會被截斷，切句比較穩
function splitSentences(text) {
  const parts = text.split(/(?<=[。！？!?；;…])|\n+/);
  const out = [];
  for (const p of parts) {
    const t = p.trim();
    if (!t) continue;
    if (t.length <= 120) { out.push(t); continue; }
    for (let i = 0; i < t.length; i += 120) out.push(t.slice(i, i + 120));
  }
  return out.length ? out : [text.trim()];
}

function speak(text) {
  if (!text.trim()) return;
  // 先跳到「唸出來」分頁，直接播放
  $$('.tab').forEach(x => x.classList.remove('active'));
  $$('.panel').forEach(x => x.classList.remove('active'));
  const tab = document.querySelector('.tab[data-tab="speak"]');
  tab.classList.add('active');
  $('#tab-speak').classList.add('active');
  $('#sp-in').value = text;
  updatePinyin();
  speakBrowser();
}

function speakBrowser() {
  const text = $('#sp-in').value;
  if (!text.trim()) return;
  if (!('speechSynthesis' in window)) { alert(t('noSpeech')); return; }
  speechSynthesis.cancel();
  const v = pickVoice();
  const lang = v ? v.lang : (LANGS[LANG].browserLang || 'en-US');
  const base = RATE[LANGS[LANG].browserLang] || 0.95;
  const rate = (parseFloat($('#sp-rate').value) || 1) * base;
  for (const part of splitSentences(text)) {
    const u = new SpeechSynthesisUtterance(part);
    if (v) u.voice = v;
    u.lang = lang;
    u.rate = rate;
    u.pitch = 1;
    speechSynthesis.speak(u);
  }
  showVoiceInfo(v);
}

function showVoiceInfo(v) {
  const L = LANGS[LANG];
  const name = v ? `${v.name}（${v.lang}${v.localService ? '' : '・網路'}）` : '（找不到語音）';
  $('#sp-voices').textContent = `${t('browserVoice')}：${name}　｜　${L.browserLang}`;
}

function stopSpeak() {
  if ('speechSynthesis' in window) speechSynthesis.cancel();
  const a = $('#sp-audio');
  if (a) { a.pause(); a.currentTime = 0; }
}

async function speakServer() {
  const text = $('#sp-in').value;
  if (!text.trim()) return;
  const L = LANGS[LANG];
  const voices = Object.entries(L.tts || {}).flatMap(([loc, vs]) => vs.map(v => ({ loc, v })));
  const voice = voices.length ? voices[0].v : '';
  const a = $('#sp-audio');
  a.removeAttribute('src');
  try {
    const r = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang: LANG, text, voice }),
    });
    if (!r.ok) {
      const j = await r.json().catch(() => ({}));
      throw new Error(j.error || ('HTTP ' + r.status));
    }
    const blob = await r.blob();
    a.src = URL.createObjectURL(blob);
    a.play();
  } catch (e) {
    alert(tf('ttsFail', { msg: e.message }));
  }
}

function updatePinyin() {
  const box = $('#sp-pinyin');
  if (LANG !== 'chinese') { box.innerHTML = ''; return; }
  const map = new Map(LANGS.chinese.words.map(w => [w.w, w.ip || '']));
  box.innerHTML = [...$('#sp-in').value].filter(c => map.has(c)).map(c =>
    `<span>${escapeHtml(c)}<small>${escapeHtml(map.get(c))}</small></span>`).join('');
}

// ── 詞典 ───────────────────────────────────────────────────────────────────
async function lookup() {
  const q = $('#lx-q').value.trim();
  if (!q) return;
  const r = await fetch(`/api/lexicon?lang=${encodeURIComponent(LANG)}&word=${encodeURIComponent(q)}`);
  const rows = await r.json();
  const box = $('#lx-result');
  if (!rows.length) { box.innerHTML = `<div class="err">${t('lxNotFound')}</div>`; return; }
  box.innerHTML = rows.map(r0 => {
    const note = r0['說明'] ? `　<span class="hint">（${escapeHtml(r0['說明'])}）</span>` : '';
    return `<div class="wordcard"><div class="w">${escapeHtml(r0['受限說法'])}` +
      `<span class="lv">${escapeHtml(r0['方式'])}</span></div>` +
      `<div class="g">${escapeHtml(r0['原文'])}</div>${note}</div>`;
  }).join('');
}

// ── 詞表 ───────────────────────────────────────────────────────────────────
function renderWords() {
  const L = LANGS[LANG];
  const q = $('#wd-q').value.trim().toLowerCase();
  const cat = $('#wd-cat').value;
  const lv = $('#wd-lv').value;
  const rows = L.words.filter(w =>
    (!q || w.w.toLowerCase().includes(q) || (w.g || '').toLowerCase().includes(q)) &&
    (!cat || w.cat === cat) &&
    (!lv || w.lv === lv));
  $('#wd-count').textContent = tf('nItems', { n: rows.length });
  $('#wd-result').innerHTML = rows.slice(0, 600).map(w =>
    `<div class="wordcard" data-word="${escapeHtml(w.w)}">` +
    `<span class="lv">${w.lv}</span>` +
    `<div class="w">${escapeHtml(w.w)}</div>` +
    `<div class="g">${escapeHtml(w.g || '')}</div>` +
    (w.ex ? `<div class="ex">${escapeHtml(w.ex)}</div>` : '') +
    `</div>`).join('');
  $$('#wd-result .wordcard').forEach(c =>
    c.addEventListener('click', () => speak(c.dataset.word)));
}

// ── 字集 ───────────────────────────────────────────────────────────────────
function buildCharSet() {
  const L = LANGS[LANG];
  const by = new Map();
  const cats = [];
  const push = (cat, item) => {
    if (!by.has(cat)) { by.set(cat, []); cats.push(cat); }
    by.get(cat).push(item);
  };
  if (L.script === 'latin') {
    for (const w of L.words) push(w.cat, { t: w.w, ip: '' });
  } else {
    // 非拉丁文字（中文、日文、韓文）：把詞拆成「字」，依類別去重
    const seen = new Set();
    for (const w of L.words) {
      for (const ch of w.w) {
        if (seen.has(ch)) continue;
        seen.add(ch);
        push(w.cat, { t: ch, ip: (L.rom && L.rom[ch]) || '' });
      }
    }
  }
  return { cats, by, latin: L.script === 'latin' };
}

function renderCharSet() {
  const cs = buildCharSet();
  const total = cs.cats.reduce((a, c) => a + cs.by.get(c).length, 0);
  $('#cs-count').textContent = tf('nItems', { n: total });
  $('#cs-list').innerHTML = cs.cats.map(cat =>
    `<div class="cs-cat"><h3>${escapeHtml(cat)}</h3><p>` +
    cs.by.get(cat).map(it =>
      `<span class="cs-u" data-u="${escapeHtml(it.t)}">` +
      (it.ip ? `<ruby>${escapeHtml(it.t)}<rt>${escapeHtml(it.ip)}</rt></ruby>` : escapeHtml(it.t)) +
      '</span>').join(cs.latin ? ' ' : '') +
    '</p></div>').join('');
  $$('#cs-list .cs-u').forEach(el => el.addEventListener('click', () => speak(el.dataset.u)));
}

function charsetText() {
  const cs = buildCharSet();
  return cs.cats.map(cat =>
    `# ${cat}\n${cs.by.get(cat).map(it => it.t).join(cs.latin ? ' ' : '')}`).join('\n\n');
}

// ── 語法 ───────────────────────────────────────────────────────────────────
function renderRules() {
  const L = LANGS[LANG];
  $('#rules-title').textContent = tf('rulesTitle', { name: L.name, n: L.rules.length });
  $('#rules').innerHTML = L.rules.map(r =>
    `<div class="rule"><div class="r">${r.id}. ${escapeHtml(r.text)}</div>` +
    (r.ex ? `<div class="e">${t('ruleEx')}：${escapeHtml(r.ex)}</div>` : '') + '</div>').join('');
}

// ── LLM 專家 ───────────────────────────────────────────────────────────────
const chatLog = [];

function renderMsgEl(m) {
  const d = document.createElement('div');
  d.className = 'msg ' + m.cls;
  d.innerHTML = msgHTML(m);
  return d;
}

// 複製（只用純文字，不含 ruby 標音）
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (e) {
    // 沒有剪貼簿權限時，用舊方法
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
    ta.remove();
    return ok;
  }
}

function flashCopy(btn, label) {
  if (!btn) return;
  const old = btn.textContent;
  btn.textContent = label;
  setTimeout(() => { btn.textContent = old; }, 1500);
}

function msgHTML(m) {
  let html = `<div class="who">${m.who}<button class="msgcopy" title="${t('copyBtn')}">⧉</button></div>`;
  if (m.reasoning) {
    html += `<details class="think"${showThink ? ' open' : ''}>` +
      `<summary>${t('thinkSummary')}</summary>` +
      `<div>${escapeHtml(m.reasoning)}</div></details>`;
  }
  const body = m.body ? withRuby(m.body) : `<span class="hint">${t('thinking')}</span>`;
  return html + `<div class="body">${body}</div>`;
}

function updateMsgEl(d, m) { d.innerHTML = msgHTML(m); }

function addMsg(who, body, cls) {
  const m = { who, body, cls: cls || who };
  chatLog.push(m);
  const d = renderMsgEl(m);
  $('#ex-chat').appendChild(d);
  $('#ex-chat').scrollTop = $('#ex-chat').scrollHeight;
  return d;
}

function rebuildChat() {
  const box = $('#ex-chat');
  box.innerHTML = '';
  chatLog.forEach((m) => box.appendChild(renderMsgEl(m)));
  box.scrollTop = box.scrollHeight;
}

async function askExpert() {
  const msg = $('#ex-in').value.trim();
  if (!msg) return;
  $('#ex-in').value = '';
  addMsg(t('you'), msg, 'user');
  chatHistory.push({ role: 'user', content: msg });

  // 串流中的回答：即時更新畫面
  const m = { who: t('expert'), body: '', cls: 'assistant', reasoning: '' };
  chatLog.push(m);
  const d = renderMsgEl(m);
  $('#ex-chat').appendChild(d);
  $('#ex-chat').scrollTop = $('#ex-chat').scrollHeight;

  let last = 0;
  const refresh = (force) => {
    if (force || Date.now() - last > 120) {
      updateMsgEl(d, m);
      $('#ex-chat').scrollTop = $('#ex-chat').scrollHeight;
      last = Date.now();
    }
  };

  try {
    const resp = await fetch('/api/expert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lang: LANG, message: msg, history: chatHistory.slice(0, -1),
        provider: $('#ex-provider').value, mode: $('#ex-mode').value,
      }),
    });
    if (!resp.ok || !resp.body) {
      const j = await resp.json().catch(() => ({}));
      throw new Error(j.error || ('HTTP ' + resp.status));
    }
    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split('\n\n');
      buf = parts.pop();
      for (const ev of parts) {
        if (!ev.startsWith('data:')) continue;
        let j;
        try { j = JSON.parse(ev.slice(5)); } catch (e) { continue; }
        if (j.type === 'reasoning') { m.reasoning += j.text; refresh(); }
        else if (j.type === 'content') { m.body += j.text; refresh(); }
        else if (j.type === 'tool') { m.body += `\n〔${j.name} ${j.ok ? '✓' : '✗'}〕\n`; refresh(); }
        else if (j.type === 'error') { m.body += (m.body ? '\n' : '') + '⚠ ' + j.text; refresh(true); }
      }
    }
  } catch (e) {
    m.body += (m.body ? '\n' : '') + '⚠ ' + (e.message || e);
  }
  if (!m.body) m.body = t('noReply');
  refresh(true);
  chatHistory.push({ role: 'assistant', content: m.body });
}

// ── 工具 ───────────────────────────────────────────────────────────────────
async function post(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return r.json();
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '\u0026amp;').replace(/</g, '\u0026lt;').replace(/>/g, '\u0026gt;')
    .replace(/"/g, '\u0026quot;');
}

document.addEventListener('DOMContentLoaded', init);
