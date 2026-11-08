# A 完整詞表

The user wants me to write a chapter called "A 完整詞表" (Complete Word List) for a Mini-Japanese textbook. This chapter's focus is "所有單位一覽" (overview of all units).

Requirements:
- Opening paragraph explaining what this chapter teaches
- 2-4 sections with ## headings, each with explanations, tables, or example sentences
- At least 5 complete example sentences in Mini-Japanese
- Use tables for comparison where needed
- 3-5 practice questions with answers at the end
- All in markdown
- Traditional Chinese explanations
- All Mini-Japanese sentences must pass checking: only use words from the word list
- Don't write "here omitted" type phrases - every sentence complete
- Don't output other explanations or say "以下是第 X 章"

Let me plan this chapter:

The chapter is about the complete word list. Since the full list has 985 words (425 core + 560 extended), I can't list all of them in the chapter (that would be excessive, but actually the appendix already has the full list). This chapter should be an overview/guide to the word list - explaining its structure, categories, how to use it, core vs extended layers.

Wait, but the requirement says "所有單位一覽" - overview of all units. Hmm. The appendix has the complete list. This chapter A should probably introduce the structure of the word list: the 11 categories, core layer (C) vs extended layer (E), word types (pron, gram, num, n, v, adj, adv), and how to use the list.

Let me structure:

## A 完整詞表

Opening paragraph: This chapter introduces the complete word list of Mini-Japanese - 985 units total, 425 core + 560 extended, organized into 11 categories. Learn how the list is organized, the difference between core and extended, and how to look up words.

Sections:
1. ## 詞表的結構：11 個類別 - table of categories with counts and examples
2. ## 核心層與擴充層 - explain C vs E, with examples
3. ## 詞的種類與用法 - pron, gram, num, n, v, adj, adv with example sentences
4. ## 怎麼用詞表說話 - the three-tier expression method (本詞、描述、外來語) with examples

Example sentences (must only use words from the list):

Let me carefully check each example sentence against the word list.

Checkable words in the list:
- 私 (C pron) - I
- は (C gram) - topic marker
- 学生 (E n) - student
- です (E gram) - is
- これ (C gram) - this
- 何 (E pron) - what
- か (E gram) - question marker
- 猫 (C n) - cat
- が (C gram)
- います (C v) - exists (animate)
- 机 (C n) - desk
- あります (C v) - exists (inanimate)
- 水と牛乳 (水 C n, 牛乳 C n)
- 食べます (C v)
- 昨日 (C n) - yesterday
- 学校 (C n) - school
- 日本語 (E n) - Japanese
- 勉強しました (勉強します C v → 勉強しました)
- 行きます (C v)
- 明日 (C n) - tomorrow
- 大きい (C adj) - big
- 犬 (C n) - dog
- 花がきれいです (花 C n, きれい C adj, です E gram)
- あそこ (C pron) - there
- 公園 (C n) - park
- あります
- 3人 (rule 19 says numbers use Arabic numerals with counters)
- いくらですか (E pron いくら + ですか)
- これは (これ C gram + は)
- コーヒー (E n, first occurrence needs parenthetical explanation: コーヒー（飲みもの）) - wait, 飲みもの... is that in the list? Let me check. 飲みます is a verb. 飲みもの is not in the list. Hmm.

The rule 23 says: 外來語用片假名，第一次出現時用括號說明；之後直接用。例：コーヒー（飲みもの）を飲みます。

But the requirement says the explanation itself must use words from the list. 飲みもの is not in the list... The example in the spec itself uses 飲みもの. Hmm, tricky. Let me use explanations that only use list words.

For コーヒー, I could say コーヒー（のみます もの）... that's awkward. Or use a different loanword. Let me think about which loanwords can be explained with list words:

