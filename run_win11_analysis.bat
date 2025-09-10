@echo off
echo Windows 11 EUC Analysis Tool
echo =============================

if "%~1"=="help" (
    echo Usage: run_win11_analysis.bat [output_file]
    echo Examples: run_win11_analysis.bat [auto-save] or run_win11_analysis.bat custom.md
    goto end
)

if "%~1"=="" (
    echo Running Windows 11 EUC analysis...
    python scripts/win11_count.py
) else (
    echo Running Windows 11 EUC analysis...
    python scripts/win11_count.py --output %~1
)

:end
echo.
pause
