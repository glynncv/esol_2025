@echo off
echo ========================================
echo    OKR Tracker Generator
echo ========================================
echo.
echo Professional OKR tracking with comprehensive reporting
echo.

if "%1"=="help" goto help
if "%1"=="monthly" goto monthly
if "%1"=="compare" goto compare
if "%1"=="metrics" goto metrics
if "%1"=="" goto default

:default
echo Running basic OKR tracker...
echo Auto-saves to data/reports/ with timestamped filename
python scripts\okr_tracker.py
goto end

:monthly
echo Running monthly OKR report...
python scripts\okr_tracker.py --output "Monthly_OKR_Report_%date:~-4,4%%date:~-10,2%%date:~-7,2%.md"
goto end

:compare
if "%2"=="" (
    echo Usage: run_okr_tracker.bat compare [previous_metrics.json]
    echo Example: run_okr_tracker.bat compare july_metrics.json
    goto end
)
echo Running OKR tracker with comparison to %2...
python scripts\okr_tracker.py --previous-data %2 --save-metrics "metrics_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json"
goto end

:metrics
echo Saving current metrics for future comparison...
python scripts\okr_tracker.py --save-metrics "metrics_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json"
goto end

:help
echo.
echo Usage Options:
echo.
echo   run_okr_tracker.bat           - Basic OKR report (auto-saves to data/reports/)
echo   run_okr_tracker.bat monthly   - Monthly report with timestamped filename
echo   run_okr_tracker.bat compare [file] - Compare with previous metrics
echo   run_okr_tracker.bat metrics   - Save current metrics for future comparison
echo   run_okr_tracker.bat help      - Show this help message
echo.
echo Examples:
echo   run_okr_tracker.bat
echo   run_okr_tracker.bat monthly
echo   run_okr_tracker.bat compare july_metrics.json
echo   run_okr_tracker.bat metrics
echo.
echo All reports auto-save to data/reports/ unless custom output specified
echo.

:end
echo.
echo Press any key to exit...
pause >nul
