#!/usr/bin/env python3
"""為 Mini-Japanese 的動詞與形容詞產生形式表（ます形以外的常見形式）。

日文不規則活用很多（五段活用、上二段活用…），用規則推導容易出錯，
所以改成請 LLM 直接列出，再由 checker 驗證。

用法：
    python tools/gen_ja_forms.py
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.llm import LLM  # noqa: E402

SYSTEM = """你是一位日文老師。我要為受限日文（Mini-Japanese）建立動詞的形式表。

規則：
1. **Mini-Japanese 只用「ます形」**（現在形）。所以本表要列出「ます形」以外的常用形式，
   好讓檢查程式能判斷「這個寫法不對，應該用ます形」。
2. 每行一個詞，格式：
   動詞原形（辞書形）<TAB>て形<TAB>た形<TAB>ない形<TAB>たい形<TAB>ます形
   - て形：例　書いて
   - た形：例　書いた
   - ない形：例　書かない
   - たい形：例　書きたい
   - ます形：例　書きます
3. 形容詞另列一張表，格式：
   形容詞原形<TAB>い形<TAB>くない形<TAB>ます形
4. 不要輸出其他文字，不要編號。
5. 如果某個形式不存在（例如他動詞沒有「ない形」以外的形式），照樣給出正確的那個。"""


def main():
    data = ROOT / 'langs' / 'mini-japanese' / 'data'
    verbs = []
    adj = []
    for cat, bucket in (('verb', verbs), ('adj', adj)):
        p = data / f'_cand_{cat}.tsv'
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            c = line.split('\t')
            if c and c[0].strip():
                bucket.append(c[0].strip())

    llm = LLM(provider='minimax')

    def one(w, kind):
        if kind == 'v':
            prompt = (f'請列出動詞「{w}」的五種形式。\n'
                      f'格式：辞書形<TAB>て形<TAB>た形<TAB>ない形<TAB>たい形<TAB>ます形')
        else:
            prompt = (f'請列出形容詞「{w}」的三種形式。\n'
                      f'格式：原形<TAB>い形<TAB>くない形<TAB>ます形')
        try:
            return llm.chat(prompt, system=SYSTEM, max_tokens=1500)
        except Exception as e:      # noqa: BLE001
            return f'ERROR {e}'

    def work(item):
        w, kind = item
        return w, kind, one(w, kind)

    items = [(w, 'v') for w in verbs] + [(w, 'a') for w in adj]
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(work, items))

    vrows = ['unit\tte\ta\tnai\ttai\tmasu']
    arows = ['unit\ti\tkunai\tmasu']
    for w, kind, r in results:
        if r.startswith('ERROR'):
            continue
        parts = [x.strip() for x in r.split('\t')]
        if kind == 'v':
            if len(parts) < 6:
                continue
            vrows.append('\t'.join(parts[:6]))
        else:
            if len(parts) < 4:
                continue
            arows.append('\t'.join(parts[:4]))
    (data / 'ja_forms.tsv').write_text('\n'.join(vrows) + '\n', encoding='utf-8')
    (data / 'ja_adj_forms.tsv').write_text('\n'.join(arows) + '\n', encoding='utf-8')
    print(f'✅ 動詞 {len(vrows) - 1} 列、形容詞 {len(arows) - 1} 列')


if __name__ == '__main__':
    main()
