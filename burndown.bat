@echo off
setlocal EnableDelayedExpansion

REM ========================================
REM Quick Burndown Analysis Launcher
REM ========================================
REM Usage:
REM   burndown.bat esol [options]    ESOL burndown analysis
REM   burndown.bat win11 [options]   Windows 11 burndown analysis
REM
REM Examples:
REM   burndown.bat esol --site-table
REM   burndown.bat win11 --site-table
REM   burndown.bat esol --category esol_2024
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

set "MODE=%~1"

if "%MODE%"=="" goto :help
if /i "%MODE%"=="help" goto :help
if /i "%MODE%"=="--help" goto :help

if /i "%MODE%"=="esol" (
    echo Running ESOL Burndown Analysis...
    python scripts/esol_count.py --burndown %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%MODE%"=="win11" (
    echo Running Windows 11 Burndown Analysis...
    python scripts/win11_count.py --burndown %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

echo Unknown mode: %MODE%
goto :help

:help
echo.
echo ========================================
echo Quick Burndown Analysis Launcher
echo ========================================
echo.
echo Usage: burndown.bat [esol^|win11] [options]
echo.
echo Modes:
echo   esol               ESOL replacement burndown
echo   win11              Windows 11 migration burndown
echo.
echo Common Options:
echo   --site-table       Include site-level breakdown
echo   --category [type]  Filter ESOL category (esol only)
echo   --output [file]    Custom output file
echo.
echo Examples:
echo   burndown.bat esol --site-table
echo   burndown.bat win11 --site-table
echo   burndown.bat esol --category esol_2024
echo.
echo ========================================
goto :end

:end
endlocal
if errorlevel 1 pause
exit /b 0
