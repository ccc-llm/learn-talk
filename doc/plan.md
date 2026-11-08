# learn-talk 計畫：小字集語言（Mini 系列）

> 目標讀者：母語不是該語言的外國人。
> 參考實作：`/Users/Shared/ccc/project/mini-lang/`（Mini-Chinese 297 字、Mini-English 1,256 詞）。
> 涵蓋語言：英、法、日、韓、中（五種）。

---

## 一、核心想法：抽象層共用，語言層分開

Mini-Chinese 最有價值的不是「297 個字」，而是那個**三層表達模型**：

| 層 | 規則 |
|---|---|
| 本詞 | 在字/詞表內 → 直接用 |
| 描述 | 表外的通用概念 → 「描述 + 類頭」（看病的地方 / a place where…） |
| 外來語 | 說不出「是哪一個」（人名、物種、品牌）→ 原文 + 第一次出現加括號說明，「先定義、後沿用」 |

加上四條通用規則：

- **數字用阿拉伯數字**（1, 2, 3、2026、20%）
- **描述模板固定**（每語言一個模板，引擎只檢查格式）
- **困難結構用固定替代說法**（被動、完成式、假設語氣、關係子句…）
- **一切用程式檢查**（單一權威詞表，其他檔案從它讀取或被它檢查）

五種語言全部照這套抽象走。把「字表／詞表」與「檢查規則」做成可插拔，語言真正不同的只有四件事，隔離成 language profile：

1. **切分單位**：中＝逐字；日＝假名 run ＋ 單字漢字；韓＝語節 eojeol（含助詞）；英法＝詞 ＋ 屈折
2. **形態規則**：英法不規則動詞表；日韓「刻意不用」的活用形
3. **語序**：中／日／韓 SOV，英法 SVO
4. **描述模板**：中「…的地方」、日「…をする場所」、韓「…하는 곳」、英「a place where…」、法「un endroit où…」

**所以：`core/` 放引擎，`langs/` 放資料。**
引擎提供 loader / checker / reverse / coverage / LLM client / web / book 生成；
每個語言只提供 spec ＋ 一個 hook（切分器、形態器、描述模板、替代說法表）。

---

## 二、Repo 結構

```
learn-talk/
  core/                 # 共用引擎（Python，不含任何語言知識）
    spec.py             # 統一 spec 格式：詞表/類別/類頭/描述模板/替代表/語法規則
    tokenizer.py        # 切分器：預設按空白+標點；各語言可覆寫
    morph.py            # 形態：預設無；英法、日、韓各自 subclass
    checker.py          # 通用檢查器（表外詞、外來詞首次須說明、禁用詞、描述合法性）
    reverse.py          # 反向翻譯（詞典比對）
    lexicon.py          # lexicon.tsv 讀寫
    coverage.py         # 覆蓋率測試
    llm.py              # NVIDIA(GLM-5.3-flash) / MiniMax(M3.1) 統一 client ＋ 重試
    gen.py              # 語料生成（給 mini-lm 用）＋ 自動檢查過濾
    book.py             # 課本骨架產生 ＋ 練習答案
    web/                # 共用前端（翻譯器/檢查器/詞表瀏覽/LLM 專家），語言參數化
  langs/
    mini-chinese/  mini-english/  mini-french/  mini-japanese/  mini-korean/
      spec.md | data/*.tsv | morph.py(可選) | prompts/ | lexicon.tsv | examples.md | report.md
  books/<lang>/         # 課本（繁中版 ＋ 英文版）
  tools/                # 跨語言 CLI（check-all / build-all / gen-all）
```

`mini-chinese` 與 `mini-english` 從 `mini-lang` **移植規格資料**（不重做），轉成新 spec 格式；其餘三語新做。

### 各語言 spec 的統一格式

| 檔案 | 內容 |
|---|---|
| `data/words.tsv` | word, level(C/E), pos, gloss, 類別 |
| `data/heads.tsv` | 類頭（描述的最後一個詞） |
| `data/desc.tsv` | 描述模板（做什麼用的、在哪裡的、像什麼的…） |
| `data/replace.tsv` | 禁用詞 → 替代說法 |
| `data/irregular.tsv` | 不規則形式（英法）／例外形式 |
| `data/gram.tsv` | 語法規則（編號、規則、替代、例句） |
| `spec.md` | 設計原則、說明文件（權威詞表由 build 產生） |

---

## 三、五種語言的設計（各自取捨）

### Mini-Chinese（沿用 297 字）

- 只做「移植 ＋ 補描述模板 ＋ 統一 checker」。
- 第三人稱一律「他」，方位一律「…邊」，量詞只六個（沿用 mini-lang 規則）。
- 外來語規則推廣為全系列共用規則。

### Mini-English（沿用 1,256 詞）

- 移植 spec ＋ `morph.py`。
- 核心 600 ＋ 擴充 656 兩層。
- 英法共用 morphology 骨架（不規則表不同）。

### Mini-French（新，目標 ~1,000 詞）

法文難點：**過去分詞、性數一致、相對子句**。做法：

- 只用複合過去（avoir/être ＋ 規則 -é 分詞），不用簡單過去
- 只用現在時 ＋ 複合過去 ＋ 近將來（va + infinitif），不用將來時
- 省略性數一致，只保留陰性詞的 le/la 例外，並在語法規則明講
- 否定只用「ne…pas」
- 描述用「un/une + 名詞 + qui/que/où + 子句」
- 類頭：chose / personne / lieu / genre / sorte

### Mini-Japanese（新，目標 ~600 單位）

