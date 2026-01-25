#!/usr/bin/env python3
"""
AI-Powered PDF Organizer
Automatically categorizes and organizes PDFs using AI content analysis
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader
import google.generativeai as genai
from collections import defaultdict
import argparse

class PDFOrganizer:
    def __init__(self, downloads_folder, ebooks_folder, api_key=None, dry_run=False, category_template=None, require_api_key=True):
        """
        Initialize the PDF organizer

        Args:
            downloads_folder: Path to Downloads folder (e.g., C:/Users/YourName/Downloads)
            ebooks_folder: Path to ebooks storage (e.g., F:/ebooks)
            api_key: Gemini API key (or set GEMINI_API_KEY env var)
            dry_run: If True, only show what would be done without moving files
        """
        # Validate required parameters
        if not ebooks_folder:
            raise ValueError("ebooks_folder is required. Please specify where to organize PDFs (e.g., F:/ebooks)")

        if not downloads_folder:
            raise ValueError("downloads_folder is required. Please specify where PDFs are located (e.g., C:/Users/YourName/Downloads)")

        self.downloads_folder = Path(downloads_folder)
        self.ebooks_folder = Path(ebooks_folder)
        self.dry_run = dry_run
        default_template = Path(__file__).resolve().parent / "category_template.json"
        self.category_template_path = Path(category_template) if category_template else default_template
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')

        if require_api_key and not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY env var or pass api_key parameter")

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
        else:
            self.client = None
        self.log_file = self.ebooks_folder / "organization_log.json"
        self.load_log()

    def cleanup(self):
        """Clean up sensitive data and API client from memory"""
        # Clear API client reference
        if hasattr(self, 'client'):
            self.client = None

        # Clear API key from memory
        if hasattr(self, 'api_key'):
            self.api_key = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.cleanup()
        return False

    def __del__(self):
        """Destructor - ensures cleanup on object deletion"""
        self.cleanup()
        
    def load_log(self):
        """Load organization history"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.log = json.load(f)
        else:
            self.log = {
                'organized_files': [],
                'category_map': {},
                'last_run': None
            }
    
    def save_log(self):
        """Save organization history"""
        self.log['last_run'] = datetime.now().isoformat()
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
    
    def analyze_existing_structure(self):
        """Analyze existing folder structure to understand categorization hierarchy"""
        print("Analyzing existing ebooks folder structure...")
        
        categories = {}
        category_tree = []
        
        # Walk through all directories in ebooks folder
        for root, dirs, files in os.walk(self.ebooks_folder):
            # Calculate relative path from ebooks root
            rel_path = Path(root).relative_to(self.ebooks_folder)
            
            # Skip the root directory itself
            if rel_path == Path('.'):
                continue
            
            # Count PDFs in this directory
            pdf_count = len([f for f in files if f.lower().endswith('.pdf')])
            
            # Calculate depth level
            path_parts = rel_path.parts
            depth = len(path_parts)
            
            # Create display path with proper separators
            category_path = '/'.join(path_parts)
            
            # Store category info
            categories[category_path] = {
                'count': pdf_count,
                'depth': depth,
                'parent': '/'.join(path_parts[:-1]) if depth > 1 else None,
                'name': path_parts[-1],
                'full_path': str(rel_path),
                'has_subdirs': len(dirs) > 0,
                'sample_files': [f for f in files if f.lower().endswith('.pdf')][:3]
            }
            
            # Add to tree structure for display
            category_tree.append({
                'path': category_path,
                'depth': depth,
                'count': pdf_count,
                'has_subdirs': len(dirs) > 0
            })
        
        # Display the category tree
        if categories:
            print(f"\nFound {len(categories)} categories in your ebooks library:")
            print("="*70)
            
            # Sort by depth first, then alphabetically
            sorted_tree = sorted(category_tree, key=lambda x: (x['depth'], x['path']))
            
            # Group by depth for cleaner display
            by_depth = defaultdict(list)
            for item in sorted_tree:
                by_depth[item['depth']].append(item)
            
            # Display by depth level
            for depth in sorted(by_depth.keys()):
                print(f"\nLevel {depth} Categories:")
                for item in by_depth[depth]:
                    # Create indentation based on depth
                    indent = "  " * (depth - 1)
                    pdf_info = f"({item['count']} PDFs)" if item['count'] > 0 else "(folder)"
                    subdir_indicator = " [+]" if item['has_subdirs'] else ""
                    print(f"{indent}📁 {item['path']} {pdf_info}{subdir_indicator}")
            
            print("="*70)
            print(f"Total: {sum(c['count'] for c in categories.values())} PDFs across {len(categories)} categories")
            print()
        else:
            print("No existing categories found. Will create new structure based on PDF content.")
            print()
        
        return categories

    def load_category_template(self):
        """Load predefined category hierarchy if available"""
        template_path = self.category_template_path
        if not template_path or not Path(template_path).exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  ⚠ Failed to load category template ({template_path}): {e}")
            return None
        
        # Normalize into the same shape as analyze_existing_structure
        categories = {}
        for entry in data.get('categories', []):
            raw_path = entry.get('path')
            if not raw_path:
                continue
            path_str = str(raw_path).replace('\\', '/').strip('/')
            path_parts = tuple(path_str.split('/'))
            depth = entry.get('depth') or len(path_parts)
            categories[path_str] = {
                'count': entry.get('count', 0),
                'depth': depth,
                'parent': '/'.join(path_parts[:-1]) if depth > 1 else None,
                'name': path_parts[-1],
                'full_path': path_str,
                'has_subdirs': False,
                'sample_files': entry.get('sample_files', [])
            }
        
        print(f"Using category template: {template_path} ({len(categories)} categories)")
        return categories

    def export_category_template(self, template_path=None):
        """Save current ebooks folder hierarchy as a reusable template"""
        categories = self.analyze_existing_structure()
        template_path = Path(template_path) if template_path else self.category_template_path
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        payload = {
            'generated_at': datetime.now().isoformat(),
            'ebooks_root': str(self.ebooks_folder),
            'category_count': len(categories),
            'categories': [
                {
                    'path': path,
                    'depth': info['depth'],
                    'count': info['count']
                }
                for path, info in sorted(categories.items(), key=lambda x: x[0])
            ]
        }
        
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        print(f"Template saved to {template_path}")
        return template_path

    def load_or_analyze_categories(self):
        """Use template when available, otherwise analyze live structure"""
        template_categories = self.load_category_template()
        if template_categories:
            # Merge live counts to template where possible
            existing = self.analyze_existing_structure()
            for path, info in existing.items():
                if path in template_categories:
                    template_categories[path]['count'] = info.get('count', template_categories[path].get('count', 0))
                    template_categories[path]['has_subdirs'] = info.get('has_subdirs', template_categories[path].get('has_subdirs', False))
                else:
                    template_categories[path] = info
            return template_categories
        
        return self.analyze_existing_structure()
    
    def build_category_hierarchy_text(self, categories):
        """Build a text representation of the category hierarchy for AI context"""
        if not categories:
            return "No existing categories."
        
        # Sort by path to maintain hierarchy
        sorted_cats = sorted(categories.items(), key=lambda x: x[0])
        
        hierarchy_lines = []
        hierarchy_lines.append("EXISTING CATEGORY HIERARCHY:")
        hierarchy_lines.append("")
        
        # Group by depth for structured display
        by_depth = defaultdict(list)
        for cat_path, info in sorted_cats:
            by_depth[info['depth']].append((cat_path, info))
        
        # Build hierarchical display
        for depth in sorted(by_depth.keys()):
            hierarchy_lines.append(f"Level {depth}:")
            for cat_path, info in by_depth[depth]:
                indent = "  " * depth
                pdf_info = f"[{info['count']} PDFs]" if info['count'] > 0 else "[empty]"
                hierarchy_lines.append(f"{indent}- {cat_path} {pdf_info}")
            hierarchy_lines.append("")
        
        # Add some examples of well-populated categories
        well_populated = [(k, v) for k, v in categories.items() if v['count'] >= 3]
        if well_populated:
            hierarchy_lines.append("Most Used Categories (3+ PDFs):")
            for cat_path, info in sorted(well_populated, key=lambda x: x[1]['count'], reverse=True)[:10]:
                hierarchy_lines.append(f"  - {cat_path} ({info['count']} PDFs)")
                if info['sample_files']:
                    hierarchy_lines.append(f"    Examples: {', '.join(info['sample_files'][:2])}")
        
        return "\n".join(hierarchy_lines)
    
    def extract_pdf_text(self, pdf_path, max_pages=3):
        """Extract metadata from PDF (filename-based approach)"""
        
        # Get basic metadata only
        try:
            reader = PdfReader(pdf_path)
            meta = reader.metadata
            metadata = {
                'title': meta.title if meta and meta.title else pdf_path.stem,
                'author': meta.author if meta and meta.author else None,
                'subject': meta.subject if meta and meta.subject else None,
            }
        except:
            metadata = {'title': pdf_path.stem, 'author': None, 'subject': None}
        
        # Use filename as primary source of information
        filename = pdf_path.stem
        
        # Simple text representation from filename
        # Convert underscores and hyphens to spaces for better readability
        readable_name = filename.replace('_', ' ').replace('-', ' ')
        
        return {
            'text': f"Filename: {readable_name}\nTitle: {metadata.get('title', 'Unknown')}",
            'metadata': metadata,
            'filename': pdf_path.name
        }
    
    def categorize_pdf_with_ai(self, pdf_data, existing_categories):
        """Use Gemini to categorize the PDF based on hierarchical structure"""
        if not self.client:
            raise RuntimeError("Gemini client not initialized. Provide an API key to categorize.")
        
        # Validate existing_categories
        if existing_categories is None:
            existing_categories = {}
        
        # Build hierarchical category context
        category_context = self.build_category_hierarchy_text(existing_categories)
        
        prompt = f"""You are helping organize a PDF library. Based on the FILENAME and metadata below, suggest the most appropriate category path that matches the EXISTING category structure.

{category_context}

PDF TO CATEGORIZE:
Filename: {pdf_data['filename']}
Readable Name: {pdf_data['text'].split('Filename: ')[1].split('\\n')[0] if 'Filename: ' in pdf_data['text'] else pdf_data['filename']}
Title: {pdf_data['metadata']['title']}
Author: {pdf_data['metadata']['author']}
Subject: {pdf_data['metadata']['subject']}

INSTRUCTIONS:
1. Analyze the FILENAME carefully - it often contains the subject matter (e.g., "Python_Programming.pdf", "Business_Finance_Guide.pdf")
2. Use the metadata title, author, and subject if available
3. Look at the EXISTING CATEGORY HIERARCHY above and find the most appropriate category path
4. Match the existing depth and structure (e.g., "Computer & ICT/Programming & Development/C++")
5. Use existing categories when they fit, creating new subcategories only if truly needed
6. Follow the same naming conventions you see in existing categories (e.g., use "&" if that's the pattern)
7. For multi-level categories, include the full path with "/" separators
8. Be specific and use appropriate depth (2-3 levels is typical)

Examples based on filenames:
- "Python_Machine_Learning.pdf" → "Computer & ICT/Programming & Development/Python"
- "Tax_Planning_2024.pdf" → "Business & Finance/Accounting/Tax Planning"
- "Quantum_Physics_Intro.pdf" → "Science/Physics/Quantum Mechanics"

Respond ONLY with a JSON object in this exact format:
{{
    "category_path": "MainCategory/Subcategory/SpecificTopic",
    "confidence": "high|medium|low",
    "reasoning": "Brief explanation based on filename and metadata",
    "alternative": "Alternative category if confidence is not high",
    "matches_existing": true|false,
    "depth_level": 2
}}"""

        try:
            message = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 500
                }
            )

            response_text = message.text or ""
            
            # Parse JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            try:
                result = json.loads(response_text.strip())
            except json.JSONDecodeError as je:
                print(f"  ⚠ Warning: Could not parse AI response as JSON: {je}")
                print(f"  Response was: {response_text[:200]}")
                # Return safe default
                return {
                    'category_path': 'Uncategorized',
                    'confidence': 'low',
                    'reasoning': 'AI response was not valid JSON',
                    'alternative': None,
                    'matches_existing': False,
                    'depth_level': 1
                }
            
            # Validate result has required fields
            if not result.get('category_path'):
                print(f"  ⚠ Warning: AI response missing category_path")
                result['category_path'] = 'Uncategorized'
            
            # Ensure category path uses proper separators
            if 'category_path' in result:
                # Ensure consistent path separator
                result['category_path'] = result['category_path'].replace('\\', '/')
                # Remove any leading/trailing slashes
                result['category_path'] = result['category_path'].strip('/')
            
            # Set defaults for missing fields
            if not result.get('confidence'):
                result['confidence'] = 'medium'
            if not result.get('reasoning'):
                result['reasoning'] = 'AI categorization'
            if 'matches_existing' not in result:
                result['matches_existing'] = False
            if 'depth_level' not in result:
                result['depth_level'] = result['category_path'].count('/') + 1
            
            return result
            
        except Exception as e:
            print(f"  ⚠ AI categorization error: {e}")
            # Return safe default
            return {
                'category_path': 'Uncategorized',
                'confidence': 'low',
                'reasoning': f'Categorization error: {str(e)}',
                'alternative': None,
                'matches_existing': False,
                'depth_level': 1
            }
    
    def organize_pdfs(self, confirm=True):
        """Main method to organize all PDFs"""
        
        # Find all PDFs in downloads (including subdirectories)
        print(f"\nScanning {self.downloads_folder} for PDFs (including subdirectories)...")
        pdf_files = []
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.downloads_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(Path(root) / file)
        
        if not pdf_files:
            print(f"No PDF files found in {self.downloads_folder} or its subdirectories")
            return
        
        print(f"\nFound {len(pdf_files)} PDF files to organize")
        
        # Show where PDFs were found
        subdirs = set(str(p.parent.relative_to(self.downloads_folder)) for p in pdf_files)
        if len(subdirs) > 1 or (len(subdirs) == 1 and list(subdirs)[0] != '.'):
            print(f"Found PDFs in {len(subdirs)} locations:")
            for subdir in sorted(subdirs):
                count = sum(1 for p in pdf_files if str(p.parent.relative_to(self.downloads_folder)) == subdir)
                display_dir = subdir if subdir != '.' else 'Downloads (root)'
                print(f"  • {display_dir}: {count} file(s)")
        
        # Analyze structure (prefer template when present)
        existing_categories = self.load_or_analyze_categories()
        print(f"Found {len(existing_categories)} categories available for sorting")
        
        # Process each PDF
        results = []
        rename_log = []
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
            print(f"  📂 Location: {pdf_path.parent}")
            
            # Extract metadata (no text extraction)
            pdf_data = self.extract_pdf_text(pdf_path)
            if not pdf_data:
                print(f"  ⚠ Could not read PDF metadata from {pdf_path.name}, skipping")
                continue
            
            # Check if file should be renamed based on metadata
            original_name = pdf_path.stem
            metadata_title = pdf_data['metadata'].get('title')
            new_name = None
            
            if metadata_title and metadata_title.strip():
                # Clean the metadata title for use as filename
                cleaned_title = self.clean_filename(metadata_title)
                
                # Check if current filename looks auto-generated or meaningless
                if self.should_rename_file(original_name, cleaned_title):
                    new_name = cleaned_title
                    print(f"  📝 Will rename: '{original_name}' → '{new_name}'")
                    rename_log.append({
                        'original': original_name,
                        'new': new_name,
                        'reason': 'metadata_title'
                    })
            
            # Update filename in pdf_data if renaming
            if new_name:
                pdf_data['filename'] = new_name + '.pdf'
                pdf_data['original_filename'] = pdf_path.name
                pdf_data['rename_to'] = new_name + '.pdf'
            
            # Categorize with AI
            print(f"  🤖 Analyzing content...")
            category_result = self.categorize_pdf_with_ai(pdf_data, existing_categories)
            
            # Validate category result
            if not category_result.get('category_path'):
                print(f"  ⚠ Warning: No category suggested, using 'Uncategorized'")
                category_result['category_path'] = 'Uncategorized'
                category_result['confidence'] = 'low'
                category_result['reasoning'] = 'Could not determine appropriate category'
            
            print(f"  📁 Suggested: {category_result['category_path']}")
            if category_result.get('matches_existing'):
                print(f"  ✓ Matches existing category structure")
            else:
                print(f"  ⭐ New category (will be created)")
            print(f"  💡 Reason: {category_result['reasoning']}")
            print(f"  📊 Confidence: {category_result['confidence']}")
            if category_result.get('depth_level'):
                print(f"  📏 Depth: Level {category_result['depth_level']}")
            
            if category_result.get('alternative'):
                print(f"  🔄 Alternative: {category_result['alternative']}")
            
            results.append({
                'filename': pdf_data['filename'],
                'original_filename': pdf_data.get('original_filename', pdf_data['filename']),
                'source': str(pdf_path),
                'category': category_result['category_path'],
                'confidence': category_result['confidence'],
                'reasoning': category_result['reasoning'],
                'rename_to': pdf_data.get('rename_to', None)
            })
        
        # Show summary and confirm
        if results:
            print("\n" + "="*70)
            print("ORGANIZATION SUMMARY")
            print("="*70)
            
            # Show renames first
            if rename_log:
                print(f"\nFILE RENAMES ({len(rename_log)} files):")
                for entry in rename_log:
                    print(f"  '{entry['original']}' → '{entry['new']}'")
            
            # Show categorization
            category_counts = defaultdict(list)
            for r in results:
                category_counts[r['category']].append(r)
            
            print(f"\nCATEGORIZATION:")
            for category, items in sorted(category_counts.items()):
                print(f"\n{category}/ ({len(items)} files)")
                for item in items:
                    display_name = item['filename']
                    if item.get('rename_to'):
                        display_name = f"{item['original_filename']} → {item['rename_to']}"
                    print(f"  • {display_name}")
            
            if self.dry_run:
                print("\n[DRY RUN] No files were moved or renamed")
                return results
            
            if confirm:
                response = input("\nProceed with moving and renaming these files? (y/n): ")
                if response.lower() != 'y':
                    print("Operation cancelled")
                    return results
            
            # Move and rename files
            print("\nProcessing files...")
            for result in results:
                # Debug: show what we're working with
                if not result.get('filename') and not result.get('rename_to'):
                    print(f"  ⚠ DEBUG: Result missing filename: {result.get('source')}")
                self.move_pdf(result)
            
            # Save log
            self.log['organized_files'].extend(results)
            self.save_log()
            
            print(f"\n✅ Successfully organized {len(results)} PDFs!")
            if rename_log:
                print(f"✅ Renamed {len(rename_log)} files based on metadata")
            
        return results
    
    def clean_filename(self, title):
        """Clean a title to make it suitable for a filename"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        cleaned = title
        
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '')
        
        # Replace multiple spaces with single space
        cleaned = ' '.join(cleaned.split())
        
        # Limit length (Windows has 255 char limit for filenames)
        max_length = 100  # Leave room for extension and path
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length].strip()
        
        # Remove leading/trailing dots and spaces
        cleaned = cleaned.strip('. ')
        
        return cleaned if cleaned else 'Untitled'
    
    def should_rename_file(self, current_name, metadata_title):
        """Determine if file should be renamed based on current name vs metadata"""
        # Don't rename if names are very similar
        if current_name.lower() == metadata_title.lower():
            return False
        
        # Check if current name looks auto-generated or meaningless
        # Patterns that suggest auto-generated names:
        # - All numbers
        # - Random alphanumeric (like "1221432HASdade")
        # - Very short names
        # - Names with many consecutive numbers
        
        # If current name is very short (less than 5 chars), consider renaming
        if len(current_name) < 5:
            return True
        
        # If current name is mostly numbers, consider renaming
        digit_count = sum(c.isdigit() for c in current_name)
        if digit_count > len(current_name) * 0.7:  # More than 70% digits
            return True
        
        # If current name has random-looking mix of upper/lower/numbers
        has_upper = any(c.isupper() for c in current_name)
        has_lower = any(c.islower() for c in current_name)
        has_digit = any(c.isdigit() for c in current_name)
        
        # Random-looking: has all three types mixed together
        if has_upper and has_lower and has_digit:
            # Check if it's not a normal camelCase or sentence
            if not current_name[0].isupper() or sum(c.isupper() for c in current_name) > 3:
                return True
        
        # If metadata title is significantly more descriptive (longer by 50%+)
        if len(metadata_title) > len(current_name) * 1.5:
            return True
        
        # Don't rename if current name looks intentional (proper words, etc.)
        return False
    
    def move_pdf(self, result):
        """Move PDF to its category folder and rename if needed"""
        source = Path(result['source'])
        
        # Validate category path
        category = result.get('category', 'Uncategorized')
        if not category or category == '':
            category = 'Uncategorized'
        
        category_path = self.ebooks_folder / category
        
        # Create category folder if it doesn't exist
        try:
            category_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"  ✗ Failed to create category folder {category}: {e}")
            # Fallback to Uncategorized
            category_path = self.ebooks_folder / 'Uncategorized'
            category_path.mkdir(parents=True, exist_ok=True)
        
        # Determine final filename with robust fallbacks
        final_filename = result.get('rename_to')  # Check for renamed version first
        
        if not final_filename:  # If no rename, try original filename
            final_filename = result.get('filename')
        
        if not final_filename:  # If still nothing, use source filename
            final_filename = source.name
        
        if not final_filename:  # Final fallback (should never happen)
            final_filename = f"unknown_{result.get('source', 'file')}.pdf"
        
        # Make sure final_filename is a string, not None
        final_filename = str(final_filename)
        
        # Destination file
        dest = category_path / final_filename
        
        # Handle duplicates
        if dest.exists():
            base = dest.stem
            ext = dest.suffix
            counter = 1
            while dest.exists():
                dest = category_path / f"{base}_{counter}{ext}"
                counter += 1
        
        # Move and rename file
        try:
            shutil.move(str(source), str(dest))
            if result.get('rename_to'):
                print(f"  ✓ Renamed and moved to: {dest.relative_to(self.ebooks_folder)}")
            else:
                print(f"  ✓ Moved to: {dest.relative_to(self.ebooks_folder)}")
        except Exception as e:
            print(f"  ✗ Failed to move {final_filename}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='AI-Powered PDF Organizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect Downloads folder for current user
  python pdf_organizer.py --ebooks "F:/ebooks"

  # Specify custom Downloads folder
  python pdf_organizer.py --downloads "C:/CustomDownloads" --ebooks "F:/ebooks"

  # Dry run (preview only)
  python pdf_organizer.py --ebooks "F:/ebooks" --dry-run
        """
    )

    # Get default Downloads folder for current user
    default_downloads = str(Path.home() / "Downloads")

    parser.add_argument('--downloads',
                       default=default_downloads,
                       help=f'Path to Downloads folder (default: {default_downloads})')
    parser.add_argument('--ebooks', required=True, help='Path to ebooks folder (e.g., F:/ebooks)')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without moving files')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--category-template', help='Path to category template JSON (default: project_root/category_template.json)')
    parser.add_argument('--export-template', action='store_true', help='Export current ebooks folder hierarchy to a template file and exit')

    args = parser.parse_args()

    # Show detected Downloads folder
    if args.downloads == default_downloads:
        print(f"Using auto-detected Downloads folder: {args.downloads}")

    # Use context manager to ensure cleanup
    with PDFOrganizer(
        downloads_folder=args.downloads,
        ebooks_folder=args.ebooks,
        api_key=args.api_key,
        dry_run=args.dry_run,
        category_template=args.category_template,
        require_api_key=not args.export_template
    ) as organizer:
        if args.export_template:
            organizer.export_category_template(args.category_template)
            print("Template export complete. No files were moved.")
            return

        organizer.organize_pdfs(confirm=not args.no_confirm)


if __name__ == "__main__":
    main()
