# 設計文件

* [plan.md](plan.md) — 整體計畫（抽象層共用、語言層分開）
* [pronunciation.md](pronunciation.md) — 發音功能（瀏覽器語音／edge-tts）
* [../README.md](../README.md) — 專案說明與快速開始

## 核心抽象

五個語言共用同一套抽象：

```
三層表達法：  本詞  →  描述 + 類頭  →  外來語 + 括號說明
固定規則：    阿拉伯數字、描述模板、困難結構的替代說法、單一權威詞表
可插拔的：    切分單位、形態規則、語序、描述模板、外來語的正字法
```

## 共用 vs 分開

| 放在哪裡 | 內容 |
|---|---|
| `core/` | spec 載入、切分、形態骨架、檢查器、詞典、反向翻譯、LLM client、生成管線、網頁、課本產生 |
| `langs/<lang>/data/` | 詞表、類頭、描述模板、替代表、禁用結構、不規則形式、專有名詞 |
| `langs/<lang>/lexicon.tsv` | 這個語言的詞典 |
| `langs/<lang>/morph` 類的 hook | 由 `core/` 依 `script` 自動選擇（han / latin / kana / hangul） |

實作上，各語言的差異集中在四個地方：

1. **切分**（`core/tokenizer.py`）：中文逐字、日文最長匹配、韓文語節、法英按詞。
2. **形態**（`core/morph.py` + `core/french.py` / `japanese.py` / `korean.py`）。
3. **語序與句型規則**（`langs/<lang>/data/gram.tsv`）。
4. **外來語的正字法**（中文用英文、日文用片假名、韓文用諺文）。
