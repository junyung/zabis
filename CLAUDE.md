# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Architecture

The request flow is: `main.py` → `core/brain.py` → `skills/system_commands.py` (checked first) or `ollama.Client.chat()` → `core/memory.py` (saved) → `voice/tts.py` (spoken).

**`core/brain.py`** — Central coordinator. `think(user_input)` checks for system commands first; if none match, it loads conversation history and calls Ollama. All strings are passed through `_clean()` to strip surrogates before JSON serialization (Windows encoding issue workaround).

**`core/memory.py`** — SQLite persistence (`memory.db`). Stores all messages with role/content/timestamp. `load_history(limit=20)` returns the last 20 messages in chronological order for the Ollama context window.

**`skills/system_commands.py`** — Pattern-matched command executor. `parse_command()` returns `(True, result_msg)` if a command fires, `(False, "")` otherwise. Commands bypass LLM entirely. To add a new skill, append to `COMMAND_PATTERNS` or add a new `if` branch.

**`voice/tts.py`** — edge-tts (Microsoft, free) saves audio to a temp `.mp3`, plays via pygame, then deletes. Failures are silently swallowed so text output is never blocked.

**`voice/stt.py`** — Disabled by default (`VOICE_ENABLED = False`). To activate microphone input, set `VOICE_ENABLED = True` and ensure `pyaudio` and `SpeechRecognition` are installed. Uses Google STT with `ko-KR` locale.

## Enabling voice input

1. Set `VOICE_ENABLED = True` in `voice/stt.py`
2. Install: `pip install SpeechRecognition pyaudio`
3. Wire `listen()` into the main loop in `main.py` (wake-word loop placeholder exists)

## Adding new skills

Add to `skills/system_commands.py`. Pattern-matched commands execute instantly without LLM overhead — prefer this for deterministic actions (open app, control volume, etc.).
