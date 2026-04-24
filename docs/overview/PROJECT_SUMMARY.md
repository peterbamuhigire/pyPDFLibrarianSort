# pyPDFLibrarianSort - Project Summary

## Overview

`pyPDFLibrarianSort` is now a Python tools workspace for practical document and content-processing tasks.

The repository was originally centered on PDFs. That remains part of the codebase, but the project direction has changed: it will host multiple standalone utilities instead of being defined only by PDF workflows.

## Current Tooling

### New General Tooling

1. `pptx_to_epub.py`
   Converts PowerPoint presentations into EPUB books by extracting slide text and ignoring images.

### Existing PDF Tooling

1. `organize_batch.py`
   AI-assisted PDF organization and renaming.
2. `pdf_signature.py`
   GUI and CLI tool for placing signatures on PDFs.
3. `watch_organizer.py`
   Watches a folder and runs PDF organization automatically.

## PowerPoint To EPUB Tool

The first new non-PDF tool is designed for turning presentation decks into readable ebooks.

Capabilities:

- accepts one `.pptx` file or a whole directory
- extracts only text content from slides
- ignores images
- creates structured EPUB output
- preserves slide order
- supports GUI and CLI usage
- lets the user choose the output directory

## Why The Project Is Being Reframed

The old positioning was too narrow for the direction of the repository. The codebase already contains several separate workflows, and future tools will expand beyond PDFs. Reframing the project now makes the repository structure, documentation, and user expectations align with the actual roadmap.

## Repository Entry Points

### Recommended for the new tool

```bash
python pptx_to_epub.py
```

### Existing PDF utilities

```bash
python organize_batch.py
python pdf_signature.py
python watch_setup.py
```

## Dependencies

For the PowerPoint-to-EPUB workflow:

- `python-pptx`
- `ebooklib`

For legacy PDF workflows:

- `pypdf`
- `reportlab`
- `Pillow`
- `Flask`
- `watchdog`

## Documentation Map

- [README](../../README.md)
- [Project Brief](../../PROJECT_BRIEF.md)
- [Quick Start](../guides/QUICK_START.md)
- [Getting Started](../guides/GET_STARTED.md)
- [Features Summary](../features/FEATURES_SUMMARY.md)
- [PowerPoint To EPUB Guide](../guides/POWERPOINT_TO_EPUB_GUIDE.md)

Legacy PDF docs are still present in the `docs/guides/` directory for the tools that already existed before this repositioning.
