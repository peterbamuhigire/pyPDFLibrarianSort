#!/usr/bin/env python3
"""
PDF Organizer - Simple Version
Interactive setup with step-by-step guidance
"""

import os
import sys
from pathlib import Path

def main():
    print("="*70)
    print("  PDF Organizer - Interactive Setup")
    print("="*70)
    print()
    
    # Step 1: Check Python packages
    print("Step 1: Checking dependencies...")
    missing = []
    
    try:
        import anthropic
        print("  ✓ anthropic")
    except ImportError:
        print("  ❌ anthropic - NOT INSTALLED")
        missing.append("anthropic")
    
    try:
        from pypdf import PdfReader
        print("  ✓ pypdf")
    except ImportError:
        print("  ❌ pypdf - NOT INSTALLED")
        missing.append("pypdf")
    
    if missing:
        print()
        print("Missing packages. Installing now...")
        print()
        
        for package in missing:
            print(f"Installing {package}...")
            os.system(f'pip install {package} --quiet')
        
        print()
        print("✓ All packages installed!")
        print()
    
    # Step 2: Get Downloads folder
    print()
    print("Step 2: Configure Downloads Folder")
    print("-" * 70)
    
    # Auto-detect
    auto_downloads = str(Path.home() / "Downloads")
    print(f"Auto-detected: {auto_downloads}")
    
    if Path(auto_downloads).exists():
        print("✓ This folder exists")
        use_auto = input("\nUse this folder? (Y/n): ").strip().lower()
        if use_auto in ['', 'y', 'yes']:
            downloads_folder = auto_downloads
        else:
            downloads_folder = input("Enter Downloads folder path: ").strip()
    else:
        print("⚠ Auto-detected folder doesn't exist")
        downloads_folder = input("Enter Downloads folder path: ").strip()
    
    # Validate Downloads folder
    if not Path(downloads_folder).exists():
        print(f"❌ ERROR: Folder not found: {downloads_folder}")
        input("Press Enter to exit...")
        return
    
    print(f"✓ Using: {downloads_folder}")
    
    # Step 3: Get Ebooks folder
    print()
    print("Step 3: Configure Ebooks Folder")
    print("-" * 70)
    print("This is where organized PDFs will be stored.")
    print("Example: F:\\ebooks or C:\\Users\\Peter\\Documents\\eBooks")
    print()
    
    ebooks_folder = input("Enter Ebooks folder path: ").strip()
    
    # Create if doesn't exist
    if not Path(ebooks_folder).exists():
        create = input(f"\nFolder doesn't exist. Create {ebooks_folder}? (Y/n): ").strip().lower()
        if create in ['', 'y', 'yes']:
            try:
                Path(ebooks_folder).mkdir(parents=True, exist_ok=True)
                print(f"✓ Created: {ebooks_folder}")
            except Exception as e:
                print(f"❌ ERROR: Could not create folder: {e}")
                input("Press Enter to exit...")
                return
        else:
            print("❌ ERROR: Ebooks folder is required")
            input("Press Enter to exit...")
            return
    else:
        print(f"✓ Using: {ebooks_folder}")
    
    # Step 4: Get API Key
    print()
    print("Step 4: Configure API Key")
    print("-" * 70)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if api_key:
        print(f"✓ Found in environment: {api_key[:10]}...")
        use_env = input("\nUse this key? (Y/n): ").strip().lower()
        if use_env not in ['', 'y', 'yes']:
            api_key = input("Enter your Anthropic API key: ").strip()
    else:
        print("No API key found in environment.")
        print()
        print("Get your API key at: https://console.anthropic.com/")
        print()
        api_key = input("Enter your Anthropic API key: ").strip()
    
    if not api_key or api_key.strip() == '':
        print("❌ ERROR: API key is required")
        input("Press Enter to exit...")
        return
    
    print("✓ API key configured")
    
    # Step 5: Summary and confirmation
    print()
    print("="*70)
    print("  Configuration Summary")
    print("="*70)
    print(f"Downloads: {downloads_folder}")
    print(f"Ebooks:    {ebooks_folder}")
    print(f"API Key:   {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Count PDFs
    pdf_count = 0
    for root, dirs, files in os.walk(downloads_folder):
        pdf_count += len([f for f in files if f.lower().endswith('.pdf')])
    
    print(f"Found {pdf_count} PDFs in Downloads folder")
    print()
    
    proceed = input("Start organizing? (Y/n): ").strip().lower()
    if proceed not in ['', 'y', 'yes']:
        print("Cancelled.")
        input("Press Enter to exit...")
        return
    
    # Step 6: Import and run
    print()
    print("="*70)
    print("  Starting Organization")
    print("="*70)
    print()
    
    try:
        from pdf_organizer import PDFOrganizer
        
        organizer = PDFOrganizer(
            downloads_folder=downloads_folder,
            ebooks_folder=ebooks_folder,
            api_key=api_key,
            dry_run=False
        )
        
        results = organizer.organize_pdfs(confirm=True)
        
        print()
        print("="*70)
        print("  Complete!")
        print("="*70)
        
        if results:
            print(f"\n✓ Organized {len(results)} PDFs")
            print(f"Check: {ebooks_folder}")
        
    except Exception as e:
        print()
        print("="*70)
        print("  ERROR")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()
        
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
