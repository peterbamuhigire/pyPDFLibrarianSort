#!/usr/bin/env python3
"""
PowerPoint to EPUB converter.

Extracts text content from `.pptx` slides, ignores images, and builds
well-structured EPUB files. Supports single-file and whole-directory
processing with both CLI and tkinter GUI entry points.
"""

from __future__ import annotations

import argparse
import html
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue

from ebooklib import epub
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER


HTML_TEMPLATE = """\
<html>
  <head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="styles/main.css"/>
  </head>
  <body>
    <section class="slide">
      <header>
        <p class="slide-number">Slide {slide_number}</p>
        <h1>{title}</h1>
      </header>
      {body}
    </section>
  </body>
</html>
"""

CSS_CONTENT = """
body {
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.6;
  margin: 0;
  padding: 0;
  color: #1f2933;
  background: #fbfaf7;
}

.slide {
  padding: 2.2rem 1.4rem 2.8rem;
}

header {
  border-bottom: 1px solid #d9d3c7;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
}

.slide-number {
  color: #7b8794;
  font-size: 0.9rem;
  letter-spacing: 0.04em;
  margin: 0 0 0.35rem;
  text-transform: uppercase;
}

h1 {
  color: #102a43;
  font-size: 1.6rem;
  margin: 0;
}

h2 {
  color: #243b53;
  font-size: 1.1rem;
  margin: 1.4rem 0 0.4rem;
}

p {
  margin: 0.45rem 0;
}

ul {
  margin: 0.5rem 0 0.8rem 1.2rem;
  padding: 0;
}

li {
  margin: 0.25rem 0;
}

.empty-slide {
  color: #7b8794;
  font-style: italic;
}
"""


@dataclass
class SlideText:
    title: str
    blocks: list[dict]


def iter_text_shapes(shapes):
    """Yield shapes that contribute text, including text inside groups."""
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from iter_text_shapes(shape.shapes)
            continue

        if getattr(shape, "has_table", False):
            yield shape
            continue

        if getattr(shape, "has_text_frame", False):
            yield shape


def clean_text(value: str) -> str:
    """Normalize whitespace while keeping intentional line breaks collapsed."""
    return " ".join(value.replace("\u00a0", " ").split())


def paragraph_to_text(paragraph) -> str:
    """Return plain text from a PowerPoint paragraph."""
    runs = "".join(run.text for run in paragraph.runs) if paragraph.runs else paragraph.text
    return clean_text(runs or "")


def placeholder_is_title(shape) -> bool:
    """Check whether a placeholder shape is a title placeholder."""
    if not getattr(shape, "is_placeholder", False):
        return False

    try:
        placeholder_type = shape.placeholder_format.type
    except Exception:
        return False

    return placeholder_type in {
        PP_PLACEHOLDER.TITLE,
        PP_PLACEHOLDER.CENTER_TITLE,
        PP_PLACEHOLDER.SUBTITLE,
    }


def extract_shape_blocks(shape) -> list[dict]:
    """Extract paragraph-level blocks from a text shape or table."""
    blocks: list[dict] = []

    if getattr(shape, "has_table", False):
        for row in shape.table.rows:
            row_text = " | ".join(
                text for text in (clean_text(cell.text) for cell in row.cells) if text
            )
            if row_text:
                blocks.append({"kind": "paragraph", "text": row_text, "level": 0})
        return blocks

    if not getattr(shape, "has_text_frame", False):
        return blocks

    for paragraph in shape.text_frame.paragraphs:
        text = paragraph_to_text(paragraph)
        if not text:
            continue
        level = max(0, int(getattr(paragraph, "level", 0) or 0))
        blocks.append({"kind": "list" if level > 0 else "paragraph", "text": text, "level": level})
    return blocks


