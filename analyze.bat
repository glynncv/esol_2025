@echo off
setlocal EnableDelayedExpansion

REM ========================================
REM EUC Analysis Tool Suite - Unified Launcher
REM ========================================
REM Get the subcommand (first argument)
set "SUBCMD=%~1"
if "%SUBCMD%"=="" set "SUBCMD=help"

REM Route to appropriate Python script
if /i "%SUBCMD%"=="dashboard" (
    echo Launching Interactive OKR Dashboard...
    python scripts/okr_dashboard.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="win11" (
    echo Running Windows 11 Analysis...
    python scripts/win11_count.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="esol" (
    echo Running ESOL Analysis...
    python scripts/esol_count.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="okr" (
    echo Running OKR Tracker...
    python scripts/okr_tracker.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="kiosk" (
    echo Running Kiosk Analysis...
    python scripts/kiosk_count.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="summary" (
    echo Running EUC Summary...
    python scripts/euc_summary.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="export" (
    echo Exporting Site Windows 11 Data...
    python scripts/export_site_win11_pending.py %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%SUBCMD%"=="help" (
    goto :help
)

echo Unknown command: %SUBCMD%
goto :help

:help
echo.
echo ========================================
echo EUC Analysis Tool Suite
echo ========================================
echo.
echo Usage: analyze.bat [command] [options]
echo.
echo Commands:
echo   dashboard               Launch interactive OKR dashboard
echo   win11 [options]         Windows 11 migration analysis
echo   esol [options]          ESOL replacement tracking
echo   okr [options]           OKR tracker reports
echo   kiosk [options]         Kiosk device analysis
echo   summary [options]       Data validation summary
echo   export [options]        Export pending Win11 devices by site
echo   help                    Show this help message
echo.
echo For detailed options, run:
echo   analyze.bat win11 --help
echo   analyze.bat esol --help
echo   analyze.bat okr --help
echo.
echo Quick Examples:
echo   analyze.bat dashboard
echo   analyze.bat win11 --site-table --burndown
echo   analyze.bat esol --site-table --burndown
echo   analyze.bat export --site Gillingham
echo.
echo ========================================
goto :end

:end
endlocal
if errorlevel 1 pause
exit /b 0
