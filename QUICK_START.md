# Quick Start Guide - Multiple Approaches

## 🚨 If Nothing Else Works - Try These

### Method 1: Simple Interactive Script (EASIEST)

**Just run this ONE command:**

```bash
python organize_simple.py
```

This will:
- ✅ Check if packages are installed (installs them if missing)
- ✅ Ask you step-by-step what you need
- ✅ Auto-detect your Downloads folder
- ✅ Guide you through setup
- ✅ Start organizing

**No configuration files, no GUI issues, just simple questions!**

---

### Method 2: Test First, Then Run

**Step 1 - Test everything:**
```bash
python test_basic.py
```

This verifies:
- Python packages installed
- API key available
- PDFOrganizer class works
- Validation working

**Step 2 - If tests pass, organize:**
```bash
python organize_simple.py
```

---

### Method 3: Command Line (Most Reliable)

**One command with everything specified:**

```bash
python pdf_organizer.py --downloads "C:\Users\Peter\Downloads" --ebooks "F:\ebooks" --api-key "your-key-here"
```

Replace:
- `C:\Users\Peter\Downloads` with your actual Downloads path
- `F:\ebooks` with where you want PDFs organized
- `your-key-here` with your Anthropic API key

---

### Method 4: Set Environment Variable, Then Run

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your-key-here
python organize_simple.py
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your-key-here"
python organize_simple.py
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
python organize_simple.py
```

---

## 🔍 What's Different About These Approaches

### organize_simple.py
- **Interactive**: Asks questions step by step
- **Auto-installs**: Installs missing packages
- **Auto-detects**: Finds your Downloads folder
- **Validates**: Checks everything before starting
- **No config files**: Everything specified when you run it

### test_basic.py
- **Diagnostic**: Tests each component
- **Safe**: Doesn't modify anything
- **Clear**: Shows exactly what's wrong
- **Quick**: Runs in seconds

---

## 📋 Absolute Minimum Setup

### 1. Install Python Packages

```bash
pip install anthropic pdfplumber pypdf
```

### 2. Get API Key

Go to: https://console.anthropic.com/
Copy your API key (starts with `sk-ant-`)

### 3. Run Simple Script

```bash
python organize_simple.py
```

Follow the prompts!

---

## 🎯 Step-by-Step: organize_simple.py

**What you'll see:**

```
======================================================================
  PDF Organizer - Interactive Setup
======================================================================

Step 1: Checking dependencies...
  ✓ anthropic
  ✓ pdfplumber
  ✓ pypdf

Step 2: Configure Downloads Folder
----------------------------------------------------------------------
Auto-detected: C:\Users\Peter\Downloads
✓ This folder exists

Use this folder? (Y/n): y
✓ Using: C:\Users\Peter\Downloads

Step 3: Configure Ebooks Folder
----------------------------------------------------------------------
This is where organized PDFs will be stored.
Example: F:\ebooks or C:\Users\Peter\Documents\eBooks

Enter Ebooks folder path: F:\ebooks

Folder doesn't exist. Create F:\ebooks? (Y/n): y
✓ Created: F:\ebooks

Step 4: Configure API Key
----------------------------------------------------------------------
Get your API key at: https://console.anthropic.com/

Enter your Anthropic API key: sk-ant-your-key-here
✓ API key configured

======================================================================
  Configuration Summary
======================================================================
Downloads: C:\Users\Peter\Downloads
Ebooks:    F:\ebooks
API Key:   sk-ant-xxx...xxx

Found 15 PDFs in Downloads folder

Start organizing? (Y/n): y

======================================================================
  Starting Organization
======================================================================

[Processing PDFs...]
```

---

## ❌ Common Issues & Quick Fixes

### "ModuleNotFoundError: No module named 'anthropic'"

**Fix:**
```bash
pip install anthropic pdfplumber pypdf
```

### "Error: ebooks_folder is required"

**Fix:** Use `organize_simple.py` - it will guide you through setup

### "API key not found"

**Fix:** `organize_simple.py` will ask you for it

### GUI not working

**Fix:** Skip the GUI, use `organize_simple.py` instead

### Configuration confusing

**Fix:** Ignore all config files, use `organize_simple.py`

---

## 🆘 Emergency Procedure

If NOTHING works:

**Step 1:**
```bash
python test_basic.py
```
Read the output carefully. It will tell you exactly what's wrong.

**Step 2:**
Fix what `test_basic.py` reports.

**Step 3:**
```bash
python organize_simple.py
```

**Step 4:**
If still failing, copy the FULL error message and check `ERROR_HANDLING.md`

---

## 💡 Why organize_simple.py is Better

| Feature | organize_simple.py | GUI | Command Line |
|---------|-------------------|-----|--------------|
| Auto-installs packages | ✅ Yes | ❌ No | ❌ No |
| Interactive setup | ✅ Yes | ⚠ Manual | ⚠ Manual |
| Auto-detects paths | ✅ Yes | ⚠ Partial | ❌ No |
| No config files needed | ✅ Yes | ❌ No | ✅ Yes |
| Validates before running | ✅ Yes | ⚠ Partial | ❌ No |
| Shows clear errors | ✅ Yes | ⚠ Sometimes | ✅ Yes |
| Works when GUI fails | ✅ Yes | ❌ N/A | ✅ Yes |

---

## 🎓 Example Complete Session

```bash
C:\Users\Peter\Downloads\files> python organize_simple.py

======================================================================
  PDF Organizer - Interactive Setup
======================================================================

Step 1: Checking dependencies...
  ✓ anthropic
  ✓ pdfplumber
  ✓ pypdf

Step 2: Configure Downloads Folder
----------------------------------------------------------------------
Auto-detected: C:\Users\Peter\Downloads
✓ This folder exists
Use this folder? (Y/n): y
✓ Using: C:\Users\Peter\Downloads

Step 3: Configure Ebooks Folder
----------------------------------------------------------------------
Enter Ebooks folder path: F:\ebooks
✓ Using: F:\ebooks

Step 4: Configure API Key
----------------------------------------------------------------------
Enter your Anthropic API key: sk-ant-api03-xxxxx
✓ API key configured

======================================================================
  Configuration Summary
======================================================================
Downloads: C:\Users\Peter\Downloads
Ebooks:    F:\ebooks
API Key:   sk-ant-api...xxxx

Found 23 PDFs in Downloads folder

Start organizing? (Y/n): y

Analyzing existing ebooks folder structure...
Found 15 categories in your ebooks library:
[Processing begins...]

✓ Organized 23 PDFs
Check: F:\ebooks

Press Enter to exit...
```

---

## ✅ Recommended Workflow

1. **First time:** `python test_basic.py` (verify setup)
2. **Every time:** `python organize_simple.py` (organize PDFs)

That's it! No GUI, no complex config, just simple scripts that work.

---

**TL;DR: Just run `python organize_simple.py` and answer the questions!** 🎯
