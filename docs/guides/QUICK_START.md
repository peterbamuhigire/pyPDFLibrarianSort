# Quick Start

## Fastest Way To Try The New Direction

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the new PowerPoint-to-EPUB GUI:

```bash
python pptx_to_epub.py
```

Then:

1. choose a single `.pptx` file or a directory of `.pptx` files
2. choose the output directory
3. click `Convert to EPUB`

## CLI Examples

Single PowerPoint:

```bash
python pptx_to_epub.py --input "C:\slides\deck.pptx" --output-dir "C:\exports\epubs"
```

Whole directory:

```bash
python pptx_to_epub.py --input "C:\slides" --output-dir "C:\exports\epubs"
```

## What The Tool Produces

- one EPUB per PowerPoint file
- one section per slide
- text-only extraction
- no embedded slide images

## Other Scripts Still In The Repo

The repository still includes PDF-specific utilities:

```bash
python organize_batch.py
python pdf_signature.py
python watch_setup.py
```

Those remain available, but they are no longer the only focus of the project.
