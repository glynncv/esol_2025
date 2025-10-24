@echo off
echo ESOL Burndown Analysis Tool
echo ============================

if "%~1"=="help" goto help
if "%~1"=="full" goto full
echo Running ESOL burndown analysis...
python scripts/esol_count.py --burndown %*
goto end

:full
echo Running ESOL full burndown analysis (site + burndown)...
python scripts/esol_count.py --burndown --site-table
goto end

:help
echo Usage: run_esol_burndown.bat [mode] [options]
echo Modes:
echo   [no args]           - Burndown analysis for all ESOL categories
echo   full               - Full burndown analysis (site + burndown data)
echo   --site-table       - Include site-level breakdown
echo   --category [cat]   - Specific ESOL category (e.g., esol_2024)
echo   --output filename  - Custom output file
echo Examples:
echo   run_esol_burndown.bat
echo   run_esol_burndown.bat full
echo   run_esol_burndown.bat --site-table
echo   run_esol_burndown.bat --category esol_2024
echo   run_esol_burndown.bat --output esol_burndown_report.md

:end
echo.
pause