# pyPDFLibrarianSort - Project Brief

## 30-Second Overview

`pyPDFLibrarianSort` is now a broader Python tools repository for document and content-processing workflows.

It started as a PDF project, but it is being repositioned into a workspace for multiple utilities. The current expansion starts with a PowerPoint-to-EPUB converter that extracts slide text and generates readable EPUB books through a GUI or CLI.

## Current Product Shape

The repository now contains:

1. document conversion tools
2. extraction and restructuring scripts
3. legacy PDF workflow tools already built in the project

## First Non-PDF Tool

### PowerPoint To EPUB

`pptx_to_epub.py`:

1. reads `.pptx` files
2. extracts text from slides
3. ignores images
4. creates structured EPUB output
5. supports one file or a whole directory
6. lets the user choose the output directory
7. includes a desktop GUI and CLI mode

## Existing Tool Families

### PDF Utilities

- AI-assisted PDF organization
- PDF signature placement
- watch-mode PDF automation

These remain supported, but they no longer define the entire project.

## Target Users

- people who need desktop-friendly Python tools for document workflows
- researchers and educators converting presentation material into reading formats
- office users who want batch conversion tools without complex setup
- users who still need the existing PDF utilities

## Technical Stack

- Python 3.x
- `python-pptx` for reading PowerPoint slides
- `ebooklib` for EPUB generation
- `tkinter` for desktop GUI workflows
- existing PDF stack for legacy tools: `pypdf`, `reportlab`, `Pillow`, `Flask`, `watchdog`

## Immediate Direction

1. reposition the repo as a multi-tool Python workspace
2. ship the PowerPoint-to-EPUB converter as the first expansion
3. keep existing PDF tools available as part of the wider toolkit

## Key Documents

- [README.md](README.md)
- [Quick Start](docs/guides/QUICK_START.md)
- [Getting Started](docs/guides/GET_STARTED.md)
- [Project Summary](docs/overview/PROJECT_SUMMARY.md)
- [PowerPoint To EPUB Guide](docs/guides/POWERPOINT_TO_EPUB_GUIDE.md)

## Status

Active development, with the repository transitioning from a PDF-specific product into a general Python tools collection.
