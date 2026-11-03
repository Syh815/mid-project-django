@echo off
title Django Server (Port 8000)
cd /d "%~dp0"

if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" start_server.py
) else (
    python start_server.py
)

pause
