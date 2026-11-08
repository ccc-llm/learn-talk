"""由 spec 產生語言的規格文件（spec.md）與給 LLM 的系統提示詞（prompts/system.md）。

詞表只有一份（data/words.tsv），spec.md 的附錄與 prompts/system.md 都由它產生，
檢查器再回頭檢查三者是否一致。
"""
from __future__ import annotations

import re
from pathlib import Path

from . import morph


def _table(headers: list[str], rows: list[str]) -> str:
    out = ['| ' + ' | '.join(headers) + ' |',
           '|' + '|'.join('---' for _ in headers) + '|']
    out.extend(rows)
    return '\n'.join(out)


def build(spec) -> None:
    spec.dir.mkdir(parents=True, exist_ok=True)
    (spec.dir / 'spec.md').write_text(build_spec_md(spec), encoding='utf-8')
    (spec.dir / 'prompts').mkdir(exist_ok=True)
    (spec.dir / 'prompts' / 'system.md').write_text(build_system_md(spec), encoding='utf-8')


# ── spec.md ───────────────────────────────────────────────────────────────────

def build_spec_md(spec) -> str:
    rows = spec.word_table_rows()
    cat_rows = []
    for cat in spec.categories:
        ws = spec.by_category().get(cat, [])
        n_c = sum(1 for w in ws if w.level == 'C')
        cat_rows.append(f'| {cat} | {len(ws)} | {n_c} |')
    parts = [
        f'# {spec.name}：規格',
        '',
        f'> {spec.native}　單位：{spec.unit_kind}　核心層 '
        f'{len(spec.core)} ＋ 擴充層 {len(spec.words) - len(spec.core)}',
        '',
        '## 1. 設計目標',
        '',
        '| 目標 | 做法 |',
        '|---|---|',
        '| 字少 | 所有句子只由詞表內的單位組成；數字用阿拉伯數字 |',
        '| 是真正的該語言 | 寫出來的一定是正確、自然的該語言，不是另一種語言 |',
        '| 靠組合 | 學會詞表就能讀懂更多說法 |',
        '| 語法固定 | 只用編號的句型規則，困難結構用固定替代說法 |',
        '| 說不出來就換句話說 | 表外的概念用「描述 ＋ 類頭」，說不出是哪一個就用外來語 |',
        '',
        '## 2. 詞表',
        '',
        _table(['詞', '層', '詞性', '意思', '類別'] + (['例子'] if any(w.example for w in spec.words.values()) else []), rows),
        '',
        '### 分類統計',
        '',
        _table(['類別', '總數', '核心層'], cat_rows),
        '',
        '## 3. 三層表達法',
        '',
        '| 層 | 什麼時候用 | 說法 |',
        '|---|---|---|',
        '| 本詞 | 詞表內的詞 | 直接用 |',
        '| 描述 | 表外的通用概念 | 描述 ＋ 類頭 |',
        '| 外來語 | 說不出「是哪一個」（人名、地名、物種、品牌） | 原文 ＋ 第一次出現加括號說明 |',
        '',
    ]
    if spec.heads:
        parts += ['### 類頭', '', '、'.join(spec.heads), '']
    if spec.desc_templates:
        parts += ['### 描述模板', '']
        for t in spec.desc_templates:
            parts.append(f'- {t}')
        parts.append('')
    if spec.rules:
        parts += ['## 4. 語法規則', '']
        for r in spec.rules:
            ex = f'　例：{r.example}' if r.example else ''
            parts.append(f'{r.rid}. {r.text}{ex}')
        parts.append('')
    if spec.replace:
        parts += ['## 5. 禁用詞與替代說法', '',
                  _table(['禁用', '改用'], [f'| {k} | {v} |' for k, v in sorted(spec.replace.items())]), '']
    parts += ['## 附錄：完整詞表', '',
              '這是唯一的權威詞表。`#` 開頭的行是類別。', '', '```text',
              spec.appendix_block(), '```', '']
    if spec.affixes:
        parts += ['## 附錄：允許的字首字尾', '',
                  _table(['字首／字尾', '類型', '意思'],
                         [f'| {a["affix"]} | {a["kind"]} | {a["meaning"]} |' for a in spec.affixes]), '']
    if spec.irregular:
        parts += ['## 附錄：保留的不規則形式', '',
                  _table(['原形', '形式'],
                         [f'| {k} | {" / ".join(v)} |' for k, v in sorted(spec.irregular.items())]), '']
    return '\n'.join(parts)


