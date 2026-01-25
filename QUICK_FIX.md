# Quick Fix Guide - "File Not Found" Error

## Problem

You're seeing this error:

```
python: can't open file 'C:\Windows\System32\pdf_organizer_gui.py': 
[Errno 2] No such file or directory
```

## Why This Happens

The batch file is running from the wrong directory (System32 instead of where your files are).

## ✅ SOLUTION - Use START_HERE.bat

**The easiest fix:** Use the new `START_HERE.bat` file instead of `run_gui.bat`

1. **Double-click `START_HERE.bat`** in the folder containing all the PDF Organizer files
2. It will automatically use the correct directory

This new launcher:

- ✓ Shows you exactly where it's running from
- ✓ Checks if all files are present
- ✓ Offers to install dependencies if missing
- ✓ Provides detailed error messages

---

## Alternative Solutions

### Option 1: Run from Command Prompt (Recommended)

1. **Open File Explorer** and navigate to the folder with your PDF Organizer files
2. **Type `cmd`** in the address bar and press Enter
3. **Run:** `python pdf_organizer_gui.py`

This guarantees you're in the right directory.

### Option 2: Fix run_gui.bat

The updated `run_gui.bat` should work now. If you downloaded it again, try:

1. Right-click `run_gui.bat`
2. Select **"Edit"**
3. Make sure the first command after the comments is: `cd /d "%~dp0"`
4. Save and close
5. Double-click to run

### Option 3: Create a Shortcut (Best for Desktop)

1. **Right-click** on `pdf_organizer_gui.py`
2. Select **"Create shortcut"**
3. **Right-click** the shortcut → **Properties**
4. In **"Target"** field, change it to:

   ```
   python "C:\full\path\to\your\folder\pdf_organizer_gui.py"
   ```

   (Replace with your actual path)
5. In **"Start in"** field, put:

   ```
   C:\full\path\to\your\folder
   ```

6. Click **OK**
7. Move the shortcut to your Desktop

### Option 4: Use PowerShell Installer

If nothing else works, use the PowerShell installer:

1. **Right-click** `install_simple.ps1`
2. Select **"Run with PowerShell"**
3. It will set everything up correctly

---

## Where Should Your Files Be?

All these files must be in the **SAME FOLDER**:

- ✓ pdf_organizer_gui.py
- ✓ pdf_organizer.py  
- ✓ requirements.txt
- ✓ setup.py
- ✓ START_HERE.bat (or run_gui.bat)

**Good locations:**

- `C:\Users\YourName\Documents\PDF-Organizer\`
- `C:\PDF-Organizer\`
- `D:\Tools\PDF-Organizer\`

**Bad locations:**

- ❌ Desktop (can work but not ideal)
- ❌ Downloads (files might get mixed up)
- ❌ System folders (C:\Windows, C:\Program Files)

---

## Step-by-Step: Starting Fresh

If you want to start clean:

1. **Create a new folder:**

   ```
   C:\PDF-Organizer
   ```

2. **Move ALL these files** into that folder:
   - pdf_organizer_gui.py
   - pdf_organizer.py
   - requirements.txt
   - setup.py
   - START_HERE.bat
   - install_simple.ps1
   - (all other .py, .bat, .ps1, .txt, .md files)

3. **Open Command Prompt in that folder:**
   - Navigate to `C:\PDF-Organizer` in File Explorer
   - Type `cmd` in the address bar
   - Press Enter

4. **Install dependencies:**

   ```
   python -m pip install -r requirements.txt
   ```

5. **Run the setup:**

   ```
   python setup.py
   ```

6. **Launch the GUI:**

   ```
   python pdf_organizer_gui.py
   ```

Or just double-click `START_HERE.bat`!

---

## Still Not Working?

### Check Python Installation

Open Command Prompt anywhere and run:

```
python --version
```

If you see `'python' is not recognized`, then:

1. Python is not installed, OR
2. Python is not in your PATH

**Fix:**

- Reinstall Python from <https://www.python.org/>
- ✅ CHECK "Add Python to PATH" during installation

### Check Dependencies

```
python -m pip list
```

Look for:

- google-generativeai
- pdfplumber
- pypdf

If missing, install:

```
python -m pip install google-generativeai pdfplumber pypdf
```

---

## Quick Test

To verify everything works:

```
cd C:\PDF-Organizer
python -c "import google.generativeai; import pdfplumber; import pypdf; print('All good!')"
```

If you see "All good!" - you're ready to run the GUI!

```
python pdf_organizer_gui.py
```

---

## Need More Help?

1. Read `INSTALLATION.md` for detailed setup instructions
2. Check error messages - they usually tell you what's wrong
3. Make sure you're running from the correct folder
4. Verify Python is installed and in PATH
