@echo off
echo ESOL Analysis Tool
echo ==================

if "%~1"=="help" goto help
if "%~1"=="full" goto full
if "%~1"=="esol_2024" goto esol_2024
if "%~1"=="esol_2025" goto esol_2025
if "%~1"=="esol_2026" goto esol_2026
echo Running ESOL analysis...
python scripts/esol_count.py %*
goto end

:full
echo Running ESOL full analysis (site + burndown)...
python scripts/esol_count.py --site-table --burndown
goto end

:esol_2024
echo Running ESOL 2024 analysis...
python scripts/esol_count.py --category esol_2024
goto end

:esol_2025
echo Running ESOL 2025 analysis...
python scripts/esol_count.py --category esol_2025
goto end

:esol_2026
echo Running ESOL 2026 analysis...
python scripts/esol_count.py --category esol_2026
goto end

:help
echo Usage: run_esol_analysis.bat [mode] [options]
echo Modes:
echo   [no args]           - Basic ESOL analysis (all categories)
echo   full               - Full analysis (site + burndown data)
echo   esol_2024          - ESOL 2024 analysis only
echo   esol_2025          - ESOL 2025 analysis only  
echo   esol_2026          - ESOL 2026 analysis only
echo   --site-table       - Include site-level breakdown only
echo   --burndown         - Include burndown analysis only
echo   --site-table --burndown - Both site and burndown analysis
echo   --output filename  - Custom output file
echo Examples:
echo   run_esol_analysis.bat
echo   run_esol_analysis.bat full
echo   run_esol_analysis.bat esol_2024
echo   run_esol_analysis.bat --site-table
echo   run_esol_analysis.bat --burndown
echo   run_esol_analysis.bat --site-table --burndown

:end
echo.
pause