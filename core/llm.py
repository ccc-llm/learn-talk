"""LLM 統一介面：NVIDIA（GLM 5.3 Flash）與 MiniMax（M3.1 Flash）。

用法：
    from core.llm import LLM
    llm = LLM(provider='nvidia')
    print(llm.chat('用一句話說明什麼是程式設計'))
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / '.env'


def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_env()

PROVIDERS = {
    'nvidia': {
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'model': 'z-ai/glm-5.3-flash',
        'key': 'NVIDIA_API_KEY',
    },
    'minimax': {
        'base_url': 'https://api.minimax.chat/v1',
        'model': 'minimax-m3.1-flash',
        'key': 'MINIMAX_API_KEY',
    },
}


class LLM:
    def __init__(self, provider: str = 'nvidia', model: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 8192, system: str = ''):
        if provider not in PROVIDERS:
            raise SystemExit(f'未知的 provider：{provider}（可用：{", ".join(PROVIDERS)}）')
        self.provider = provider
        cfg = PROVIDERS[provider]
        self.base_url = cfg['base_url']
        self.model = model or cfg['model']
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system = system
        key = os.environ.get(cfg['key'])
        if not key:
            raise SystemExit(f'找不到 {cfg["key"]}（可以放進 {ENV_FILE} 或環境變數）')
        from openai import OpenAI
        self.client = OpenAI(base_url=self.base_url, api_key=key)
        self.usage = {'calls': 0, 'prompt_tokens': 0, 'completion_tokens': 0}

    # ── 單次呼叫 ────────────────────────────────────────────────────────────
    def chat(self, prompt: str, system: str | None = None, retries: int = 3,
             max_tokens: int | None = None) -> str:
        msgs = []
        sys = system if system is not None else self.system
        if sys:
            msgs.append({'role': 'system', 'content': sys})
        msgs.append({'role': 'user', 'content': prompt})
        last = None
        for attempt in range(retries):
            try:
                extra = {}
                if self.provider == 'minimax':
                    # MiniMax 會把推理內容放在 content 裡，用 reasoning_split 分開；
                    # 推理吃掉的 token 太多時 content 會變空，所以關掉深度推理。
                    extra['reasoning_split'] = True
                    extra['reasoning_effort'] = 'low'
                r = self.client.chat.completions.create(
                    model=self.model,
                    messages=msgs,
                    temperature=self.temperature,
                    max_tokens=max_tokens or (16384 if self.provider == 'minimax' else self.max_tokens),
                    extra_body=extra or None,
                )
                msg = r.choices[0].message
                text = (msg.content or '').strip()
                if not text and getattr(msg, 'reasoning_content', None):
                    text = msg.reasoning_content.strip()
                u = r.usage
                if u:
                    self.usage['calls'] += 1
                    self.usage['prompt_tokens'] += getattr(u, 'prompt_tokens', 0) or 0
                    self.usage['completion_tokens'] += getattr(u, 'completion_tokens', 0) or 0
                return text
            except Exception as e:      # noqa: BLE001
                last = e
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f'LLM 呼叫失敗：{last}')

    def chat_json(self, prompt: str, system: str | None = None, retries: int = 3):
        """要求回傳 JSON（容忍 ```json 包裝與前後雜訊）。"""
        raw = self.chat(prompt, system=system, retries=retries)
        s = raw.strip()
        if s.startswith('```'):
            s = s.split('```')[1]
            if s.startswith('json'):
                s = s[4:]
        s = s.strip()
        start = s.find('[')
        end = s.rfind(']')
        if start >= 0 and end > start:
            s = s[start:end + 1]
        else:
            start = s.find('{')
            end = s.rfind('}')
            s = s[start:end + 1]
        return json.loads(s)

    def chat_lines(self, prompt: str, system: str | None = None, retries: int = 3,
                   max_tokens: int | None = None) -> list[str]:
        """要求一行一條的清單。"""
        raw = self.chat(prompt, system=system, retries=retries, max_tokens=max_tokens)
        out = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            line = line.lstrip('-*0123456789. ').strip()
            line = line.strip('「」"')
            if line:
                out.append(line)
        return out

    # ── 批次 ────────────────────────────────────────────────────────────────
    def batch(self, items, prompt_fn, system=None, workers: int = 3):
        """對每個 item 呼叫 prompt_fn(item)。回傳結果清單（保持順序）。"""
        from concurrent.futures import ThreadPoolExecutor
        results = [None] * len(items)

        def work(i_item):
            i, item = i_item
            try:
                return i, prompt_fn(item)
            except Exception as e:      # noqa: BLE001
                return i, f'ERROR: {e}'

        with ThreadPoolExecutor(max_workers=workers) as ex:
            for i, r in ex.map(work, list(enumerate(items))):
                results[i] = r
        return results

    def stats(self) -> str:
        u = self.usage
        return (f"呼叫 {u['calls']} 次｜prompt {u['prompt_tokens']} tokens｜"
                f"completion {u['completion_tokens']} tokens")
