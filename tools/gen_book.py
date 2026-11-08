#!/usr/bin/env python3
"""用 LLM 寫課本：根據每個語言的規格生成章節。

用法：
    python tools/gen_book.py --lang fr --chapters 40
"""
from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.llm import LLM  # noqa: E402

BOOK_NAME = {
    'chinese': 'Mini-Chinese 簡易中文',
    'english': 'Mini-English 簡易英文',
    'french': 'Mini-French 簡易法文',
    'japanese': 'Mini-Japanese 簡易日文',
    'korean': 'Mini-Korean 簡易韓文',
}

# 章節大綱（跟 mini-lang 的課本結構一致）
CHAPTERS = [
    ('01.1', '什麼是 {name}', '介紹這個受限語言：它有幾個單位、能做什麼、不能做什麼。'),
    ('01.2', '為什麼 {n} 個單位就夠了', '用「表達力」而不是「詞頻」選詞的原理。'),
    ('01.3', '怎麼用這本書', '學習方法：每天的進度、練習怎麼做、怎麼用檢查工具。'),
    ('02.1', '詞表總覽', '十一大類（或該語言的類別）的總覽與學習順序。'),
    ('02.2', '代詞・指示與語法（功能詞）', '最核心的一類，先學會才能造句。'),
    ('02.3', '數量、時間、方位・地點', '描述「多少、什麼時候、在哪裡」。'),
    ('02.4', '自然・天氣與動作', '最常用的動詞與自然界的東西。'),
    ('02.5', '性質、事物、社交・人', '形容詞、具體的東西、以及和人打交道的話。'),
    ('02.6', '抽象概念', '想法、關係、時間、社會這一類比較難的詞。'),
    ('03.1', '形態：免費的變化', '屈折、派生、活用：哪些變化是免費的、哪些要另外學。'),
    ('03.2', '不規則形式', '這個語言裡少數要特別記的形式。'),
    ('03.3', '複合詞與量詞', '怎麼把兩個單位組成一個詞。'),
    ('03.4', '數字、單位與專有名詞', '數字怎麼寫、外來語怎麼處理。'),
    ('04.1', '句子的骨架', '這個語言的基本語序。'),
    ('04.2', '語法規則（上）', '編號的語法規則，前一半。'),
    ('04.3', '語法規則（下）', '編號的語法規則，後一半。'),
    ('04.4', '困難結構的固定替代', '這個語言不用的結構，以及要怎麼改說。'),
    ('04.5', '自然度：讀起來會不會怪', '怎麼寫出「母語者讀起來自然」的句子。'),
    ('05.1', '見面與自我介紹', '對話：見面、介紹自己。'),
    ('05.2', '買東西', '對話：在商店買東西、問價格。'),
    ('05.3', '問路', '對話：問路、說方向。'),
    ('05.4', '看醫生', '對話：說哪裡不舒服、看醫生。'),
    ('05.5', '說感受與講一個小故事', '對話：說心情、講一件發生的事。'),
    ('05.6', '十二週學習計畫', '每週學什麼、怎麼複習。'),
    ('06.1', '本詞、描述、外來語', '三層表達法：表外的概念怎麼說。'),
    ('06.2', '描述加類頭', '描述的公式與類頭清單。'),
    ('06.3', '外來語與專有名詞', '外來語的寫法與說明規則。'),
    ('06.4', '先定義、後沿用', '一篇文章裡怎麼處理第一次出現的外來語。'),
    ('06.5', '改寫流程：七步', '把一般文章改寫成受限語言的步驟。'),
    ('07.1', '實例：日常與新聞', '把一般文章改寫成受限語言的實例。'),
    ('07.2', '實例：科普、議論與說明', '更多改寫實例。'),
    ('07.3', '最常犯的錯', '學習者最常犯的錯，以及怎麼改。'),
    ('07.4', '檢查工具、網頁翻譯器與 LLM 專家', '怎麼用工具檢查自己的句子。'),
    ('08.1', '與既有方案的對照', '和 Basic English、Globish、Toki Pona 等比較。'),
    ('08.2', '{name} 的設計與驗證', '這個語言是怎麼設計出來的、驗證結果。'),
    ('09.1', '已知的三個限制', '還做不到什麼。'),
    ('09.2', '接下來會做什麼', '後續計畫。'),
    ('A', '完整詞表', '所有單位一覽。'),
    ('B', '常用但禁止的詞與替代說法', '最常用的表外詞，以及要怎麼改說。'),
    ('C', '練習答案', '各章練習的參考答案。'),
]


