@echo off
REM PDF Organizer Launcher for Windows
REM Double-click this file to run the GUI version

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ================================================
echo   AI-Powered PDF Organizer
echo ================================================
echo.
echo Running from: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

REM Check if the GUI file exists
if not exist "pdf_organizer_gui.py" (
    echo ERROR: pdf_organizer_gui.py not found in current directory
    echo Please make sure all files are in the same folder
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo Starting PDF Organizer GUI...
echo.

REM Run the GUI
python pdf_organizer_gui.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo   An error occurred
    echo ================================================
    echo.
    echo If this is your first time running the tool:
    echo 1. Make sure all files are in the same folder
    echo 2. Run: python setup.py
    echo 3. Make sure dependencies are installed: pip install -r requirements.txt
    echo.
    pause
)
