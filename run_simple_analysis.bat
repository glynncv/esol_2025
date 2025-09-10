@echo off
echo Simple ESOL Analysis Tool
echo =========================

if "%~1"=="" (
    echo Running all categories...
    python scripts/esol_count.py
) else if "%~1"=="help" (
    echo Usage: run_simple_analysis.bat [category]
    echo Categories: esol_2024, esol_2025, esol_2026
    echo Example: run_simple_analysis.bat esol_2024
) else (
    echo Running category: %~1
    python scripts/esol_count.py --category %~1
)

echo.
pause