def find_errors(text, checker, s):
    """找出章節裡不合規則的例句。回傳錯誤清單。"""
    out = []
    for block in re.findall(r'```\n(.*?)```', text, re.S):
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r'^[甲乙丙丁][：:]\s*', '', line)
            line = re.sub(r'^[-*]\s*', '', line)
            if not line:
                continue
            # 純中文的行是翻譯／答案，不檢查
            if re.search(r'[一-鿿]', line) and not re.search(
                    r'[a-zA-Z぀-ヿ가-힯]', line):
                continue
            if re.search(r'[一-鿿]', line):
                # 中英混排：只檢查英文那一段
                seg = re.search(r'[a-zA-Z぀-ヿ가-힯][^\n]*$', line)
                if seg:
                    line = seg.group(0).strip()
                else:
                    continue
            for e in checker.check(line):
                out.append(f'{line[:40]} → {e}')
    for line in text.splitlines():
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2 or set(cells[0]) <= set('-: '):
            continue
        first = cells[0]
        if len(first) < 2 or len(first) > 60:
            continue
        if re.search(r'[一-鿿]', first):
            continue
        if not re.search(r'[a-zA-Z぀-ヿ가-힯]', first):
            continue
        if re.fullmatch(r'[A-Za-z]+', first) and first not in checker.spec.vocab \
                and first.lower() not in checker.accepted:
            continue
        if first.startswith('`') and first.endswith('`'):
            continue
        if first.startswith('Mini-') or first == s.code:
            continue
        for e in checker.check(first):
            out.append(f'{first[:40]} → {e}')
    return out


def build_system(s, checker):
    spec_text = (s.dir / 'spec.md').read_text(encoding='utf-8')
    return f"""你是一位教外國人學 {s.name} 的老師，正在寫課本。

{spec_text}

寫課本的規則：
1. 用繁體中文寫解釋（讀者是中文母語者），例句用 {s.name}。
2. **所有 {s.name} 的例句都要通過檢查**：只能用詞表內的字詞，
   外來語第一次出現時加括號說明，說明本身也要用詞表內的字詞。
3. 不要寫「這裡省略了之類的說法」，每一句都要完整。
4. 每一章用 markdown，有小標題（##）、表格、對話區塊。
5. 對話用這個格式：
   ```
   甲：……
   乙：……
   ```
6. 最後給 3–5 題練習（用 `- [ ]` 清單），每題後面空一行寫答案（用 `> 答案：……`）。
7. 不要輸出其他解釋，不要說「以下是第 X 章」。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    ap.add_argument('--chapters', type=int, default=0, help='0 = 全部')
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--out', default=None, help='輸出目錄（預設 books/<code>）')
    a = ap.parse_args()

    s = spec_mod.load(a.lang)
    checker = Checker(s)
    name = BOOK_NAME.get(s.code, s.name)
    n = len(s.words)
    llm = LLM(provider=a.provider)
    system = build_system(s, checker)

    out_dir = Path(a.out) if a.out else ROOT / 'books' / s.code
    out_dir.mkdir(parents=True, exist_ok=True)

    chapters = CHAPTERS[:a.chapters] if a.chapters else CHAPTERS

    def one(ch):
        num, title, brief = ch
        t = title.replace('{name}', name).replace('{n}', str(n))
        prompt = (f'請寫「{num} {t}」這一章。\n'
                  f'這一章的重點：{brief}\n\n'
                  f'要求：\n'
                  f'- 開頭用一段話說明這一章要學什麼。\n'
                  f'- 中間分成 2–4 個小節（用 ## 標題），每節有說明、表格或例句。\n'
                  f'- 至少 5 個完整例句（用 {name} 寫），必要時用表格對照。\n'
                  f'- 最後給 3–5 題練習與答案。\n'
                  f'- 全文用 markdown。')
        try:
            text = llm.chat(prompt, system=system, max_tokens=8192)
        except Exception as e:      # noqa: BLE001
            return num, t, f'ERROR {e}'

        # 自我修正：把檢查出來的錯回饋給模型，讓它改
        for _ in range(2):
            if num in ('A', 'B', 'C'):
                break
            errs = find_errors(text, checker, s)
            if not errs:
                break
            bad = '\n'.join(f'- {e}' for e in errs[:15])
            fix_prompt = (f'你寫的「{num} {t}」這一章裡，以下例句不合規則：\n\n{bad}\n\n'
                          f'請把整章重寫一次，把這些例句改對。'
                          f'其他內容可以保留。\n'
                          f'只輸出改好的 markdown 章節，不要解說。')
            try:
                text = llm.chat(fix_prompt, system=system, max_tokens=8192)
            except Exception:      # noqa: BLE001
                break
        return num, t, text

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, chapters))

    bad = 0
    for num, title, text in results:
        if text.startswith('ERROR'):
            print(f'❌ {num} {title}：{text[:80]}')
            bad += 1
            continue
        # 附錄（A 詞表、B 禁用詞、C 答案）本來就會包含表外的詞，不檢查
        if num in ('A', 'B', 'C'):
            errs = []
        else:
            errs = find_errors(text, checker, s)
        for e in errs[:8]:
            print(f'❌ {num} {title}：{e}')
        bad += len(errs)
        fn = out_dir / f'{num}-{title.replace("/", "／")}.md'
        fn.write_text(f'# {num} {title}\n\n{text}\n', encoding='utf-8')
    nbad = sum(1 for num, title, text in results if num in ('A', 'B', 'C')
               or not text.startswith('ERROR'))
    print(f'✅ {nbad} 章寫好（{bad} 個例子問題）→ {out_dir}')
    print(llm.stats())


if __name__ == '__main__':
    main()
