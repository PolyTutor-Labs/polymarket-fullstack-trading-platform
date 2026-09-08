@echo off
setlocal
title PolyBot Services
echo Starting PolyBot background services...

:: scripts/windows -> repository root
cd /d "%~dp0..\.."
set "ROOT=%CD%"
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

:: Kill any existing instances
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq PolyBot*" >nul 2>&1

:: Start API server hidden
start /B /MIN "PolyBot API" cmd /c "cd /d "%ROOT%" && python -m uvicorn api.main:app --port 8010 > logs\api.log 2>&1"

:: Wait for API
timeout /t 3 /nobreak >nul

:: Start frontend hidden (dev mode — no build required)
start /B /MIN "PolyBot Frontend" cmd /c "cd /d "%ROOT%\web" && npx next dev --port 3010 > "%ROOT%\logs\frontend.log" 2>&1"

echo PolyBot services started in background.
echo Logs: logs\api.log, logs\frontend.log
echo To stop: taskkill /F /IM python.exe /FI "WINDOWTITLE eq PolyBot*"