# ── prompts/system.md ─────────────────────────────────────────────────────────

def build_system_md(spec) -> str:
    units = '字' if spec.unit_kind == 'char' else '詞'
    parts = [
        f'# 系統提示詞：{spec.name}',
        '',
        '> 把下面「---」之間的內容整段放進 LLM 的系統提示詞（system prompt）。',
        '',
        '---',
        '',
        f'你是 {spec.name} 的翻譯者與作者。{spec.name} 是受限的{spec.name}：'
        f'每一句都是母語者看得懂、說法自然的{spec.name}，只是用字受到限制。'
        '你要能把一般文字翻成受限語言、把受限語言翻回一般文字，以及直接用受限語言寫文章。',
        '',
        f'## 1. 詞表：只能用這些{units}',
        '',
        '```text',
        spec.appendix_block(),
        '```',
        '',
        '## 2. 三個原則',
        '',
        f'1. **只用詞表內的{units}。** 標題、對話、外來語的說明也一樣。',
        '2. **每一句都是自然的該語言。** 不造新詞、不改字義；意思不能變。',
        '3. **數字用阿拉伯數字。**',
        '',
        '## 3. 換詞：依序試三層',
        '',
        '| 層 | 什麼時候用 | 做法 |',
        '|---|---|---|',
        '| 本詞 | 詞表內 | **一律保留原樣** |',
        '| 描述 | 表外的通用概念 | 描述 ＋ 類頭 |',
        '| 外來語 | 說不出「是哪一個」 | 原文，第一次出現時用括號說明 |',
        '',
        '**先定義、後沿用**：第一次用描述或外來語時說明，之後直接用。',
        '',
        '## 4. 外來語',
        '',
        '- 只在描述說不出「是哪一個」時用（人名、地名、物種、品牌、術語）。',
        '- 外來語**不變化**。',
        '- **第一次出現時**，後面用括號加上用詞表內的字詞組成的說明；之後直接用。',
        '',
        '## 5. 數字與單位',
        '',
        '- 計數、日期、時間、年齡、價錢、百分比一律用阿拉伯數字。',
        '- 單位用國際符號（km、kg、°C、%）。',
        '',
    ]
    if spec.heads:
        parts += ['## 6. 類頭', '', '、'.join(spec.heads), '']
    if spec.desc_templates:
        parts += ['### 描述模板', '']
        for t in spec.desc_templates:
            parts.append(f'- {t}')
        parts.append('')
    if spec.replace:
        parts += ['## 7. 常用但禁止的詞與替代說法', '',
                  _table(['禁用', '改用'], [f'| {k} | {v} |' for k, v in sorted(spec.replace.items())]), '']
    # 最容易不小心寫出來的詞（詞表外的常用詞）── 提醒模型注意
    if spec.common_outside:
        parts += ['### 最容易不小心寫出來的詞', '',
                  '這些詞很常用，但**不在詞表內**，寫的時候要換成別的說法：', '',
                  '、'.join(spec.common_outside), '']
    if spec.rules:
        parts += ['## 8. 語法規則', '']
        for r in spec.rules:
            ex = f'　例：{r.example}' if r.example else ''
            parts.append(f'{r.rid}. {r.text}{ex}')
        parts.append('')
    parts += [
        '## 9. 每次輸出前的自我檢查',
        '',
        f'1. 逐字檢查：每個單位都在第 1 節的詞表裡嗎？不在的，回到第 3、7 節改寫。',
        '2. 數字都是阿拉伯數字嗎？',
        '3. 外來語第一次出現時有說明嗎？說明本身只用詞表內的字詞嗎？',
        '4. 唸一次：是自然的該語言嗎？意思和原文一樣嗎？',
        '',
        '如果某個意思真的說不出來，用最接近的說法，並在譯文後面用「〔註：…〕」說明你省略或改變了什麼。',
        '',
        '---',
        '',
    ]
    return '\n'.join(parts)
