#!/usr/bin/env python3
"""
PDF Organizer - Batch Version
Processes ALL PDFs in a single API call to save costs
Cost: ~$0.05 per batch vs $0.05 per PDF!
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

class BatchPDFOrganizer:
    def __init__(self, downloads_folder, ebooks_folder, api_key=None, dry_run=False, category_template=None):
        """Initialize batch PDF organizer"""
        if not ebooks_folder:
            raise ValueError("ebooks_folder is required")
        if not downloads_folder:
            raise ValueError("downloads_folder is required")

        self.downloads_folder = Path(downloads_folder)
        self.ebooks_folder = Path(ebooks_folder)
        self.dry_run = dry_run
        default_template = Path(__file__).resolve().parent / "category_template.json"
        self.category_template_path = Path(category_template) if category_template else default_template
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')

        if not self.api_key:
            raise ValueError("Gemini API key required")

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)
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
        """Analyze existing folder structure"""
        print("Analyzing existing ebooks folder structure...")
        categories = {}
        
        for root, dirs, files in os.walk(self.ebooks_folder):
            rel_path = Path(root).relative_to(self.ebooks_folder)
            if rel_path == Path('.'):
                continue
            
            pdf_count = len([f for f in files if f.lower().endswith('.pdf')])
            path_parts = rel_path.parts
            category_path = '/'.join(path_parts)
            
            categories[category_path] = {
                'count': pdf_count,
                'depth': len(path_parts)
            }
        
        if categories:
            print(f"\nFound {len(categories)} existing categories")
            # Show top categories
            by_depth = defaultdict(list)
            for cat, info in categories.items():
                by_depth[info['depth']].append((cat, info['count']))
            
            for depth in sorted(by_depth.keys())[:3]:  # Show first 3 levels
                print(f"\nLevel {depth}:")
                for cat, count in sorted(by_depth[depth])[:5]:  # Top 5 per level
                    print(f"  • {cat} ({count} PDFs)")
        else:
            print("No existing categories found")
        
        return categories

    def load_category_template(self):
        """Load predefined category hierarchy if present"""
        template_path = self.category_template_path
        if not template_path or not Path(template_path).exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  ⚠ Failed to load category template ({template_path}): {e}")
            return None
        
        categories = {}
        for entry in data.get('categories', []):
            raw_path = entry.get('path')
            if not raw_path:
                continue
            path_str = str(raw_path).replace('\\', '/').strip('/')
            depth = entry.get('depth') or len(path_str.split('/'))
            categories[path_str] = {
                'count': entry.get('count', 0),
                'depth': depth
            }
        
        print(f"Using category template: {template_path} ({len(categories)} categories)")
        return categories

    def load_or_analyze_categories(self):
        """Prefer template, then merge live counts"""
        template_categories = self.load_category_template()
        if template_categories:
            existing = self.analyze_existing_structure()
            for path, info in existing.items():
                if path in template_categories:
                    template_categories[path]['count'] = info.get('count', template_categories[path].get('count', 0))
                else:
                    template_categories[path] = info
            return template_categories
        return self.analyze_existing_structure()
    
    def get_pdf_info(self, pdf_path):
        """Get basic info from PDF"""
        try:
            reader = PdfReader(pdf_path)
            meta = reader.metadata
            title = meta.title if meta and meta.title else pdf_path.stem
            author = meta.author if meta and meta.author else ""
        except:
            title = pdf_path.stem
            author = ""
        
        return {
            'path': str(pdf_path),
            'filename': pdf_path.name,
            'stem': pdf_path.stem,
            'title': title,
            'author': author
        }
    
    def batch_categorize_all(self, pdf_list, categories):
        """Categorize ALL PDFs in a single API call"""
        
        # Build category structure text
        category_text = self.build_category_text(categories)
        
        # Build PDF list for prompt
        pdf_descriptions = []
        for i, pdf_info in enumerate(pdf_list, 1):
            # Clean filename for better parsing
            name = pdf_info['filename'][:100]  # Limit length
            desc = f"{i}. {name}"
            if pdf_info['title'] and pdf_info['title'] != pdf_info['stem']:
                title = str(pdf_info['title'])[:100]
                desc += f" | Title: {title}"
            pdf_descriptions.append(desc)
        
        pdf_list_text = "\n".join(pdf_descriptions)
        
        # Create mega-prompt with explicit formatting
        prompt = f"""You are organizing {len(pdf_list)} PDFs. Categorize each one.

EXISTING CATEGORIES:
{category_text}

PDFs TO CATEGORIZE:
{pdf_list_text}

IMPORTANT: Return ONLY valid JSON. No explanations, no markdown, just pure JSON.

For each PDF, provide:
- number: PDF number (1-{len(pdf_list)})
- category: matching existing category structure (e.g., "Computer & ICT/Programming/Python")
- confidence: "high" or "medium" or "low"

Return a JSON array like this (NO markdown, NO backticks, ONLY JSON):
[
{{"number":1,"category":"Computer & ICT/Programming","confidence":"high"}},
{{"number":2,"category":"Business/Finance","confidence":"medium"}}
]

