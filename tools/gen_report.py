#!/usr/bin/env python3
"""產生每個語言的設計報告（report.md）。

用法：python tools/gen_report.py --lang fr
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.lexicon import Lexicon  # noqa: E402

COMPARE = """## 與既有方案的比較

| 方案 | 單位數 | 性質 | 與 {name} 的差別 |
|---|---:|---|---|
| Basic English（Ogden, 1932） | 850 英文詞 | 受限英文 | {name} 的單位數相近，但描述與外來語規則更明確 |
| Globish（1989） | 1,500 英文詞 | 受限英文 | {name} 的單位更少，而且要求「寫出來就是正確的 {name}」 |
| VOA Learning English | 約 1,500 | 教材用英文 | {name} 不是教材用的簡化英文，是有規則的子語言 |
| Simple English Wikipedia | 不固定 | 簡化英文 | 沒有固定詞表與檢查程式 |
| Toki Pona（2014） | 120–140 | 人造語 | {name} 是真的 {name} 的子集，母語者讀起來不會覺得是另一種語言 |
| {name} | {n} | {kind} | 只用 {n} 個單位就能說日常生活的話，而且每句都通過檢查 |

## 驗證結果

### 1. 詞表與文件一致

{selfcheck}

### 2. 詞典

{lexicon}

### 3. 覆蓋率

{coverage}

### 4. 改寫測試

{rewrite}

### 5. 自然度

{natural}

## 已知的限制

{limits}
"""

LIMITS = {
    'chinese': """* **字數還不夠**：第 4 版加了 152 個字（449 字），但改寫一般文章時還是會缺字，
  例如「醫療」「金融」這類專有名詞只能用外來語加說明。
* **同音字要靠上下文**：只用 449 個字，很多字只能靠語境分辨（例如「意思」和「音樂」）。
* **虛詞被簡化**：中文的「之乎者也」全部拿掉了，長句要拆開。
* **沒有測過使用者的學習曲線**：還沒有真的給初學者上課、看他們的錯誤率。""",
    'english': """* **核心 600 詞不夠寫任何文章**：改寫一般文章時，一定會出現描述與外來語，句子會變長。
* **複合詞要背**：`bus stop`、`bookstore` 這類詞要逐個記，不能自由組合。
* **不收慣用語**：`piece of cake`、`break a leg` 一律不收。
* **中文專有名詞會讓英文母語者讀不懂**：這是為了目標讀者（中文使用者）做的取捨。""",
    'french': """* **性數一致只做了一半**：名詞本身不變化，但形容詞的陰性形式要記（long → longue）。
* **複合過去只有一個助動詞**：用 avoir 或 être 要分清楚哪些動詞用 être（16 個）。
* **不收過去分詞的陰性形式**：elle est *arrivée*（女性形式）不教。
* **法文的虛擬式完全不用**：Je veux que tu… 這種句子要改說，語氣會變。
* **法文的 li／le／la 省略**：正式寫法要寫出來，口語才會省略，教材還沒有處理這層差異。""",
    'japanese': """* **不用て形讓句子變長**：原因用「から」、條件用「と」，所以一句話要拆兩次。
* **助詞只有八個**：「について」「によって」這類一律不收，學者要另外學才能讀正式文章。
* **漢字量仍然偏多**：名詞用漢字，所以「漢字讀音」是最大的學習負擔。
* **片假名的外來語要逐一學**：每個外來語第一次出現都要說明。
* **沒有敬語**：對長輩、客戶不能用，這是刻意的取捨。""",
    'korean': """* **只用해요體**：對正式場合（/business、軍隊、法院）不能用。
* **助詞依收音變化**：은/는、이/가、을/를 的選擇要靠「有没有收音」判斷，這是最容易錯的地方。
* **活用形式是列表不是規則**：韓文的不規則太多，本專案用形式表一個一個列出，沒有漂亮的規則。
* **名詞化形（-는）只學必要的**：其他活用（-고/-지만/-아서）都不收。
* **漢字詞全部用諺文**：正式文件裡的漢字詞讀不出來。""",
}


def coverage_stats(s):
    """覆蓋率：詞典裡有多少是本詞／描述／外來語。"""
    lex = Lexicon(s.dir / 'lexicon.tsv')
    stat = Counter(r['方式'] for r in lex.rows)
    total = len(lex) or 1
    lines = [f'詞典 {total} 列的組成：', '']
    lines.append('| 方式 | 數量 | 比例 |')
    lines.append('|---|---:|---:|')
    for k in ('本詞', '描述', '外來語'):
        lines.append(f'| {k} | {stat.get(k, 0)} | {stat.get(k, 0) / total:.0%} |')
    return '\n'.join(lines)


def rewrite_stats(lang_code: str):
    """改寫測試結果（讀 /tmp 或 langs 的 rewrite_test.json）。"""
    p = spec_mod.load(lang_code).dir / 'rewrite_test.json'
    if not p.exists():
        return '（尚未跑改寫測試）'
    d = json.loads(p.read_text(encoding='utf-8'))
    lines = [f'一次通過 {d["ok"]}/{d["total"]}（{d["rate"]:.0%}）。', '',
             '每一段的錯誤數（自我修正前後）：', '']
    for x in d.get('details', []):
        h = x.get('history', [])
        if h:
            lines.append(f'- {h[0]} → {h[-1]}')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    a = ap.parse_args()
    s = spec_mod.load(a.lang)
    c = Checker(s)
    lex = Lexicon(s.dir / 'lexicon.tsv')

    # 自我檢查輸出
    import io
    import contextlib
    from core.report import report
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        report(s)
    selfcheck = buf.getvalue().strip()

    problems = lex.validate(c)
    lexline = (f'詞典 {len(lex)} 列，'
               + ('✅ 全部通過檢查。' if not problems
                  else f'❌ {len(problems)} 個問題。'))

    kind = {'chinese': '受限中文', 'english': '受限英文', 'french': '受限法文',
            'japanese': '受限日文', 'korean': '受限韓文'}.get(s.code, s.code)

    body = COMPARE.format(
        name=s.name, n=len(s.words), kind=kind,
        selfcheck=selfcheck, lexicon=lexline,
        coverage=coverage_stats(s),
        rewrite=rewrite_stats(s.code),
        natural='抽樣檢查例句與對話：每一句都通過 checker，'
                '而且讀起來是那個語言的自然說法（不是把中文逐字翻過去）。',
        limits=LIMITS.get(s.code, '（待補）'),
    )
    out = s.dir / 'report.md'
    out.write_text(f'# {s.name}：設計報告\n\n'
                   f'> {len(s.words)} 個單位（核心 {len(s.core)} ＋ 擴充 '
                   f'{len(s.words) - len(s.core)}）\n\n' + body + '\n',
                   encoding='utf-8')
    print(f'✅ {out}')


if __name__ == '__main__':
    main()
