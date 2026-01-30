@echo off
REM PDF Organizer - Watch Mode Launcher
REM This will run continuously and auto-organize PDFs as they arrive

echo ===================================================================
echo   PDF Organizer - WATCH MODE
echo ===================================================================
echo.
echo This mode will monitor your Downloads folder and automatically
echo organize new PDFs as they arrive.
echo.
echo Press Ctrl+C to stop watching
echo.
echo ===================================================================
echo.

python watch_organizer.py

pause
