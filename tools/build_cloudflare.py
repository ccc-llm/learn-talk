#!/usr/bin/env python3
"""由靜態版產生 Cloudflare 版。

- core/staticweb/*            → core/cloudflare/src/public/*（前端改為從 /api 載入資料）
- core/web/data.js 的 LANGS   → core/cloudflare/data/langs.json（放在 R2／KV，不進版控）

用法：python tools/build_cloudflare.py
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'core' / 'staticweb'
DST = ROOT / 'core' / 'cloudflare'
PUB = DST / 'src' / 'public'


def patch_index(html: str) -> str:
    # 資料改由 /api 取得，不再內嵌 data.js
    html = html.replace('<script src="data.js"></script>\n', '')
    html = html.replace('<link rel="stylesheet" href="style.css">',
                        '<meta name="data-base" content="">\n'
                        '<meta name="tts-url" content="/api/tts">\n'
                        '<link rel="stylesheet" href="style.css">')
    html = html.replace('靜態版：沒有後端。把自己的 API Key 填在「LLM 專家」分頁上，'
                        '瀏覽器直接呼叫 LLM（串流）；金鑰只存在這臺電腦的瀏覽器裡。',
                        'Cloudflare 版：詞表與提示詞放在後端（R2／KV），'
                        '用自己的 API Key 在瀏覽器直接呼叫 LLM（串流）；金鑰只存在你的瀏覽器裡。')
    return html


def patch_app(js: str) -> str:
    # 1) 宣告 LANGS（改成從 API 載入）
    old = "let LANG = 'chinese';"
    new = """let LANG = 'chinese';
let LANGS = {};          // 從 /api 載入（Cloudflare 版）
let LANGS_META = [];     // 語言清單
const DATA_BASE = (document.querySelector('meta[name="data-base"]') || {}).content || '';

async function apiJSON(path) {
  const r = await fetch(DATA_BASE + path);
  if (!r.ok) throw new Error('HTTP ' + r.status + '（' + path + '）');
  return r.json();
}

async function loadLangMeta() {
  LANGS_META = await apiJSON('/api/langs');
}

async function loadLangData(code) {
  if (LANGS[code]) return;
  LANGS[code] = await apiJSON('/api/data?lang=' + encodeURIComponent(code));
}"""
    assert js.count(old) == 1
    js = js.replace(old, new)

    # 2) init：先載入語言清單與第一個語言的資料
    old = """function init() {
  // 介面語言"""
    new = """async function init() {
  // 介面語言"""
    assert js.count(old) == 1
    js = js.replace(old, new)

    old = """  // 學習語言（Mini-X）
  const sel = $('#lang');
  Object.keys(LANGS).forEach((code) => {
    const o = document.createElement('option');
    o.value = code;
    o.textContent = `${LANGS[code].name}（${LANGS[code].words.length} ${t('units')}）`;
    sel.appendChild(o);
  });
  sel.value = 'chinese';
  sel.addEventListener('change', () => { LANG = sel.value; onLangChange(); });"""
    new = """  // 學習語言（Mini-X）：清單與資料都來自後端
  const sel = $('#lang');
  sel.addEventListener('change', async () => {
    LANG = sel.value;
    $('#langinfo').textContent = t('loading');
    try {
      await loadLangData(LANG);
      onLangChange();
    } catch (e) {
      $('#langinfo').textContent = '⚠ ' + (e.message || e);
    }
  });"""
    assert js.count(old) == 1
    js = js.replace(old, new)

    old = """  applyUI();
  onLangChange();
}"""
    new = """  applyUI();

  // 載入語言清單與資料
  try {
    await loadLangMeta();
    LANGS_META.forEach((m) => {
      const o = document.createElement('option');
      o.value = m.code;
      o.textContent = `${m.name}（${m.words} ${t('units')}）`;
      sel.appendChild(o);
    });
    sel.value = LANG;
    await loadLangData(LANG);
    onLangChange();
  } catch (e) {
    $('#langinfo').innerHTML =
      `<span class="err">⚠ ${e.message || e}</span><br>` +
      '（請確認後端已部署資料：把 core/cloudflare/data/langs.json 放到 R2 或 KV）';
  }
}"""
    assert js.count(old) == 1
    js = js.replace(old, new)

    # 3) 介面語言切換時，語言資料要重新載入
    old = """  ui.addEventListener('change', () => {
    UILANG = ui.value;
    try { localStorage.setItem('lt-ui-lang', UILANG); } catch (e) { /* 忽略 */ }
    applyUI();
    onLangChange();
  });"""
    new = """  ui.addEventListener('change', () => {
    UILANG = ui.value;
    try { localStorage.setItem('lt-ui-lang', UILANG); } catch (e) { /* 忽略 */ }
    applyUI();
    if (LANGS[LANG]) onLangChange();
  });"""
    assert js.count(old) == 1
    js = js.replace(old, new)

    # 4) onLangChange：資料還沒載入就先跳過
    old = """function onLangChange() {
  const L = LANGS[LANG];"""
    new = """function onLangChange() {
  const L = LANGS[LANG];
  if (!L) return;"""
    assert js.count(old) == 1
    js = js.replace(old, new)

    # 5) i18n：loading
    js = js.replace(" needKey: '請先填入 API Key（只存在你的瀏覽器裡）',",
                    " needKey: '請先填入 API Key（只存在你的瀏覽器裡）', loading: '載入中…',")
    js = js.replace(" needKey: 'Please enter your API key (stored only in your browser)',",
                    " needKey: 'Please enter your API key (stored only in your browser)', loading: 'Loading…',")
    js = js.replace(" needKey: 'Veuillez saisir votre clé API (elle reste dans votre navigateur)',",
                    " needKey: 'Veuillez saisir votre clé API (elle reste dans votre navigateur)', loading: 'Chargement…',")
    js = js.replace(" needKey: '先に API キーを入力してください（ブラウザーにだけ保存されます）',",
                    " needKey: '先に API キーを入力してください（ブラウザーにだけ保存されます）', loading: '読み込み中…',")
    js = js.replace(" needKey: '먼저 API 키를 입력하세요(브라우저에만 저장됩니다)',",
                    " needKey: '먼저 API 키를 입력하세요(브라우저에만 저장됩니다)', loading: '불러오는 중…',")

    return js


def main():
    PUB.mkdir(parents=True, exist_ok=True)
    (DST / 'data').mkdir(parents=True, exist_ok=True)

    html = patch_index((SRC / 'index.html').read_text(encoding='utf-8'))
    (PUB / 'index.html').write_text(html, encoding='utf-8')
    shutil.copy(SRC / 'style.css', PUB / 'style.css')

    js = patch_app((SRC / 'app.js').read_text(encoding='utf-8'))
    (PUB / 'app.js').write_text(js, encoding='utf-8')

    # 資料：從 core/web/data.js 取出 LANGS 物件
    raw = (ROOT / 'core' / 'web' / 'data.js').read_text(encoding='utf-8')
    m = re.match(r'const LANGS = (\{.*\});\s*$', raw, re.S)
    data = json.loads(m.group(1))
    out = DST / 'data' / 'langs.json'
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'✅ {out}（{len(data)} 個語言、{out.stat().st_size / 1024:.0f} KB）')
    print(f'✅ {PUB}/index.html、app.js、style.css')


if __name__ == '__main__':
    main()
