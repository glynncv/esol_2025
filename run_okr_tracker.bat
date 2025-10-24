@echo off
echo OKR Tracker Generator
echo =====================

if "%~1"=="help" goto help
if "%~1"=="monthly" goto monthly
if "%~1"=="compare" goto compare
if "%~1"=="metrics" goto metrics

echo Running basic OKR tracker...
echo Auto-saves to data/reports/ with timestamped filename
python scripts/okr_tracker.py %*
goto end

:monthly
echo Running monthly OKR report...
python scripts/okr_tracker.py --output "Monthly_OKR_Report_%date:~-4,4%%date:~-10,2%%date:~-7,2%.md"
goto end

:compare
if "%~2"=="" (
    echo Usage: run_okr_tracker.bat compare [previous_metrics.json]
    echo Example: run_okr_tracker.bat compare july_metrics.json
    goto end
)
echo Running OKR tracker with comparison to %2...
python scripts/okr_tracker.py --previous-data %2 --save-metrics "metrics_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json"
goto end

:metrics
echo Saving current metrics for future comparison...
python scripts/okr_tracker.py --save-metrics "metrics_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json"
goto end

:help
echo Usage: run_okr_tracker.bat [mode] [options]
echo Modes:
echo   [no args]           - Basic OKR report (auto-save)
echo   monthly            - Monthly report with timestamped filename
echo   compare [file]     - Compare with previous metrics
echo   metrics            - Save current metrics for future comparison
echo Options:
echo   --output filename  - Custom output file
echo Examples:
echo   run_okr_tracker.bat
echo   run_okr_tracker.bat monthly
echo   run_okr_tracker.bat compare july_metrics.json
echo   run_okr_tracker.bat metrics

:end
echo.
pause