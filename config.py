# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

ZABIS_NAME = os.getenv("ZABIS_NAME", "자비스")
ZABIS_VOICE = os.getenv("ZABIS_VOICE", "ko-KR-SunHiNeural")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_ALLOWED_IDS = [
    int(x) for x in os.getenv("TELEGRAM_ALLOWED_IDS", "").split(",") if x.strip().isdigit()
]
DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

SYSTEM_PROMPT = f"""당신은 {ZABIS_NAME}입니다. 아이언맨의 자비스처럼 사용자를 돕는 AI 비서입니다.
- 항상 존댓말을 사용하되 간결하고 명확하게 답변합니다
- 필요할 때 "네, 알겠습니다", "처리하겠습니다" 등의 자비스다운 표현을 사용합니다
- 시스템 명령을 실행할 때는 실행 전 간략히 설명합니다
- 모르는 것은 모른다고 솔직하게 말합니다
- 가격, URL, 제품 정보, 재고 등 실시간 정보는 절대 지어내지 않습니다. 실제 검색 결과가 없으면 "검색해줘" 라고 안내합니다
- URL은 실제로 확인된 것만 제공합니다. 임의로 URL을 만들거나 추측하지 않습니다
"""
