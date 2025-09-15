@echo off
echo EUC Summary Validation Tool
echo ============================

if "%~1"=="help" (
    echo Usage: run_euc_summary.bat [options]
    echo Examples: 
    echo   run_euc_summary.bat [basic validation]
    echo   run_euc_summary.bat --output summary.txt
    echo   run_euc_summary.bat --format json --output metrics.json
    goto end
)

if "%~1"=="" (
    echo Running EUC summary validation...
    python scripts/euc_summary.py
) else (
    echo Running EUC summary validation...
    python scripts/euc_summary.py %*
)

:end
echo.
pause
