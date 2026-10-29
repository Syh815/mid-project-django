@echo off
title Django Server (Port 8000)
cd /d "%~dp0"

echo ================================================================
echo   [啟動中] 國立大學  網路選課系統 (Port 8000)
echo   本地網址: http://127.0.0.1:8000/
echo   Cloudflare Tunnel 連接埠: 8000
echo   若要關閉請直接關閉此視窗，或雙擊 stop_server.bat
echo ================================================================
echo.

if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
) else (
    python manage.py runserver 0.0.0.0:8000
)

pause