日文難點：**漢字量 ＋ 活用**。做法：

- **只用平假名寫動詞、形容詞**；漢字只收名詞（約 300 字）
- **只保留 ます体**：ます・ました・ません・たい；て形一律不出現（理由/條件句改用「から」「と」）
- 助詞只 8 個：は・が・を・に・で・と・の・も；「は」只作主題提示
- 描述用「〜をする人」「〜の場所」；外來語用片假名
- 效果：外國人用假名拼出的日文，母語者讀起來「簡單但正確」

### Mini-Korean（新，目標 ~700 詞）

韓文難點：**助詞 ＋ 活用 ＋ 語序**。做法：

- **只用 해요체**（現在/過去/將來），不用하십시오체、반말
- 助詞只 8 個：은/는(이/가)、을/를、에、에서、도、의、하고
- 詞尾只 5 個：-아요 / -어요 / -해요 / 過去 -았어요・었어요 / 未來 -(으)ㄹ 거예요
- 否定用「안 ＋ 動詞」；能力用「-(으)ㄹ 수 있다」
- 描述用「〜하는 사람 / 장소 / 것」
- 不收漢字，避免兩層負擔；書附羅馬字標音 ＋ 中文解釋

---

## 四、程式：共用 vs 分開

| 功能 | 共用（core/） | 分開（langs/） |
|---|---|---|
| spec 載入、詞表索引 | ✅ | — |
| 檢查器骨架（表外詞、外來詞首次須括號、禁用詞、描述格式） | ✅ | hook：切分器、屈折表、外來詞規則 |
| 反向翻譯 → 該語言原文 | ✅ 演算法 | ✅ 詞典資料 |
| 覆蓋率測試（抽 200 常用詞，統計 本詞/描述/外來詞/說不好） | ✅ | ✅ 各語言抽樣詞表 |
| LLM client（NVIDIA GLM-5.3-flash / MiniMax M3.1-flash） | ✅ | prompt 內容 |
| 語料生成（給 mini-lm）＋ 自動過濾 | ✅ 流程 | ✅ 各語言 prompt ＋ 主題 |
| 網頁（翻譯器/檢查器/詞表/LLM 專家） | ✅ 一份前端 | ✅ 參數與資料 |
| 課本骨架與練習答案 | ✅ 模板 | ✅ 內容 |
| 詞表／描述／語法規則／替代表 | — | ✅ 每語言 |
| 詞典 lexicon.tsv | ✅ 格式 | ✅ 內容 |
| 教學語法規則（句型表） | — | ✅ 每語言（規則編號統一、格式一致） |

---

## 五、生成程式（LLM）

`core/llm.py`：統一 client，`--provider nvidia|minimax`、`--model`、stream、重試、輸出解析、成本統計。
預設 **NVIDIA `z-ai/glm-5.3-flash`**，備援 **MiniMax `minimax-m3.1-flash`**。
環境變數：`NVIDIA_API_KEY`、`MINIMAX_API_KEY`。

`core/gen.py` 三種用途：

1. **語料蒸餾**（對應 mini-lang 的 mini-lm）：依語言 spec ＋ 主題清單產生 pretrain/finetune 語料；每批產出後自動跑 checker，不通過的丟掉並回報一次通過率 → 餵回改 spec（mini-lang 已驗證有效的迴路）
2. **翻譯／改寫測試**：一般文章 → 受限語言 → checker → 統計一次通過率、最常錯的詞
3. **詞典擴充**：從常用詞表產生 Mini 說法候選 → 挑選 → lexicon.tsv

---

## 六、書

沿用 mini-english/book 的章節骨架，每語言一本（繁體中文讀者版 ＋ 英文版）：

1. 這是什麼／為什麼 n 個單位就夠／怎麼用
2. 詞表總覽與分類
3. 形態與單位（英法：屈折＋派生；日韓：活用簡化）
4. 語法規則（編號句型表）
5. 日常場景（見面、買東西、問路、看醫生、說感受）＋學習計畫
6. 三層表達法與改寫流程
7. 範例改寫 ＋ 最常犯的錯
8. 工具與網頁
9. 與既有方案對照
   附錄 A 完整字表／B 禁用詞／C 練習答案／D 來源與版本

每本約 40–50 篇 md，含練習題（由 `core/book.py` 產生答案）。

---

## 七、執行階段（每階段停下來給結果再繼續）

- **階段 0**：統一 spec 格式 ＋ core 引擎骨架 ＋ 移植 Mini-Chinese／Mini-English（先證明抽象真的共用得起來）
- **階段 1**：Mini-French 完整（spec、grammar、check、lexicon、examples、prompt、report）
- **階段 2**：Mini-Japanese 完整
- **階段 3**：Mini-Korean 完整
- **階段 4**：LLM 生成管線 ＋ 覆蓋率／改寫／自然度驗證 ＋ 回饋修訂
- **階段 5**：五本書 ＋ 網頁

---

## 八、待決事項

1. **書的讀者**：以繁體中文讀者（像 mini-english/book/tw）為主，還是每語言都出英文版（工作量 ×2）？
2. **是否直接把 `mini-lang` 的 mini-chinese／mini-english 搬進 learn-talk**？
   傾向：搬，改成新 spec 格式，保留 git 歷史引用；不重做。
3. **Mini-French 規模**：~1,000 詞（與英文對稱）還是更激進的 ~600 詞？
4. **是否也要做「小語言模型」部分**（mini-lm 重訓五種語言），還是本專案只到「語言 ＋ 轉換器 ＋ 生成器 ＋ 書」為止？
