@echo off
REM Quick OKR Status Check - Daily Use
REM This batch file provides a quick status overview

echo OKR Quick Status Check
echo =====================

.\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format quick

echo.
echo Press any key to exit...
pause >nul
