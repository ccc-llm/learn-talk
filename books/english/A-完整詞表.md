# A 完整詞表

The user wants me to write a chapter "A 完整詞表" (Complete Word List) for a Mini-English textbook. This chapter should be an overview of all units (words) in the vocabulary.

Requirements:
- Opening paragraph explaining what this chapter teaches
- 2-4 sections with ## headings, each with explanations, tables, or example sentences
- At least 5 complete example sentences in Mini-English
- Tables for comparison where needed
- 3-5 exercises with answers at the end
- All in markdown
- Traditional Chinese explanations, Mini-English examples
- All example sentences must use only words from the word list
- Dialogue format available (甲：…… 乙：……)
- Exercises use `- [ ]` lists with answers in `> 答案：……` format

Let me plan the chapter structure:

## A 完整詞表

Opening paragraph: This chapter gives a complete overview of all units in Mini-English — the core layer (600) and extension layer (656), organized by 11 categories. Students learn how the word list is organized, what C/E means, and how to use the list.

### Sections (2-4):

1. ## 詞表的結構：核心層與擴充層
   - Explain C (core) vs E (extension)
   - Table of category statistics (from the spec)
   - Explain the 11 categories

2. ## 十一個類別總覽
   - Table listing each category with example words
   - Maybe examples of how words from different categories combine

3. ## 從詞表到句子：單位如何組合
   - Show how words from different categories combine into sentences
   - Example sentences with word-by-word breakdown
   - Maybe a dialogue

4. ## 怎麼查詞表
   - How to use the list when you can't find a word
   - Three-layer expression method reminder (本詞/描述/外來語)
   - Examples

Let me count example sentences — need at least 5 complete Mini-English sentences.

Let me verify words against the word list carefully:

- "I am a student." — I (C, pron), am (C), a (C), student (C). ✓
- "She is my sister." — she, is, my, sister — all C. ✓
- "The sun is hot today." — the, sun, is, hot, today — all C. ✓
- "My mother works in a shop." — my, mother, works (work + -s), in, a, shop — all C. ✓
- "We will go to the park tomorrow." — we, will, go, to, the, park, tomorrow — all C. ✓
- "There are many people in the city." — there, are, many, people, in, the, city — all C. ✓
- "He can swim very well." — he, can, swim, very, well — all C. ✓
- "I drink a cup of tea every morning." — I, drink, a, cup, of, tea, every, morning — all C. ✓
- "The dog is under the table." — the, dog, is, under, the, table — all C. ✓
- "They are my good friends." — they, are, my, good, friends — all C. ✓
- "I want to buy a new book." — I, want, to, buy, a, new, book — all C. ✓
- "It is going to rain." — it, is, going (go+ing), to, rain — all C. ✓
- "The train station is near my home." — the, train, station, is, near, my, home — all C. ✓
- "She has a small black cat." — she, has, a, small, black, cat — all C. ✓
- "I speak Chinese and English." — I, speak, Chinese, and, English — all C. ✓
- "The weather is very cold in winter." — winter is E layer. Hmm, winter is E (extension). That's fine — E words are still in the word list. But maybe for a basic chapter I should note which are core vs extension. Actually the chapter is about the complete word list, so using E words is fine, but I could mark them.

Actually, let me be careful: the chapter is "A 完整詞表" — complete word list overview. So I should present the structure: core 600 + extension 656 = 1256 units. Wait, the spec says "核心層 600 ＋ 擴充層 656". Let me check the statistics table:

| 類別 | 總數 | 核心層 |
|---|---|---|
| 代詞・指示 | 67 | 60 |
| 語法（功能詞） | 132 | 116 |
| 數量・比例 | 10 | 8 |
| 時間 | 52 | 30 |
| 方位・地點 | 123 | 44 |
| 自然・天氣 | 77 | 29 |
| 動作 | 231 | 128 |
| 性質 | 154 | 74 |
| 事物 | 181 | 48 |
| 社交・人 | 74 | 34 |
| 抽象概念 | 155 | 29 |