- カメラ（写真をとる道具）- 写真 C n, 道具 E n... "写真をとる" - とる is not in list. Hmm. 写真の道具? That works: カメラ（写真の道具）
- テレビ（映画を見るもの）- 映画 C n, 見ます C v... 見る is the dictionary form; the list has 見ます. Rule 10 says only ます form. Hmm, but the description templates use …をする人 etc. The templates in section 3 use dictionary forms: …をする人、…の場所. So descriptions can use する forms? The templates are given as …をする人 etc. I think for descriptions, it's acceptable to use the する form as per templates. But to be safe, maybe use noun-based descriptions.

Actually, let me look at the description templates again:
- …をする人
- …の場所
- …のもの
- …ということ
- …という種類
- …の仕事
- …の道具

These use する. So in descriptions, using dictionary form verbs is allowed by the template. But rule 10 says only ます形 for verbs in sentences. The templates are part of the spec, so I'll follow them for descriptions.

For loanword explanations, I'll use noun phrases like:
- コーヒー（茶の飲みもの）? 飲みもの not in list. Hmm.
- コーヒー（茶の一種）? 種類 E n is in the list. 一種... 一 C num, 種 C n (seed). Hmm, 一種 could be read as "one kind". That's a bit of a stretch but uses list words.

Alternatively:
- カメラ（写真の道具）- all list words: 写真 (C n), の (C gram), 道具 (E n). 
- デパート（大きい店）- 大きい (C adj), 店 (C n). 
- コンビニ（小さい店）- 小さい (C adj), 店 (C n). 
- バス（大きい車）- 大きい, 車 (C n). 
- タクシー（小さい車）- hmm, taxis aren't small... but for simplicity. Actually maybe skip.
- プール（水の場所）- 水 (C n), 場所 (E n). "水の場所" = water place. OK-ish.
- ケーキ（甘い食べもの）- 食べもの not in list. 甘い (E adj) is in list. Hmm.
- ケーキ（甘いもの）- 甘い (E adj), もの (E pron). That works! ケーキ（甘いもの）
- ラーメン（麺の料理）- 麺 (C n), 料理 (E n). 
- チーズ（白い食べもの）... again 食べもの issue. チーズ（白いもの）? Weak but works.
- パソコン（仕事の機械）- 仕事 (C n), 機械 (E n). 
- メール（電話の言葉）? Hmm. メール（手紙のようなもの）- 手紙 not in list. Skip メール.

OK so I have good options. Let me now design the chapter.

Since this chapter is "A 完整詞表" - the overview of all units - I should present:
1. The structure: 985 units, 11 categories, core 425 + extended 560
2. Category table with examples
3. Core vs Extended explanation
4. Word classes (詞性): pron, gram, num, n, v, adj, adv
5. How to use the list (three-tier expression)

Wait, actually, should I reproduce the entire word list in this chapter? That would be 985 words - very long. The appendix already has it. The chapter title says "完整詞表" and the focus is "所有單位一覽". Hmm. The instruction says "中間分成 2–4 個小節（用 ## 標題），每節有說明、表格或例句". 

I think the intent is a guided tour of the word list, not a full reproduction (which is in the appendix). But "所有單位一覽" suggests showing all units... Reproducing all 985 words would be extremely long. But maybe that's what's wanted? The appendix is described as "完整詞表" too ("附錄：完整詞表　這是唯一的權威詞表").

Given chapter A is titled "A 完整詞表" and the appendix is "附錄：完整詞表", the chapter A is probably the pedagogical introduction to the word list, teaching how to read/use it, while the appendix holds the raw list. I'll write chapter A as the guide: structure, categories with counts, core/extended distinction, word classes, and how to find/use words, with examples. I'll reference the appendix for the full list.

Actually, let me reconsider. The user says "這一章的重點：所有單位一覽" - the chapter's focus: overview of all units. A "一覽" (overview/at-a-glance) could be satisfied by the category statistics table plus representative examples from each category. I'll include a comprehensive category table (all 11 categories with counts, core counts, and sample words), plus maybe a fuller listing of the core layer's most important words per category? The core layer is 425 words - still too many to list all.

