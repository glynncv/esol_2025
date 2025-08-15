@echo off
setlocal enabledelayedexpansion

:: Simple ESOL Analysis Tool Batch Script
:: Usage: run_simple_analysis.bat [category]

set PYTHON_EXE=python
set SCRIPT_PATH=scripts/euc_count.py

if "%~1"=="help" (
    echo Simple ESOL Analysis Tool
    echo =========================
    echo Usage:
    echo   run_simple_analysis.bat [category]
    echo.
    echo Available categories:
    echo   run_simple_analysis.bat           - All categories (default)
    echo   run_simple_analysis.bat esol_2024 - ESOL 2024 devices only
    echo   run_simple_analysis.bat esol_2025 - ESOL 2025 devices only
    echo   run_simple_analysis.bat esol_2026 - Non-ESOL devices only
    echo   run_simple_analysis.bat help      - Show this help
    echo.
    echo Examples:
    echo   run_simple_analysis.bat esol_2024
    echo   run_simple_analysis.bat esol_2025
    goto :end
)

if "%~1"=="" (
    echo Generating ESOL Analysis Report (all categories)...
    %PYTHON_EXE% %SCRIPT_PATH%
    goto :end
)

if "%~1"=="esol_2024" (
    echo Generating ESOL 2024 Analysis...
    %PYTHON_EXE% %SCRIPT_PATH% --category esol_2024
    goto :end
)

if "%~1"=="esol_2025" (
    echo Generating ESOL 2025 Analysis...
    %PYTHON_EXE% %SCRIPT_PATH% --category esol_2025
    goto :end
)

if "%~1"=="esol_2026" (
    echo Generating Non-ESOL Analysis...
    %PYTHON_EXE% %SCRIPT_PATH% --category esol_2026
    goto :end
)

echo Invalid category. Use 'help' for available options.

:end
echo.
pause
