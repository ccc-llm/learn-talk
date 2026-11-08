#!/usr/bin/env python3
"""產生某語言的常用詞清單（用 LLM），作為詞典與覆蓋率測試的素材。

用法：
    python tools/gen_wordlist.py --lang fr --n 600 --out /tmp/fr_words.txt
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.llm import LLM  # noqa: E402

CATS = [
    '人與身分（醫生、律師、學生、司機、老師…）',
    '身體與健康（頭、手、腿、疼痛、疾病、藥…）',
    '家庭與人際（父母、兄弟、朋友、鄰居…）',
    '住家與家具（房子、房間、廚房、床、桌子…）',
    '食物與飲品（麵包、起司、午餐、咖啡…）',
    '衣物與日用品（衣服、鞋子、肥皂、雨傘…）',
    '城市與交通（街道、公車、鐵路、機場、方向…）',
    '自然與天氣（雨、雪、風、天空、河流…）',
    '動植物（狗、貓、樹、花、魚…）',
    '工作與學校（工作、公司、會議、考試、課程…）',
    '購物與金錢（商店、價格、鈔票、付款…）',
    '旅行與觀光（旅行、飯店、行李、景點…）',
    '時間與日期（早上、星期、月份、以前、馬上…）',
    '情感與想法（高興、害怕、想法、原因…）',
    '社會與抽象（法律、政府、國家、歷史、科學…）',
    '動作與事件（吃、跑、給、發生、開始…）',
    '性質與狀態（大小、冷熱、新舊、快慢…）',
    '科技與媒體（電腦、手機、電視、網路…）',
]

LANG_HINT = {
    'fr': ('法文', '法文詞'),
    'french': ('法文', '法文詞'),
    'ja': ('日文', '日文詞'),
    'japanese': ('日文', '日文詞'),
    'ko': ('韓文', '韓文詞'),
    'korean': ('韓文', '韓文詞'),
}

SYSTEM = """你是一位語言學家，正在研究{lang}的常用詞。
請依序分類列出日常會用到的具體詞彙。
要求：只要名詞、形容詞、動詞等「詞」本身，不要句子，不要解釋，不要編號以外的文字。"""


def build_system(lang: str) -> str:
    name, _ = LANG_HINT.get(lang, (lang, lang + '詞'))
    return SYSTEM.format(lang=name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', default='fr')
    ap.add_argument('--n', type=int, default=600)
    ap.add_argument('--out', required=True)
    ap.add_argument('--provider', default='minimax')
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()

    llm = LLM(provider=a.provider)
    per = max(10, a.n // len(CATS))
    name = LANG_HINT.get(a.lang, (a.lang, a.lang + '詞'))[0]

    def one(cat):
        prompt = (f'請列出 {per} 個{name}的常用詞，屬於這一類：{cat}。\n'
                  f'一行一個詞，只要詞，不要解釋。')
        try:
            return llm.chat_lines(prompt, system=build_system(a.lang), max_tokens=3000)
        except Exception as e:      # noqa: BLE001
            return [f'ERROR {e}']

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, CATS))

    seen = set()
    out = []
    for lines in results:
        for l in lines:
            w = l.strip().strip('「」"')
            if not w or w.startswith('ERROR') or ' ' in w:
                continue
            if len(w) > 24:
                continue
            if w.lower() in seen:
                continue
            seen.add(w.lower())
            out.append(w)
    Path(a.out).write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'✅ {len(out)} 個詞 → {a.out}')


if __name__ == '__main__':
    main()
