"""
Smoke tests for the PDF to Markdown converter.

Run with: python test_pdf_to_epub.py
"""

import sys
import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from pdf_to_epub import PdfToMarkdownConverter


def create_sample_pdf(target: Path) -> Path:
    pdf = canvas.Canvas(str(target), pagesize=letter)
    pdf.setTitle("Sample PDF Book")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, 720, "Sample PDF Book")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(72, 690, "Getting Started")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 666, "This is the first paragraph on page one.")
    pdf.drawString(72, 650, "It should appear in the Markdown output.")
    pdf.drawString(72, 626, "1. First numbered item")
    pdf.drawString(72, 610, "2. Second numbered item")
    pdf.save()
    return target


def assert_contains(text: str, expected: str):
    if expected not in text:
        raise AssertionError(f"Expected to find {expected!r}")


def test_single_file_conversion():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pdf_path = create_sample_pdf(temp_path / "book.pdf")
        output_dir = temp_path / "out"

        converter = PdfToMarkdownConverter()
        results = converter.convert(pdf_path, output_dir)

        if len(results) != 1:
            raise AssertionError(f"Expected 1 Markdown file, got {len(results)}")

        markdown_path = results[0]
        if not markdown_path.exists():
            raise AssertionError("Markdown file was not created")

        content = markdown_path.read_text(encoding="utf-8")
        assert_contains(content, "# Sample PDF Book")
        assert_contains(content, "## Getting Started")
        assert_contains(content, "This is the first paragraph on page one. It should appear in the Markdown output.")
        assert_contains(content, "1. First numbered item")


def main():
    tests = [("Single File Conversion", test_single_file_conversion)]
    failures = 0

    for name, func in tests:
        try:
            func()
            print(f"OK {name}")
        except Exception as exc:
            failures += 1
            print(f"FAIL {name}: {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
