@echo off
REM Complete OKR Analysis Helper
REM Provides menu for different analysis types

echo OKR Analysis Tool
echo =================
echo.
echo Select analysis type:
echo 1. Quick Status Check (recommended for daily use)
echo 2. Executive Summary 
echo 3. Full OKR Tracker
echo 4. Site Analysis
echo 5. JSON Export
echo 6. Save Executive Summary to File
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Running Quick Status Check...
    .\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format quick
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running Executive Summary...
    .\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format executive
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Running Full OKR Tracker...
    .\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format full
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Running Site Analysis...
    .\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format site --top-sites 10
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Running JSON Export...
    .\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format json
    goto end
)

if "%choice%"=="6" (
    set TIMESTAMP=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
    set TIMESTAMP=%TIMESTAMP: =0%
    echo.
    echo Saving Executive Summary to file...
    .\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format executive --output "data\reports\Executive_Summary_%TIMESTAMP%.md"
    echo Report saved to: data\reports\Executive_Summary_%TIMESTAMP%.md
    goto end
)

if "%choice%"=="7" (
    echo Goodbye!
    exit /b
)

echo Invalid choice. Please try again.

:end
echo.
echo Press any key to exit...
pause >nul
