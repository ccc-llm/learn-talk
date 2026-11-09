#!/usr/bin/env python3
"""learn-talk 的本機網頁伺服器。

提供：
  /                     網頁本體（翻譯器／檢查器／詞表／專家／發音）
  /api/lang             列出語言
  /api/check            檢查一段文字（回傳錯誤清單）
  /api/translate        規則翻譯（受限語言 → 一般語言，用詞典查表）
  /api/lexicon          查詞典
  /api/expert           呼叫 LLM 專家（工具呼叫：檢查、查詞典）
  /api/tts              文字轉語音（edge-tts，免金鑰）→ mp3
  /api/romaji           羅馬字／拼音（中文、拼音）

金鑰從 .env 或環境變數讀取，只留在這台機器上，不會送到瀏覽器。
只聽本機（127.0.0.1）。

用法：
    python core/web/server.py
    python core/web/server.py --port 8770
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from core import spec as spec_mod  # noqa: E402
from core.checker import Checker  # noqa: E402
from core.lexicon import Lexicon, Reverser  # noqa: E402

WEB = Path(__file__).resolve().parent

from core.web.voices import BROWSER_LANG, TTS_VOICES  # noqa: E402

# 中文拼音表（mini-chinese/data 內的 pinyin.tsv 沒有移植過來，這裡用最小的表）
PINYIN = {
    '我': 'wǒ', '你': 'nǐ', '他': 'tā', '她': 'tā', '們': 'men', '這': 'zhè',
    '那': 'nà', '誰': 'shéi', '什': 'shén', '麼': 'me', '哪': 'nǎ', '怎': 'zěn',
    '樣': 'yàng', '自': 'zì', '己': 'jǐ', '每': 'měi',
    '的': 'de', '了': 'le', '過': 'guò', '嗎': 'ma', '呢': 'ne', '吧': 'ba',
    '不': 'bù', '沒': 'méi', '是': 'shì', '有': 'yǒu', '在': 'zài', '和': 'hé',
    '也': 'yě', '都': 'dōu', '很': 'hěn', '太': 'tài', '最': 'zuì', '更': 'gèng',
    '還': 'hái', '就': 'jiù', '再': 'zài', '會': 'huì', '能': 'néng', '要': 'yào',
    '可': 'kě', '以': 'yǐ', '得': 'de', '給': 'gěi', '對': 'duì', '從': 'cóng',
    '到': 'dào', '為': 'wèi', '因': 'yīn', '所': 'suǒ', '果': 'guǒ', '只': 'zhǐ',
    '起': 'qǐ', '比': 'bǐ',
    '一': 'yī', '百': 'bǎi', '千': 'qiān', '萬': 'wàn', '兩': 'liǎng', '幾': 'jǐ',
    '半': 'bàn', '第': 'dì', '個': 'gè', '些': 'xiē', '次': 'cì', '點': 'diǎn',
    '塊': 'kuài', '歲': 'suì', '數': 'shù', '量': 'liàng',
    '年': 'nián', '月': 'yuè', '日': 'rì', '天': 'tiān', '時': 'shí', '候': 'hòu',
    '今': 'jīn', '明': 'míng', '昨': 'zuó', '早': 'zǎo', '晚': 'wǎn', '午': 'wǔ',
    '現': 'xiàn', '分': 'fēn', '鐘': 'zhōng', '週': 'zhōu', '先': 'xiān',
    '上': 'shàng', '下': 'xià', '左': 'zuǒ', '右': 'yòu', '前': 'qián', '後': 'hòu',
    '裡': 'lǐ', '外': 'wài', '中': 'zhōng', '間': 'jiān', '東': 'dōng', '南': 'nán',
    '西': 'xī', '邊': 'biān', '方': 'fāng', '地': 'dì',
    '來': 'lái', '去': 'qù', '走': 'zǒu', '坐': 'zuò', '站': 'zhàn', '住': 'zhù',
    '回': 'huí', '進': 'jìn', '出': 'chū', '開': 'kāi', '關': 'guān', '拿': 'ná',
    '放': 'fàng', '用': 'yòng', '做': 'zuò', '作': 'zuò', '說': 'shuō', '話': 'huà',
    '聽': 'tīng', '看': 'kàn', '見': 'jiàn', '寫': 'xiě', '學': 'xué', '教': 'jiāo',
    '問': 'wèn', '叫': 'jiào', '想': 'xiǎng', '知': 'zhī', '道': 'dào', '懂': 'dǒng',
    '記': 'jì', '覺': 'jué', '喜': 'xǐ', '歡': 'huān', '愛': 'ài', '吃': 'chī',
    '喝': 'hē', '睡': 'shuì', '買': 'mǎi', '賣': 'mài', '找': 'zhǎo', '等': 'děng',
    '幫': 'bāng', '穿': 'chuān', '洗': 'xǐ', '玩': 'wán', '打': 'dǎ', '生': 'shēng',
    '完': 'wán', '動': 'dòng', '死': 'sǐ', '活': 'huó', '笑': 'xiào', '哭': 'kū',
    '怕': 'pà', '跳': 'tiào', '唱': 'chàng',
    '大': 'dà', '小': 'xiǎo', '多': 'duō', '少': 'shǎo', '長': 'cháng', '高': 'gāo',
    '老': 'lǎo', '好': 'hǎo', '壞': 'huài', '新': 'xīn', '快': 'kuài', '慢': 'màn',
    '冷': 'lěng', '熱': 'rè', '難': 'nán', '真': 'zhēn', '忙': 'máng', '病': 'bìng',
    '重': 'zhòng', '遠': 'yuǎn', '近': 'jìn', '白': 'bái', '黑': 'hēi', '紅': 'hóng',
    '色': 'sè', '樂': 'lè', '貴': 'guì', '綠': 'lǜ', '藍': 'lán', '甜': 'tián',
    '苦': 'kǔ', '圓': 'yuán',
    '人': 'rén', '男': 'nán', '女': 'nǚ', '子': 'zǐ', '孩': 'hái', '爸': 'bà',
    '媽': 'mā', '哥': 'gē', '姐': 'jiě', '弟': 'dì', '妹': 'mèi', '朋': 'péng',
    '友': 'yǒu', '師': 'shī', '家': 'jiā', '名': 'míng', '字': 'zì', '身': 'shēn',
    '體': 'tǐ', '頭': 'tóu', '手': 'shǒu', '眼': 'yǎn', '口': 'kǒu', '心': 'xīn',
    '水': 'shuǐ', '火': 'huǒ', '山': 'shān', '雨': 'yǔ', '氣': 'qì', '電': 'diàn',
    '車': 'chē', '路': 'lù', '門': 'mén', '房': 'fáng', '書': 'shū', '衣': 'yī',
    '服': 'fú', '錢': 'qián', '飯': 'fàn', '菜': 'cài', '茶': 'chá', '肉': 'ròu',
    '花': 'huā', '校': 'xiào', '醫': 'yī', '店': 'diàn', '國': 'guó', '文': 'wén',
    '語': 'yǔ', '事': 'shì', '題': 'tí', '工': 'gōng', '腦': 'nǎo', '機': 'jī',
    '飛': 'fēi', '意': 'yì', '思': 'sī', '聲': 'shēng', '音': 'yīn', '光': 'guāng',
    '味': 'wèi', '海': 'hǎi', '河': 'hé', '風': 'fēng', '雲': 'yún', '雪': 'xuě',
    '冰': 'bīng', '星': 'xīng', '石': 'shí', '土': 'tǔ', '樹': 'shù', '草': 'cǎo',
    '空': 'kōng', '金': 'jīn', '鳥': 'niǎo', '魚': 'yú', '蟲': 'chóng', '馬': 'mǎ',
    '牛': 'niú', '豬': 'zhū', '雞': 'jī', '蛋': 'dàn', '腳': 'jiǎo', '臉': 'liǎn',
    '牙': 'yá', '鼻': 'bí', '髮': 'fà', '血': 'xuè', '物': 'wù', '球': 'qiú',
    '紙': 'zhǐ', '刀': 'dāo', '木': 'mù', '城': 'chéng', '法': 'fǎ', '理': 'lǐ',
    '力': 'lì', '兒': 'ér', '歌': 'gē', '畫': 'huà', '詞': 'cí', '句': 'jù',
    '請': 'qǐng', '謝': 'xiè', '迎': 'yíng',
}


def pinyin_of(text: str) -> list[dict]:
    """把中文句子拆成 [{char, pinyin}]。"""
    out = []
    for ch in text:
        if '一' <= ch <= '鿿':
            out.append({'char': ch, 'pinyin': PINYIN.get(ch, '')})
    return out


# ── 載入語言 ─────────────────────────────────────────────────────────────────
_cache: dict[str, dict] = {}
_lock = threading.Lock()


def load(code: str) -> dict:
    with _lock:
        if code in _cache:
            return _cache[code]
        s = spec_mod.load(code)
        lex = Lexicon(s.dir / 'lexicon.tsv')
        info = {
            'spec': s,
            'checker': Checker(s),
            'lexicon': lex,
            'reverser': Reverser(lex, s),
        }
        _cache[code] = info
        return info


def load_prompt(code: str) -> str:
    s = spec_mod.load(code)
    p = s.dir / 'prompts' / 'system.md'
    if not p.exists():
        return ''
    text = p.read_text(encoding='utf-8')
    m = re.search(r'\n---\n(.*?)(?:\n---\n|$)', text, re.S)
    return m.group(1).strip() if m else text


# ── 反向翻譯成介面語言 ───────────────────────────────────────────────────────
UI_LANG_NAMES = {'en': 'English', 'fr': 'Français', 'ja': '日本語', 'ko': '한국어'}
_llm_cache: dict[str, object] = {}


def get_ui_llm():
    """翻譯用的 LLM（快取）。沒有金鑰時回 None。"""
    if 'llm' not in _llm_cache:
        try:
            from core.llm import LLM
            _llm_cache['llm'] = LLM(provider='nvidia', temperature=0.3, max_tokens=2048)
        except (Exception, SystemExit):
            _llm_cache['llm'] = None
    return _llm_cache['llm']


# ── 快速模式的系統提示（字表＋外來語規則，不用工具） ─────────────────────────
_fast_cache: dict[str, str] = {}


def fast_system(code: str) -> str:
    from core.web.build import fast_prompt
    if code in _fast_cache:
        return _fast_cache[code]
    out = fast_prompt(load(code)['spec'])
    _fast_cache[code] = out
    return out


# ── 伺服器 ───────────────────────────────────────────────────────────────────
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB), **kw)

    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        # 網頁與指令碼常常改，要求瀏覽器每次重新驗證，避免用舊快取
        self.send_header('Cache-Control', 'no-cache')
        # 讓靜態版／Cloudflare 版可以跨站呼叫（例如借用本機的 edge-tts）
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        n = int(self.headers.get('Content-Length', 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode('utf-8'))
        except Exception:      # noqa: BLE001
            return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/api/lang':
            out = []
            for d in spec_mod.all_langs():
                s = spec_mod.Spec(d)
                out.append({
                    'code': s.code, 'name': s.name, 'native': s.native,
                    'unit': s.unit_kind, 'script': s.script,
                    'words': len(s.words), 'core': len(s.core),
                    'tts': TTS_VOICES.get(s.code, {}),
                    'browserLang': BROWSER_LANG.get(s.code, 'en-US'),
                    'target': s.target_reader,
                })
            return self._json(out)
        if path == '/api/lexicon':
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code = q.get('lang', ['chinese'])[0]
            word = q.get('word', [''])[0].strip().lower()
            info = load(code)
            rows = [r for r in info['lexicon'].rows if r['原文'].lower() == word]
            if not rows:
                rows = [r for r in info['lexicon'].rows
                        if word and word in r['原文'].lower()][:20]
            return self._json(rows)
        if path == '/api/romaji':
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            text = q.get('text', [''])[0]
            return self._json(pinyin_of(text))
        return super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        data = self._read_json()
        if path == '/api/check':
            code = data.get('lang', 'chinese')
            text = data.get('text', '')
            info = load(code)
            errors = info['checker'].check(text)
            return self._json({
                'ok': not errors,
                'errors': [{'kind': e.kind, 'msg': e.msg, 'token': e.token}
                           for e in errors],
            })
        if path == '/api/translate':
            return self.do_translate(data)
        if path == '/api/tts':
            return self.do_tts(data)
        if path == '/api/expert':
            return self.do_expert(data)
        return self._json({'error': 'unknown endpoint'}, 404)

    # ── TTS ─────────────────────────────────────────────────────────────────
    def do_tts(self, data):
        text = data.get('text', '')
        code = data.get('lang', 'chinese')
        voice = data.get('voice', '')
        if not text.strip():
            return self._json({'error': 'no text'}, 400)
        try:
            import asyncio

            import edge_tts
        except ImportError:
            return self._json({'error': 'edge-tts 未安裝（pip install edge-tts）'}, 503)
        voices = TTS_VOICES.get(code, {})
        default = next(iter(voices.values()), [''])[0] if voices else ''
        voice = voice or default
        if not voice:
            return self._json({'error': '這個語言沒有設定語音'}, 400)

        async def make():
            comm = edge_tts.Communicate(text, voice)
            chunks = []
            async for c in comm.stream():
                if c['type'] == 'audio':
                    chunks.append(c['data'])
            return b''.join(chunks)

        try:
            audio = asyncio.run(make())
        except Exception as e:      # noqa: BLE001
            return self._json({'error': f'TTS 失敗：{e}'}, 500)
        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Content-Length', str(len(audio)))
        self.end_headers()
        self.wfile.write(audio)

    # ── 反向翻譯（SSE 串流）──────────────────────────────────────────────────
    def do_translate(self, data):
        """先送規則翻譯（base），介面語言非中文時串流 LLM 改寫（content）。"""
        code = data.get('lang', 'chinese')
        text = data.get('text', '')
        ui = data.get('ui', 'zh-Hant')
        info = load(code)
        base = info['reverser'].to_source(text)

        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

        def send(obj):
            self.wfile.write(b'data: ' + json.dumps(obj, ensure_ascii=False).encode('utf-8') + b'\n\n')
            self.wfile.flush()

        try:
            send({'type': 'base', 'text': base})
            name = UI_LANG_NAMES.get(ui)
            llm = get_ui_llm() if name else None
            if name and llm:
                prompt = ('下面是把受限語言逐詞對譯成的中文（詞序可能不自然、可能有括號註解）。\n'
                          f'請把它改寫成通順、自然的{name}，意思不要增減。\n'
                          '只輸出譯文，不要任何說明。\n\n' + base)
                try:
                    stream = llm.client.chat.completions.create(
                        model=llm.model,
                        messages=[{'role': 'system', 'content': '你是翻譯器。只輸出譯文本體。'},
                                  {'role': 'user', 'content': prompt}],
                        temperature=0.3, max_tokens=2048, stream=True)
                    for chunk in stream:
                        if not chunk.choices:
                            continue
                        if chunk.choices[0].delta.content:
                            send({'type': 'content', 'text': chunk.choices[0].delta.content})
                except Exception as e:      # noqa: BLE001
                    send({'type': 'error', 'text': f'LLM 失敗：{e}'})
            send({'type': 'done'})
        except (Exception, SystemExit):
            pass  # 客戶端已中斷

    # ── LLM 專家 ────────────────────────────────────────────────────────────
    def do_expert(self, data):
        code = data.get('lang', 'chinese')
        message = data.get('message', '')
        history = data.get('history', [])
        provider = data.get('provider', 'nvidia')
        fast = data.get('mode', 'strict') == 'fast'
        try:
            from core.llm import LLM
        except ImportError:
            return self._json({'error': 'openai 套件未安裝'}, 503)
        try:
            llm = LLM(provider=provider)
        except Exception as e:      # noqa: BLE001
            return self._json({'error': str(e)}, 503)
        info = load(code)
        system = fast_system(code) if fast else load_prompt(code)

        def tool_list():
            return [{
                'type': 'function',
                'function': {
                    'name': 'check_mini',
                    'description': f'檢查一段 {info["spec"].name} 文字是否合規則。'
                                   '回傳是否通過、以及哪裡不對。輸出任何受限語言之前都要先用它檢查。',
                    'parameters': {
                        'type': 'object',
                        'properties': {'text': {'type': 'string',
                                                'description': '要檢查的文字'}},
                        'required': ['text'],
                    },
                },
            }, {
                'type': 'function',
                'function': {
                    'name': 'lookup_word',
                    'description': f'查 {info["spec"].name} 詞典：一般的詞在受限語言怎麼說。'
                                   '回傳本詞／描述／外來語與說法。',
                    'parameters': {
                        'type': 'object',
                        'properties': {'words': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': '要查的詞',
                        }},
                        'required': ['words'],
                    },
                },
            }]

        def run_tool(name, args):
            if name == 'check_mini':
                errs = info['checker'].check(args.get('text', ''))
                if not errs:
                    return '✅ 通過：這段文字全部在詞表內。'
                return '❌ 有問題：\n' + '\n'.join(f'- {e}' for e in errs[:20])
            if name == 'lookup_word':
                lines = []
                for w in args.get('words', [])[:20]:
                    hit = next((r for r in info['lexicon'].rows
                                if r['原文'].lower() == w.lower()), None)
                    if hit:
                        note = f"（{hit['說明']}）" if hit['說明'] else ''
                        lines.append(f'{w} → {hit["受限說法"]}{note}　［{hit["方式"]}］')
                    else:
                        lines.append(f'{w} → 詞典裡沒有，請用描述或外來語。')
                return '\n'.join(lines) or '（沒有詞）'
            return '（不明的工具）'

        msgs = [{'role': 'system', 'content': system}]
        for h in history[-6:]:
            msgs.append({'role': h['role'], 'content': h['content']})
        msgs.append({'role': 'user', 'content': message})

        # SSE：思考與內容即時推送到瀏覽器
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

        def send(obj):
            self.wfile.write(b'data: ' + json.dumps(obj, ensure_ascii=False).encode('utf-8') + b'\n\n')
            self.wfile.flush()

        try:
            from openai import OpenAI
            kwargs = {'model': llm.model, 'messages': msgs,
                      'temperature': 0.7, 'max_tokens': 4096, 'stream': True}
            if not fast:
                kwargs['tools'] = tool_list()
                kwargs['tool_choice'] = 'auto'
            for _ in range(5):
                stream = llm.client.chat.completions.create(**kwargs)
                tool_calls = {}
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta
                    rc = getattr(delta, 'reasoning_content', None)
                    if rc:
                        send({'type': 'reasoning', 'text': rc})
                    if delta.content:
                        send({'type': 'content', 'text': delta.content})
                    for tc in (getattr(delta, 'tool_calls', None) or []):
                        slot = tool_calls.setdefault(tc.index, {'id': '', 'name': '', 'args': ''})
                        if tc.id:
                            slot['id'] = tc.id
                        if tc.function and tc.function.name:
                            slot['name'] = tc.function.name
                        if tc.function and tc.function.arguments:
                            slot['args'] += tc.function.arguments
                if not tool_calls:
                    break
                # 執行工具，把結果送回去再要一次回答
                msgs.append({'role': 'assistant', 'content': None, 'tool_calls': [
                    {'id': s['id'], 'type': 'function',
                     'function': {'name': s['name'], 'arguments': s['args']}}
                    for s in tool_calls.values()]})
                for s in tool_calls.values():
                    try:
                        args = json.loads(s['args'] or '{}')
                    except Exception:      # noqa: BLE001
                        args = {}
                    out = run_tool(s['name'], args)
                    send({'type': 'tool', 'name': s['name'], 'ok': '✅' in out})
                    msgs.append({'role': 'tool', 'tool_call_id': s['id'], 'content': out})
            send({'type': 'done'})
        except (Exception, SystemExit) as e:      # noqa: BLE001
            try:
                send({'type': 'error', 'text': f'LLM 失敗：{e}'})
            except Exception:      # noqa: BLE001
                pass  # 客戶端已中斷


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8770)
    ap.add_argument('--host', default='127.0.0.1')
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f'learn-talk 網頁：http://localhost:{a.port}/')
    print('（Ctrl+C 結束）')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\nbye')


if __name__ == '__main__':
    main()
