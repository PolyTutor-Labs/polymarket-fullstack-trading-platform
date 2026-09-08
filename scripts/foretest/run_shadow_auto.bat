@echo off
setlocal
REM Hands-free shadow foretest: snapshot any live 2-day Elon market near its halfway mark.
REM Scheduled twice daily so the ~14h "40-70% elapsed" window is never missed.
REM scripts/foretest -> repository root
cd /d "%~dp0..\.."
set PYTHONUTF8=1
if not exist "research\experiments\foretest" mkdir "research\experiments\foretest"
python -W ignore "scripts\foretest\shadow_foretest.py" --auto >> "research\experiments\foretest\auto_run.log" 2>&1
echo --- run finished %DATE% %TIME% --- >> "research\experiments\foretest\auto_run.log"