def extract_slide_text(slide, slide_number: int) -> SlideText:
    """Extract structured text from one slide."""
    title = ""
    blocks: list[dict] = []

    for shape in iter_text_shapes(slide.shapes):
        shape_blocks = extract_shape_blocks(shape)
        if not shape_blocks:
            continue

        if placeholder_is_title(shape) and not title:
            title = shape_blocks[0]["text"]
            shape_blocks = shape_blocks[1:]

        blocks.extend(shape_blocks)

    if not title:
        title = f"Slide {slide_number}"

    return SlideText(title=title, blocks=blocks)


def blocks_to_html(blocks: list[dict]) -> str:
    """Render extracted blocks into XHTML-safe markup."""
    if not blocks:
        return '<p class="empty-slide">This slide has no extractable text.</p>'

    parts: list[str] = []
    list_open = False

    for block in blocks:
        text = html.escape(block["text"])
        if block["kind"] == "list":
            if not list_open:
                parts.append("<ul>")
                list_open = True
            parts.append(f"<li>{text}</li>")
            continue

        if list_open:
            parts.append("</ul>")
            list_open = False
        parts.append(f"<p>{text}</p>")

    if list_open:
        parts.append("</ul>")

    return "\n".join(parts)


def presentation_title(presentation: Presentation, source_path: Path) -> str:
    """Choose the best available book title."""
    core_title = clean_text(getattr(presentation.core_properties, "title", "") or "")
    if core_title:
        return core_title

    for index, slide in enumerate(presentation.slides, start=1):
        extracted = extract_slide_text(slide, index)
        if extracted.title and not extracted.title.startswith("Slide "):
            return extracted.title

    return source_path.stem.replace("_", " ").strip() or source_path.stem


class PowerPointToEpubConverter:
    """Convert PowerPoint files into EPUBs."""

    def extract_slides(self, pptx_path: Path) -> tuple[str, list[SlideText]]:
        presentation = Presentation(str(pptx_path))
        title = presentation_title(presentation, pptx_path)
        slides = [
            extract_slide_text(slide, index)
            for index, slide in enumerate(presentation.slides, start=1)
        ]
        return title, slides

    def build_epub(self, pptx_path: Path, output_path: Path) -> Path:
        title, slides = self.extract_slides(pptx_path)
        book = epub.EpubBook()
        book.set_identifier(str(output_path.resolve()))
        book.set_title(title)
        book.set_language("en")
        book.add_author("pyPDFLibrarianSort")

        chapters = []
        for index, slide in enumerate(slides, start=1):
            chapter = epub.EpubHtml(
                title=slide.title,
                file_name=f"slide_{index:03d}.xhtml",
                lang="en",
            )
            chapter.content = HTML_TEMPLATE.format(
                slide_number=index,
                title=html.escape(slide.title),
                body=blocks_to_html(slide.blocks),
            )
            book.add_item(chapter)
            chapters.append(chapter)

        style = epub.EpubItem(
            uid="style_main",
            file_name="styles/main.css",
            media_type="text/css",
            content=CSS_CONTENT,
        )
        book.add_item(style)
        book.toc = tuple(chapters)
        book.spine = ["nav", *chapters]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        output_path.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(output_path), book, {})
        return output_path

    def collect_inputs(self, input_path: Path) -> list[Path]:
        if input_path.is_file():
            if input_path.suffix.lower() != ".pptx":
                raise ValueError("Only .pptx files are supported.")
            return [input_path]

        if input_path.is_dir():
            files = sorted(path for path in input_path.rglob("*.pptx") if path.is_file())
            if not files:
                raise ValueError(f"No .pptx files found in {input_path}")
            return files

        raise ValueError(f"Input path not found: {input_path}")

    def convert(self, input_path: Path, output_dir: Path, progress_callback=None) -> list[Path]:
        files = self.collect_inputs(input_path)
        results: list[Path] = []
        base_dir = input_path if input_path.is_dir() else input_path.parent

        for index, pptx_path in enumerate(files, start=1):
            if input_path.is_dir():
                relative_path = pptx_path.relative_to(base_dir).with_suffix(".epub")
                output_path = output_dir / relative_path
            else:
                output_path = output_dir / f"{pptx_path.stem}.epub"

            result = self.build_epub(pptx_path, output_path)
            results.append(result)

            if progress_callback:
                progress_callback(index, len(files), pptx_path, result)

        return results


