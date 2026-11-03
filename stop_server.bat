@echo off
title Stop Django Server (Port 8000)
cd /d "%~dp0"

if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" stop_server.py
) else (
    python stop_server.py
)

echo.
pause