Hmm, but maybe I should list ALL core words? 425 words in a compact multi-column format... That's a lot but doable? Actually no - it would make the chapter enormous and it duplicates the appendix. The textbook design has the appendix as the authoritative full list. Chapter A should teach the map of the territory.

Let me go with: guided overview with complete category table (all 11 categories, counts, examples), core/extended system, word classes, usage guide. I'll make the category table show a good sample of words from each category so readers get a feel for "所有單位" at a glance.

Actually, you know, let me include a fairly generous sampling in the category tables - maybe 8-12 words per category showing both C and E layers. That gives a real "一覽" feel without duplicating 985 words.

Let me now carefully draft the sections.

# A 完整詞表

Opening paragraph:
這一章帶你認識 Mini-Japanese 的完整詞表。Mini-Japanese 的所有句子，只能由詞表內的單位組成——核心層 425 個，擴充層 560 個，一共 985 個單位。學會這一章，你就知道詞表怎麼分類、每個類別裡有什麼、遇到表外的東西要怎麼辦。之後查附錄的完整詞表時，你會知道自己在看什麼。

## 1. 詞表的骨架：11 個類別

Explain: every word belongs to one of 11 categories. Table with category, total count, core count, examples.

| 類別 | 總數 | 核心層 | 例詞 |
|---|---|---|---|
| 代詞・指示 | 82 | 13 | 私、これ、あそこ、何 |
| 語法（功能詞） | 99 | 15 | は、が、を、に、で、と、の、も |
| 數量・比例 | 76 | 17 | 一、十、百、倍、割 |
| 時間 | 71 | 44 | 今日、明日、朝、月曜日 |
| 方位・地點 | 83 | 34 | 学校、駅、家、上、下 |
| 自然・天氣 | 63 | 48 | 水、空、雨、犬、猫 |
| 動作 | 157 | 57 | 食べます、行きます、見ます |
| 性質 | 95 | 65 | 大きい、おいしい、新しい |
| 事物 | 135 | 62 | 本、車、ご飯、コーヒー |
| 社交・人 | 54 | 27 | 友達、先生、家族 |
| 抽象概念 | 70 | 43 | 気持ち、理由、方法 |

Note: 動作 is the biggest category (157), 社交・人 smallest (54). Natural/weather has the highest core ratio (48/63).

## 2. 核心層（C）與擴充層（E）

Explain: C = core, the first 425 words you must learn; E = extended, adds precision. Every entry marked C or E. Examples showing pairs:

- 私（C）→ 俺たち、僕たち（E）
- これ（C）→ これらの（E）
- どこ（C）→ どこか、どこか、どこで、どこへ（E）
- 食べます（C）→ たべます（E）hmm that's hiragana variant
- 大きい（C）→ 細かい、薄い（E）

Table: 概念 | 核心層 | 擴充層
| 我 | 私 | 俺たち／僕たち |
| 這個 | これ | これらの |
| 哪裡 | どこ | どこか／どこで／どこへ |
| 吃 | 食べます | たべます |
| 好的 | 良い | いい |

Hmm wait, 良い is C and いい is E. Interesting.

Also mention: 核心層 425 個單位就能說大部分的話；擴充層讓句子更精確、更自然。

## 3. 七種詞性：每個詞的角色

Explain the POS labels: pron 代詞、gram 功能詞、num 數詞、n 名詞、v 動詞、adj 形容詞、adv 副詞。

Table: 詞性 | 意思 | 例詞 | 在句中的工作
| pron | 代詞 | 私、これ、あそこ | 代替人或東西的名字 |
| gram | 功能詞 | は、が、を、に、で、と、の、も | 把詞連接起來 |
| num | 數詞 | 一、十、百、倍、割 | 說數量 |
| n | 名詞 | 本、学校、水 | 人、東西、地方、時間的名字 |
| v | 動詞 | 食べます、行きます | 動作 |
| adj | 形容詞 | 大きい、おいしい | 性質 |
| adv | 副詞 | 今、毎日、とても | 時間、程度 |