Total: 67+132+10+52+123+77+231+154+181+74+155 = let me add: 67+132=199; 199+10=209; 209+52=261; 261+123=384; 384+77=461; 461+231=692; 692+154=846; 846+181=1027; 1027+74=1101; 1101+155=1256. 

Core: 60+116+8+30+44+29+128+74+48+34+29 = 60+116=176; +8=184; +30=214; +44=258; +29=287; +128=415; +74=489; +48=537; +34=571; +29=600. ✓ 600 core.

So total 1256, core 600, extension 656. ✓ Matches the spec.

Now, structure of the chapter:

Opening paragraph: explain that this chapter is the map of all units — 1256 words in 11 categories, core 600 + extension 656, and how to read the list (C/E markers), and that with these units plus 20 grammar rules you can say anything.

### Section 1: ## 兩層詞表：核心層與擴充層
- Explain C = core (600), E = extension (656)
- Learning strategy: master core first, then extension
- Table with statistics

### Section 2: ## 十一個類別
- Table: category, what it contains, example words (with C/E marks)
- Maybe pick 3 categories to show sample words

### Section 3: ## 單位如何組成句子
- Show sentences built from different categories
- A breakdown table: sentence → words → categories
- At least 5 complete sentences here
- Maybe a dialogue

### Section 4: ## 查不到的詞怎麼辦
- Three-layer method: 本詞 / 描述＋類頭 / 外來語
- Examples: e.g., "piano" → a big thing for music, with black and white keys... wait "keys" is in list (key C). "black" and "white" are in list. So: "a big thing for music with black and white keys" — all words in list? a, big, thing, for, music, with, black, and, white, keys — yes all in list. 
- "kangaroo" → an animal from Australia with a bag on its body... "bag" C, "body" C, "animal" C, "Australia" E. ✓
- "chopsticks" → 2 small sticks for food... sticks (stick C), food C, small C. ✓ "You eat with 2 small sticks." 
- Foreign word example: "sushi（日本食物，用飯和魚做的）" — hmm, Japan is in list (japan E). The parenthetical explanation must use word-list words: "a food from japan with rice and fish" — rice C, fish C, food C, from C, japan E. ✓

Wait — the rule says 外來語第一次出現時加括號說明，說明本身也要用詞表內的字詞. So if I use a foreign word like "sushi", the explanation in parentheses must use only list words.

Let me now design example sentences. I want variety across categories. Let me draft 6-8 sentences and verify each word:

1. "I am a student." — I✓ am✓ a✓ student✓ (all core)
2. "She is my sister." — ✓ (all core)
3. "The sun is hot today." — the✓ sun✓ is✓ hot✓ today✓ (all core)
4. "My mother works in a shop." — my✓ mother✓ work+s✓ in✓ a✓ shop✓ (all core)
5. "We will go to the park tomorrow." — we✓ will✓ go✓ to✓ the✓ park✓ tomorrow✓ (all core)
6. "There are many people in the city." — there✓ are✓ many✓ people✓ in✓ the✓ city✓ (all core)
7. "He can swim very well." — he✓ can✓ swim✓ very✓ well✓ (all core)
8. "I drink a cup of tea every morning." — I✓ drink✓ a✓ cup✓ of✓ tea✓ every✓ morning✓ (all core)
9. "The dog is under the table." — ✓
10. "They are my good friends." — they✓ are✓ my✓ good✓ friend+s✓ ✓
11. "I want to buy a new book." — ✓
12. "The train station is near my home." — train✓ station✓ near✓ home✓ ✓
13. "She has a small black cat." — ✓
14. "It is very cold in winter." — winter is E. Fine, mark it.
15. "The movie was very interesting." — movie is E. ✓

For the combination table, I can show how one sentence draws words from multiple categories:

"I drink a cup of hot tea every morning."
- I → 代詞・指示
- drink → 動作
- a → 語法（功能詞）
- cup → 事物
- of → 語法（功能詞）
- hot → 性質
- tea → 事物
- every → 語法（功能詞）
- morning → 時間

That's 5 categories in one sentence. 

Another: "My friend will take the train to the big city tomorrow."
- my → 代詞
- friend → 社交・人
- will → 語法
- take → 動作
- the → 語法
- train → 方位・地點
- to → 語法
- big → 性質
- city → 方位・地點
- tomorrow → 時間

That's 6 categories! Nice.

Another with 數量・比例 and 自然・天氣:
"Half of the water is in the sea." — half✓ of✓ the✓ water✓ is✓ in✓ the✓ sea✓. Categories: 數量・比例, 語法, 自然・天氣, 語法.

Or "The wind is strong near the sea." — wind (自然), strong (性質), near (語法), sea (自然).

Let me include 抽象概念: "I have a question about the work." — question (抽象概念), about (語法), work (動作/事物... work is listed under 動作 category with v/n). Actually in the word list, "work" is in 動作 category. Hmm, interesting — work is listed under 動作. OK.

"Music is an important part of my life." — music (抽象概念), important (性質), part (抽象概念, E), life (抽象概念). All in list ✓.

Dialogue example:
甲：What is this?
乙：This is a map of my city.
甲：Where is the train station?
乙：It is near the park.

Check: what✓ is✓ this✓, map✓ city✓, where✓ train✓ station✓, near✓ park✓. All good.

Now for section 4 (查不到的詞), examples:

- 想說「鋼琴 piano」：表外 → 描述＋類頭："a big thing for music with black and white keys" — check: a✓ big✓ thing✓ for✓ music✓ with✓ black✓ and✓ white✓ key+s✓. All in list ✓.
- 想說「筷子 chopsticks」："2 small sticks for food" — 2 (number, arabic numerals allowed), small✓ stick+s✓ for✓ food✓ ✓.
- 說不出是哪一個 → 外來語："pizza（一種圓的義大利食物）" — hmm, "圓的" — round is E ✓, "義大利" italy E ✓, food ✓, "一種" a kind of — kind is C ✓ (kind adj/n 善良的；種類). So: "pizza（a round food from italy）" — round✓ food✓ from✓ italy✓ ✓. 
- Or "sushi（a food from japan with rice and fish）" — japan✓ rice✓ fish✓ ✓.

Also mention 類頭 list briefly: thing, person, place, kind, way... and 描述模板: a place where..., a person who..., a thing that..., a kind of..., a thing for...

Example with template:
- "library" is in the list, but if it weren't: "a place with many books" — place✓ with✓ many✓ book+s✓ ✓.

Now exercises (3-5):

1. 分類題：把這些詞放到正確的類別：sun, teacher, drink, blue, tomorrow
   - sun → 自然・天氣
   - teacher → 社交・人
   - drink → 動作
   - blue → 性質
   - tomorrow → 時間
   
2. 判斷 C/E：these words are core or extension? winter, mother, airport, big
   - winter → E（擴充層）
   - mother → C（核心層）
   - airport → E
   - big → C

3. 用詞表內的詞造句 or 完成句子：___ is my good friend. (答案示例: She / He / My teacher...)
   Actually maybe: "用括號裡的類別各寫一個詞，組成句子" — hmm, might be complex. Let me do fill-in-the-blank:
   "I drink a cup of ___ every morning."（答案：tea / coffee / milk — 都在詞表內）
   tea✓ coffee✓ milk✓ all C ✓.

4. 描述練習：用「描述＋類頭」說出「雨傘」以外的詞，例如「枕頭」— hmm, pillow is not in the list. "a thing for your head in bed" — thing✓ for✓ your✓ head✓ in✓ bed✓ ✓. Good exercise: 用詞表內的詞描述「枕頭」。
   答案示例：a thing for your head on the bed / a soft thing for your head in bed — soft✓ ✓.

