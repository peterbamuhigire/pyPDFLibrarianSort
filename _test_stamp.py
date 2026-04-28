"""
Test the new show_pdf_page stamping engine.
Creates a synthetic test: a 6-page PDF where pages alternate rot=0 and rot=270,
stamps it, then pixel-checks each page's bottom-left corner for non-white pixels.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import fitz
from PIL import Image, ImageDraw
from io import BytesIO
import tempfile

# --- build a synthetic signature PNG (red rectangle) ---
sig_img = Image.new("RGBA", (200, 80), (0, 0, 0, 0))
draw = ImageDraw.Draw(sig_img)
draw.rectangle([0, 0, 199, 79], fill=(200, 30, 30, 220))
sig_buf = BytesIO()
sig_img.save(sig_buf, format="PNG")
sig_bytes = sig_buf.getvalue()

# --- build a synthetic 6-page PDF with alternating rotations ---
src_doc = fitz.open()
rotations = [0, 90, 180, 270, 0, 270]
for rot in rotations:
    page = src_doc.new_page(width=595, height=842)
    page.set_rotation(rot)
    page.insert_text((50, 100), f"Rotation {rot}", fontsize=24)
src_file = os.path.join(tempfile.gettempdir(), "_test_src.pdf")
out_file  = os.path.join(tempfile.gettempdir(), "_test_out.pdf")
sig_file  = os.path.join(tempfile.gettempdir(), "_test_sig.png")
src_doc.save(src_file)
src_doc.close()
with open(sig_file, "wb") as f:
    f.write(sig_bytes)

# --- stamp it ---
from pdf_signature import PDFSignature
ps = PDFSignature(
    signature_image_path=sig_file,
    position="bottom-left",
    scale=0.15,
    opacity=0.9,
    x_offset=0.3,
    y_offset=0.3,
)
total, signed = ps._add_signature_to_pdf_with_pymupdf(src_file, out_file)
print(f"total={total}  signed={signed}")
assert signed == total, f"Not all pages signed: {signed}/{total}"

# --- verify non-white pixels in BL corner of every page ---
doc = fitz.open(out_file)
all_ok = True
for i in range(doc.page_count):
    page = doc.load_page(i)
    r = page.rect
    clip = fitz.Rect(r.x0, r.y1 * 0.80, r.x1 * 0.25, r.y1)
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), clip=clip)
    s = pix.samples
    non_white = sum(1 for j in range(0, len(s), 3)
                    if not (s[j] > 240 and s[j+1] > 240 and s[j+2] > 240))
    status = "OK" if non_white > 20 else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  Page {i+1}: rot={rotations[i]}  non-white={non_white}  {status}")
doc.close()

# cleanup
for f in (src_file, out_file, sig_file):
    try: os.remove(f)
    except: pass

if all_ok:
    print("\nALL PAGES PASSED")
else:
    print("\nSOME PAGES FAILED")
    sys.exit(1)