Wait - 毎日 is adv in the list (C adv). とても is E adv. 今 is C adv. OK.

Also note rule 21: 動詞與形容詞一律用平假名；名詞用漢字。Hmm, but the list has verbs in kanji like 食べます (kanji + hiragana). The rule says verbs and adjectives use hiragana... but examples show 食べます、大きい. OK the rule as written: "動詞與形容詞一律用平假名；名詞用漢字。例：食べます、大きい、山" - the examples contradict (食べます has kanji). I'll not dwell on this; I'll just use the words as they appear in the list.

## 4. 怎麼用詞表說話：三層表達法

Explain: 本詞 → 描述 → 外來語. With examples:

- 本詞：私 は 学生 です。
- 描述：表外概念用「描述＋類頭」。例：カメラ（写真の道具）
- 外來語：コーヒー（茶の飲みもの）... no, 飲みもの not in list.

Let me fix: コーヒー（のみもの）? Not in list. コーヒー（茶の一種）? Hmm. Actually the spec's own example is コーヒー（飲みもの）を飲みます。The spec itself uses 飲みもの in the explanation. But my instruction says the explanation must also use list words. Conflict. I'll choose explanations that are fully in-list:

- カメラ（写真の道具）✓ (写真 C n, 道具 E n)
- デパート（大きい店）✓ (大きい C adj, 店 C n)
- コンビニ（小さい店）✓
- ケーキ（甘いもの）✓ (甘い E adj, もの E pron)
- ラーメン（麺の料理）✓ (麺 C n, 料理 E n)
- バス（大きい車）✓
- プール（水の場所）✓ (水 C n, 場所 E n)
- パソコン（仕事の機械）✓ (仕事 C n, 機械 E n)

Good, these all work.

Class heads (類頭): 人、もの、ところ、とき、こと、言葉、気持ち、考え、種類、問題、仕事、学校、物語、道、道具、材料、自然

Wait - 問題 and 物語 are listed as 類頭 but are they in the word list? Let me check... 問題 - searching... not in the word list! 物語 - not in the list either! Hmm. The spec section 3 lists them as 類頭 anyway. I'll present the 類頭 as given in the spec. Actually wait, let me double check the word list for 問題... In 抽象概念: 不安、世界、価値、効果、勇気、原因、喜び、地域、場合、変化、好み、希望、平和、平等、影響、役、怒り、性格、悲しみ、意味、感情、方法、期待、条件、権利、比較、気持ち、状態、理由、環境、目的、社会、立場、組織、経済、結果、考え、自信、自由、規則、責任、身分、関係、交流、人間、内容、制度、協力、反対、地位、基準、嬉しさ、寂しさ、形式、役割、思い、思い出、恐怖、想像、意見、態度、政治、敬意、正義、法律、満足、現実、義務、記憶、集団. No 問題. And 物語 not in 事物. So the spec's 類頭 list includes two words not in the vocab list. That's the spec's own inconsistency. I'll just present the 類頭 as the spec defines them (they're special "class head" words). Or to be safe, I could list only the ones that are in the word list... but the spec explicitly defines the 類頭 set. I'll present the spec's list as-is since it's the authoritative design. Hmm, but my checking rule says example sentences must only use list words. The 類頭 list isn't an example sentence, it's a reference list. I'll keep the spec's 類頭 list.

Actually, to be careful, maybe I present 類頭 as in spec. Fine.

Example sentences for section 4:

1. 私は日本語を勉強します。(私 C, は C, 日本語 E, を C, 勉強します C)
2. これは何ですか。(これ C, は C, 何 E, ですか E)
3. 猫がいます。(猫 C, が C, います C)
4. 机の上に本があります。(机 C, の C, 上 E n, に C, 本 C, あります C)
5. 明日学校に行きます。(明日 C, 学校 C, に C, 行きます C)
6. この花はきれいです。(この C, 花 C, は C, きれい C, です E)
7. コーヒー（茶の飲みもの）… no. Let me do: コーヒー（甘くないのみもの）… no. 

For coffee: コーヒー（黒いのみもの）? のみもの not in list. Ugh. OK coffee explanation alternatives: コーヒー（茶の一種）- uses 茶 C n, 一 C num, 種 C n. "茶の一種" = a kind of tea. Coffee isn't tea... but in Japanese, コーヒー is sometimes considered 珈琲... it's a stretch. Better: skip coffee, use other loanwords with clean explanations.

Loanword examples:
- カメラ（写真の道具）を買います。(買います E v) ✓
- デパート（大きい店）で服を買いました。✓ (デパート E n, 大きい C, 店 C, で C, 服 C n, 買いました from 買います E)
- ケーキ（甘いもの）を食べます。✓

Description examples (描述＋類頭):
- Something not in the list... e.g., "醫院裡幫醫生的人" → 看護師: 病院で医者を助ける人. Check: 病院 C, で C, 医者 E n, 助ける... 助けます C v / 助 E v. Dictionary form 助ける - the templates use する form (…をする人), so 助ける人 follows the same pattern. 人 C n. So: 看護師 → 病院で医者を助ける人. That's a nice example.
- Or simpler: パン屋 → パンを作る店? Hmm, パン C n, 作る from 作ります C v, 店 C n. パンを作る店（パン屋）... but 屋 isn't needed. Actually for descriptions we don't need to name the outside word; we just describe. E.g., "我想說『圖書管理員』：図書館で本を管理する人" - 管理 not in list. Use: 図書館で本を貸す人 (貸します E v → 貸す). Hmm.

Let me use the spec's own template style: …をする人. E.g.:
- 「司機」→ 車を運転する人 - 運転 not in list. 
- 「司機」→ 車を走らせる人 - no.
- Hmm. 車の仕事をする人? Weird.

Better description examples:
- 「廚師」→ 料理を作る人 (料理 E n, 作る from 作ります C v, 人 C n) ✓ 
- 「麵包店」→ パンを売る店 (パン C n, 売る from 売ります E v, 店 C n) ✓
- 「游泳池」→ 泳ぐ場所 - 泳ぎます E v → 泳ぐ, 場所 E n. 泳ぐ場所 ✓. Actually プール is in the list (E n), so no need to describe. Use something else: 「海邊」→... 海 C n, 岸 C n is in the list (岸 = 海岸). Hmm.
- 「動物園」is in list. 
- 「醫生」is in list (医者 E).
- 「護士」→ 病院で医者を助ける人 ✓ good.
- 「老師的房間」... 
- 「火車」→ 電車... describe: 駅を走る長い車? 長い C adj, 走ります C v → 走る. 駅を走る長い車 ✓. Hmm, "在車站跑的長的車" - that's a train! Nice example.

OK. Now let me also include a dialogue block? The rules say "對話用這個格式" - it's a formatting rule for when I use dialogues. The chapter requirements say each section has 說明、表格或例句. Dialogues optional but nice. Requirement says "至少 5 個完整例句". I can include a small dialogue in one section to demonstrate using the word list. Let me add one dialogue in section 4 showing how to look up words / ask about words.

Dialogue example:
甲：これは何ですか。
乙：カメラ（写真の道具）です。
甲：カメラは高いですか。
乙：いいえ、安いです。

Check: これ C, は C, 何 E, ですか E, カメラ C n (first occurrence - add explanation カメラ（写真の道具）), です E, 高い C, いいえ E adv, 安い C. All good. But wait - カメラ appears first in 甲's... no, 乙 says カメラ（写真の道具）です first, so the explanation is there. Then 甲 uses カメラ again without explanation - correct per rule 23 (之後直接用).