5. 找錯誤題：下面哪一句用了詞表外的詞？改成詞表內的說法。
   - "I am very tired." ✓ all in list
   - "This movie is awesome." — awesome is banned (改 very good). movie is E (in list, OK). So the error is "awesome" → "very good".
   - "She has a huge dog." — huge is banned → "very big". 
   
   Let me make one sentence with an error: "The movie is awesome." → "The movie is very good." Check: movie (E, in list ✓), very✓ good✓.
   
   Or: "He bought a huge house." → bought is past of buy (bought is in irregular list ✓), huge banned → very big. "He bought a very big house." ✓

Let me design 4 exercises:

- [ ] 練習 1（分類）：把這 5 個詞寫進正確的類別：sun、teacher、drink、blue、tomorrow
  > 答案：sun → 自然・天氣；teacher → 社交・人；drink → 動作；blue → 性質；tomorrow → 時間

- [ ] 練習 2（核心層與擴充層）：下面哪些是核心層（C）、哪些是擴充層（E）？mother、winter、big、airport
  > 答案：mother（C）、big（C）、winter（E）、airport（E）

- [ ] 練習 3（完成句子）：在空格裡填一個詞表內的詞：I drink a cup of ___ every morning.
  > 答案：tea / coffee / milk（都可以，都在詞表內）

- [ ] 練習 4（描述＋類頭）：「枕頭」不在詞表裡。用詞表內的詞描述它。
  > 答案示例：a soft thing for your head on the bed（每個詞都在詞表內）

- [ ] 練習 5（找出禁用詞）：這一句有一個詞表外的詞，請改正：The movie is awesome.
  > 答案：awesome 是禁用詞，改用 very good → The movie is very good.

That's 5 exercises, good.

Now let me also think about whether to include a dialogue. The rules say "對話用這個格式" — dialogues should use that format if included. Not mandatory, but nice. I'll include one in section 3.

Let me now think about the category overview table. 11 categories with example words. For each category, give 3-4 example words with C/E marks:

| 類別 | 內容 | 例子 |
|---|---|---|
| 代詞・指示 | 我、你、他、這、那… | I（C）、she（C）、this（C）、something（C） |
| 語法（功能詞） | the、a、in、and、very… | the（C）、and（C）、very（C）、through（E） |
| 數量・比例 | 一半、兩倍、百分比… | half（C）、double（C）、percent（C）、hundred（E） |
| 時間 | 天、月、早上… | day（C）、morning（C）、today（C）、winter（E） |
| 方位・地點 | 家、學校、左右… | home（C）、school（C）、left（C）、airport（E） |
| 自然・天氣 | 水、太陽、動物… | water（C）、sun（C）、dog（C）、mountain（E） |
| 動作 | 吃、去、說… | eat（C）、go（C）、say（C）、borrow（E） |
| 性質 | 大、好、紅… | big（C）、good（C）、red（C）、cheap（E） |
| 事物 | 書、桌子、錢… | book（C）、table（C）、money（C）、bowl（E） |
| 社交・人 | 朋友、家人、老師… | friend（C）、family（C）、teacher（C）、boss（E） |
| 抽象概念 | 工作、問題、故事… | job（C）、question（C）、story（C）、idea（E） |

Verify each: I✓ she✓ this✓ something✓; the✓ and✓ very✓ through✓ (E); half✓ double✓ percent✓ hundred✓ (E); day✓ morning✓ today✓ winter✓ (E); home✓ school✓ left✓ airport✓ (E); water✓ sun✓ dog✓ mountain✓ (E); eat✓ go✓ say✓ borrow✓ (E); big✓ good✓ red✓ cheap✓ (E); book✓ table✓ money✓ bowl✓ (E); friend✓ family✓ teacher✓ boss✓ (E); job✓ question✓ story✓ idea✓ (E). All correct.

