# 發音功能

網頁的「唸出來」分頁可以用**語音**唸出任何段落文章。提供兩種方式，可以自由切換。

## 方式一：瀏覽器語音（Web Speech API）

* **免金鑰、離線可用**：用的是瀏覽器內建的語音引擎。
* **用法**：在「唸出來」分頁貼上文字 → 按「🔊 瀏覽器唸」。
* **語言自動配對**：每個語言有對應的 locale。

  | 語言 | locale | 瀏覽器會選的聲音 |
  |---|---|---|
  | Mini-Chinese | `zh-CN` | 中文（普通話）女聲／男聲 |
  | Mini-English | `en-US` | 英文女聲／男聲 |
  | Mini-French | `fr-FR` | 法文女聲／男聲 |
  | Mini-Japanese | `ja-JP` | 日文女聲／男聲 |
  | Mini-Korean | `ko-KR` | 韓文女聲／男聲 |

* **可調速度**：0.5–1.5 倍。
* **限制**：音色品質隨瀏覽器而異（macOS Safari／Chrome 的品質最好，Firefox 較少）；離線時可能沒有語音。

## 方式二：伺服器語音（edge-tts）

* **免金鑰**：Microsoft 的 Edge 朗讀服務，不需要申請 API key。
* **用法**：在「唸出來」分頁貼上文字 → 按「🔊 伺服器唸（mp3）」。會產生一個 mp3 併自動播放。
* **音色**：每個語言有多個自然音色（Neural TTS），比瀏覽器的好很多。

  | 語言 | 音色 |
  |---|---|
  | Mini-Chinese | `zh-CN-XiaoxiaoNeural`、`zh-CN-YunxiNeural`、`zh-TW-HsiaoChenNeural`、`zh-TW-YunJheNeural` |
  | Mini-English | `en-US-AriaNeural`、`en-US-GuyNeural`、`en-GB-SoniaNeural` |
  | Mini-French | `fr-FR-DeniseNeural`、`fr-FR-HenriNeural` |
  | Mini-Japanese | `ja-JP-NanamiNeural`、`ja-JP-KeitaNeural` |
  | Mini-Korean | `ko-KR-SunHiNeural`、`ko-KR-InJoonNeural` |

* **安裝**：

  ```bash
  uv pip install edge-tts
  ```

* **注意**：edge-tts 需要連到微軟的伺服器（不是離線功能）。第一次呼叫若失敗，通常是網路問題。

## 中文另外附拼音

Mini-Chinese 的「唸出來」分頁會同時顯示**逐字拼音**（羅馬字），因為漢字本身不標音。拼音表在 `core/web/server.py` 的 `PINYIN` 字典裡。

## API

```
POST /api/tts
Content-Type: application/json

{"lang": "chinese", "text": "你好世界", "voice": "zh-CN-XiaoxiaoNeural"}
→ audio/mpeg
```

`voice` 不填就用該語言的第一個預設音色。

## 之後可以做的事

* **把 mp3 存起來**：目前只串流播放，可以改成存成檔案，讓學者反覆聽同一段。
* **逐句朗讀**：一個句子一個 mp3，方便跟讀（需要先切句）。
* **真人錄音**：把 `edge-tts` 換成自己的錄音檔，品質最好，但要錄很多。
* **離線 TTS**：用 `piper`、`coqui-tts` 之類的本機模型，完全離線但要另外裝。
