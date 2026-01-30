# CLAUDE.md

This file provides guidance to AI coding assistants when working with code in this repository.

## Project Overview

pyPDFLibrarianSort is an AI-powered PDF library organizer that uses AI (Gemini, Anthropic, or DeepSeek) to automatically categorize and organize PDFs. The key innovation is **batch processing**: processing 200 PDFs in one API call costs $0.10 vs $10 for individual processing (100x cost savings).

## Core Architecture

### Two Processing Modes

**Single Mode (`pdf_organizer.py`)**

- Processes PDFs one at a time with individual API calls
- Higher accuracy (95%) but expensive ($0.05 per PDF)
- Uses `PDFOrganizer` class
- Best for important documents requiring precision

**Batch Mode (`pdf_organizer_batch.py`)** (Recommended)

- Processes ALL PDFs in a single API call
- Cost-effective ($0.05-0.10 for 200+ PDFs)
- Uses `BatchPDFOrganizer` class
- Handles automatic chunking for large batches (500+ PDFs)
- 90-95% accuracy with massive cost savings

### Key Components

**Main Classes:**

- `PDFOrganizer` (pdf_organizer.py) - Single-file processing engine
- `BatchPDFOrganizer` (pdf_organizer_batch.py) - Batch processing engine

**Interactive Launchers:**

- `organize_simple.py` - Interactive setup for single mode
- `organize_batch.py` - Interactive setup for batch mode (recommended)
- `watch_setup.py` - Interactive setup for watch mode (auto-organize)
- `watch_organizer.py` - Watch mode script (monitors folder for new PDFs)
- `web_interface.py` - Modern web UI with drag & drop (NEW!)

**Category System:**

- `category_template.json` - Pre-generated hierarchical category structure
- `fetch-categories.py` - Generates category template from existing ebooks folder
- Both organizers analyze existing folder structure and preserve deep hierarchies (up to 3+ levels)

**Other Tools:**

- `pdf_organizer_gui.py` - Tkinter GUI interface (legacy)
- `test_basic.py` - Diagnostic tests for dependencies and basic functionality
- `diagnose.py` - System diagnostic tool
- `setup.py` - Interactive setup wizard

### Data Flow

1. **Discovery**: Recursively find PDFs in Downloads folder
2. **Metadata Extraction**: Use pypdf to extract title, author from PDF metadata
3. **Structure Analysis**: Scan existing ebooks folder hierarchy OR load category_template.json
4. **AI Categorization**: Send batch of filenames + metadata + category structure to Gemini
5. **Response Parsing**: AI returns JSON with category paths and suggested filenames
6. **File Operations**: Move PDFs to appropriate folders with smart renaming

### Category Template System

The organizers can use a pre-generated category template (`category_template.json`) to avoid scanning large ebooks folders every time:

```json
{
  "generated_at": "2026-01-11T10:00:00",
  "ebooks_root": "F:/ebooks",
  "category_count": 47,
  "categories": [
    {"path": "Computer & ICT/Programming/Python", "depth": 3, "count": 34},
    {"path": "Business/Finance", "depth": 2, "count": 45}
  ]
}
```

To generate from an existing ebooks folder:

```bash
cd /path/to/ebooks
python /path/to/pyPDFLibrarianSort/fetch-categories.py
```

Both `PDFOrganizer` and `BatchPDFOrganizer` support `category_template` parameter.

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_basic.py

# System diagnostics
python diagnose.py

# Setup wizard
python setup.py
```

### Usage

```bash
# Web Interface (recommended for best user experience) ✨ NEW!
python web_interface.py
# Then open browser to http://localhost:5000

# Batch mode (recommended for one-time organization)
python organize_batch.py

# Single mode
python organize_simple.py

# Watch mode (recommended for continuous auto-organization)
python watch_setup.py
# Or directly:
python watch_organizer.py --ebooks F:/ebooks --provider gemini --api-key YOUR_KEY

# GUI mode (legacy)
python pdf_organizer_gui.py

# Direct invocation (batch)
python pdf_organizer_batch.py

# Direct invocation (single)
python pdf_organizer.py --downloads /path/to/downloads --ebooks /path/to/ebooks
```

### Generate category template

```bash
# From your ebooks folder
cd F:/ebooks
python C:/path/to/pyPDFLibrarianSort/fetch-categories.py
# Creates category_template.json in current directory

# Copy to project root for use by organizers
copy category_template.json C:/path/to/pyPDFLibrarianSort/
```

## Important Implementation Details

### API Key Management

- Supports three AI providers: Gemini, Anthropic (Claude), and DeepSeek
- Interactive launchers prompt for provider selection and corresponding API key
- Can be passed as parameter: `PDFOrganizer(api_key="...", provider="gemini")`
- Can optionally be stored in `~/.pdf_organizer_settings.json` (by setup.py)
- Provider-specific API key URLs:
  - Gemini: https://aistudio.google.com/app/apikey
  - Anthropic: https://console.anthropic.com/
  - DeepSeek: https://platform.deepseek.com/

### File Operations

- All operations are local - PDFs never uploaded to API
- Only filenames and metadata sent to AI provider (Gemini, Anthropic, or DeepSeek)
- Uses `shutil.move()` for file operations
- Maintains `organization_log.json` in ebooks folder for tracking
- Dry-run mode available: `PDFOrganizer(dry_run=True)`

### Category Hierarchy

- Preserves multi-level folder structures (e.g., "Computer & ICT/Programming/Python")
- AI receives complete existing structure to maintain consistency
- Creates new categories when appropriate
- Falls back to "Uncategorized" for unclear PDFs

### Error Handling

- PDFs that fail to read skip gracefully
- API errors reported but don't stop batch processing
- Validation ensures required folders exist before processing
- Comprehensive error messages for common issues

## Testing

```bash
# Run basic diagnostic tests
python test_basic.py

# Test with dry-run (no files moved)
python -c "from pdf_organizer import PDFOrganizer; o = PDFOrganizer('downloads', 'ebooks', dry_run=True); o.organize_pdfs()"
```

## Dependencies

Runtime dependencies (see requirements.txt):

- `google-generativeai>=0.7.2` - Gemini AI API client
- `anthropic>=0.36.0` - Anthropic (Claude) API client
- `openai>=1.0.0` - OpenAI-compatible client (for DeepSeek)
- `pypdf>=3.17.0` - PDF metadata extraction
- `watchdog>=3.0.0` - File system monitoring (for watch mode)
- `flask>=3.0.0` - Web framework (for web interface)
- `flask-cors>=4.0.0` - CORS support (for web interface)

Optional (for legacy GUI):

- `tkinter` - Usually included with Python

Note: `pdfplumber` is imported in test_basic.py but not used in production code.

## Configuration Files

- `requirements.txt` - Python package dependencies
- `setup.py` - Interactive setup wizard
- `category_template.json` - Pre-generated category hierarchy (optional)
- `~/.pdf_organizer_settings.json` - User settings (created by setup.py)
- `organization_log.json` - Created in ebooks folder, tracks organized files

## Platform Support

- Cross-platform: Windows, macOS, Linux
- Batch scripts for Windows: `run_gui.bat`, `START_HERE.bat`, etc.
- Shell scripts for Unix: `run_gui.sh`
