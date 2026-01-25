@echo off
REM PDF Organizer - Alternative Launcher
REM This launcher is more explicit about the working directory

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo ================================================
echo   AI-Powered PDF Organizer
echo ================================================
echo.
echo Batch file location: %~f0
echo Working directory: %SCRIPT_DIR%
echo.

REM Change to the script directory
cd /d "%SCRIPT_DIR%"
echo Changed to: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo During installation, make sure to check:
    echo [X] Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM List files in current directory
echo Files in current directory:
dir /b *.py 2>nul
if errorlevel 1 (
    echo [WARNING] No Python files found in this directory
    echo.
)
echo.

REM Check if GUI file exists
if not exist "pdf_organizer_gui.py" (
    echo [ERROR] pdf_organizer_gui.py not found!
    echo.
    echo Please ensure all these files are in the same folder:
    echo - pdf_organizer_gui.py
    echo - pdf_organizer.py
    echo - requirements.txt
    echo - run_gui.bat (this file)
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [OK] pdf_organizer_gui.py found
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import google.generativeai" 2>nul
if errorlevel 1 (
    echo [WARNING] Dependencies may not be installed
    echo.
    echo Do you want to install them now? (Y/N)
    set /p INSTALL_DEPS=
    if /i "!INSTALL_DEPS!"=="Y" (
        echo.
        echo Installing dependencies...
        python -m pip install -r requirements.txt
        echo.
    )
)

echo.
echo ================================================
echo   Launching PDF Organizer GUI...
echo ================================================
echo.

REM Run the GUI with full path
python "%SCRIPT_DIR%\pdf_organizer_gui.py"

if errorlevel 1 (
    echo.
    echo ================================================
    echo   Error Running Application
    echo ================================================
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure dependencies are installed:
    echo    python -m pip install -r requirements.txt
    echo.
    echo 2. Try running directly:
    echo    python pdf_organizer_gui.py
    echo.
    echo 3. Check the error message above for details
    echo.
    pause
) else (
    echo.
    echo [OK] Application closed successfully
)

endlocal
