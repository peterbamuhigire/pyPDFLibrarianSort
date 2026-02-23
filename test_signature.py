"""
Unit Tests for PDF Signature Tool

Run with: python test_signature.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install pillow")
    sys.exit(1)

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf")
    sys.exit(1)

try:
    from pdf_signature import PDFSignature
except ImportError:
    print("ERROR: pdf_signature.py not found!")
    sys.exit(1)


def create_test_signature():
    """Create a test signature PNG"""
    # Create a simple 200x100 transparent PNG with text
    img = Image.new('RGBA', (200, 100), (255, 255, 255, 0))

    # Draw a simple signature shape (just colored pixels for testing)
    pixels = img.load()
    for x in range(50, 150):
        for y in range(30, 70):
            if (x - 100) ** 2 / 2500 + (y - 50) ** 2 / 400 < 1:  # Ellipse
                pixels[x, y] = (0, 0, 255, 200)  # Semi-transparent blue

    # Save to temp file
    temp_sig = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_sig.name, 'PNG')
    temp_sig.close()

    return temp_sig.name


def create_test_pdf(num_pages=1):
    """Create a test PDF with specified number of pages"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    c = canvas.Canvas(temp_pdf.name, pagesize=letter)

    for i in range(num_pages):
        c.drawString(100, 750, f"Test Page {i + 1}")
        c.showPage()

    c.save()
    temp_pdf.close()

    return temp_pdf.name


def test_position_calculation():
    """Test position calculation for all 4 corners"""
    print("\n" + "=" * 60)
    print("TEST: Position Calculation")
    print("=" * 60)

    sig_path = create_test_signature()

    try:
        signer = PDFSignature(sig_path, position='bottom-right', scale=0.3)

        # Test page dimensions
        page_width, page_height = 612, 792  # Letter size in points
        sig_width = page_width * 0.3
        sig_height = sig_width * (100 / 200)  # Aspect ratio

        positions = {
            'bottom-right': (page_width - sig_width - 36, 36),
            'bottom-left': (36, 36),
            'top-right': (page_width - sig_width - 36, page_height - sig_height - 36),
            'top-left': (36, page_height - sig_height - 36)
        }

        for pos_name, expected in positions.items():
            signer.position = pos_name
            x, y = signer._calculate_position(page_width, page_height, sig_width, sig_height)

            # Allow small floating-point differences
            if abs(x - expected[0]) < 1 and abs(y - expected[1]) < 1:
                print(f"  OK {pos_name}: ({x:.1f}, {y:.1f})")
            else:
                print(f"  FAIL {pos_name}: Expected {expected}, got ({x:.1f}, {y:.1f})")
                return False

        # Close the image to release file handle
        signer.signature_image.close()
        return True

    finally:
        try:
            os.unlink(sig_path)
        except PermissionError:
            pass  # File still in use, will be cleaned up later


