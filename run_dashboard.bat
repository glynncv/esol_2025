@echo off
echo OKR Dashboard Launcher
echo ======================

if "%~1"=="help" goto help
echo Starting OKR Dashboard...
echo ========================
python scripts/okr_dashboard.py
goto end

:help
echo Usage: run_dashboard.bat
echo Description: Interactive dashboard for OKR analysis
echo Features:
echo   - Quick Status Check (Daily)
echo   - Executive Summary
echo   - Full OKR Tracker
echo   - Site Analysis (ESOL)
echo   - Windows 11 Site Analysis
echo   - Save Executive Report
echo Example:
echo   run_dashboard.bat

:end
echo.
echo Dashboard closed.
pause