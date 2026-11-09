"""語音設定：伺服器 TTS（edge-tts）與瀏覽器語音的語言標籤。

server.py 用 TTS_VOICES 提供 /api/tts；
build.py 把兩個表都寫進 data.js，前端用 BROWSER_LANG 挑瀏覽器語音。
"""
from __future__ import annotations

# edge-tts 語音（伺服器唸，mp3）：語言 → 地區 → 語音清單
TTS_VOICES = {
    'chinese': {'zh-CN': ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural',
                          'zh-TW-HsiaoChenNeural', 'zh-TW-YunJheNeural']},
    'english': {'en-US': ['en-US-AriaNeural', 'en-US-GuyNeural',
                          'en-GB-SoniaNeural']},
    'french': {'fr-FR': ['fr-FR-DeniseNeural', 'fr-FR-HenriNeural']},
    'japanese': {'ja-JP': ['ja-JP-NanamiNeural', 'ja-JP-KeitaNeural']},
    'korean': {'ko-KR': ['ko-KR-SunHiNeural', 'ko-KR-InJoonNeural']},
}

# 瀏覽器 SpeechSynthesis 用的語言標籤
BROWSER_LANG = {
    'chinese': 'zh-CN', 'english': 'en-US', 'french': 'fr-FR',
    'japanese': 'ja-JP', 'korean': 'ko-KR',
}
