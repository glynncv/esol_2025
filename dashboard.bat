@echo off
REM ========================================
REM Quick OKR Dashboard Launcher
REM ========================================
REM Usage:
REM   dashboard.bat           Launch interactive dashboard
REM   dashboard.bat --help    Show help options
REM ========================================

REM Change to script directory (project root) to ensure correct paths
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

python scripts/okr_dashboard.py %*
if errorlevel 1 pause
