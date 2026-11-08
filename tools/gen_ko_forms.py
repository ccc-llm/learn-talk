#!/usr/bin/env python3
"""為 Mini-Korean 的動詞與形容詞產生完整形式表。

韓文的活用不規則很多（ㅣ／ㅡ／ㅎ 收縮、ㄹ 脫落、ㅂ 不規則…），
用規則推導容易出錯，所以改成請 LLM 直接列出每一個詞的形式，
再用本程式檢查一致性。

用法：
    python tools/gen_ko_forms.py --lang korean
"""
from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.llm import LLM  # noqa: E402

SYSTEM = """你是一位韓文老師。我要為受限韓文（Mini-Korean）建立動詞與形容詞的形式表。

規則：
1. **只用 해요體**。現在式＝해요／過去式＝았어요·었어요／未來式＝(으)ㄹ 거예요。
2. 名詞化（描述用）：動詞的「-는」形，例如 먹는＝吃的、운전하는＝開車的。
3. 形容詞的冠形詞形（修飾名詞時用）：좋은 책、큰 집、예쁜 꽃。
   規則：無收音加「ㄴ」、有收音加「은」；但「ㄹ 收音」用「ㄹ」也不對，請照實際寫法給。
4. 不要用敬語（하십시오체），不要用半語。
5. 每行一個詞，格式：
   詞<TAB>現在式<TAB>過去式<TAB>未來式<TAB>名詞化／冠形詞形
6. 不要輸出其他文字。詞只給原形（現在式），不要編號。"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default='korean')
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()

    data = ROOT / 'langs' / 'mini-korean' / 'data'
    words = []
    for cat in ('verb', 'adj'):
        p = data / f'_cand_{cat}.tsv'
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8').splitlines()[1:]:
            c = line.split('\t')
            if c and c[0].strip():
                words.append(c[0].strip())

    # 只處理還沒有的詞
    existing = set()
    kof = data / 'ko_forms.tsv'
    if kof.exists():
        for line in kof.read_text(encoding='utf-8').splitlines()[1:]:
            c = line.split('\t')
            if len(c) >= 2 and c[1].strip():
                existing.add(c[1].strip())
    words = [w for w in words if w not in existing]
    print(f'需要補 {len(words)} 個詞')

    llm = LLM(provider=a.provider)

    def one(w):
        prompt = (f'請列出「{w}」的四种形式。\n'
                  f'格式：詞<TAB>現在式<TAB>過去式<TAB>未來式<TAB>名詞化／冠形詞形\n'
                  f'名詞化／冠形詞形：動詞給 -는 形，形容詞給冠形詞形。')
        try:
            return llm.chat(prompt, system=SYSTEM, max_tokens=2000)
        except Exception as e:      # noqa: BLE001
            return f'ERROR {e}'

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, words))

    rows = ['unit\tpresent\tpast\tfuture\ttopic']
    bad = 0
    for w, r in zip(words, results):
        if r.startswith('ERROR'):
            bad += 1
            continue
        parts = [x.strip() for x in r.split('\t')]
        if len(parts) < 5:
            parts = [x.strip() for x in r.split('|')]
        if len(parts) < 5:
            bad += 1
            continue
        unit = parts[0] or w
        present, past, future, topic = parts[1], parts[2], parts[3], parts[4]
        if not past or not future:
            bad += 1
            continue
        rows.append(f'{unit}\t{present}\t{past}\t{future}\t{topic}')
    # 合併到既有檔案（以「現在式」為 key，不重複）
    merged = {}
    if kof.exists():
        for line in kof.read_text(encoding='utf-8').splitlines()[1:]:
            c = [x.strip() for x in line.split('\t')]
            if len(c) >= 5 and c[1]:
                merged[c[1]] = c[1:5]
    for r in rows[1:]:
        c = r.split('\t')
        if len(c) >= 5 and c[1]:
            merged[c[1]] = c[1:5]
    out = ['unit\tpresent\tpast\tfuture\ttopic']
    for k, v in sorted(merged.items()):
        out.append('\t'.join([k] + v))
    kof.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'✅ {len(rows) - 1} 列（{bad} 個失敗）→ {data / "ko_forms.tsv"}')


if __name__ == '__main__':
    main()
