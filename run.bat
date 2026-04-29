@echo off
cd /d %~dp0
if "%1"=="telegram" (
    python -X utf8 main.py --telegram
) else if "%1"=="text" (
    python -X utf8 main.py --text
) else (
    python -X utf8 main.py
)
