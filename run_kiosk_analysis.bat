@echo off
echo Kiosk EUC Analysis Tool
echo =======================

if "%~1"=="help" (
    echo Usage: run_kiosk_analysis.bat [output_file]
    echo Examples: run_kiosk_analysis.bat [auto-save] or run_kiosk_analysis.bat custom.md
    goto end
)

if "%~1"=="" (
    echo Running Kiosk EUC analysis...
    python scripts/kiosk_count.py
) else (
    echo Running Kiosk EUC analysis...
    python scripts/kiosk_count.py --output %~1
)

:end
echo.
pause