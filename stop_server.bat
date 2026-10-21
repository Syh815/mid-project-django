@echo off
chcp 65001 >nul
title 關閉 Django Server (Port 8000)
cd /d "%~dp0"

if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" stop_server.py
) else (
    python stop_server.py
)

echo.
echo 請按任意鍵關閉此視窗...
pause >nul
