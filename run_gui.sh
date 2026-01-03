#!/bin/bash
# PDF Organizer Launcher for macOS/Linux
# Run this file to launch the GUI version

# Change to the directory where this script is located
cd "$(dirname "$0")"

echo "================================================"
echo "  AI-Powered PDF Organizer"
echo "================================================"
echo ""
echo "Running from: $(pwd)"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if the GUI file exists
if [ ! -f "pdf_organizer_gui.py" ]; then
    echo "ERROR: pdf_organizer_gui.py not found in current directory"
    echo "Please make sure all files are in the same folder"
    echo "Current directory: $(pwd)"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Starting PDF Organizer GUI..."
echo ""

# Run the GUI
python3 pdf_organizer_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "================================================"
    echo "  An error occurred"
    echo "================================================"
    echo ""
    echo "If this is your first time running the tool:"
    echo "1. Make sure all files are in the same folder"
    echo "2. Run: python3 setup.py"
    echo "3. Make sure dependencies are installed: pip3 install -r requirements.txt"
    echo ""
    read -p "Press Enter to exit..."
fi
