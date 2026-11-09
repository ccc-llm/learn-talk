# learn-talk on Cloudflare

詞表、規則、羅馬字、詞典與提示詞放在**後端**（R2 或 KV），網站本身只有幾個小檔案。
使用者在自己的瀏覽器填入 API Key，直接呼叫 NVIDIA／MiniMax（串流），金鑰不會經過 Worker。

```
core/cloudflare/
  wrangler.toml          Worker 設定（靜態檔＋KV）
  src/worker.js          Worker：/api/langs、/api/data、/api/tts
  src/public/            網頁（index.html / app.js / style.css，合計約 2.5 KB gzip）
  data/langs.json        資料（由 tools/build_cloudflare.py 產生，放進 KV）
```

線上版：https://learn-talk.ccckmit.workers.dev

## 部署

```bash
cd core/cloudflare

# 1. 產生前端與資料（改了 core/web 的資料或 core/staticweb 要重跑）
python ../../tools/build_cloudflare.py

# 2. 登入
npx wrangler login

# 3. 建立 KV namespace（免費方案可用；R2 需要先在後台開通）
npx wrangler kv namespace create DATA
#    → 把產生的 id 填進 wrangler.toml 的 [[kv_namespaces]]

# 4. 上傳資料
npx wrangler kv key put --binding=DATA --remote langs --path=data/langs.json

# 5. 部署
npx wrangler deploy
```

目前已部署：**https://learn-talk.ccckmit.workers.dev**
（namespace id `41191d2579554a91a4db2ef306865715` 已填在 `wrangler.toml`）

## 本機試跑

```bash
npx wrangler dev        # 會模擬 R2／KV；資料要先上傳到本機模擬器
```

本機模擬器沒有 R2 時，可在 `core/cloudflare/` 下放一個 `dev.json`（把
`data/langs.json` 的內容放進去，key 為 `langs`），Worker 會改讀本機檔案；
或直接部署到 preview 環境測試。

## 改用 R2

`wrangler.toml` 裡已把 R2 綁定註解起來。若要在後台開通 R2，取消註解並建立 bucket：

```bash
npx wrangler r2 bucket create learn-talk-data
npx wrangler r2 object put learn-talk-data/langs.json --file=data/langs.json --remote
```

Worker 會優先讀 R2，沒有才讀 KV。

## 資料放在哪

`tools/build_cloudflare.py` 會把 `core/web/data.js` 裡的 `LANGS` 物件寫成
`data/langs.json`（約 800 KB），Worker 提供：

| 端點 | 內容 |
|---|---|
| `GET /api/langs` | 語言清單（code、名稱、字數） |
| `GET /api/data?lang=chinese` | 該語言的詞表、語法規則、羅馬字、詞典、反向對照表、嚴格／快速提示詞 |

## 語音（免費、不用 key）

預設用**瀏覽器語音**，但已強化：

- 依語言挑最好的語音：優先系統語音（macOS 的 Kyoko／Yuna／Thomas／Samantha…）、
  再依偏好清單、Natural／Neural 加分，避免誤挑 Google 網路語音
- 逐句朗讀（長句不會被 Chrome 截斷）、各語言語速微調（中文 0.88、日韓 0.94…）
- 介面會顯示目前使用的語音名稱

想要更好的品質（Azure Neural 音色、免費）可以自架 edge-tts：

```bash
# 任何一台機器（VPS、家中主機）都能跑
python core/web/server.py          # 這支就有 /api/tts（edge-tts），預設 8770
```

然後把網址填進 Worker 的設定：

```toml
[vars]
TTS_UPSTREAM = "https://你的主機:8770/api/tts"
```

網頁的「edge-tts」按鈕會呼叫 `/api/tts`（Worker 代理到你的服務）；
服務沒設定或連不上時，會自動改用瀏覽器語音，不會出錯。

## 注意

- 瀏覽器直接呼叫 LLM 需要該供應商允許 CORS（NVIDIA、MiniMax 目前都可以）。
- 靜態版與此版本的前端邏輯相同，差別只在資料來源。
