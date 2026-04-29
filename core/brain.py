# -*- coding: utf-8 -*-
import ollama
from config import OLLAMA_MODEL, OLLAMA_HOST, SYSTEM_PROMPT
from core.memory import load_history, save_message
from skills.system_commands import parse_command

client = ollama.Client(host=OLLAMA_HOST)


def _clean(text: str) -> str:
    return text.encode('utf-8', errors='ignore').decode('utf-8')


def think(user_input: str) -> str:
    # 패턴 명령 먼저 처리 (파일/브라우저/앱 등)
    executed, tool_result = parse_command(user_input)

    history = load_history()

    if executed:
        # URL·파일 내용 등 정확도가 중요한 결과는 LLM을 거치지 않고 직접 반환
        save_message("user", user_input)
        save_message("assistant", tool_result)
        return tool_result
    else:
        messages = (
            [{"role": "system", "content": _clean(SYSTEM_PROMPT)}]
            + [{"role": m["role"], "content": _clean(m["content"])} for m in history]
            + [{"role": "user", "content": _clean(user_input)}]
        )
        response = client.chat(model=OLLAMA_MODEL, messages=messages)
        reply = response.message.content or ""

    save_message("user", user_input)
    save_message("assistant", reply)
    return reply