def launch_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    class App:
        def __init__(self, root):
            self.root = root
            self.root.title("PowerPoint to EPUB")
            self.root.geometry("860x620")

            self.mode = tk.StringVar(value="file")
            self.input_path = tk.StringVar()
            self.output_dir = tk.StringVar()
            self.status = tk.StringVar(value="Ready")
            self.progress = tk.DoubleVar(value=0.0)
            self.queue = Queue()
            self.worker = None

            self._build()
            self.root.after(100, self._drain_queue)

        def _build(self):
            pad = dict(padx=8, pady=4)

            main = ttk.Frame(self.root, padding=10)
            main.grid(row=0, column=0, sticky="nsew")
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main.columnconfigure(1, weight=1)
            main.rowconfigure(5, weight=1)

            ttk.Label(main, text="PowerPoint to EPUB", font=("Segoe UI", 16, "bold")).grid(
                row=0, column=0, columnspan=3, sticky="w", **pad
            )
            ttk.Label(
                main,
                text="Extract slide text, ignore images, and generate structured EPUB books.",
                foreground="#555",
            ).grid(row=1, column=0, columnspan=3, sticky="w", **pad)

            mode_frame = ttk.LabelFrame(main, text="Input Type", padding=8)
            mode_frame.grid(row=2, column=0, columnspan=3, sticky="ew", **pad)
            ttk.Radiobutton(
                mode_frame,
                text="Single PowerPoint file",
                variable=self.mode,
                value="file",
                command=self._sync_defaults,
            ).grid(row=0, column=0, sticky="w", padx=4, pady=2)
            ttk.Radiobutton(
                mode_frame,
                text="Whole directory of PowerPoint files",
                variable=self.mode,
                value="directory",
                command=self._sync_defaults,
            ).grid(row=0, column=1, sticky="w", padx=12, pady=2)

            files = ttk.LabelFrame(main, text="Paths", padding=8)
            files.grid(row=3, column=0, columnspan=3, sticky="ew", **pad)
            files.columnconfigure(1, weight=1)

            self._file_row(files, 0, "PowerPoint file or folder:", self.input_path, self._browse_input)
            self._file_row(files, 1, "Output directory:", self.output_dir, self._browse_output)

            actions = ttk.Frame(main)
            actions.grid(row=4, column=0, columnspan=3, sticky="ew", **pad)
            ttk.Button(actions, text="Convert to EPUB", command=self._start).pack(side="left", padx=4)
            ttk.Button(actions, text="Clear Log", command=self._clear_log).pack(side="left", padx=4)

            ttk.Label(main, textvariable=self.status).grid(row=5, column=0, columnspan=3, sticky="w", **pad)
            ttk.Progressbar(main, maximum=100, variable=self.progress).grid(
                row=6, column=0, columnspan=3, sticky="ew", **pad
            )

            log_frame = ttk.LabelFrame(main, text="Activity Log", padding=8)
            log_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", **pad)
            log_frame.columnconfigure(0, weight=1)
            log_frame.rowconfigure(0, weight=1)
            self.log = scrolledtext.ScrolledText(log_frame, height=20, font=("Consolas", 9))
            self.log.grid(row=0, column=0, sticky="nsew")

        def _file_row(self, parent, row, label, variable, command):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=4, pady=2)
            ttk.Button(parent, text="Browse", command=command).grid(row=row, column=2, padx=4, pady=2)

        def _browse_input(self):
            if self.mode.get() == "directory":
                selected = filedialog.askdirectory(title="Select PowerPoint Directory")
            else:
                selected = filedialog.askopenfilename(
                    title="Select PowerPoint File",
                    filetypes=[("PowerPoint files", "*.pptx")],
                )
            if selected:
                self.input_path.set(selected)
                self._sync_defaults()

        def _browse_output(self):
            selected = filedialog.askdirectory(title="Select Output Directory")
            if selected:
                self.output_dir.set(selected)

        def _sync_defaults(self):
            input_path = self.input_path.get().strip()
            if not input_path:
                return

            source = Path(input_path)
            if self.mode.get() == "directory":
                self.output_dir.set(str(source.parent / f"{source.name}_epubs"))
            else:
                self.output_dir.set(str(source.parent / "epubs"))

        def _append_log(self, message):
            self.log.insert("end", message + "\n")
            self.log.see("end")

        def _clear_log(self):
            self.log.delete("1.0", "end")

        def _start(self):
            input_value = self.input_path.get().strip()
            output_value = self.output_dir.get().strip()

            if not input_value:
                messagebox.showerror("Missing", "Please select a PowerPoint file or directory.")
                return
            if not output_value:
                messagebox.showerror("Missing", "Please select an output directory.")
                return

            input_path = Path(input_value)
            output_dir = Path(output_value)

            self._clear_log()
            self.progress.set(0)
            self.status.set("Starting conversion...")

            self.worker = threading.Thread(
                target=self._run_worker,
                args=(input_path, output_dir),
                daemon=True,
            )
            self.worker.start()

        def _run_worker(self, input_path: Path, output_dir: Path):
            converter = PowerPointToEpubConverter()

            def progress_callback(current, total, source_path, output_path):
                self.queue.put(
                    (
                        "progress",
                        (
                            current,
                            total,
                            f"Converted {source_path.name} -> {output_path.name}",
                        ),
                    )
                )

            try:
                results = converter.convert(input_path, output_dir, progress_callback=progress_callback)
                self.queue.put(("done", results))
            except Exception as exc:
                self.queue.put(("error", str(exc)))

        def _drain_queue(self):
            try:
                while True:
                    kind, payload = self.queue.get_nowait()
                    if kind == "progress":
                        current, total, message = payload
                        percent = 0 if total <= 0 else (current / total) * 100
                        self.progress.set(percent)
                        self.status.set(message)
                        self._append_log(message)
                    elif kind == "done":
                        self.progress.set(100)
                        self.status.set(f"Finished. Created {len(payload)} EPUB file(s).")
                        self._append_log(self.status.get())
                    elif kind == "error":
                        self.status.set("Conversion failed.")
                        self._append_log(f"ERROR: {payload}")
            except Empty:
                pass
            finally:
                self.root.after(100, self._drain_queue)

    root = tk.Tk()
    App(root)
    root.mainloop()


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Convert PowerPoint slide text into structured EPUB files."
    )
    parser.add_argument("--gui", action="store_true", help="Launch the converter GUI.")
    parser.add_argument("--input", help="Path to a .pptx file or a directory containing .pptx files.")
    parser.add_argument("--output-dir", help="Directory where EPUB files will be written.")
    return parser


def run_cli(args) -> int:
    if not args.input:
        raise SystemExit("--input is required in CLI mode")
    if not args.output_dir:
        raise SystemExit("--output-dir is required in CLI mode")

    converter = PowerPointToEpubConverter()
    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output_dir).expanduser()

    def progress_callback(current, total, source_path, output_path):
        print(f"[{current}/{total}] {source_path} -> {output_path}")

    results = converter.convert(input_path, output_dir, progress_callback=progress_callback)
    print(f"Created {len(results)} EPUB file(s) in {output_dir}")
    return 0


def main(argv=None) -> int:
    parser = build_arg_parser()
    argv = sys.argv[1:] if argv is None else argv

    if not argv or "--gui" in argv:
        launch_gui()
        return 0

    args = parser.parse_args(argv)
    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
