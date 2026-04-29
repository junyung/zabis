import asyncio
import os
import tempfile
import edge_tts
from config import ZABIS_VOICE

_pygame_ready = False


def _ensure_pygame():
    global _pygame_ready
    if not _pygame_ready:
        import pygame
        pygame.mixer.init()
        _pygame_ready = True


async def _speak_async(text: str):
    communicate = edge_tts.Communicate(text, ZABIS_VOICE)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    await communicate.save(tmp_path)

    import pygame
    _ensure_pygame()
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    os.unlink(tmp_path)


def speak(text: str):
    """텍스트를 음성으로 출력. 마이크 없는 환경에서는 스킵."""
    try:
        asyncio.run(_speak_async(text))
    except Exception:
        pass  # TTS 실패해도 텍스트 출력은 계속
