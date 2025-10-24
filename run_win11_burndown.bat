@echo off
echo Windows 11 Burndown Analysis Tool
echo ===================================

if "%~1"=="help" goto help
if "%~1"=="full" goto full
echo Running Windows 11 burndown analysis...
python scripts/win11_count.py --burndown %*
goto end

:full
echo Running Windows 11 full burndown analysis (site + burndown)...
python scripts/win11_count.py --burndown --site-table
goto end

:help
echo Usage: run_win11_burndown.bat [mode] [options]
echo Modes:
echo   [no args]           - Burndown analysis only
echo   full               - Full burndown analysis (site + burndown data)
echo   --site-table       - Include site-level breakdown
echo   --output filename  - Custom output file
echo Examples:
echo   run_win11_burndown.bat
echo   run_win11_burndown.bat full
echo   run_win11_burndown.bat --site-table
echo   run_win11_burndown.bat --output burndown_report.md

:end
echo.
pause