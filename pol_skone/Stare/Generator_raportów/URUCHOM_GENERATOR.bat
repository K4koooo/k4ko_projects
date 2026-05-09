@echo off
title Generator Raportow Pol-Skone
echo ==================================================
echo ROZPOCZYNAM GENEROWANIE RAPORTU...
echo ==================================================
python "%~dp0run_full_report.py"
echo.
echo ==================================================
echo PROCES ZAKONCZONY. MOZESZ ZAMKNAC TO OKNO.
echo ==================================================
pause
