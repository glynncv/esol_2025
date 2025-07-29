@echo off
REM Executive Summary Generator
REM Generates weekly executive summary reports

set TIMESTAMP=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo Generating Executive Summary Report
echo ==================================

.\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format executive --output "data\reports\Executive_Summary_%TIMESTAMP%.md"

echo.
echo Report saved to: data\reports\Executive_Summary_%TIMESTAMP%.md
echo.
echo Press any key to exit...
pause >nul