Hmm, but in my section 4 I might already use カメラ in an example sentence earlier. Then in the dialogue I shouldn't re-explain. Let me manage first-occurrence carefully across the whole chapter. Let me decide which loanwords appear and where:

Plan loanword first occurrences:
- Section 4 本詞/描述/外來語 examples: カメラ（写真の道具）、ケーキ（甘いもの）、デパート（大きい店）
- Dialogue: reuse カメラ (already explained), introduce コンビニ（小さい店）? 

Let me draft the dialogue:
甲：明日、どこへ行きますか。
乙：デパート（大きい店）へ行きます。
甲：何を買いますか。
乙：服を買います。そして、コンビニ（小さい店）でお茶を買います。

Check: 明日 C, どこへ E pron (どこへ is in list!), 行きますか (行きます C + か E), デパート E n first occurrence with explanation (大きい C, 店 C), へ C gram, 何 E, を C, 買います E, 服 C, そして E, コンビニ E n first occurrence (小さい C, 店 C), で C, お茶... hmm! お茶 - is it in the list? 茶 C n is in list, お酒 E n is in list, but お茶 is NOT. Use 茶: お茶を買います → 茶を買います. Hmm, "茶" alone is a bit odd in Japanese but it's the list word. OK: 茶を買います。

Wait, "どこへ行きますか" - どこへ is listed as E pron "去哪裡". Good, it's a single unit. 

Also 甲：何を買いますか。何 E pron ✓.

Now the "at least 5 complete example sentences" requirement. I'll have many more than 5. Let me collect and verify each:

Section 2 (core vs extended) examples:
- 私は学生です。(私 C, は C, 学生 E, です E) ✓
- 僕たちも学生です。(僕たち E, も C, 学生 E, です E) ✓

Section 3 (word classes) examples - maybe one sentence per POS or a mini table:
- 私は本を読みます。(私, は, 本, を, 読みます) ✓
- この犬は大きいです。(この C, 犬 C, は, 大きい C, です E) ✓
- 3人の子どもがいます。(3人 - rule 19 Arabic numerals with counter 人; 子ども C n, が, います C) ✓
- 明日、東京...no 東京 not in list. 明日、学校に行きます。✓
- 私は毎朝6時に起きます。(毎朝 E adv, 6時 - Arabic numeral + 時 C n, に C, 起きます C) ✓

Section 4 examples:
- 私は日本語を勉強します。✓
- これは何ですか。✓
- 猫がいます。✓
- 机の上に本があります。✓
- カメラ（写真の道具）を買います。✓
- ケーキ（甘いもの）を食べます。✓
- デパート（大きい店）で服を買いました。✓
- 護士 → 病院で医者を助ける人 ✓
- 火車 → 駅を走る長い車 ✓

Dialogue sentences all check out.

Now let me also double-check some specific words I plan to use:

- 学生: E n "學生" ✓ in list (事物 category)
- 机: C n "桌子" ✓
- 上: E n "上面" ✓ (方位・地點)
- 毎朝: E adv "每天早上" ✓
- 起きます: C v ✓
- 6時: 時 C n "点钟" ✓, Arabic numeral per rule 19
- 買います: E v ✓
- 買いました: past of 買います, per rule 28 ます→ました ✓
- 服: C n ✓
- そして: E gram ✓
- どこへ: E pron ✓
- 行きます: C v ✓
- か: E gram ✓
- ですか: E gram ✓
- 何: E pron ✓
- これ: C gram ✓
- 猫: C n ✓
- います: C v ✓
- あります: C v ✓
- 本: C n ✓
- 読みます: C v ✓
- 犬: C n ✓
- 大きい: C adj ✓
- きれい: C adj ✓
- 花: C n ✓
- 甘い: E adj ✓
- もの: E pron ✓
- 麺: C n ✓
- 料理: E n ✓
- 写真: C n ✓
- 道具: E n ✓
- 店: C n ✓
- 小さい: C adj ✓
- デパート: E n ✓
- コンビニ: E n ✓
- 茶: C n ✓
- 病院: C n ✓
- 医者: E n ✓
- 助ける: from 助けます C v ✓ (dictionary form in description template)
- 駅: C n ✓
- 走る: from 走ります C v ✓
- 長い: C adj ✓
- 車: C n ✓
- 私たち: C pron ✓
- 僕たち: E pron ✓
- 俺たち: E pron ✓
- これらの: E pron ✓
- 良い: C adj ✓
- いい: E adj ✓
- 学生: E n ✓
- 日本語: E n ✓
- 勉強します: C v ✓
- 勉強しました: past ✓
- 昨日: C n ✓
- 学校: C n ✓
- 図書館: C n ✓ (if needed)
- 毎日: C adv ✓
- とても: E adv ✓
- 今: C adv ✓

