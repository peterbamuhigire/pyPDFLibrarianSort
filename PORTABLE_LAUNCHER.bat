@echo off
REM PDF Organizer - Portable Launcher
REM Works from USB stick or any location
REM Automatically uses current user's Downloads folder

setlocal enabledelayedexpansion

REM Change to script directory (where this batch file is)
cd /d "%~dp0"

echo ================================================================
echo   AI-Powered PDF Organizer - Portable Edition
echo ================================================================
echo.
echo Running from: %CD%
echo.

REM Auto-detect current user's Downloads folder
set "DOWNLOADS_FOLDER=%USERPROFILE%\Downloads"

echo Auto-detected Settings:
echo   User: %USERNAME%
echo   Downloads: %DOWNLOADS_FOLDER%
echo.

REM Check if Downloads folder exists
if not exist "%DOWNLOADS_FOLDER%" (
    echo [WARNING] Downloads folder not found at: %DOWNLOADS_FOLDER%
    echo.
    set /p DOWNLOADS_FOLDER="Enter Downloads folder path: "
)

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

REM Check if the GUI file exists
if not exist "pdf_organizer_gui.py" (
    echo [ERROR] pdf_organizer_gui.py not found!
    echo.
    echo Please ensure all PDF Organizer files are in:
    echo %CD%
    echo.
    pause
    exit /b 1
)

echo [OK] pdf_organizer_gui.py found
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import anthropic" 2>nul
if errorlevel 1 (
    echo [WARNING] Dependencies are NOT installed
    echo.
    echo You need to install the required Python packages first.
    echo.
    set /p INSTALL_NOW="Install dependencies now? (Y/N): "
    if /i "!INSTALL_NOW!"=="Y" (
        echo.
        echo ================================================
        echo   Installing Dependencies...
        echo ================================================
        echo.
        
        REM Check if requirements.txt exists, create if not
        if not exist "requirements.txt" (
            echo Creating requirements.txt...
            (
                echo anthropic^>=0.39.0
                echo pdfplumber^>=0.11.0
                echo pypdf^>=3.17.0
                echo pdf2image^>=1.17.0
                echo pytesseract^>=0.3.10
            ) > requirements.txt
        )
        
        echo Upgrading pip...
        python -m pip install --upgrade pip --quiet
        echo.
        echo Installing packages...
        python -m pip install anthropic pdfplumber pypdf --quiet
        echo.
        echo [OK] Installation complete!
        echo.
        pause
    ) else (
        echo.
        echo [INFO] Please install dependencies before running.
        echo Run: INSTALL_DEPENDENCIES.bat
        echo   Or: pip install anthropic pdfplumber pypdf
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies installed
)
echo.

echo ================================================================
echo   Launching PDF Organizer...
echo ================================================================
echo.
echo Configuration:
echo   Downloads Folder: %DOWNLOADS_FOLDER%
echo   Tool Location: %CD%
echo.
echo The tool will open with your Downloads folder pre-configured.
echo You only need to set your Ebooks folder and API key.
echo.
pause

REM Launch the GUI
python pdf_organizer_gui.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo   Error Running Application
    echo ================================================
    echo.
    echo Troubleshooting:
    echo 1. Make sure dependencies are installed
    echo 2. Check the error message above
    echo 3. Try running: python pdf_organizer_gui.py
    echo.
    pause
)

endlocal
