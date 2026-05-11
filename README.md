# pyPDFLibrarianSort

Python tools workspace for practical document and content-processing utilities.

The repository started as a PDF-focused project. It now includes conversion, extraction, organization, and publishing helpers, with a stronger focus on Markdown as the output format for downstream AI use.

## Current Direction

The main conversion tools are:

- `pptx_to_epub.py`: converts PowerPoint files into structured Markdown
- `pdf_to_epub.py`: converts text-based PDFs into structured Markdown

Existing PDF tools still in the repo:

- `organize_batch.py`: AI-assisted PDF organization
- `pdf_signature.py`: PDF signature placement with GUI support
- `watch_organizer.py`: watch-mode PDF organization

## Tool: PowerPoint To Markdown

`pptx_to_epub.py` converts `.pptx` files into Markdown by extracting slide text and preserving slide structure.

What it does:

- extracts text from slide titles, text boxes, and tables
- preserves slide order
- renders nested bullets as nested Markdown lists
- creates one Markdown section per slide
- supports a single PowerPoint file or an entire directory
- includes both GUI and CLI modes

GUI:

```bash
python pptx_to_epub.py
```

CLI:

```bash
python pptx_to_epub.py --input "C:\path\deck.pptx" --output-dir "C:\path\markdown"
python pptx_to_epub.py --input "C:\path\slides" --output-dir "C:\path\markdown"
```

## Tool: PDF To Markdown

`pdf_to_epub.py` converts text-based `.pdf` files into Markdown by extracting page text and inferring headings, paragraphs, lists, and simple code blocks.

What it does:

- extracts readable text from PDF pages
- infers heading levels from font size and emphasis
- merges wrapped lines into paragraphs
- renders detected lists as Markdown lists
- supports a single PDF file or an entire directory
- includes both GUI and CLI modes

What it does not do:

- OCR scanned or image-only PDFs
- preserve visual PDF layout exactly

GUI:

```bash
python pdf_to_epub.py
```

CLI:

```bash
python pdf_to_epub.py --input "C:\path\book.pdf" --output-dir "C:\path\markdown"
python pdf_to_epub.py --input "C:\path\pdfs" --output-dir "C:\path\markdown"
```

## Installation

```bash
git clone https://github.com/peterbamuhigire/pyPDFLibrarianSort.git
cd pyPDFLibrarianSort
pip install -r requirements.txt
```

Core dependencies for the Markdown converters:

- `python-pptx`
- `pdfplumber`
- `pypdf`

## Documentation

- [Project Brief](PROJECT_BRIEF.md)
- [Project Summary](docs/overview/PROJECT_SUMMARY.md)
- [Quick Start](docs/guides/QUICK_START.md)
- [Getting Started](docs/guides/GET_STARTED.md)
- [Features Summary](docs/features/FEATURES_SUMMARY.md)
- [PowerPoint To EPUB Guide](docs/guides/POWERPOINT_TO_EPUB_GUIDE.md)
- [PDF To EPUB Guide](docs/guides/PDF_TO_EPUB_GUIDE.md)
- [Web Interface Guide](docs/guides/WEB_INTERFACE_GUIDE.md)
- [PDF Signature Guide](docs/guides/SIGNATURE_GUIDE.md)

## Testing

```bash
python test_pptx_to_epub.py
python test_pdf_to_epub.py
python test_signature.py
```

## License

MIT License.
