# Getting Started - PDF Organizer

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
**Double-click:** `INSTALL_DEPENDENCIES.bat`

This will install all required Python packages. It only needs to be done once.

### Step 2: Get API Key
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Create an API key
4. Copy the key (starts with `sk-ant-`)

### Step 3: Run the Tool
**Double-click:** `START_HERE.bat`

Enter your API key in the GUI and start organizing!

---

## 📋 What You Need

- ✅ Windows (7, 10, or 11)
- ✅ Python 3.8 or higher ([Download here](https://www.python.org/downloads/))
- ✅ Anthropic API key (free to get, pay per use)
- ✅ Internet connection (for AI processing)

---

## 💰 Cost

- **Free to install** - No upfront cost
- **Pay per use** - Approximately $0.01-0.03 per PDF
- **Example:** Organizing 100 PDFs ≈ $1-3

You only pay when the AI categorizes PDFs. Preview mode (dry run) is free.

---

## 📁 File Overview

**Essential Files:**
- `START_HERE.bat` - Launch the tool (GUI)
- `INSTALL_DEPENDENCIES.bat` - One-time setup
- `pdf_organizer_gui.py` - Main application (GUI version)
- `pdf_organizer.py` - Core logic (CLI version)
- `requirements.txt` - List of dependencies

**Documentation:**
- `README.md` - Full user guide
- `INSTALLATION.md` - Detailed setup instructions
- `QUICK_FIX.md` - Troubleshooting common errors
- `GET_STARTED.md` - This file

**Installers:**
- `install.ps1` - PowerShell auto-installer (admin)
- `install_simple.ps1` - PowerShell installer (no admin)
- `setup.py` - Python setup wizard

**Other:**
- `run_gui.bat` / `run_gui.sh` - Alternative launchers

---

## ❓ Common Issues

### "Python is not recognized"
**Problem:** Python not installed or not in PATH

**Fix:**
1. Install Python from https://www.python.org/
2. ✅ CHECK "Add Python to PATH" during installation
3. Restart your computer
4. Try again

### "ModuleNotFoundError: No module named 'pdfplumber'"
**Problem:** Dependencies not installed

**Fix:** Run `INSTALL_DEPENDENCIES.bat`

### "API key not found"
**Problem:** No API key configured

**Fix:** Get a key from https://console.anthropic.com/ and enter it in the GUI

### Tool is running from wrong folder
**Problem:** Batch file can't find Python files

**Fix:**
1. Make sure ALL files are in the SAME folder
2. Use `START_HERE.bat` instead of `run_gui.bat`
3. Or run from Command Prompt in the correct folder

---

## 🎯 First Time Workflow

1. **Install Python** (if not already installed)
2. **Run INSTALL_DEPENDENCIES.bat** 
3. **Get Anthropic API key**
4. **Run START_HERE.bat**
5. **Configure in GUI:**
   - Set Downloads folder
   - Set Ebooks folder (e.g., F:\ebooks)
   - Enter API key
6. **Check "Dry Run"** to preview first
7. **Click "Organize PDFs"**
8. **Review suggestions**
9. **Uncheck "Dry Run" and run again** to actually move files

---

## 📞 Need Help?

1. **Read QUICK_FIX.md** - Solutions for common errors
2. **Read INSTALLATION.md** - Detailed setup guide
3. **Check error messages** - They usually explain what's wrong
4. **Try the manual steps** in INSTALLATION.md

---

## ✅ Checklist Before First Run

- [ ] Python is installed (`python --version` works in Command Prompt)
- [ ] Dependencies are installed (ran INSTALL_DEPENDENCIES.bat)
- [ ] I have an Anthropic API key
- [ ] All files are in the same folder
- [ ] I know my Downloads folder path
- [ ] I know my Ebooks folder path (or will create it)

If all checked, you're ready! Run `START_HERE.bat` 🎉

---

## 🎓 How It Works

1. **Scans** your Downloads folder for PDFs
2. **Extracts** text from the first few pages
3. **Analyzes** your existing ebooks folder structure
4. **Uses AI** (Claude) to categorize based on content
5. **Suggests** categories with confidence levels
6. **Moves** files to organized subdirectories

The AI reads the content and metadata to understand what each PDF is about, then suggests the most appropriate category based on your existing organization.

---

## 🔒 Privacy

- PDF content is sent to Anthropic's API for analysis
- Only text is sent, not the actual PDF files
- Your API key stays on your computer
- All file operations are local
- See Anthropic's privacy policy: https://www.anthropic.com/legal/privacy

---

**Ready?** Run `INSTALL_DEPENDENCIES.bat` to begin! 🚀
