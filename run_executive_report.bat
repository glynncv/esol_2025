@echo off
REM Executive Summary Generator
REM Generates weekly executive summary reports

REM Create a clean timestamp without invalid characters
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "TIMESTAMP=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

echo Generating Executive Summary Report
echo ==================================

.\.venv\Scripts\python.exe scripts\separated_esol_analyzer.py --format executive --output "data\reports\Executive_Summary_%TIMESTAMP%.md"

echo.
echo Report saved to: data\reports\Executive_Summary_%TIMESTAMP%.md
echo.
echo Press any key to exit...
pause >nul
