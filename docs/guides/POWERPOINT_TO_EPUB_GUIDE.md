# PowerPoint To EPUB Guide

## Purpose

`pptx_to_epub.py` converts PowerPoint presentations into EPUB books by extracting text from slides and ignoring images.

This is useful when you want to turn slide decks into readable ebook-style documents.

## What Gets Extracted

- slide titles
- text boxes
- table cell text
- paragraph content in slide order

## What Gets Ignored

- images
- decorative shapes without text
- non-text visual content

## GUI Usage

Run:

```bash
python pptx_to_epub.py
```

Then:

1. choose `Single PowerPoint file` or `Whole directory of PowerPoint files`
2. browse to the input file or folder
3. choose the output directory
4. click `Convert to EPUB`

## CLI Usage

Single file:

```bash
python pptx_to_epub.py --input "C:\slides\deck.pptx" --output-dir "C:\exports\epubs"
```

Directory mode:

```bash
python pptx_to_epub.py --input "C:\slides" --output-dir "C:\exports\epubs"
```

## Output Behavior

- each `.pptx` produces one `.epub`
- when converting a directory, `.pptx` files are found recursively
- relative folder structure is preserved inside the output directory
- slide order is preserved in the EPUB spine and table of contents

## EPUB Structure

For each presentation:

- the presentation becomes one EPUB
- each slide becomes one section or chapter
- slide titles are used as section headings where available
- slides without extractable text get a placeholder note

## Limitations

- supports `.pptx` files, not legacy `.ppt`
- image text is not OCR'd
- visual slide layout is not reproduced; this is text extraction, not design export

## Recommended Validation

Run the smoke test:

```bash
python test_pptx_to_epub.py
```
