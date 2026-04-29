@echo off
cd /d %~dp0
title ZABIS - 텔레그램 봇
echo.
echo  ===========================
echo   Z.A.B.I.S Telegram Bot
echo  ===========================
echo.
python -X utf8 main.py --telegram
pause
