# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 목표

아이언맨의 자비스처럼 똑똑한 AI 비서를 만드는 것이 목표입니다.

1. **반영 후 검증**: 요청사항을 구현한 뒤 반드시 검증 절차를 거치고 결과를 보고합니다.
2. **검증 결과 보고**: 구현 완료 시 테스트 결과를 명확히 알립니다.

### 중점사항

1. **육아 비서**: 수유·수면·기저귀·성장 기록, 예방접종 일정, 발달 이정표 등 육아 전반을 지원합니다.
2. **텔레그램 정확한 피드백**: 텔레그램으로 소통 시 모호한 답변 없이 정확하고 명확한 피드백을 제공합니다.

---

## Running the project

```bash
# Must use -X utf8 flag to handle Korean text correctly on Windows
python -X utf8 main.py

# Or use the provided batch script
run.bat
```

Ollama must be running locally (`http://localhost:11434`) with gemma3 pulled:
```bash
ollama pull gemma3
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed. Key variables:

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_MODEL` | `gemma3` | Ollama model name |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `ZABIS_NAME` | `자비스` | Assistant display name |
| `ZABIS_VOICE` | `ko-KR-SunHiNeural` | edge-tts voice ID |
| `TELEGRAM_TOKEN` | `` | Telegram bot token |
| `TELEGRAM_ALLOWED_IDS` | `` | 쉼표로 구분된 허용 유저 ID |

## Architecture

The request flow is: `main.py` → `core/brain.py` → `skills/system_commands.py` (checked first) or `ollama.Client.chat()` → `core/memory.py` (saved) → `voice/tts.py` (spoken).

**`core/brain.py`** — Central coordinator. `think(user_input)` checks for system commands first; if none match, it loads conversation history and calls Ollama. All strings are passed through `_clean()` to strip surrogates before JSON serialization (Windows encoding issue workaround).

**`core/memory.py`** — SQLite persistence (`memory.db`). Stores conversation messages and baby tracking data. `init_db()` creates all tables on first run. `load_history(limit=20)` returns the last 20 messages in chronological order for the Ollama context window.

**`skills/system_commands.py`** — Pattern-matched command executor. `parse_command()` returns `(True, result_msg)` if a command fires, `(False, "")` otherwise. Commands bypass LLM entirely. To add a new skill, append a new `if` branch.

**`skills/parenting.py`** — 육아 비서 핵심 모듈. 아기 프로필 등록, 수유·수면·기저귀 기록, 성장 추적, 한국 표준 예방접종 일정(11종), 월령별 발달 이정표를 제공합니다. SQLite 테이블 3개(`baby_profiles`, `baby_logs`, `growth_records`)를 사용합니다.

**`skills/telegram_bot.py`** — Telegram bot with inline keyboard for quick parenting actions. Supports `/start`, `/quick`, `/clear`, `/id` commands and callback query handling for button presses.

**`voice/tts.py`** — edge-tts (Microsoft, free) saves audio to a temp `.mp3`, plays via pygame, then deletes. Failures are silently swallowed so text output is never blocked.

**`voice/stt.py`** — Disabled by default (`VOICE_ENABLED = False`). To activate microphone input, set `VOICE_ENABLED = True` and ensure `pyaudio` and `SpeechRecognition` are installed. Uses Google STT with `ko-KR` locale.

## 육아 명령어

| 명령어 예시 | 기능 |
|---|---|
| `아기 등록 지민 2024-06-01` | 아기 프로필 등록 |
| `수유` / `분유 먹였어` / `수유 120ml` | 수유 기록 |
| `잠들었어` / `재웠어` | 수면 시작 기록 |
| `일어났어` / `기상` | 기상 기록 |
| `기저귀 갈았어` / `기저귀 갈았어 대변` | 기저귀 교체 기록 |
| `키 75cm 몸무게 9.5kg` | 성장 기록 |
| `마지막 수유` | 마지막 수유 경과 시간 확인 |
| `오늘 육아 요약` | 당일 수유·수면·기저귀 요약 |
| `예방접종 일정` | 월령 기준 접종 현황 |
| `발달 단계` | 현재 월령 발달 이정표 |

## Enabling voice input

1. Set `VOICE_ENABLED = True` in `voice/stt.py`
2. Install: `pip install SpeechRecognition pyaudio`
3. Wire `listen()` into the main loop in `main.py` (wake-word loop placeholder exists)

## Adding new skills

Add a new `if` branch to `skills/system_commands.py`. Pattern-matched commands execute instantly without LLM overhead — prefer this for deterministic actions (open app, control volume, parenting logs, etc.).

For parenting-specific features, add functions to `skills/parenting.py` and wire them into `system_commands.py`.

## 검증 절차 (Verification Protocol)

모든 구현 후 다음을 확인합니다:

1. `python -m py_compile <파일>` — 구문 오류 없음
2. 신규 함수 단위 테스트 실행
3. 패턴 명령어 매칭 테스트
4. 결과를 사용자에게 명확히 보고
