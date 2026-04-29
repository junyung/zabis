# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

ZABIS_NAME = os.getenv("ZABIS_NAME", "자비스")
ZABIS_VOICE = os.getenv("ZABIS_VOICE", "ko-KR-SunHiNeural")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

SYSTEM_PROMPT = f"""당신은 {ZABIS_NAME}입니다. 아이언맨의 자비스처럼 사용자를 돕는 AI 비서입니다.
- 항상 존댓말을 사용하되 간결하고 명확하게 답변합니다
- 필요할 때 "네, 알겠습니다", "처리하겠습니다" 등의 자비스다운 표현을 사용합니다
- 시스템 명령을 실행할 때는 실행 전 간략히 설명합니다
- 모르는 것은 모른다고 솔직하게 말합니다
"""