Numbers: 一 C, 十 C, 百 C, 千 C, 万 C, 倍 C, 割 C ✓

Time: 今日 C, 明日 C, 昨日 C, 朝 C, 夜 C, 月曜日 C ✓

Places: 学校 C, 駅 C, 家 C, 病院 C, 公園 C ✓

Nature: 水 C, 空 C, 雨 C, 雪 C, 犬 C, 猫 C, 花 C ✓

Things: 本 C, 車 C, ご飯 C, 電話 C, 眼鏡 C ✓

People: 友達 C, 先生 C, 家族 C, 母 C, 父 C ✓

Abstract: 気持ち C, 理由 C, 方法 C, 世界 C, 自由 C ✓

Grammar: は、が、を、に、で、と、の、も all C ✓

OK. Now, about the category table - I want to include all 11 categories with counts from the 分類統計 table:

| 類別 | 總數 | 核心層 |
|---|---|---|
| 代詞・指示 | 82 | 13 |
| 語法（功能詞） | 99 | 15 |
| 數量・比例 | 76 | 17 |
| 時間 | 71 | 44 |
| 方位・地點 | 83 | 34 |
| 自然・天氣 | 63 | 48 |
| 動作 | 157 | 57 |
| 性質 | 95 | 65 |
| 事物 | 135 | 62 |
| 社交・人 | 54 | 27 |
| 抽象概念 | 70 | 43 |

Total: 82+99+76+71+83+63+157+95+135+54+70 = let me add: 82+99=181; 181+76=257; 257+71=328; 328+83=411; 411+63=474; 474+157=631; 631+95=726; 726+135=861; 861+54=915; 915+70=985. ✓ 985 total.
Core: 13+15+17+44+34+48+57+65+62+27+43 = 13+15=28; +17=45; +44=89; +34=123; +48=171; +57=228; +65=293; +62=355; +27=382; +43=425. ✓ 425 core.
Extended: 985-425=560 ✓.

Great, the numbers check out.

Now for the "一覽" aspect - I'll add sample words per category in the table, maybe a third column with representative words (mixing C and E). Let me pick ~6-8 per category:

- 代詞・指示: 私、これ、あそこ、どこ（C）／いつ、どちら、誰か（E）
- 語法: は、が、を、に、で、と、の、も（C）／から、まで、だけ、ましょう...no ましょう not in list. から、でも、そして（E）
- 數量・比例: 一、十、百、万、倍、割（C）／二十、五十、三割（E）
- 時間: 今日、明日、朝、夜、月曜日（C）／去年、来年、すぐ、まだ、もう（E）
- 方位・地點: 学校、駅、家、店（C）／上、下、中、右、左、隣（E）
- 自然・天氣: 水、空、雨、雪、犬、猫、花（C）／晴れ、地震、滝（E）
- 動作: 食べます、飲みます、行きます、見ます、書きます（C）／買います、使います、忘れます（E）
- 性質: 大き
