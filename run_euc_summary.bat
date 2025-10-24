@echo off
echo EUC Summary Validation Tool
echo ============================

if "%~1"=="help" goto help
echo Running EUC summary validation...
python scripts/euc_summary.py %*
goto end

:help
echo Usage: run_euc_summary.bat [options]
echo Options:
echo   [no args]           - Basic validation summary
echo   --output filename   - Custom output file
echo   --format text or json - Output format (default: text)
echo   --quiet            - Quiet mode for automation
echo Examples:
echo   run_euc_summary.bat
echo   run_euc_summary.bat --output summary.txt
echo   run_euc_summary.bat --format json --output metrics.json

:end
echo.
pause