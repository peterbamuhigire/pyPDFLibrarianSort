"""
Smoke tests for the PowerPoint to EPUB converter.

Run with: python test_pptx_to_epub.py
"""

import sys
import tempfile
import zipfile
from pathlib import Path

from pptx import Presentation

from pptx_to_epub import PowerPointToEpubConverter


def create_sample_pptx(target: Path) -> Path:
    presentation = Presentation()

    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "Introduction"
    slide.placeholders[1].text = "Overview paragraph\nFirst bullet\nSecond bullet"

    slide2 = presentation.slides.add_slide(presentation.slide_layouts[5])
    textbox = slide2.shapes.add_textbox(left=1000000, top=1200000, width=6000000, height=3000000)
    frame = textbox.text_frame
    frame.text = "Body-only slide"
    frame.add_paragraph().text = "Follow-up point"

    presentation.save(target)
    return target


def assert_contains(text: str, expected: str):
    if expected not in text:
        raise AssertionError(f"Expected to find {expected!r}")


def test_single_file_conversion():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pptx_path = create_sample_pptx(temp_path / "deck.pptx")
        output_dir = temp_path / "out"

        converter = PowerPointToEpubConverter()
        results = converter.convert(pptx_path, output_dir)

        if len(results) != 1:
            raise AssertionError(f"Expected 1 EPUB, got {len(results)}")

        epub_path = results[0]
        if not epub_path.exists():
            raise AssertionError("EPUB file was not created")

        with zipfile.ZipFile(epub_path, "r") as archive:
            names = set(archive.namelist())
            if "EPUB/slide_001.xhtml" not in names:
                raise AssertionError("First slide chapter missing from EPUB")
            if "EPUB/nav.xhtml" not in names:
                raise AssertionError("Navigation file missing from EPUB")

            chapter = archive.read("EPUB/slide_001.xhtml").decode("utf-8")
            assert_contains(chapter, "Introduction")
            assert_contains(chapter, "Overview paragraph")


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
