# Portable Usage Guide

## 🎒 Using PDF Organizer from Any Location

The PDF Organizer is now fully portable! You can run it from:
- ✅ USB flash drive
- ✅ External hard drive
- ✅ Network drive
- ✅ Any folder on your PC
- ✅ Cloud sync folders (Dropbox, OneDrive, etc.)

The tool **automatically detects** the current user's Downloads folder, so it works regardless of:
- Which computer you're on
- Which user account is logged in
- Where the tool is installed

---

## 🚀 Quick Start (Portable Mode)

### Step 1: Copy All Files
Copy these files to your USB stick or any folder:
- All `.py` files
- All `.bat` files
- `requirements.txt`
- All `.md` documentation files

### Step 2: Install Dependencies (One Time Per Computer)
On each computer where you'll use the tool:

**Double-click:** `INSTALL_DEPENDENCIES.bat`

This installs Python packages to the user account (not the USB stick).

> **Note:** Dependencies need to be installed once per computer, not per USB stick.

### Step 3: Run from Anywhere
**Double-click:** `PORTABLE_LAUNCHER.bat`

The tool will:
- ✓ Auto-detect the current user's Downloads folder
- ✓ Work from whatever location it's in
- ✓ Remember your ebooks folder path
- ✓ Remember your API key

---

## 📋 What Gets Auto-Detected

### ✅ Automatically Detected
- **Downloads Folder:** `C:\Users\[CurrentUser]\Downloads`
  - Works for any user on any computer
  - No configuration needed

### 🔧 You Configure Once
- **Ebooks Folder:** e.g., `F:\ebooks` or `D:\MyLibrary`
  - Set once in the GUI
  - Saved in settings file
- **API Key:** Your Anthropic API key
  - Enter once in the GUI
  - Saved in settings file

---

## 💾 Where Settings Are Saved

Settings are saved in the **user's home folder**, not on the USB stick:

**Windows:**
```
C:\Users\[YourName]\.pdf_organizer_settings.json
```

**Mac/Linux:**
```
/Users/[YourName]/.pdf_organizer_settings.json
OR
/home/[YourName]/.pdf_organizer_settings.json
```

This means:
- ✅ Settings persist across sessions
- ✅ Different computers can have different settings
- ✅ Multiple users on same computer have separate settings
- ✅ USB stick doesn't store personal data

---

## 🔄 Multi-Computer Workflow

### Computer A (Home)
1. Run from USB stick: `PORTABLE_LAUNCHER.bat`
2. Auto-detects: `C:\Users\HomeUser\Downloads`
3. Configure: Ebooks → `F:\ebooks`
4. Organize PDFs

### Computer B (Work)
1. Same USB stick: `PORTABLE_LAUNCHER.bat`
2. Auto-detects: `C:\Users\WorkUser\Downloads`
3. Configure: Ebooks → `E:\WorkLibrary`
4. Organize PDFs

Each computer remembers its own settings!

---

## 📁 Recommended Setup

### For USB Stick Usage:

```
USB-Drive:\
├── PDF-Organizer\          ← All tool files here
│   ├── PORTABLE_LAUNCHER.bat
│   ├── INSTALL_DEPENDENCIES.bat
│   ├── pdf_organizer_gui.py
│   ├── pdf_organizer.py
│   └── requirements.txt
│
└── MyEbooks\               ← Optional: Store ebooks here too
    ├── Technology\
    ├── Business\
    └── Science\
```

Then set ebooks folder to: `E:\MyEbooks` (or whatever your USB drive letter is)

### For Network Drive:

```
\\NetworkDrive\Tools\PDF-Organizer\
```

Configure ebooks to a network location:
```
\\NetworkDrive\SharedLibrary\Ebooks\
```

---

## 🔧 Command-Line Portable Mode

The command-line version also auto-detects:

```bash
# Auto-detects current user's Downloads
python pdf_organizer.py --ebooks "F:\ebooks"

# Specify custom Downloads if needed
python pdf_organizer.py --downloads "D:\MyDownloads" --ebooks "F:\ebooks"

# Dry run
python pdf_organizer.py --ebooks "F:\ebooks" --dry-run
```

---

## 🎯 Use Cases

### 1. Work + Home
- Keep tool on USB stick
- Use at work and home
- Each location organizes its own Downloads
- Point to different ebook libraries

### 2. Multiple Users, One Computer
- Each user has their own Downloads folder
- Tool auto-detects current user
- Different ebook libraries per user

### 3. IT Support / Admin
- Keep tool on USB stick
- Help users organize their Downloads
- Works on any computer instantly

### 4. Library Management
- Store tool with your ebook library
- Open from library location
- Always points to correct folders

---

## ⚙️ Advanced: Custom Downloads Location

If you need to organize a folder other than Downloads:

### GUI Method:
1. Launch the tool
2. Click "Browse" next to Downloads Folder
3. Select any folder you want

### Command-Line Method:
```bash
python pdf_organizer.py --downloads "C:\MyFolder" --ebooks "F:\ebooks"
```

---

## 🔒 Privacy Note

When running from USB stick:
- ✓ Settings (including API key) are saved to user's home folder
- ✓ API key is NOT stored on the USB stick
- ✓ Each computer has separate settings
- ✓ Safe to share USB stick (no personal data on it)

If you want API key on USB stick (for single-user USB):
- Set environment variable on the USB stick (advanced)
- Or enter it each time you launch

---

## 📊 What Works Where

| Feature | USB Stick | Network Drive | Cloud Folder |
|---------|-----------|---------------|--------------|
| Tool Files | ✅ Yes | ✅ Yes | ✅ Yes |
| Auto-detect Downloads | ✅ Yes | ✅ Yes | ✅ Yes |
| Save Settings | ✅ User Home | ✅ User Home | ✅ User Home |
| Ebooks Location | ✅ Any | ✅ Any | ✅ Any |
| Dependencies | Computer | Computer | Computer |

---

## 🆘 Troubleshooting Portable Mode

### "Python not found"
**Problem:** Python not installed on this computer

**Solution:** Install Python on each computer you'll use (one-time setup)

### "Dependencies not installed"
**Problem:** Packages not installed on this computer

**Solution:** Run `INSTALL_DEPENDENCIES.bat` once per computer

### "Wrong Downloads folder detected"
**Problem:** Wants to use different folder

**Solution:** 
1. Launch GUI
2. Click "Browse" 
3. Select correct folder
4. Settings will be saved for this computer

### "Can't save settings"
**Problem:** No write permission to user home folder

**Solution:** 
- Check user permissions
- Or enter settings each time (they won't save)

---

## ✅ Portable Mode Checklist

Before unplugging USB stick:

- [ ] All `.py` files copied to USB
- [ ] All `.bat` files copied to USB
- [ ] `requirements.txt` copied to USB
- [ ] Dependencies installed on this computer
- [ ] Tested: Can launch from USB
- [ ] Settings saved (ebooks folder, API key)

Ready to use on other computers!

---

## 🎓 How Auto-Detection Works

```python
# The tool uses Python's pathlib to detect user home
from pathlib import Path
downloads = Path.home() / "Downloads"

# Example outputs:
# Windows: C:\Users\Peter\Downloads
# Mac: /Users/Peter/Downloads  
# Linux: /home/peter/Downloads
```

This ensures it works for **any user** on **any computer**! 🎉

---

**Enjoy your portable PDF organizer!** 📚✨
