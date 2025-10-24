@echo off
echo Windows 11 EUC Analysis Tool
echo =============================

if "%~1"=="help" goto help
if "%~1"=="full" goto full
echo Running Windows 11 EUC analysis...
python scripts/win11_count.py %*
goto end

:full
echo Running Windows 11 full analysis (site + burndown)...
python scripts/win11_count.py --site-table --burndown
goto end

:help
echo Usage: run_win11_analysis.bat [mode] [options]
echo Modes:
echo   [no args]           - Basic Windows 11 analysis (auto-save)
echo   full               - Full analysis (site + burndown data)
echo   --site-table       - Include site-level breakdown only
echo   --burndown         - Include burndown analysis only
echo   --site-table --burndown - Both site and burndown analysis
echo   --output filename  - Custom output file
echo Examples:
echo   run_win11_analysis.bat
echo   run_win11_analysis.bat full
echo   run_win11_analysis.bat --site-table
echo   run_win11_analysis.bat --burndown
echo   run_win11_analysis.bat --site-table --burndown
echo   run_win11_analysis.bat --output custom_report.md

:end
echo.
pause