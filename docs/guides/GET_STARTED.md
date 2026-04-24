# Getting Started

## Project Scope

This repository is no longer just a PDF project. It is being developed into a collection of Python utilities for document and content-processing workflows.

The first step in that broader direction is a PowerPoint-to-EPUB converter.

## Setup

### 1. Install Python

Use Python 3.8 or newer.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start With The New Tool

```bash
python pptx_to_epub.py
```

## PowerPoint To EPUB Workflow

The new tool:

1. opens one `.pptx` file or scans a whole directory
2. extracts text from slides
3. ignores images
4. builds an EPUB for each presentation
5. writes output into the directory you choose

## CLI Usage

Single file:

```bash
python pptx_to_epub.py --input "C:\presentations\deck.pptx" --output-dir "C:\books"
```

Directory mode:

```bash
python pptx_to_epub.py --input "C:\presentations" --output-dir "C:\books"
```

When using directory mode, the tool searches recursively for `.pptx` files and mirrors their relative structure into the output directory.

## Files To Know

- `pptx_to_epub.py`: new PowerPoint-to-EPUB GUI and CLI tool
- `test_pptx_to_epub.py`: smoke test for the new converter
- `organize_batch.py`: existing PDF organization tool
- `pdf_signature.py`: existing PDF signing tool

## Existing PDF Documentation

The repository still contains the previous PDF documentation for users who rely on those scripts. Those guides are now tool-specific references rather than the main identity of the project.

## Recommended First Test

Run:

```bash
python test_pptx_to_epub.py
```

Then open the GUI and convert a small sample PowerPoint deck.
