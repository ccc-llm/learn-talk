#!/usr/bin/env python3
"""用 LLM 產生某個語言的詞表候選，再人工校訂。

用法：
    python tools/gen_words.py --lang fr --category verb --n 120
輸出到 langs/mini-french/data/_cand_verb.tsv（人工校訂後合併進 words.tsv）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.llm import LLM  # noqa: E402

CATEGORY_HINT = {
    'pron': '代詞、指示詞、疑問詞、關係代詞',
    'gram': '功能詞：冠詞、介詞、連接詞、代詞、否定詞、助動詞',
    'num': '數字、數量、比例',
    'time': '時間、日期、星期、季節、時刻',
    'place': '方位、地點、場所',
    'nature': '自然、天氣、動植物',
    'verb': '動作、狀態動詞',
    'adj': '性質、顏色、情緒',
    'noun': '事物、身體、衣物、食物、器物',
    'social': '社交、人、稱呼',
    'abstr': '抽象概念：想法、時間、關係、社會、情緒',
}

SYSTEM = """你是一位語言學家，正在為外國人設計一套受限法文（叫 Mini-French）。
Mini-French 的詞表要能表達日常生活，選詞原則是：
1. 選「表達力強、能構詞」的詞，不看詞頻。
2. 一個概念一個詞，去掉同義詞（只留 grand，不留 gros / immense）。
3. 能用其他詞輕鬆說出來的不收（hôpital → «l'endroit où les médecins soignent les malades»）。
4. 盡量避免難寫、容易唸錯的詞。

你只要輸出詞表，不要解釋。每行一個詞，格式：
法文詞<TAB>詞性<TAB>中文意思
詞性只用：n（名詞）、v（動詞）、adj（形容詞）、adv（副詞）、det（限定詞）、pron（代詞）、num（數詞）、gram（功能詞）
不要輸出表頭以外的任何文字。"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default='fr')
    ap.add_argument('--category', required=True)
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    lang_dir = ROOT / 'langs' / f'mini-{a.lang}'
    llm = LLM(provider=a.provider)
    hint = CATEGORY_HINT.get(a.category, a.category)
    prompt = (f'請給 Mini-French 的「{a.category}」類別出 {a.n} 個詞。\n'
              f'這一類是：{hint}。\n'
              f'每行一個：法文詞<TAB>詞性<TAB>中文意思\n'
              f'不要重複，不要輸出其他文字。')
    lines = llm.chat_lines(prompt, system=SYSTEM)
    out = Path(a.out) if a.out else lang_dir / 'data' / f'_cand_{a.category}.tsv'
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = ['unit\tpos\tgloss']
    for l in lines:
        parts = l.split('\t')
        if len(parts) < 2:
            parts = l.split('|')
        if len(parts) < 2:
            continue
        w = parts[0].strip()
        pos = parts[1].strip().split('/')[0].strip()
        gloss = parts[2].strip() if len(parts) > 2 else ''
        if not w or ' ' in w:
            continue
        rows.append(f'{w}\t{pos}\t{gloss}')
    out.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'✅ {len(rows) - 1} 個候選 → {out}')


if __name__ == '__main__':
    main()
