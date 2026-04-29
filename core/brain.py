# -*- coding: utf-8 -*-
import ollama
from config import OLLAMA_MODEL, OLLAMA_HOST, ZABIS_NAME, SYSTEM_PROMPT


def _clean(text: str) -> str:
    return text.encode('utf-8', errors='ignore').decode('utf-8')
from core.memory import load_history, save_message
from skills.system_commands import parse_command

client = ollama.Client(host=OLLAMA_HOST)


def think(user_input: str) -> str:
    # 시스템 명령 우선 처리
    executed, cmd_result = parse_command(user_input)
    if executed:
        save_message("user", user_input)
        save_message("assistant", cmd_result)
        return cmd_result

    history = load_history()
    messages = [{"role": "system", "content": _clean(SYSTEM_PROMPT)}] + \
               [{"role": m["role"], "content": _clean(m["content"])} for m in history] + \
               [{"role": "user", "content": _clean(user_input)}]

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=messages,
    )

    reply = response.message.content
    save_message("user", user_input)
    save_message("assistant", reply)
    return reply
