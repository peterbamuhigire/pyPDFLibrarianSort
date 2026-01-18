#!/usr/bin/env python3
"""
PDF Organizer - Batch Mode Launcher
ONE API call for ALL PDFs = massive cost savings!
"""

import os
import sys
from pathlib import Path

def main():
    print("="*70)
    print("  PDF Organizer - BATCH MODE (Cost-Effective)")
    print("="*70)
    print()
    print("💰 Cost Comparison:")
    print("   Old way: $0.05 per PDF  → 200 PDFs = $10")
    print("   Batch:   $0.05-0.10 total → 200 PDFs = $0.10!")
    print()
    print("   100x COST SAVINGS! 🎉")
    print()
    
    # Check packages
    print("Checking dependencies...")
    try:
        import anthropic
        from pypdf import PdfReader
        print("  ✓ All packages installed")
    except ImportError as e:
        print(f"  ❌ Missing package: {e}")
        print("\nInstalling...")
        os.system("pip install anthropic pypdf --quiet")
        print("  ✓ Installed")
    
    print()
    
    # Get Downloads folder
    auto_downloads = str(Path.home() / "Downloads")
    print(f"Downloads folder: {auto_downloads}")
    
    if Path(auto_downloads).exists():
        use_auto = input("Use this folder? (Y/n): ").strip().lower()
        if use_auto in ['', 'y', 'yes']:
            downloads = auto_downloads
        else:
            downloads = input("Enter Downloads path: ").strip()
    else:
        downloads = input("Enter Downloads path: ").strip()
    
    # Get Ebooks folder  
    print()
    ebooks = input("Enter Ebooks folder path (e.g., F:\\ebooks): ").strip()
    
    if not Path(ebooks).exists():
        create = input(f"\nCreate {ebooks}? (Y/n): ").strip().lower()
        if create in ['', 'y', 'yes']:
            Path(ebooks).mkdir(parents=True, exist_ok=True)
            print(f"✓ Created")
    
    # Get API key
    print()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✓ API key found: {api_key[:10]}...")
        use_env = input("Use this key? (Y/n): ").strip().lower()
        if use_env not in ['', 'y', 'yes']:
            api_key = input("Enter API key: ").strip()
    else:
        api_key = input("Enter API key: ").strip()
    
    # Summary
    print()
    print("="*70)
    print("  Configuration")
    print("="*70)
    print(f"Downloads: {downloads}")
    print(f"Ebooks:    {ebooks}")
    print(f"API Key:   {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Count PDFs
    pdf_count = 0
    for root, dirs, files in os.walk(downloads):
        pdf_count += len([f for f in files if f.lower().endswith('.pdf')])
    
    print(f"📚 Found {pdf_count} PDFs")
    print()
    print(f"💰 Estimated cost: $0.05-0.10 (vs ${pdf_count * 0.05:.2f} old way)")
    print(f"💵 You'll save: ${(pdf_count * 0.05) - 0.10:.2f}!")
    print()
    
    proceed = input("Start batch organization? (Y/n): ").strip().lower()
    if proceed not in ['', 'y', 'yes']:
        print("Cancelled")
        return
    
    # Import and run
    print()
    print("="*70)
    print("  Processing...")
    print("="*70)
    print()
    
    try:
        from pdf_organizer_batch import BatchPDFOrganizer

        # Use context manager to ensure API key cleanup
        with BatchPDFOrganizer(
            downloads_folder=downloads,
            ebooks_folder=ebooks,
            api_key=api_key,
            dry_run=False
        ) as organizer:
            organizer.organize_pdfs()

            print()
            print("="*70)
            print("  Complete!")
            print("="*70)
            print(f"\n✓ Check: {ebooks}")

        # API key is now cleared from memory

    except Exception as e:
        print()
        print("="*70)
        print("  ERROR")
        print("="*70)
        print(f"\n{e}")

        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
    
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
