@echo off
echo Windows 11 Burndown Analysis Tool
echo ==================================

if "%~1"=="help" (
    echo Usage: run_win11_burndown.bat [options]
    echo Options:
    echo   [no args]           - Burndown analysis only
    echo   --site-table       - Include site-level breakdown
    echo   --output filename  - Custom output file
    echo Examples:
    echo   run_win11_burndown.bat
    echo   run_win11_burndown.bat --site-table
    echo   run_win11_burndown.bat --output burndown_report.md
    goto end
)

if "%~1"=="" (
    echo Running Windows 11 burndown analysis...
    python scripts/win11_count.py --burndown
    goto end
)

echo Running Windows 11 burndown analysis...
python scripts/win11_count.py --burndown %*

:end
echo.
pause
