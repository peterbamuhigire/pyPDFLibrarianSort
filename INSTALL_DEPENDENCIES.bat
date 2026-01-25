@echo off
REM PDF Organizer - Install Dependencies
REM Run this ONCE to install all required Python packages

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo ================================================================
echo   PDF Organizer - Dependency Installer
echo ================================================================
echo.
echo This will install all required Python packages.
echo This only needs to be done once.
echo.
echo Installing to: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python first:
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Download Python 3.8 or higher
    echo 3. Run installer and CHECK "Add Python to PATH"
    echo 4. Then run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [INFO] Creating requirements.txt...
    (
        echo google-generativeai^>=0.7.2
        echo pdfplumber^>=0.11.0
        echo pypdf^>=3.17.0
        echo pdf2image^>=1.17.0
        echo pytesseract^>=0.3.10
    ) > requirements.txt
    echo [OK] requirements.txt created
    echo.
)

echo ================================================================
echo   Installing Packages
echo ================================================================
echo.
echo This may take a few minutes. Please wait...
echo.

REM Upgrade pip first
echo [1/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Pip upgrade had issues, continuing anyway...
) else (
    echo [OK] Pip upgraded
)
echo.

REM Install each package individually with progress
echo [2/6] Installing google-generativeai (Gemini AI library)...
python -m pip install "google-generativeai>=0.7.2" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install google-generativeai
    set INSTALL_FAILED=1
) else (
    echo [OK] google-generativeai installed
)
echo.

echo [3/6] Installing pdfplumber (PDF text extraction)...
python -m pip install "pdfplumber>=0.11.0" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install pdfplumber
    set INSTALL_FAILED=1
) else (
    echo [OK] pdfplumber installed
)
echo.

echo [4/6] Installing pypdf (PDF manipulation)...
python -m pip install "pypdf>=3.17.0" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install pypdf
    set INSTALL_FAILED=1
) else (
    echo [OK] pypdf installed
)
echo.

echo [5/6] Installing pdf2image (PDF to image conversion)...
python -m pip install "pdf2image>=1.17.0" --quiet
if errorlevel 1 (
    echo [WARNING] pdf2image failed (optional package)
) else (
    echo [OK] pdf2image installed
)
echo.

echo [6/6] Installing pytesseract (OCR support)...
python -m pip install "pytesseract>=0.3.10" --quiet
if errorlevel 1 (
    echo [WARNING] pytesseract failed (optional package)
) else (
    echo [OK] pytesseract installed
)
echo.

REM Verify installations
echo ================================================================
echo   Verifying Installation
echo ================================================================
echo.

set ALL_OK=1

echo Checking required packages...
echo.

python -c "import google.generativeai" 2>nul
if errorlevel 1 (
    echo [FAIL] google-generativeai - NOT installed
    set ALL_OK=0
) else (
    echo [PASS] google-generativeai - Installed
)

python -c "import pdfplumber" 2>nul
if errorlevel 1 (
    echo [FAIL] pdfplumber - NOT installed
    set ALL_OK=0
) else (
    echo [PASS] pdfplumber - Installed
)

python -c "import pypdf" 2>nul
if errorlevel 1 (
    echo [FAIL] pypdf - NOT installed
    set ALL_OK=0
) else (
    echo [PASS] pypdf - Installed
)

python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [FAIL] tkinter - NOT installed (comes with Python)
    set ALL_OK=0
) else (
    echo [PASS] tkinter - Installed
)

echo.

if "%ALL_OK%"=="1" (
    echo ================================================================
    echo   SUCCESS! All dependencies installed
    echo ================================================================
    echo.
    echo You're ready to use the PDF Organizer!
    echo.
    echo Next steps:
    echo 1. Get your Gemini API key from: https://aistudio.google.com/app/apikey
    echo 2. Double-click START_HERE.bat to launch the tool
    echo    OR run: python pdf_organizer_gui.py
    echo.
    echo Have fun organizing your PDFs! 📚
    echo.
) else (
    echo ================================================================
    echo   WARNING: Some packages failed to install
    echo ================================================================
    echo.
    echo Try these solutions:
    echo.
    echo 1. Run as Administrator:
    echo    Right-click this file and "Run as administrator"
    echo.
    echo 2. Install manually:
    echo    pip install google-generativeai pdfplumber pypdf
    echo.
    echo 3. Use virtual environment:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
)

echo.
pause

endlocal
