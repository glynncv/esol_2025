@echo off
setlocal enabledelayedexpansion

:: Simple ESOL Analysis Tool Batch Script
:: Usage: run_simple_analysis.bat [format] [output_file]

set PYTHON_EXE=python
set SCRIPT_PATH=scripts/esol-data-analysis-python.py
set DATA_FILE=data/raw/EUC_ESOL.xlsx

if "%~1"=="help" (
    echo Simple ESOL Analysis Tool
    echo =========================
    echo Usage:
    echo   run_simple_analysis.bat [format] [output_file]
    echo.
    echo Available commands:
    echo   run_simple_analysis.bat           - Full report to console
    echo   run_simple_analysis.bat report    - Save full report to file
    echo   run_simple_analysis.bat json      - JSON metrics to console
    echo   run_simple_analysis.bat jsave     - Save JSON metrics to file
    echo   run_simple_analysis.bat help      - Show this help
    echo.
    echo Examples:
    echo   run_simple_analysis.bat report my_report.md
    echo   run_simple_analysis.bat jsave metrics.json
    goto :end
)

if "%~1"=="report" (
    if "%~2"=="" (
        set OUTPUT_FILE=data/reports/esol_report_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.md
    ) else (
        set OUTPUT_FILE=%~2
    )
    echo Generating report and saving to !OUTPUT_FILE!...
    %PYTHON_EXE% %SCRIPT_PATH% --output "!OUTPUT_FILE!"
    echo Report saved to !OUTPUT_FILE!
    goto :end
)

if "%~1"=="json" (
    echo Generating JSON metrics...
    %PYTHON_EXE% %SCRIPT_PATH% --json
    goto :end
)

if "%~1"=="jsave" (
    if "%~2"=="" (
        set OUTPUT_FILE=data/reports/esol_metrics_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.json
    ) else (
        set OUTPUT_FILE=%~2
    )
    echo Generating JSON metrics and saving to !OUTPUT_FILE!...
    %PYTHON_EXE% %SCRIPT_PATH% --json --output "!OUTPUT_FILE!"
    echo Metrics saved to !OUTPUT_FILE!
    goto :end
)

:: Default - full report to console
echo Generating ESOL Analysis Report...
%PYTHON_EXE% %SCRIPT_PATH%

:end
