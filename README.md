# pyPDFLibrarianSort

Python tools workspace for practical document and content-processing utilities.

The repository started as a PDF-focused project. It is now being expanded into a broader collection of Python scripts and desktop tools for file conversion, extraction, organization, and publishing workflows.

## Current Direction

The project is no longer limited to PDF operations. Existing PDF tools remain available, but the repository now serves as a home for multiple independent utilities.

The first expansion beyond PDFs is:

- `pptx_to_epub.py`: extract text from PowerPoint slides, ignore images, and export well-structured EPUB books

Existing PDF tools still in the repo:

- `organize_batch.py`: AI-assisted PDF organization
- `pdf_signature.py`: PDF signature placement with GUI support
- `watch_organizer.py`: watch-mode PDF organization

## New Tool: PowerPoint To EPUB

`pptx_to_epub.py` converts `.pptx` files into EPUBs by reading slide text only.

What it does:

- extracts text from slide titles, text boxes, and tables
- ignores images and other non-text content
- creates one EPUB section per slide
- supports a single PowerPoint file or an entire directory
- lets you choose the output directory
- includes both GUI and CLI modes

### GUI

```bash
python pptx_to_epub.py
```

From the GUI you can:

- choose one PowerPoint file or a whole folder
- choose the output directory
- run conversion with progress feedback

### CLI

Single file:

```bash
python pptx_to_epub.py --input "C:\path\deck.pptx" --output-dir "C:\path\epubs"
```

Whole directory:

```bash
python pptx_to_epub.py --input "C:\path\slides" --output-dir "C:\path\epubs"
```

When the input is a directory, the converter scans for `.pptx` files recursively and mirrors the relative folder structure inside the selected output directory.

## Installation

```bash
git clone https://github.com/peterbamuhigire/pyPDFLibrarianSort.git
cd pyPDFLibrarianSort
pip install -r requirements.txt
```

Core dependencies for the new PowerPoint tool:

- `python-pptx`
- `ebooklib`

## Documentation

### Project Docs

- [Project Brief](PROJECT_BRIEF.md)
- [Project Summary](docs/overview/PROJECT_SUMMARY.md)
- [Quick Start](docs/guides/QUICK_START.md)
- [Getting Started](docs/guides/GET_STARTED.md)
- [Features Summary](docs/features/FEATURES_SUMMARY.md)

### PowerPoint To EPUB

- [PowerPoint To EPUB Guide](docs/guides/POWERPOINT_TO_EPUB_GUIDE.md)

### Existing PDF Tools

These are still part of the repository, but they are no longer the entire project scope:

- [Web Interface Guide](docs/guides/WEB_INTERFACE_GUIDE.md)
- [PDF Signature Guide](docs/guides/SIGNATURE_GUIDE.md)
- [Watch Mode Guide](docs/guides/WATCH_MODE_README.md)
- [Smart Renaming Guide](docs/guides/SMART_RENAMING_GUIDE.md)

## Testing

PowerPoint converter smoke test:

```bash
python test_pptx_to_epub.py
```

Existing PDF signature tests:

```bash
python test_signature.py
```

## Roadmap

Planned direction for the repository:

- more document conversion tools
- more extraction and restructuring utilities
- more GUI-first scripts for non-technical users
- shared patterns for batch processing and output organization

## License

MIT License.
