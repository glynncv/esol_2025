@echo off
echo ESOL Burndown Analysis Tool
echo ===========================
echo Running ESOL burndown analysis...
python scripts/esol_count.py --burndown %*
echo.
pause