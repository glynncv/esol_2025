@echo off
REM ========================================
REM Quick OKR Dashboard Launcher
REM ========================================
REM Usage:
REM   dashboard.bat           Launch interactive dashboard
REM   dashboard.bat --help    Show help options
REM ========================================
python scripts/okr_dashboard.py %*
if errorlevel 1 pause
