@echo off
REM EUC ESOL Analysis Runner
REM This batch file makes it easier to run the EUC analysis script

set PYTHON_PATH=.\.venv\Scripts\python.exe
set SCRIPT_PATH=scripts\euc_esol_count.py

echo EUC ESOL Analysis Tool
echo ======================

if "%1"=="help" (
    echo Usage:
    echo   run_euc_analysis.bat [category]
    echo.
    echo Available commands:
    echo   run_euc_analysis.bat         - Analyze 2026 ESOL devices
    echo   run_euc_analysis.bat 2024    - Analyze 2024 ESOL devices
    echo   run_euc_analysis.bat 2025    - Analyze 2025 ESOL devices  
    echo   run_euc_analysis.bat 2026    - Analyze 2026 ESOL devices
    echo   run_euc_analysis.bat help    - Show this help
    echo   run_euc_analysis.bat cats    - Show available categories
    goto :eof
)

if "%1"=="cats" (
    %PYTHON_PATH% %SCRIPT_PATH% --help-categories
    goto :eof
)

if "%1"=="2024" (
    %PYTHON_PATH% %SCRIPT_PATH% --category esol_2024 --output-path "data/processed/euc_2024_site_summary"
    goto :eof
)

if "%1"=="2025" (
    %PYTHON_PATH% %SCRIPT_PATH% --category esol_2025 --output-path "data/processed/euc_2025_site_summary"
    goto :eof
)

if "%1"=="2026" (
    %PYTHON_PATH% %SCRIPT_PATH% --category esol_2026 --output-path "data/processed/euc_2026_site_summary"
    goto :eof
)

if "%1"=="" (
    %PYTHON_PATH% %SCRIPT_PATH%
    goto :eof
)

echo Unknown option: %1
echo Use 'run_euc_analysis.bat help' for usage information