CRITICAL: 
- Return ONLY the JSON array
- No markdown code blocks
- No explanations
- Valid JSON only"""

        print("\n🚀 Sending batch request to AI (this may take 30-60 seconds)...")
        print(f"📊 Processing {len(pdf_list)} PDFs in one call...")
        
        try:
            message = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 8000
                }
            )
            
            response_text = (message.text or "").strip()
            
            # Aggressive cleaning
            # Remove any markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Remove any leading/trailing text before/after JSON array
            # Find first [ and last ]
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
            
            print(f"\n📝 Response preview: {response_text[:200]}...")
            
            # Try to parse
            try:
                categorizations = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"\n⚠️ JSON parse error at position {e.pos}")
                print(f"   Error: {e.msg}")
                print(f"\n   Problematic section: ...{response_text[max(0,e.pos-50):e.pos+50]}...")
                
                # Try to fix common issues
                print("\n🔧 Attempting to fix JSON...")
                
                # Fix: trailing commas
                response_text = response_text.replace(',]', ']').replace(',}', '}')
                
                # Fix: single quotes to double quotes
                response_text = response_text.replace("'", '"')
                
                # Try again
                categorizations = json.loads(response_text)
            
            if not isinstance(categorizations, list):
                print(f"⚠️ Expected list, got {type(categorizations)}")
                return []
            
            print(f"✅ Received categorizations for {len(categorizations)} PDFs")
            
            return categorizations
            
        except json.JSONDecodeError as e:
            print(f"\n❌ Could not parse AI response as JSON")
            print(f"   Error: {e}")
            print(f"\n   Response was ({len(response_text)} chars):")
            print(f"   {response_text[:500]}")
            print(f"   ...")
            print(f"   {response_text[-500:]}")
            
            # Fallback: Use simple categorization
            print("\n🔄 Falling back to simple categorization...")
            return self.simple_fallback_categorization(pdf_list)
            
        except Exception as e:
            print(f"❌ Batch categorization failed: {e}")
            import traceback
            print(traceback.format_exc())
            
            # Fallback
            print("\n🔄 Falling back to simple categorization...")
            return self.simple_fallback_categorization(pdf_list)
    
    def simple_fallback_categorization(self, pdf_list):
        """Simple fallback: categorize based on filename keywords"""
        print("Using keyword-based categorization...")
        
        categorizations = []
        
        # Simple keyword mapping
        keywords = {
            'python': 'Computer & ICT/Programming/Python',
            'java': 'Computer & ICT/Programming/Java',
            'javascript': 'Computer & ICT/Programming/JavaScript',
            'web': 'Computer & ICT/Web Development',
            'business': 'Business/General',
            'finance': 'Business/Finance',
            'accounting': 'Business/Accounting',
            'tax': 'Business/Accounting/Tax',
            'science': 'Science/General',
            'physics': 'Science/Physics',
            'math': 'Science/Mathematics',
            'biology': 'Science/Biology',
        }
        
        for i, pdf_info in enumerate(pdf_list, 1):
            filename_lower = pdf_info['filename'].lower()
            category = 'Uncategorized'
            
            # Check for keywords
            for keyword, cat in keywords.items():
                if keyword in filename_lower:
                    category = cat
                    break
            
            categorizations.append({
                'number': i,
                'category': category,
                'confidence': 'low',
                'rename': None
            })
        
        print(f"✓ Categorized {len(categorizations)} PDFs using keywords")
        return categorizations
    
    def build_category_text(self, categories):
        """Build concise category structure text"""
        if not categories:
            return "No existing categories. Create new structure."
        
        lines = ["EXISTING CATEGORIES:"]
        by_depth = defaultdict(list)
        
        for cat, info in categories.items():
            by_depth[info['depth']].append((cat, info['count']))
        
        for depth in sorted(by_depth.keys()):
            lines.append(f"\nLevel {depth}:")
            for cat, count in sorted(by_depth[depth]):
                lines.append(f"  - {cat} ({count} PDFs)")
        
        return "\n".join(lines)
    
    def organize_pdfs(self):
        """Main batch organization method"""
        
        # Find all PDFs
        print(f"\nScanning {self.downloads_folder} for PDFs...")
        pdf_files = []
        for root, dirs, files in os.walk(self.downloads_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(Path(root) / file)
        
        if not pdf_files:
            print("No PDFs found")
            return []
        
        print(f"Found {len(pdf_files)} PDFs")
        
        # Analyze structure (template-aware)
        categories = self.load_or_analyze_categories()
        
        # Get info for all PDFs
        print("\n📋 Reading PDF metadata...")
        pdf_list = []
        for pdf_path in pdf_files:
            info = self.get_pdf_info(pdf_path)
            pdf_list.append(info)
        
        print(f"✅ Read metadata from {len(pdf_list)} PDFs")
        
        # Check if we need to chunk
        CHUNK_SIZE = 150  # Process 150 PDFs at a time for reliability
        
        if len(pdf_list) > CHUNK_SIZE:
            print(f"\n⚠️ Large batch detected ({len(pdf_list)} PDFs)")
            print(f"📦 Will process in chunks of {CHUNK_SIZE} for reliability")
            print(f"💰 Estimated cost: ${(len(pdf_list) // CHUNK_SIZE + 1) * 0.05:.2f}")
            print()
            
            proceed = input(f"Process {len(pdf_list)} PDFs in {(len(pdf_list) // CHUNK_SIZE + 1)} chunks? (y/n): ")
            if proceed.lower() != 'y':
                print("Cancelled")
                return []
            
            # Process in chunks
            all_categorizations = []
            for i in range(0, len(pdf_list), CHUNK_SIZE):
                chunk = pdf_list[i:i+CHUNK_SIZE]
                chunk_num = (i // CHUNK_SIZE) + 1
                total_chunks = (len(pdf_list) // CHUNK_SIZE) + 1
                
                print(f"\n📦 Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} PDFs)...")
                
                categorizations = self.batch_categorize_all(chunk, categories)
                
                if categorizations:
                    # Adjust numbers for offset
                    for cat in categorizations:
                        cat['number'] += i
                    all_categorizations.extend(categorizations)
                else:
                    print(f"⚠️ Chunk {chunk_num} failed, using fallback")
            
            categorizations = all_categorizations
        else:
            # Batch categorize - ONE API CALL!
            categorizations = self.batch_categorize_all(pdf_list, categories)
        
        if not categorizations:
            print("❌ Categorization failed")
            return []
        
        # Match categorizations to PDFs
        results = []
        categorization_map = {cat['number']: cat for cat in categorizations}
        
        for i, pdf_info in enumerate(pdf_list, 1):
            cat_result = categorization_map.get(i, {
                'category': 'Uncategorized',
                'confidence': 'low',
                'rename': None
            })
            
            results.append({
                'source': pdf_info['path'],
                'filename': pdf_info['filename'],
                'category': cat_result.get('category', 'Uncategorized'),
                'confidence': cat_result.get('confidence', 'low'),
                'rename_to': cat_result.get('rename')
            })
        
        # Show summary
        print("\n" + "="*70)
        print("CATEGORIZATION SUMMARY")
        print("="*70)
        
        category_counts = defaultdict(list)
        for r in results:
            category_counts[r['category']].append(r)
        
        for category, items in sorted(category_counts.items()):
            print(f"\n{category}/ ({len(items)} files)")
            for item in items[:3]:  # Show first 3
                name = item['filename'][:60]  # Truncate long names
                if item['rename_to']:
                    name = f"{item['filename'][:30]} → {item['rename_to'][:30]}"
                print(f"  • {name}")
            if len(items) > 3:
                print(f"  ... and {len(items) - 3} more")
        
        if self.dry_run:
            print("\n[DRY RUN] No files were moved")
            return results
        
        # Confirm
        response = input("\nProceed with moving files? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled")
            return results
        
        # Move files
        print("\n📦 Moving files...")
        for result in results:
            self.move_pdf(result)
        
        self.log['organized_files'].extend(results)
        self.save_log()
        
        print(f"\n✅ Organized {len(results)} PDFs!")
        
        return results
    
    def move_pdf(self, result):
        """Move PDF to category folder"""
        source = Path(result['source'])
        category = result.get('category', 'Uncategorized')
        category_path = self.ebooks_folder / category
        
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Determine filename
        if result.get('rename_to'):
            filename = result['rename_to']
            if not filename.endswith('.pdf'):
                filename += '.pdf'
        else:
            filename = result['filename']
        
        dest = category_path / filename
        
        # Handle duplicates
        if dest.exists():
            base = dest.stem
            ext = dest.suffix
            counter = 1
            while dest.exists():
                dest = category_path / f"{base}_{counter}{ext}"
                counter += 1
        
        # Move
        try:
            shutil.move(str(source), str(dest))
            print(f"  ✓ {filename}")
        except Exception as e:
            print(f"  ✗ {filename}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Batch PDF Organizer (Cost-Effective)')

    default_downloads = str(Path.home() / "Downloads")

    parser.add_argument('--downloads', default=default_downloads,
                       help=f'Downloads folder (default: {default_downloads})')
    parser.add_argument('--ebooks', required=True, help='Ebooks folder (e.g., F:/ebooks)')
    parser.add_argument('--api-key', help='Gemini API key')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--category-template', help='Path to category template JSON (default: project_root/category_template.json)')

    args = parser.parse_args()

    print("="*70)
    print("  PDF Organizer - BATCH MODE (Cost-Effective)")
    print("="*70)
    print("\n💰 This version uses ONE API call for all PDFs")
    print(f"   Cost: ~$0.05-0.10 total vs $0.05 per PDF!")
    print()

    # Use context manager to ensure cleanup
    with BatchPDFOrganizer(
        downloads_folder=args.downloads,
        ebooks_folder=args.ebooks,
        api_key=args.api_key,
        dry_run=args.dry_run,
        category_template=args.category_template
    ) as organizer:
        organizer.organize_pdfs()


if __name__ == "__main__":
    main()
