#!/usr/bin/env python3
"""
Setup script for PDF Organizer
Helps with initial configuration and testing
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print("✅ Python version OK")
    return True

def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Try running manually: pip install -r requirements.txt")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Package Imports")
    
    packages = [
        ('google.generativeai', 'google-generativeai'),
        ('pdfplumber', 'pdfplumber'),
        ('pypdf', 'pypdf'),
        ('tkinter', 'tkinter (GUI)')
    ]
    
    all_ok = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - not found")
            all_ok = False
    
    return all_ok

def setup_api_key():
    """Help user set up API key"""
    print_header("API Key Configuration")
    
    # Check if already set
    existing_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if existing_key:
        print(f"✅ API key already set: {existing_key[:8]}...{existing_key[-4:]}")
        change = input("\nDo you want to change it? (y/n): ").lower()
        if change != 'y':
            return True
    
    print("\nYou need a Gemini API key to use this tool.")
    print("Get one at: https://aistudio.google.com/app/apikey")
    print("\nOptions:")
    print("1. Enter API key now (will be saved to config file)")
    print("2. Set as environment variable (recommended)")
    print("3. Skip (you can enter it in the GUI later)")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '1':
        api_key = input("\nEnter your Gemini API key: ").strip()
        if api_key:
            # Save to config file
            config_file = Path.home() / '.pdf_organizer_settings.json'
            import json
            config = {}
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            config['api_key'] = api_key
            with open(config_file, 'w') as f:
                json.dump(config, f)
            print("✅ API key saved to config file")
            return True
    
    elif choice == '2':
        api_key = input("\nEnter your Gemini API key: ").strip()
        if api_key:
            print("\nTo set as environment variable:")
            if sys.platform == 'win32':
                print(f'\nRun in Command Prompt:\nsetx GEMINI_API_KEY "{api_key}"')
                print(f'\nOr in PowerShell:\n$env:GEMINI_API_KEY = "{api_key}"')
            else:
                print(f'\nRun in terminal:\nexport GEMINI_API_KEY="{api_key}"')
                print(f'\nAdd to ~/.bashrc or ~/.zshrc to make permanent')
            input("\nPress Enter after you've set the environment variable...")
            return True
    
    elif choice == '3':
        print("⚠ You'll need to enter the API key when running the tool")
        return True
    
    return False

def configure_folders():
    """Help user configure folder paths"""
    print_header("Folder Configuration")
    
    config_file = Path.home() / '.pdf_organizer_settings.json'
    import json
    
    config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    # Downloads folder
    print("\n1. Downloads Folder")
    if config.get('downloads_path'):
        print(f"   Current: {config['downloads_path']}")
        change = input("   Keep this path? (y/n): ").lower()
        if change == 'y':
            downloads = config['downloads_path']
        else:
            downloads = input("   Enter Downloads folder path: ").strip()
    else:
        # Suggest default
        default_downloads = str(Path.home() / "Downloads")
        print(f"   Suggested: {default_downloads}")
        use_default = input("   Use suggested path? (y/n): ").lower()
        if use_default == 'y':
            downloads = default_downloads
        else:
            downloads = input("   Enter Downloads folder path: ").strip()
    
    # Ebooks folder
    print("\n2. Ebooks Storage Folder")
    if config.get('ebooks_path'):
        print(f"   Current: {config['ebooks_path']}")
        change = input("   Keep this path? (y/n): ").lower()
        if change == 'y':
            ebooks = config['ebooks_path']
        else:
            ebooks = input("   Enter ebooks folder path: ").strip()
    else:
        ebooks = input("   Enter ebooks folder path (e.g., F:\\ebooks): ").strip()
    
    # Verify folders exist
    if not Path(downloads).exists():
        print(f"\n⚠ Warning: {downloads} doesn't exist")
        create = input("   Create it? (y/n): ").lower()
        if create == 'y':
            Path(downloads).mkdir(parents=True, exist_ok=True)
    
    if not Path(ebooks).exists():
        print(f"\n⚠ Warning: {ebooks} doesn't exist")
        create = input("   Create it? (y/n): ").lower()
        if create == 'y':
            Path(ebooks).mkdir(parents=True, exist_ok=True)
    
    # Save config
    config['downloads_path'] = downloads
    config['ebooks_path'] = ebooks
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Folder paths saved")
    return True

def run_test():
    """Run a quick test"""
    print_header("Running Test")
    
    print("Testing PDF organizer import...")
    try:
        from pdf_organizer import PDFOrganizer
        print("✅ PDF organizer module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading PDF organizer: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  PDF ORGANIZER - SETUP WIZARD")
    print("="*70)
    print("\nThis wizard will help you set up the PDF Organizer tool.\n")
    
    # Step 1: Check Python
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print("\nReady to install dependencies?")
    install = input("Install now? (y/n): ").lower()
    if install == 'y':
        if not install_dependencies():
            print("\n⚠ Installation had issues. Please fix them and try again.")
            sys.exit(1)
    else:
        print("⚠ Skipping installation. Make sure to run: pip install -r requirements.txt")
    
    # Step 3: Test imports
    if not test_imports():
        print("\n⚠ Some packages are missing. Please install them.")
        sys.exit(1)
    
    # Step 4: API Key
    if not setup_api_key():
        print("\n⚠ API key setup incomplete. You can configure it later.")
    
    # Step 5: Configure folders
    configure_folders()
    
    # Step 6: Run test
    run_test()
    
    # Done!
    print_header("Setup Complete!")
    print("\nYou're all set! Here's how to use the tool:\n")
    print("GUI Version (Recommended):")
    print("  python pdf_organizer_gui.py")
    print("\nCommand Line:")
    print("  python pdf_organizer.py --downloads <path> --ebooks <path>")
    print("\nFor more information, see README.md")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
