@echo off
setlocal enabledelayedexpansion

:: OKR Analysis Tool Batch Script
:: Usage: run_okr_analysis.bat [format] [additional_args]

set PYTHON_EXE=C:/Users/cglynn/myPython/esol_2025/.venv/Scripts/python.exe
set SCRIPT_PATH=scripts/separated_esol_analyzer.py
set DATA_FILE=data/raw/EUC_ESOL.xlsx

if "%~1"=="help" (
    echo OKR Analysis Tool
    echo =================
    echo Usage:
    echo   run_okr_analysis.bat [format]
    echo.
    echo Available formats:
    echo   run_okr_analysis.bat           - Full OKR report to console
    echo   run_okr_analysis.bat full      - Full OKR report to console  
    echo   run_okr_analysis.bat quick     - Quick status check
    echo   run_okr_analysis.bat exec      - Executive summary to console
    echo   run_okr_analysis.bat site      - Site analysis to console
    echo   run_okr_analysis.bat json      - JSON metrics to console
    echo   run_okr_analysis.bat save      - Save full report to file
    echo   run_okr_analysis.bat weekly    - Generate timestamped weekly update
    echo   run_okr_analysis.bat help      - Show this help
    goto :end
)

if "%~1"=="exec" (
    echo Generating Executive Summary...
    %PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE% --format executive
    goto :end
)

if "%~1"=="quick" (
    echo Quick Status Check...
    %PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE% --format quick
    goto :end
)

if "%~1"=="site" (
    echo Generating Site Analysis...
    %PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE% --format site --top-sites 5
    goto :end
)

if "%~1"=="json" (
    echo Generating JSON Metrics...
    %PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE% --format json
    goto :end
)

if "%~1"=="save" (
    echo Saving Full OKR Report...
    %PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE% --output data/reports/full_okr_report.md
    echo Report saved to data/reports/full_okr_report.md
    goto :end
)

if "%~1"=="weekly" (
    :: Generate timestamped weekly update
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE=%%c%%a%%b
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a%%b
    set TIMESTAMP=%DATE%_%TIME%
    set TIMESTAMP=%TIMESTAMP: =0%
    
    echo Generating Weekly Update with timestamp %TIMESTAMP%...
    %PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE% --format executive --output data/reports/Technical_Debt_OKR_Update_%TIMESTAMP%.md
    echo Weekly update saved to data/reports/Technical_Debt_OKR_Update_%TIMESTAMP%.md
    goto :end
)

:: Default - full report to console
if "%~1"=="full" (
    echo Generating Full OKR Report...
) else if "%~1"=="" (
    echo Generating Full OKR Report...
) else (
    echo Unknown format: %~1
    echo Use 'run_okr_analysis.bat help' for available options
    goto :end
)

%PYTHON_EXE% %SCRIPT_PATH% %DATA_FILE%

:end
