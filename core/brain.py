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
        # 도구 실행 결과를 LLM에 전달해 자연스러운 답변 생성
        messages = (
            [{"role": "system", "content": _clean(SYSTEM_PROMPT)}]
            + [{"role": m["role"], "content": _clean(m["content"])} for m in history]
            + [{"role": "user", "content": _clean(user_input)}]
            + [{"role": "assistant", "content": f"[실행 결과]\n{_clean(tool_result)}"}]
            + [{"role": "user", "content": "위 실행 결과를 바탕으로 간결하게 답변해줘."}]
        )
        response = client.chat(model=OLLAMA_MODEL, messages=messages)
        reply = response.message.content or tool_result
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
