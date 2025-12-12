@echo off
setlocal EnableDelayedExpansion

REM ========================================
REM Generate All Possible File Outputs
REM ========================================
REM This script runs all analysis scripts with all possible
REM command-line option combinations to generate every file output.

REM Change to script directory (project root) to ensure correct paths
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

echo.
echo ========================================
echo GENERATE ALL OUTPUTS
echo ========================================
echo Start Time: %date% %time%
echo.

REM Create output directories if they don't exist
if not exist "data\reports" mkdir "data\reports"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\history" mkdir "data\history"

set ERROR_COUNT=0
set TOTAL_COMMANDS=0

REM ========================================
REM 1. WINDOWS 11 ANALYSIS
REM ========================================
echo.
echo ========================================
echo SECTION 1: Windows 11 Analysis
echo ========================================
echo Running comprehensive version with all options (generates count, site-table, and burndown outputs)

set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\win11_count.py --site-table --burndown
echo --------------------------------------------------------------------------------
python scripts\win11_count.py --site-table --burndown
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ========================================
REM 2. ESOL ANALYSIS
REM ========================================
echo.
echo ========================================
echo SECTION 2: ESOL Analysis
echo ========================================
echo Running comprehensive versions with all options for each category
echo (generates count, site-table, and burndown outputs for each)

REM ESOL All Categories - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\esol_count.py --category all --site-table --burndown
echo --------------------------------------------------------------------------------
python scripts\esol_count.py --category all --site-table --burndown
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ESOL 2024 - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\esol_count.py --category esol_2024 --site-table --burndown
echo --------------------------------------------------------------------------------
python scripts\esol_count.py --category esol_2024 --site-table --burndown
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ESOL 2025 - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\esol_count.py --category esol_2025 --site-table --burndown
echo --------------------------------------------------------------------------------
python scripts\esol_count.py --category esol_2025 --site-table --burndown
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ESOL 2026 - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\esol_count.py --category esol_2026 --site-table --burndown
echo --------------------------------------------------------------------------------
python scripts\esol_count.py --category esol_2026 --site-table --burndown
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ========================================
REM 3. OKR TRACKER
REM ========================================
echo.
echo ========================================
echo SECTION 3: OKR Tracker
echo ========================================
echo Running comprehensive versions with Excel export for each level
echo (generates markdown report and Excel file for each)

REM OKR All Levels - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\okr_tracker.py --level all --excel
echo --------------------------------------------------------------------------------
python scripts\okr_tracker.py --level all --excel
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM OKR Country Level - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\okr_tracker.py --level country --excel
echo --------------------------------------------------------------------------------
python scripts\okr_tracker.py --level country --excel
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM OKR SDM Level - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\okr_tracker.py --level sdm --excel
echo --------------------------------------------------------------------------------
python scripts\okr_tracker.py --level sdm --excel
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM OKR Site Level - comprehensive version only
set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\okr_tracker.py --level site --excel
echo --------------------------------------------------------------------------------
python scripts\okr_tracker.py --level site --excel
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ========================================
REM 4. KIOSK ANALYSIS
REM ========================================
echo.
echo ========================================
echo SECTION 4: Kiosk Analysis
echo ========================================

set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\kiosk_count.py
echo --------------------------------------------------------------------------------
python scripts\kiosk_count.py
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ========================================
REM 5. EUC SUMMARY
REM ========================================
echo.
echo ========================================
echo SECTION 5: EUC Summary
echo ========================================

set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\euc_summary.py --format text
echo --------------------------------------------------------------------------------
python scripts\euc_summary.py --format text
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

set /a TOTAL_COMMANDS+=1
echo.
echo [%TOTAL_COMMANDS%] Running: python scripts\euc_summary.py --format json
echo --------------------------------------------------------------------------------
python scripts\euc_summary.py --format json
if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)

REM ========================================
REM 6. SITE-SPECIFIC EXPORTS
REM ========================================
echo.
echo ========================================
echo SECTION 6: Site-Specific Exports
echo ========================================
echo Discovering available sites...

REM Get site list using helper script
python scripts\get_all_sites.py > sites_list.txt 2>nul
if exist sites_list.txt (
    set SITE_COUNT=0
    for /f "usebackq delims=" %%s in ("sites_list.txt") do (
        set /a SITE_COUNT+=1
        set SITE_NAME=%%s
        echo   Exporting for: !SITE_NAME!
        set /a TOTAL_COMMANDS+=1
        echo.
        echo [%TOTAL_COMMANDS%] Running: python scripts\export_site_win11_pending.py --site "!SITE_NAME!"
        echo --------------------------------------------------------------------------------
        python scripts\export_site_win11_pending.py --site "!SITE_NAME!"
        if errorlevel 1 (set /a ERROR_COUNT+=1) else (echo [OK] Command completed successfully)
    )
    if !SITE_COUNT! EQU 0 (
        echo [WARNING] No sites found in data file
        set /a ERROR_COUNT+=1
    ) else (
        echo Exported data for !SITE_COUNT! sites
    )
    del sites_list.txt
) else (
    echo [WARNING] Could not discover sites, skipping site-specific exports
    set /a ERROR_COUNT+=1
)

REM ========================================
REM SUMMARY
REM ========================================
echo.
echo ========================================
echo GENERATION COMPLETE
echo ========================================
echo End Time: %date% %time%
echo.
echo Total commands executed: %TOTAL_COMMANDS%
if %ERROR_COUNT% GTR 0 (
    echo Warnings/Errors: %ERROR_COUNT%
) else (
    echo All commands completed successfully!
)
echo.
echo Output locations:
echo   - Markdown reports: data\reports\
echo   - CSV/JSON data: data\processed\
echo   - Excel files: data\reports\
echo   - Historical snapshots: data\history\
echo.
pause
exit /b 0
