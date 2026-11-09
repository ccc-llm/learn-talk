/**
 * learn-talk Cloudflare Worker
 *
 * - /api/langs          → 語言清單（輕量）
 * - /api/data?lang=xx   → 該語言的完整資料（詞表、規則、羅馬字、詞典、反向表、提示詞）
 * - 其他路徑              → 靜態檔案（src/public）
 *
 * 資料來源（二選一）：
 *   R2 binding  BUCKET  → 物件 langs.json
 *   KV binding  DATA    → key  langs
 */

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,OPTIONS',
  'access-control-allow-headers': 'content-type',
};

let cache = null;   // 同一個 isolate 內快取

async function loadData(env) {
  if (cache) return cache;
  let text = null;
  if (env.BUCKET) {
    const obj = await env.BUCKET.get('langs.json');
    if (obj) text = await obj.text();
  }
  if (!text && env.DATA) {
    text = await env.DATA.get('langs');
  }
  if (!text) return null;
  cache = JSON.parse(text);
  return cache;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=600', ...CORS },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (url.pathname === '/api/langs') {
      const data = await loadData(env);
      if (!data) return json({ error: 'no data: put langs.json into R2 (or langs into KV)' }, 404);
      const list = Object.entries(data).map(([code, v]) => ({
        code,
        name: v.name,
        native: v.native,
        unit: v.unit,
        script: v.script,
        words: v.words.length,
      }));
      return json(list);
    }

    if (url.pathname === '/api/rom') {
      // 各語言的字→羅馬字（中文拼音／日文羅馬字／韓文 RR），供 ruby 標音
      const data = await loadData(env);
      if (!data) return json({ error: 'no data' }, 404);
      const rom = {};
      for (const code of ['chinese', 'japanese', 'korean']) {
        if (data[code] && data[code].rom) rom[code] = data[code].rom;
      }
      return json(rom);
    }

    if (url.pathname === '/api/data') {
      const code = url.searchParams.get('lang') || 'chinese';
      const data = await loadData(env);
      if (!data) return json({ error: 'no data' }, 404);
      if (!data[code]) return json({ error: 'unknown language: ' + code }, 404);
      return json(data[code]);
    }

    if (url.pathname === '/api/tts') {
      // 代理到自架的 edge-tts 服務（免費高品質）。
      // 在 wrangler.toml 設定 vars.TTS_UPSTREAM = "https://你的服務/api/tts"
      const upstream = env.TTS_UPSTREAM;
      if (!upstream) {
        return new Response('edge-tts 尚未設定（TTS_UPSTREAM）', { status: 501, headers: CORS });
      }
      const body = await request.text();
      const r = await fetch(upstream, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body,
      });
      return new Response(r.body, {
        status: r.status,
        headers: { 'content-type': r.headers.get('content-type') || 'audio/mpeg', ...CORS },
      });
    }

    return env.ASSETS.fetch(request);
  },
};