def test_page_selection():
    """Test page selection parsing"""
    print("\n" + "=" * 60)
    print("TEST: Page Selection")
    print("=" * 60)

    sig_path = create_test_signature()

    try:
        test_cases = [
            ('all', 5, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            ('first', 1, 10, [1]),
            ('last', 10, 10, [10]),
            ('odd', None, 10, [1, 3, 5, 7, 9]),
            ('even', None, 10, [2, 4, 6, 8, 10]),
            ('1-3,7,9-10', None, 10, [1, 2, 3, 7, 9, 10])
        ]

        signers = []
        for pages_param, _, total, expected in test_cases:
            signer = PDFSignature(sig_path, pages=pages_param)
            signers.append(signer)

            result = [p for p in range(1, total + 1) if signer._should_sign_page(p, total)]

            if result == expected:
                print(f"  OK {pages_param}: {result}")
            else:
                print(f"  FAIL {pages_param}: Expected {expected}, got {result}")
                return False

        # Close all images
        for signer in signers:
            signer.signature_image.close()

        return True

    finally:
        try:
            os.unlink(sig_path)
        except PermissionError:
            pass


def test_single_pdf_signing():
    """Test signing a single PDF"""
    print("\n" + "=" * 60)
    print("TEST: Single PDF Signing")
    print("=" * 60)

    sig_path = create_test_signature()
    pdf_path = create_test_pdf(num_pages=5)

    try:
        signer = PDFSignature(
            sig_path,
            position='bottom-right',
            scale=0.25,
            pages='all'
        )

        output_path = pdf_path.replace('.pdf', '_signed.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success']:
            # Verify output exists
            if os.path.exists(output_path):
                # Verify page count
                reader = PdfReader(output_path)
                if len(reader.pages) == 5:
                    print(f"  OK Signed PDF created with {len(reader.pages)} pages")
                    print(f"  OK Pages signed: {result['pages_signed']}")
                    os.unlink(output_path)
                    return True
                else:
                    print(f"  FAIL Page count mismatch")
                    return False
            else:
                print(f"  FAIL Output file not created")
                return False
        else:
            print(f"  FAIL Signing failed: {result['error']}")
            return False

    finally:
        try:
            os.unlink(sig_path)
        except (PermissionError, FileNotFoundError):
            pass
        try:
            os.unlink(pdf_path)
        except (PermissionError, FileNotFoundError):
            pass


def test_page_filtering():
    """Test signing only specific pages"""
    print("\n" + "=" * 60)
    print("TEST: Page Filtering (First & Last Only)")
    print("=" * 60)

    sig_path = create_test_signature()
    pdf_path = create_test_pdf(num_pages=10)

    try:
        # Test first page only
        signer = PDFSignature(sig_path, pages='first')
        output_path = pdf_path.replace('.pdf', '_first.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success'] and result['pages_signed'] == 1:
            print(f"  OK First page only: {result['pages_signed']} page signed")
            os.unlink(output_path)
        else:
            print(f"  FAIL First page test failed")
            return False

        # Test last page only
        signer = PDFSignature(sig_path, pages='last')
        output_path = pdf_path.replace('.pdf', '_last.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success'] and result['pages_signed'] == 1:
            print(f"  OK Last page only: {result['pages_signed']} page signed")
            os.unlink(output_path)
        else:
            print(f"  FAIL Last page test failed")
            return False

        # Test odd pages
        signer = PDFSignature(sig_path, pages='odd')
        output_path = pdf_path.replace('.pdf', '_odd.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success'] and result['pages_signed'] == 5:  # Pages 1,3,5,7,9
            print(f"  OK Odd pages: {result['pages_signed']} pages signed")
            os.unlink(output_path)
            return True
        else:
            print(f"  FAIL Odd pages test failed: {result['pages_signed']} signed")
            return False

    finally:
        try:
            os.unlink(sig_path)
        except (PermissionError, FileNotFoundError):
            pass
        try:
            os.unlink(pdf_path)
        except (PermissionError, FileNotFoundError):
            pass


def test_skip_pages():
    """Test skipping specific pages"""
    print("\n" + "=" * 60)
    print("TEST: Skip Pages")
    print("=" * 60)

    sig_path = create_test_signature()
    pdf_path = create_test_pdf(num_pages=10)

    try:
        # Test skip single page (sign all except page 5)
        signer = PDFSignature(sig_path, pages='all', skip_pages='5')
        output_path = pdf_path.replace('.pdf', '_skip_single.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success'] and result['pages_signed'] == 9:
            print(f"  OK Skip single page: {result['pages_signed']} pages signed (10 - 1 = 9)")
            os.unlink(output_path)
        else:
            print(f"  FAIL Skip single page test failed: {result['pages_signed']} signed")
            return False

        # Test skip range (sign all except pages 2-4)
        signer = PDFSignature(sig_path, pages='all', skip_pages='2-4')
        output_path = pdf_path.replace('.pdf', '_skip_range.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success'] and result['pages_signed'] == 7:  # Pages 1,5,6,7,8,9,10
            print(f"  OK Skip range: {result['pages_signed']} pages signed (10 - 3 = 7)")
            os.unlink(output_path)
        else:
            print(f"  FAIL Skip range test failed: {result['pages_signed']} signed")
            return False

        # Test skip multiple ranges and singles (sign odd pages except 1 and 5-7)
        signer = PDFSignature(sig_path, pages='odd', skip_pages='1,5-7')
        output_path = pdf_path.replace('.pdf', '_skip_complex.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        # Odd pages: 1,3,5,7,9 -> Skip 1,5,7 -> Only 3,9 remain
        if result['success'] and result['pages_signed'] == 2:
            print(f"  OK Skip with page filter: {result['pages_signed']} pages signed (odd except 1,5-7)")
            os.unlink(output_path)
            return True
        else:
            print(f"  FAIL Skip with page filter test failed: {result['pages_signed']} signed")
            return False

    finally:
        try:
            os.unlink(sig_path)
        except (PermissionError, FileNotFoundError):
            pass
        try:
            os.unlink(pdf_path)
        except (PermissionError, FileNotFoundError):
            pass


def test_opacity_and_rotation():
    """Test opacity and rotation settings"""
    print("\n" + "=" * 60)
    print("TEST: Opacity and Rotation")
    print("=" * 60)

    sig_path = create_test_signature()
    pdf_path = create_test_pdf(num_pages=1)

    try:
        # Test with 50% opacity and 45-degree rotation
        signer = PDFSignature(
            sig_path,
            opacity=0.5,
            rotation=45
        )

        output_path = pdf_path.replace('.pdf', '_transformed.pdf')
        result = signer.add_signature_to_pdf(pdf_path, output_path)

        if result['success']:
            print(f"  OK Signed with 50% opacity and 45° rotation")
            os.unlink(output_path)
            return True
        else:
            print(f"  FAIL Failed: {result['error']}")
            return False

    finally:
        try:
            os.unlink(sig_path)
        except (PermissionError, FileNotFoundError):
            pass
        try:
            os.unlink(pdf_path)
        except (PermissionError, FileNotFoundError):
            pass


def test_batch_processing():
    """Test batch processing multiple PDFs"""
    print("\n" + "=" * 60)
    print("TEST: Batch Processing")
    print("=" * 60)

    sig_path = create_test_signature()

    # Create temp directory with multiple PDFs
    temp_dir = tempfile.mkdtemp()

    try:
        # Create 3 test PDFs
        for i in range(3):
            pdf_path = create_test_pdf(num_pages=2)
            dest_path = os.path.join(temp_dir, f'test_{i}.pdf')
            os.rename(pdf_path, dest_path)

        # Batch sign
        signer = PDFSignature(sig_path)
        results = signer.batch_sign_pdfs(temp_dir)

        if results['total_pdfs'] == 3 and results['successful'] == 3:
            print(f"  OK Batch signed {results['successful']}/{results['total_pdfs']} PDFs")
            print(f"  OK Log created: {results['log_path']}")
            return True
        else:
            print(f"  FAIL Expected 3/3, got {results['successful']}/{results['total_pdfs']}")
            return False

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.unlink(sig_path)


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n" + "=" * 60)
    print("TEST: Error Handling")
    print("=" * 60)

    sig_path = create_test_signature()

    try:
        # Test invalid position
        try:
            signer = PDFSignature(sig_path, position='invalid')
            print("  FAIL Invalid position should raise error")
            return False
        except ValueError:
            print("  OK Invalid position rejected")

        # Test invalid scale
        try:
            signer = PDFSignature(sig_path, scale=1.5)
            print("  FAIL Invalid scale should raise error")
            return False
        except ValueError:
            print("  OK Invalid scale rejected")

        # Test invalid opacity
        try:
            signer = PDFSignature(sig_path, opacity=2.0)
            print("  FAIL Invalid opacity should raise error")
            return False
        except ValueError:
            print("  OK Invalid opacity rejected")

        # Test invalid rotation
        try:
            signer = PDFSignature(sig_path, rotation=400)
            print("  FAIL Invalid rotation should raise error")
            return False
        except ValueError:
            print("  OK Invalid rotation rejected")

        return True

    finally:
        try:
            os.unlink(sig_path)
        except (PermissionError, FileNotFoundError):
            pass


def main():
    """Run all tests"""
    print("=" * 60)
    print("PDF SIGNATURE TOOL - UNIT TESTS")
    print("=" * 60)

    tests = [
        ("Position Calculation", test_position_calculation),
        ("Page Selection", test_page_selection),
        ("Single PDF Signing", test_single_pdf_signing),
        ("Page Filtering", test_page_filtering),
        ("Skip Pages", test_skip_pages),
        ("Opacity & Rotation", test_opacity_and_rotation),
        ("Batch Processing", test_batch_processing),
        ("Error Handling", test_error_handling)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n  FAIL Test crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
