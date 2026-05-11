# PDF To Markdown Guide

## Purpose

`pdf_to_epub.py` converts text-based PDF documents into Markdown files.

This is useful when you want a cleaner text format that AI tools and documentation workflows can work with directly.

## What Gets Extracted

- document title from PDF metadata when available
- headings inferred from font size and emphasis
- paragraph text with wrapped lines merged back together
- ordered and unordered lists
- simple indented monospace code blocks

## What Gets Ignored

- original PDF page layout
- images and non-text visual content
- OCR for scanned PDFs

## GUI Usage

Run:

```bash
python pdf_to_epub.py
```

Then:

1. choose `Single PDF file` or `Whole directory of PDF files`
2. browse to the input file or folder
3. choose the output directory
4. click `Convert to Markdown`

## CLI Usage

Single file:

```bash
python pdf_to_epub.py --input "C:\books\guide.pdf" --output-dir "C:\exports\markdown"
```

Directory mode:

```bash
python pdf_to_epub.py --input "C:\books" --output-dir "C:\exports\markdown"
```

## Output Behavior

- each `.pdf` produces one `.md`
- when converting a directory, `.pdf` files are found recursively
- relative folder structure is preserved inside the output directory
- the converter tries to infer document headings, paragraphs, lists, and code blocks

## Limitations

- best results come from text-based PDFs
- scanned or image-only PDFs may produce poor output unless OCR is added first
- visual formatting is simplified into readable Markdown

## Recommended Validation

```bash
python test_pdf_to_epub.py
```
