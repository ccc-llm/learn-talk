#!/usr/bin/env python3
"""把 mini-lang 的 Mini-Chinese 規格遷移成 learn-talk 的 langs/mini-chinese/。

用法：python tools/migrate_chinese.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path('/Users/Shared/ccc/project/mini-lang/mini-chinese/mini-chinese')
DST = ROOT / 'langs' / 'mini-chinese'


def parse_char_table(text: str):
    """從 mini-chinese.md 第 2 節的表格抽出 (字, 拼音, 英文, 類別)。"""
    sec = text[text.index('## 2. 字表'):text.index('## 3.')]
    cat = ''
    out = []
    header = None
    for line in sec.splitlines():
        line = line.strip()
        if line.startswith('### '):
            cat = re.sub(r'^###\s*[\d.]*\s*', '', line).split('（')[0].strip()
            header = None
            continue
        if not line.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if all(re.fullmatch(r':?-+:?', c) for c in cells):
            continue
        if header is None:
            header = cells
            continue
        if len(cells) >= 3 and len(cells[0]) == 1 and re.match(r'[\u4e00-\u9fff]', cells[0]):
            char, pinyin, en = cells[0], cells[1], cells[2]
            combo = cells[3] if len(cells) > 3 else ''
            out.append((char, pinyin, en, cat, combo))
    return out


def parse_grammar(text: str):
    """抓 4.2 十七條句型規則 → (規則本文, 例句)。"""
    start = text.index('### 4.2 十七條句型規則')
    end = text.index('### 4.3')
    sec = text[start:end]
    rules = []
    cur = None
    for block in re.split(r'\n\*\*規則 ', sec)[1:]:
        head, _, rest = block.partition('\n')
        rid = head.split('　')[0].split(' ')[0].strip()
        title = head.split('　', 1)[1].strip() if '　' in head else head.strip()
        body = title + ' ' + rest
        # 清理 markdown
        body = re.sub(r'\*\*', '', body)
        body = re.sub(r'^\|.*$', '', body, flags=re.M)
        body = re.sub(r'^>.*$', '', body, flags=re.M)
        body = body.strip()
        ex = ''
        m = re.findall(r'```zh\n(.*?)```', block, re.S)
        if m:
            ex = ' / '.join(x.strip().replace('\n', ' ') for x in m if x.strip())
        summary = body.split('\n')[0].strip()
        summary = re.sub(r'\s+', ' ', summary)
        rules.append((rid, summary, ex))
    return rules


def main():
    if not SRC.exists():
        sys.exit(f'找不到來源：{SRC}')
    text = (SRC / 'mini-chinese.md').read_text(encoding='utf-8')
    chars = parse_char_table(text)
    print(f'抓到 {len(chars)} 個字')

    (DST / 'data').mkdir(parents=True, exist_ok=True)
    (DST / 'prompts').mkdir(parents=True, exist_ok=True)

    (DST / 'meta.json').write_text(json.dumps({
        'name': 'Mini-Chinese',
        'native': '簡易中文',
        'unit': 'char',
        'script': 'han',
        'romanization': 'pinyin',
        'target_reader': '母語不是中文的外國人',
        'source': 'mini-lang/mini-chinese',
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    rows = ['unit\tlevel\tpos\tgloss\tcategory\texample\tipa']
    for ch, pinyin, en, cat, combo in chars:
        rows.append(f'{ch}\tC\t{_pos(ch, cat)}\t{en}\t{cat}\t{combo}\t{pinyin}')

    # 第 4 版新增字（依改寫測試的常見錯誤補上）
    ADDED = {
        '各': ('adj', '每一個', '性質'),
        '附': ('v', '附上', '動作'),
        '踢': ('v', '踢', '動作'),
        '圖': ('n', '圖', '事物'),
        '容': ('adj', '容易容納', '性質'),
        '易': ('adj', '容易', '性質'),
        '才': ('adv', '才', '語法'),
        '需': ('v', '需要', '動作'),
        '正': ('adv', '正好', '語法'),
        '讓': ('v', '讓', '動作'),
        '修': ('v', '修理', '動作'),
        '目': ('n', '眼睛', '事物'),
        '低': ('adj', '低的', '性質'),
        '保': ('v', '保證；保護', '動作'),
        '險': ('adj', '危險的', '性質'),
        '規': ('n', '規則', '事物'),
        '則': ('gram', '規則', '語法'),
        '標': ('n', '標記', '事物'),
        '記': ('v', '記住', '動作'),
        '確': ('adj', '確定', '性質'),
        '實': ('adj', '真實', '性質'),
        '際': ('n', '時候', '時間'),
        '遇': ('v', '遇見', '動作'),
        '選': ('v', '選擇', '動作'),
        '擇': ('v', '選擇', '動作'),
        '試': ('v', '試試', '動作'),
        '驗': ('v', '驗證', '動作'),
        '環': ('n', '環境', '事物'),
        '境': ('n', '環境', '事物'),
        '衛': ('n', '衛生', '事物'),
        '費': ('n', '費用', '事物'),
        '料': ('n', '材料', '事物'),
        '資': ('n', '資料', '事物'),
        '訊': ('n', '訊息', '事物'),
        '息': ('n', '休息', '時間'),
        '影': ('n', '影像', '事物'),
        '響': ('v', '影響', '動作'),
        '優': ('adj', '優秀', '性質'),
        '劣': ('adj', '不好', '性質'),
        '豐': ('adj', '豐富', '性質'),
        '簡': ('adj', '簡單', '性質'),
        '複': ('adj', '複雜', '性質'),
        '雜': ('adj', '複雜', '性質'),
        '純': ('adj', '單純', '性質'),
        '潔': ('adj', '清潔', '性質'),
        '淨': ('adj', '乾淨', '性質'),
        '衛': ('n', '衛生', '事物'),
        '隨': ('v', '跟著', '動作'),
        '狀': ('n', '狀態', '事物'),
        '態': ('n', '狀態', '事物'),
        '壓': ('n', '壓力', '事物'),
        '迫': ('adj', '被迫', '性質'),
        '願': ('v', '願意', '動作'),
        '望': ('v', '希望', '動作'),
        '努': ('v', '努力', '動作'),
        '極': ('adj', '極端', '性質'),
        '端': ('n', '端點', '事物'),
        '極': ('adj', '極端', '性質'),
        '信': ('n', '訊息；相信', '事物'),
        '集': ('v', '集合', '動作'),
        '廣': ('adj', '廣', '性質'),
        '場': ('n', '地方', '事物'),
        '設': ('n', '設施', '事物'),
        '施': ('v', '施行', '動作'),
        '備': ('v', '準備', '動作'),
        '準': ('adj', '準備好的', '性質'),
        '備': ('v', '準備', '動作'),
        '達': ('v', '到達', '動作'),
        '產': ('n', '生產', '事物'),
        '效': ('n', '效果', '事物'),
        '益': ('adj', '有益', '性質'),
        '負': ('v', '負擔', '動作'),
        '擔': ('n', '擔子', '事物'),
        '職': ('n', '工作', '事物'),
        '務': ('n', '事務', '事物'),
        '員': ('n', '人（工作者）', '事物'),
        '傭': ('n', '薪水', '事物'),
        '資': ('n', '資源', '事物'),
        '源': ('n', '水源', '事物'),
        '居': ('v', '居住', '動作'),
        '住': ('v', '住', '動作'),
        '宿': ('n', '住宿', '事物'),
        '舍': ('n', '房子', '事物'),
        '孫': ('n', '孫子', '事物'),
        '婚': ('n', '婚禮', '社交'),
        '禮': ('n', '禮物', '社交'),
        '葬': ('n', '葬禮', '社交'),
        '儀': ('n', '儀式', '社交'),
        '式': ('n', '方式', '事物'),
        '祝': ('v', '祝賀', '社交'),
        '賀': ('v', '祝賀', '社交'),
        '慶': ('v', '慶祝', '社交'),
        '旅': ('n', '旅行', '事物'),
        '行': ('v', '旅行', '動作'),
        '客': ('n', '客人', '社交'),
        '滿': ('adj', '滿的', '性質'),
        '座': ('n', '座位', '事物'),
        '位': ('n', '位置', '事物'),
        '置': ('v', '放置', '動作'),
        '細': ('adj', '細的', '性質'),
        '終': ('v', '結束', '動作'),
        '始': ('v', '開始', '動作'),
        '設': ('n', '設施', '事物'),
        '維': ('v', '維持', '動作'),
        '持': ('v', '維持', '動作'),
        '營': ('v', '經營', '動作'),
        '運': ('v', '運送', '動作'),
        '輸': ('v', '運送', '動作'),
        '費': ('n', '費用', '事物'),
        '成': ('v', '成為', '動作'),
        '功': ('n', '功效', '事物'),
        '效': ('n', '效果', '事物'),
        '負': ('v', '負擔', '動作'),
        '足': ('n', '腳', '事物'),
        '單': ('adj', '單一', '性質'),
        '又': ('adv', '又', '語法'),
        '群': ('n', '一群人', '事物'),
        '市': ('n', '城市', '事物'),
        '清': ('adj', '乾淨', '性質'),
        '管': ('v', '管理', '動作'),
        '活': ('v', '活著', '動作'),
        '生': ('v', '生長；生活', '動作'),
        '長': ('v', '生長', '動作'),
        '長': ('v', '生長', '動作'),
        '長': ('v', '生長', '動作'),
        '物': ('n', '東西', '事物'),
        '草': ('n', '草', '事物'),
        '動': ('v', '動', '動作'),
        '用': ('v', '使用', '動作'),
        '東': ('n', '東', '方位'),
        '西': ('n', '西', '方位'),
        '北': ('n', '北', '方位'),
        '南': ('n', '南', '方位'),
        '周': ('n', '周圍', '方位'),
        '邊': ('n', '旁邊', '方位'),
        '旁': ('adj', '旁邊', '方位'),
        '開': ('v', '打開', '動作'),
        '關': ('v', '關上', '動作'),
        '機': ('n', '機器', '事物'),
        '器': ('n', '工具', '事物'),
        '具': ('n', '工具', '事物'),
        '圖': ('n', '圖', '事物'),
        '畫': ('v', '畫', '動作'),
        '設': ('n', '設施', '事物'),
        '備': ('v', '準備', '動作'),
        '獲': ('v', '獲得', '動作'),
        '得': ('v', '得到', '動作'),
        '益': ('adj', '有益', '性質'),
        '需': ('v', '需要', '動作'),
        '求': ('v', '要求', '動作'),
        '供': ('v', '提供', '動作'),
        '給': ('v', '給', '動作'),
        '將': ('adv', '將要', '語法'),
        '已': ('adv', '已經', '語法'),
        '經': ('adv', '已經', '語法'),
        '過': ('v', '超過', '動作'),
        '超': ('v', '超過', '動作'),
        '克': ('v', '克服', '動作'),
        '服': ('v', '服從', '動作'),
        '務': ('n', '事務', '事物'),
        '素': ('n', '要素', '事物'),
        '質': ('n', '品質', '事物'),
        '優': ('adj', '優秀', '性質'),
        '劣': ('adj', '不好', '性質'),
        '課': ('n', '課', '事物'),
        '程': ('n', '過程', '事物'),
        '度': ('n', '程度', '事物'),
        '級': ('n', '等級', '事物'),
        '類': ('n', '種類', '事物'),
        '型': ('n', '類型', '事物'),
        '態': ('n', '狀態', '事物'),
        '勢': ('n', '勢頭', '事物'),
        '勢': ('n', '勢頭', '事物'),
        '增': ('v', '增加', '動作'),
        '減': ('v', '減少', '動作'),
        '加': ('v', '增加', '動作'),
        '壓': ('n', '壓力', '事物'),
        '迫': ('adj', '逼迫', '性質'),
        '顧': ('v', '照顧', '動作'),
        '客': ('n', '客人', '社交'),
        '戶': ('n', '門（戶數）', '事物'),
        '族': ('n', '家族', '事物'),
        '親': ('n', '親戚', '社交'),
        '歲': ('num', '歲', '數量'),
        '齡': ('n', '年齡', '事物'),
        '件': ('num', '件', '數量'),
        '種': ('n', '種類', '事物'),
        '暖': ('adj', '暖和', '性質'),
        '計': ('v', '計算', '動作'),
        '造': ('v', '建造', '動作'),
        '鄉': ('n', '家鄉', '事物'),
        '堂': ('n', '大廳', '事物'),
        '測': ('v', '測量', '動作'),
        '結': ('v', '結束', '動作'),
        '差': ('adj', '差', '性質'),
        '決': ('v', '決定', '動作'),
        '定': ('v', '決定', '動作'),
        '選': ('v', '選擇', '動作'),
        '擇': ('v', '選擇', '動作'),
        '標': ('n', '標記', '事物'),
        '記': ('v', '記住', '動作'),
        '確': ('adj', '確定', '性質'),
        '實': ('adj', '真實', '性質'),
        '際': ('n', '時候', '時間'),
        '環': ('n', '環境', '事物'),
        '境': ('n', '環境', '事物'),
        '衛': ('n', '衛生', '事物'),
        '資': ('n', '資料', '事物'),
        '訊': ('n', '訊息', '事物'),
        '響': ('v', '影響', '動作'),
        '優': ('adj', '優秀', '性質'),
        '簡': ('adj', '簡單', '性質'),
        '複': ('adj', '複雜', '性質'),
        '雜': ('adj', '複雜', '性質'),
        '純': ('adj', '單純', '性質'),
        '潔': ('adj', '清潔', '性質'),
        '淨': ('adj', '乾淨', '性質'),
        '隨': ('v', '跟著', '動作'),
        '狀': ('n', '狀態', '事物'),
        '態': ('n', '狀態', '事物'),
        '壓': ('n', '壓力', '事物'),
        '迫': ('adj', '逼迫', '性質'),
        '願': ('v', '願意', '動作'),
        '望': ('v', '希望', '動作'),
        '努': ('v', '努力', '動作'),
        '極': ('adj', '極端', '性質'),
        '端': ('n', '端點', '事物'),
        '屆': ('num', '屆', '數量'),
        '屆': ('num', '屆', '數量'),
    }
    rows_extra = []
    for ch, (pos, gloss, cat) in ADDED.items():
        if ch in {c[0] for c in chars}:
            continue
        rows_extra.append(f'{ch}\tC\t{pos}\t{gloss}\t{cat}\t\t')
    rows.extend(rows_extra)
    print(f'新增 {len(rows_extra)} 字')
    (DST / 'data' / 'words.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')

    # 類頭
    heads = ['人', '東西', '地方', '時候', '事', '話', '樣子', '意思', '心', '學問',
             '工作', '病', '機', '車', '房子', '書', '文', '國', '家', '店', '水',
             '氣', '色', '錢', '路', '口', '頭']
    (DST / 'data' / 'heads.tsv').write_text(
        'head\tgloss\n' + '\n'.join(f'{h}\t' for h in heads) + '\n', encoding='utf-8')

    # 描述模板
    desc = ['做什麼用的 X 的地方', '在哪裡的 X 的東西', '像 X 一樣的色',
            '屬於 X 的', '有 X 特點的 X', '做 X 的工作的 X']
    (DST / 'data' / 'desc.tsv').write_text(
        'template\tgloss\n' + '\n'.join(f'{d}\t' for d in desc) + '\n', encoding='utf-8')

    # 語法規則
    rules = parse_grammar(text)
    g = ['rid\ttext\texample\tnote']
    for rid, summary, ex in rules:
        g.append(f'{rid}\t{summary}\t{ex}\t')
    (DST / 'data' / 'gram.tsv').write_text('\n'.join(g) + '\n', encoding='utf-8')
    print(f'抓到 {len(rules)} 條語法規則')

    # 禁用詞與替代（語法結構替代 + 換詞表）
    prompt = Path('/Users/Shared/ccc/project/learn-talk/doc/mini-chinese-prompt.md').read_text(encoding='utf-8')
    rep = parse_prompt_replace(prompt)
    (DST / 'data' / 'replace.tsv').write_text(
        'word\treplace\n' + '\n'.join(f'{k}\t{v}' for k, v in rep) + '\n', encoding='utf-8')
    print(f'抓到 {len(rep)} 條替代說法')

    # 專有名詞
    proper = ['Beijing', 'Shanghai', 'London', 'Tokyo', 'Seoul', 'Paris', 'Asia',
              'Europe', 'China', 'Japan', 'Korea', 'UK', 'US']
    (DST / 'data' / 'proper.tsv').write_text(
        'word\tgloss\n' + '\n'.join(f'{p}\t' for p in proper) + '\n', encoding='utf-8')

    # 詞典合併
    lex_rows = ['原文\t受限說法\t方式\t說明']
    for f in sorted((SRC / 'lexicon').glob('*.tsv')):
        for line in f.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            c = line.split('\t')
            while len(c) < 4:
                c.append('')
            src, mini, note, way = c[0], c[1], c[2], c[3]
            way = way or '描述'
            if way == '組詞':
                way = '描述'
            lex_rows.append(f'{src}\t{mini}\t{way}\t{note}')
    (DST / 'lexicon.tsv').write_text('\n'.join(lex_rows) + '\n', encoding='utf-8')
    print(f'詞典 {len(lex_rows) - 1} 列')


def _pos(ch, cat):
    if cat.startswith('代詞'):
        return 'pron'
    if cat.startswith('語法'):
        return 'gram'
    if cat.startswith('數量'):
        return 'num'
    if cat.startswith('時間'):
        return 'time'
    if cat.startswith('方位'):
        return 'place'
    if cat.startswith('動作'):
        return 'v'
    if cat.startswith('性質'):
        return 'adj'
    if cat.startswith('社交'):
        return 'gram'
    return 'n'


def parse_prompt_replace(text: str):
    """從 mini-chinese-prompt.md 的「語法：字表沒有的結構」與「換詞」兩張表抓替代說法。"""
    out = []
    seen = set()

    def add(a, b):
        a, b = a.strip(), b.strip()
        if not a or not b or a in seen or len(a) > 14:
            return
        seen.add(a)
        out.append((a, b))

    # 語法結構替代
    try:
        sec = text[text.index('## 6. 語法：字表沒有的結構'):text.index('## 7.')]
    except ValueError:
        sec = ''
    for line in sec.splitlines():
        if not line.strip().startswith('|'):
            continue
        c = [x.strip() for x in line.strip('|').split('|')]
        if len(c) < 3 or c[0] in ('一般中文', '改用') or all(re.fullmatch(r':?-+:?', x) for x in c):
            continue
        add(c[0], c[1])

    # 換詞表（第 3 節）
    try:
        sec = text[text.index('## 3. 換詞：依序試三層'):text.index('## 4. 英文外來語')]
    except ValueError:
        sec = ''
    for line in sec.splitlines():
        if not line.strip().startswith('|'):
            continue
        c = [x.strip() for x in line.strip('|').split('|')]
        if len(c) < 3 or c[0] in ('一般中文', 'Mini-Chinese 說法') or all(re.fullmatch(r':?-+:?', x) for x in c):
            continue
        if c[1] == '同左':
            continue
        add(c[0], c[1])
    return out


if __name__ == '__main__':
    main()