Now the sentence breakdown table for section 3:

句子 1：I drink a cup of hot tea every morning.
| 詞 | 類別 |
|---|---|
| I | 代詞・指示 |
| drink | 動作 |
| a | 語法（功能詞） |
| cup | 事物 |
| of | 語法（功能詞） |
| hot | 性質 |
| tea | 事物 |
| every | 語法（功能詞） |
| morning | 時間 |

5 categories in one sentence.

句子 2：My friend will take the train to the big city tomorrow.
| my | 代詞・指示 |
| friend | 社交・人 |
| will | 語法（功能詞） |
| take | 動作 |
| the | 語法（功能詞） |
| train | 方位・地點 |
| to | 語法（功能詞） |
| big | 性質 |
| city | 方位・地點 |
| tomorrow | 時間 |

6 categories!

Then a list of complete sentences (at least 5 total across the chapter — I'll have plenty):

1. I am a student.
2. She has a small black cat.
3. We will go to the park tomorrow.
4. There are many people in the city.
5. He can swim very well.
6. The train station is near my home.
7. I drink a cup of hot tea every morning.
8. My friend will take the train to the big city tomorrow.

Maybe mark which are core-only. Sentences 1-6 all core. 7-8 all core too. Let me add one with E words to show extension:
9. It is very cold in winter.（winter 是擴充層）
10. The movie was very interesting.（movie 是擴充層）

Check 10: the✓ movie✓(E) was✓ very✓ interesting✓. ✓

Dialogue:
甲：What is this?
乙：This is a map of my city.
甲：Where is the train station?
乙：It is near the park. You can walk there in 10 minutes.

Check: what✓ is✓ this✓ map✓ of✓ my✓ city✓ where✓ the✓ train✓ station✓ near✓ park✓ it✓ you✓ can✓ walk✓ there✓ in✓ 10✓ minute+s✓. All ✓. "walk there in 10 minutes" — fine.

Section 4 examples:

表外概念 → 描述＋類頭：
- 鋼琴（piano）→ a big thing for music with black and white keys
  Check: a✓ big✓ thing✓ for✓ music✓ with✓ black✓ and✓ white✓ keys✓ ✓
- 筷子（chopsticks）→ 2 small sticks for food
  Check: 2✓ small✓ sticks✓ for✓ food✓ ✓
- 枕頭（pillow）→ a soft thing for your head on the bed
  Check: soft✓ thing✓ your✓ head✓ bed✓ ✓

描述模板：
- a place where ... → a place where people read books（圖書館的概念；不過 library 本身在擴充層）
  Hmm, maybe use a non-list word: 幼兒園 → "a place where small children play and learn" — place✓ where✓ small✓ child+ren✓ play✓ and✓ learn✓ ✓. Nice.
- a person who ... → 牙醫 → "a person who helps with your teeth" — person✓ who✓ help+s✓ with✓ your✓ teeth✓ ✓ (teeth is irregular plural of tooth, in the appendix ✓).
- a thing for ... → 剪刀 → "a tool for cutting" — tool✓ cutting (cut+ing)✓ ✓. Actually scissors → "a tool for cutting with 2 sharp parts"... keep simple: "a tool for cutting".

外來語：
- 說不出是哪一個 → 用原文＋括號說明：
  - sushi（a food from japan with rice and fish）
  - kimchi（a hot food from korea）— korea✓ hot✓ food✓ from✓ ✓
  
Check sushi explanation: a✓ food✓ from✓ japan✓ with✓ rice✓ and✓ fish✓ ✓.
kimchi: a✓ hot✓ food✓ from✓ korea✓ ✓.

Good.

Also should mention: 數字用阿拉伯數字 (numbers written as digits) — e.g., "I have 3 books." — have✓ 3✓ book+s✓ ✓. And 字首字尾 allowed: un-, re-, -er, -est, -ly, -ness — e.g., teacher = teach + er, quickly = quick + ly. Maybe mention briefly in section 1 or 3. Actually that could be a small note: 詞表裡的單位還可以加字首字尾：teach → teacher, quick → quickly, happy → happiness (happiness = happy + ness ✓).

Hmm, where to put this? Maybe in section 3 as "單位還會變形" — plural -s, past tense, prefixes/suffixes. Keep it brief since this chapter is about the word list overview.

Let me also think: the opening paragraph. Something like:

這一章是整本課本的地圖。Mini-English 一共有 1256 個單位，分成核心層（600）與擴充層（656），再分成 11 個類別。學會這一章，你就知道詞表長什麼樣、每個類別放什麼詞、以及查不到某個詞的時候該怎麼辦。之後每一章的新詞，都是從這張地圖裡拿出來的。

Good.

Section 1: ## 先看懂兩層：核心層與擴充層

Explain:
- C = core 核心層，600 個。最常用，先學。
- E = extension 擴充層，656 個。核心學完再加。
- 詞表是唯一的權威：句子裡只能用詞表內的單位。
- 統計表。

Also mention: 每個單位有詞性（n / v / adj / adv / prep / det / pron / conj / num / interj）— maybe briefly explain abbreviations. That's useful for reading the word list. Add a small table:

| 縮寫 | 意思 | 例子 |
|---|---|---|
| n | 名詞 | book |
| v | 動詞 | eat |
| adj | 形容詞 | big |
| adv | 副詞 | very |
| prep | 介系詞 | in |
| det | 限定詞 | the |
| pron | 代詞 | I |
| conj | 連接詞 | and |
| num | 數詞 | half |
| interj | 感嘆詞 | hello |

All examples in list ✓.

Section 2: ## 11 個類別：詞表的地圖

The big table + maybe a note that the categories help you find words and understand how they combine.

Section 3: ## 從單位到句子

- Show that a sentence mixes categories
- The two breakdown tables
- List of complete sentences
- Dialogue

Section 4: ## 查不到的詞：三層表達法

- 本詞 / 描述＋類頭 / 外來語
- 類頭 examples
- 描述模板
- Examples

Then exercises.

Length: should be reasonable, comprehensive but not bloated. Use markdown with ## headings. The chapter title itself — should I use # for chapter title? The instruction says "每一章用 markdown，有小標題（##）". So chapter title could be # or ##. I'll use # for the chapter title "A 完整詞表" and ## for sections. Actually the instruction says "中間分成 2–4 個小節（用 ## 標題）" — so sections use ##. Chapter title can be #.

Let me double check a few more sentences I plan to use:

- "I have 3 books." — have✓ 3✓ books✓ ✓
- "She has a small black cat." ✓
- "The train station is near my home." ✓
- "He can swim very well." ✓
- "There are many people in the city." ✓
- "We will go to the park tomorrow." ✓
- "It is very cold in winter." — winter E ✓
- "The movie was very interesting." — movie E ✓
- "Music is an important part of my life." — music✓ an✓ important✓ part✓(E) of✓ my✓ life✓ ✓

For the "quickly" example: quick is E... "quick → quickly" — quick (E) + -ly. Maybe use "slow → slowly" (slow C ✓) or "happy → happiness" (happy C ✓). Use slow→slowly and happy→happiness, teach→teacher (all core). ✓

Wait, "happiness" — happy + ness, y→i? The appendix allows -ness suffix. happiness is standard. Fine.

Also plural/past: book → books, walk → walked. Fine.

One more check on the dialogue: "You can walk there in 10 minutes." — minutes plural of minute ✓ (regular plural). ✓

Exercise 4 answer: "a soft thing for your head on the bed" — all ✓.

Now, about the 統計表 — I'll reproduce it in section 1. The totals: 1256 total, 600 core. Let me present:

| 類別 | 總數 | 核心層（C） | 擴充層（E） |
|---|---|---|---|
| 代詞・指示 | 67 | 60 | 7 |
| 語法（功能詞） | 132 | 116 | 16 |
| 數量・比例 | 10 | 8 | 2 |
| 時間 | 52 | 30 | 22 |
| 方位・地點 | 123 | 44 | 79 |
| 自然・天氣 | 77 | 29 | 48 |
| 動作 | 231 | 128 | 103 |
| 性質 | 154 | 74 | 80 |
| 事物 | 181 | 48 | 133 |
| 社交・人 | 74 | 34 | 40 |
| 抽象概念 | 155 | 29 | 126 |
| 合計 | 1256 | 600 | 656 |

Let me verify the E column: 67-60=7 ✓; 132-116=16 ✓; 10-8=2 ✓; 52-30=22 ✓; 123-44=79 ✓; 77-29=48 ✓; 231-128=103 ✓; 154-74=80 ✓; 181-48=133 ✓; 74-34=40 ✓; 155-29=126 ✓. Sum of E: 7+16+2+22+79+48+103+80+133+40+126 = 7+16=23; +2=25; +22=47; +79=126; +48=174; +103=277; +80=357; +133=490; +40=530; +126=656 ✓. 

Total row: 1256 = 600 + 656 ✓.

Good, adding the E column makes the table more informative.

Now write the chapter. Keep explanations in Traditional Chinese. Make sure no meta-commentary like "以下是第 X 章". Start directly with # A 完整詞表.

Also rule 3: 不要寫「這裡省略了」之類的說法 — every sentence complete.

Let me also make sure example sentences in tables (word examples) are fine — those are single words, fine.

One consideration: In section 2's table I list example words. I'll mark C/E in parentheses.

Also I should explain what "單位" means — the word list units include multi-word entries like "bus stop". Note: "bus stop" is one unit (兩個字算一個單位). Also "o'clock". Good detail to mention: 詞表裡的單位大多是 1 個字，也有少數是固定組合，像 bus stop。

Let me draft the full chapter now.

---

# A 完整詞表

開頭段：
這一章是整本課本的地圖。Mini-English 的所有句子，都由詞表裡的「單位」組成：核心層 600 個，加上擴充層 656 個，一共 1256 個單位，分成 11 個類別。學完這一章，你會知道詞表怎麼分層、每個類別放什麼詞、單位怎麼組成句子，以及遇到詞表外的概念時，怎麼用「描述＋類頭」或外來語把話說完整。

## 單位與兩層詞表

先說明「單位」：
- 一個單位通常是一個字：book、eat、big。
- 少數單位是固定組合，算一個單位：bus stop。
- 數字不用字，直接寫阿拉伯數字：3、10、2024。

兩層：
- C（core，核心層）：600 個。日常生活最需要的詞，先學這一層。
- E（extension，擴充層）：656 個。核心層學熟之後再加。
- 規則只有一條：句子裡的每一個單位，都要在詞表內。

詞性縮寫表。

統計表。

## 11 個類別：詞表的地圖

大表格。

說明：類別不是文法，是「找詞的地圖」。想說時間，去「時間」類找；想說動作，去「動作」類找。

## 從單位到句子

說明：一句話常常同時用到好幾個類別。看下面兩句的拆解。

Table 1: I drink a cup of hot tea every morning.
Table 2: My friend will take the train to the big city tomorrow.

完整例句清單（標注 E 詞）：
1. I am a student.
2. She has a small black cat.
3. We will go to the park tomorrow.
4. There are many people in the city.
5. He can swim very well.
6. The train station is near my home.
7. It is very cold in winter.（winter 是擴充層）
8. The movie was very interesting.（movie 是擴充層）

單位會變形：詞表給的是原形，句子裡照文法規則變化：
- 複數：book → books
- 過去式：walk → walked
