/* learn-talk 網頁：翻譯器／檢查器／唸出來／詞典／詞表／語法／LLM 專家 */

let LANG = 'chinese';
let LANGS = LANGS || {};
let chatHistory = [];

// ── 初始化 ─────────────────────────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

function init() {
  // 語言選單
  const sel = $('#lang');
  Object.keys(LANGS).forEach((code) => {
    const o = document.createElement('option');
    o.value = code;
    o.textContent = `${LANGS[code].name}（${LANGS[code].words.length} 單位）`;
    sel.appendChild(o);
  });
  sel.value = 'chinese';
  sel.addEventListener('change', () => { LANG = sel.value; onLangChange(); });

  // 分頁
  $$('.tab').forEach((t) => t.addEventListener('click', () => {
    $$('.tab').forEach((x) => x.classList.remove('active'));
    $$('.panel').forEach((x) => x.classList.remove('active'));
    t.classList.add('active');
    $('#tab-' + t.dataset.tab).classList.add('active');
  }));

  $('#tr-check').addEventListener('click', checkTranslate);
  $('#tr-rev').addEventListener('click', reverseTranslate);
  $('#tr-speak').addEventListener('click', () => speak($('#tr-in').value));
  $('#tr-out-speak').addEventListener('click', () => speak($('#tr-out').value));

  $('#ck-go').addEventListener('click', checkOnly);
  $('#ck-file').addEventListener('click', () => $('#ck-file-input').click());
  $('#ck-file-input').addEventListener('change', (e) => {
    const f = e.target.files[0];
    if (!f) return;
    f.text().then((t) => { $('#ck-in').value = t; checkOnly(); });
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
    const t = $('#wd-result').querySelector('.wordcard');
    if (t) speak(t.dataset.word);
  });

  $('#ex-go').addEventListener('click', askExpert);
  $('#ex-in').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) askExpert();
  });
  $('#ex-clear').addEventListener('click', () => { chatHistory = []; $('#ex-chat').innerHTML = ''; });

  onLangChange();
}

function onLangChange() {
  const L = LANGS[LANG];
  $('#langinfo').textContent =
    `${L.native}　${L.unit === 'char' ? '以「字」為單位' : '以「詞」為單位'}` +
    `　核心 ${L.words.filter(w => w.lv === 'C').length} ＋ 擴充 ${L.words.filter(w => w.lv === 'E').length}` +
    `　對象：${L.target}`;

  // 類別選單
  const cats = [...new Set(L.words.map(w => w.cat))];
  $('#wd-cat').innerHTML = '<option value="">全部類別</option>' +
    cats.map(c => `<option value="${c}">${c}</option>`).join('');

  renderWords();
  renderRules();
  $('#sp-voices').textContent =
    `瀏覽器語音：${L.browserLang}　｜　伺服器語音：${Object.entries(L.tts || {}).flatMap(([loc, vs]) => vs.map(v => loc + ' / ' + v)).join('　') || '（未設定）'}`;
  updatePinyin();
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
  const r = await post('/api/translate', { lang: LANG, text });
  $('#tr-out').value = r.text || '';
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
    box.innerHTML = '<div class="ok">✅ 全部在字表內，語法也正確。</div>';
    return;
  }
  const items = r.errors.map(e =>
    `<li><b>${e.kind}</b>：${escapeHtml(e.msg)}` +
    (e.token ? `　<span class="hint">（${escapeHtml(e.token)}）</span>` : '') + '</li>').join('');
  box.innerHTML = `<div class="err">❌ 有 ${r.errors.length} 個問題：</div><ul>${items}</ul>`;
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

function pickVoice() {
  const L = LANGS[LANG];
  const want = L.browserLang;
  const vs = loadVoices();
  if (!vs.length) return null;
  return vs.find(v => v.lang === want) ||
    vs.find(v => v.lang && v.lang.startsWith(want.slice(0, 2))) || null;
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
  if (!('speechSynthesis' in window)) { alert('這個瀏覽器不支援語音朗讀。'); return; }
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const v = pickVoice();
  if (v) u.voice = v;
  u.lang = LANGS[LANG].browserLang;
  u.rate = parseFloat($('#sp-rate').value) || 1;
  u.pitch = 1;
  speechSynthesis.speak(u);
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
    alert('伺服器語音失敗：' + e.message + '\n（請確認有安裝 edge-tts）');
  }
}

async function updatePinyin() {
  const box = $('#sp-pinyin');
  if (LANG !== 'chinese') { box.innerHTML = ''; return; }
  const r = await fetch('/api/romaji?text=' + encodeURIComponent($('#sp-in').value));
  const j = await r.json();
  box.innerHTML = j.map(x =>
    `<span>${escapeHtml(x.char)}<small>${escapeHtml(x.pinyin || '')}</small></span>`).join('');
}

// ── 詞典 ───────────────────────────────────────────────────────────────────
async function lookup() {
  const q = $('#lx-q').value.trim();
  if (!q) return;
  const r = await fetch(`/api/lexicon?lang=${encodeURIComponent(LANG)}&word=${encodeURIComponent(q)}`);
  const rows = await r.json();
  const box = $('#lx-result');
  if (!rows.length) { box.innerHTML = '<div class="err">詞典裡沒有這個詞。試試用「描述」或「外來語」。</div>'; return; }
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
  $('#wd-count').textContent = `${rows.length} 個`;
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

// ── 語法 ───────────────────────────────────────────────────────────────────
function renderRules() {
  const L = LANGS[LANG];
  $('#rules-title').textContent = `${L.name} 的語法規則（${L.rules.length} 條）`;
  $('#rules').innerHTML = L.rules.map(r =>
    `<div class="rule"><div class="r">${r.id}. ${escapeHtml(r.text)}</div>` +
    (r.ex ? `<div class="e">例：${escapeHtml(r.ex)}</div>` : '') + '</div>').join('');
}

// ── LLM 專家 ───────────────────────────────────────────────────────────────
function addMsg(who, body, cls) {
  const d = document.createElement('div');
  d.className = 'msg ' + (cls || who);
  d.innerHTML = `<div class="who">${who}</div><div class="body">${escapeHtml(body)}</div>`;
  $('#ex-chat').appendChild(d);
  $('#ex-chat').scrollTop = $('#ex-chat').scrollHeight;
  return d;
}

async function askExpert() {
  const msg = $('#ex-in').value.trim();
  if (!msg) return;
  $('#ex-in').value = '';
  addMsg('你', msg, 'user');
  chatHistory.push({ role: 'user', content: msg });
  const pending = addMsg('專家', '思考中…', 'assistant');
  const r = await post('/api/expert', {
    lang: LANG, message: msg, history: chatHistory.slice(0, -1),
    provider: $('#ex-provider').value,
  });
  pending.remove();
  if (r.error) { addMsg('錯誤', r.error, 'error'); return; }
  addMsg('專家', r.reply || '（沒有回應）', 'assistant');
  chatHistory.push({ role: 'assistant', content: r.reply || '' });
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
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', init);
