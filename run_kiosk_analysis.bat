@echo off
echo Kiosk EUC Analysis Tool
echo =======================

if "%~1"=="help" goto help
echo Running Kiosk EUC analysis...
python scripts/kiosk_count.py %*
goto end

:help
echo Usage: run_kiosk_analysis.bat [options]
echo Options:
echo   [no args]           - Basic kiosk analysis (auto-save)
echo   --output filename   - Custom output file
echo Examples:
echo   run_kiosk_analysis.bat
echo   run_kiosk_analysis.bat --output custom_kiosk_report.md

:end
echo.
pause