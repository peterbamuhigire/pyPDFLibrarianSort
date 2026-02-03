"""
PDF Signature Tool - Core Module

Adds PNG signature images to PDFs with extensive configuration options.
No AI credits required - pure PDF manipulation.

Features:
- 4 corner positions (bottom-right, bottom-left, top-right, top-left)
- Page selection (all, first, last, odd, even, ranges)
- Adjustable scaling (10-100% of page width)
- Configurable margins (X/Y offsets in inches)
- Opacity control (10-100% transparency)
- Rotation (0-360 degrees)
- Batch processing support
"""

import os
import json
from datetime import datetime
from pathlib import Path
from io import BytesIO
import re

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install pillow")
    raise

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError:
    print("ERROR: ReportLab not installed. Run: pip install reportlab")
    raise

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf")
    raise


class PDFSignature:
    """Core signature placement engine"""

    VALID_POSITIONS = ['bottom-right', 'bottom-left', 'top-right', 'top-left']
    VALID_PAGE_OPTIONS = ['all', 'first', 'last', 'odd', 'even']

    def __init__(self, signature_image_path, position='bottom-left',
                 scale=0.3, x_offset=0.5, y_offset=0.5, opacity=1.0,
                 rotation=0, pages='all'):
        """
        Initialize PDF signature configuration.

        Args:
            signature_image_path: Path to PNG signature image
            position: Corner position - 'bottom-right', 'bottom-left', 'top-right', 'top-left'
            scale: Signature width as fraction of page width (0.1-1.0)
            x_offset: Horizontal margin from edge in inches (0.1-2.0)
            y_offset: Vertical margin from edge in inches (0.1-2.0)
            opacity: Transparency level (0.1-1.0, where 1.0 is opaque)
            rotation: Rotation angle in degrees (0-360)
            pages: Page selection - 'all', 'first', 'last', 'odd', 'even', or range like '1-5,10,15-20'
        """
        # Validate signature image
        if not os.path.exists(signature_image_path):
            raise ValueError(f"Signature image not found: {signature_image_path}")

        try:
            img = Image.open(signature_image_path)
            if img.format != 'PNG':
                raise ValueError("Signature must be PNG format")
            self.signature_image = img
            self.signature_path = signature_image_path
        except Exception as e:
            raise ValueError(f"Failed to load signature image: {e}")

        # Validate position
        if position not in self.VALID_POSITIONS:
            raise ValueError(f"Position must be one of: {self.VALID_POSITIONS}")
        self.position = position

        # Validate scale
        if not 0.1 <= scale <= 1.0:
            raise ValueError("Scale must be between 0.1 and 1.0")
        self.scale = scale

        # Validate offsets
        if not 0.1 <= x_offset <= 2.0:
            raise ValueError("X offset must be between 0.1 and 2.0 inches")
        if not 0.1 <= y_offset <= 2.0:
            raise ValueError("Y offset must be between 0.1 and 2.0 inches")
        self.x_offset = x_offset * 72  # Convert inches to points
        self.y_offset = y_offset * 72

        # Validate opacity
        if not 0.1 <= opacity <= 1.0:
            raise ValueError("Opacity must be between 0.1 and 1.0")
        self.opacity = opacity

        # Validate rotation
        if not 0 <= rotation <= 360:
            raise ValueError("Rotation must be between 0 and 360 degrees")
        self.rotation = rotation

        # Validate and parse pages
        self.pages = pages
        self._validate_pages_format()

    def _validate_pages_format(self):
        """Validate the pages parameter format"""
        if self.pages in self.VALID_PAGE_OPTIONS:
            return

        # Check if it's a valid range format (e.g., "1-5,10,15-20")
        if not re.match(r'^[\d\s,\-]+$', self.pages):
            raise ValueError(f"Invalid pages format. Use 'all', 'first', 'last', 'odd', 'even', or ranges like '1-5,10,15-20'")

    def _should_sign_page(self, page_num, total_pages):
        """
        Determine if a page should be signed based on pages filter.

        Args:
            page_num: Current page number (1-indexed)
            total_pages: Total number of pages in PDF

        Returns:
            bool: True if page should be signed
        """
        if self.pages == 'all':
            return True
        elif self.pages == 'first':
            return page_num == 1
        elif self.pages == 'last':
            return page_num == total_pages
        elif self.pages == 'odd':
            return page_num % 2 == 1
        elif self.pages == 'even':
            return page_num % 2 == 0
        else:
            # Parse range format (e.g., "1-5,10,15-20")
            page_set = set()
            for part in self.pages.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-')
                    page_set.update(range(int(start), int(end) + 1))
                else:
                    page_set.add(int(part))
            return page_num in page_set

    def _calculate_position(self, page_width, page_height, sig_width, sig_height):
        """
        Calculate x,y coordinates based on position and offsets.

        Args:
            page_width: Page width in points
            page_height: Page height in points
            sig_width: Signature width in points
            sig_height: Signature height in points

        Returns:
            tuple: (x, y) coordinates in points
        """
        # PDF coordinates: (0,0) at bottom-left
        if self.position == 'bottom-right':
            x = page_width - sig_width - self.x_offset
            y = self.y_offset
        elif self.position == 'bottom-left':
            x = self.x_offset
            y = self.y_offset
        elif self.position == 'top-right':
            x = page_width - sig_width - self.x_offset
            y = page_height - sig_height - self.y_offset
        elif self.position == 'top-left':
            x = self.x_offset
            y = page_height - sig_height - self.y_offset

        return x, y

    def _create_signature_overlay(self, page_width, page_height):
        """
        Create ReportLab canvas with positioned, rotated, transparent signature.

        Args:
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            BytesIO: PDF overlay as bytes
        """
        # Create in-memory PDF
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # Calculate signature dimensions maintaining aspect ratio
        sig_width = page_width * self.scale
        sig_height = sig_width * (self.signature_image.height / self.signature_image.width)

        # Warn if signature is too large
        if sig_width > page_width * 0.5 or sig_height > page_height * 0.5:
            print(f"Warning: Signature is large ({sig_width:.0f}x{sig_height:.0f} pts on {page_width:.0f}x{page_height:.0f} page)")

        # Calculate position
        x, y = self._calculate_position(page_width, page_height, sig_width, sig_height)

        # Apply opacity
        c.setFillAlpha(self.opacity)

        # Handle rotation
        if self.rotation != 0:
            # Save state
            c.saveState()

            # Move to center of signature
            center_x = x + sig_width / 2
            center_y = y + sig_height / 2

            # Translate to center, rotate, translate back
            c.translate(center_x, center_y)
            c.rotate(self.rotation)
            c.translate(-sig_width / 2, -sig_height / 2)

            # Draw signature
            c.drawImage(ImageReader(self.signature_image),
                       0, 0,
                       width=sig_width,
                       height=sig_height,
                       mask='auto')  # Preserve PNG transparency

            # Restore state
            c.restoreState()
        else:
            # Draw signature without rotation
            c.drawImage(ImageReader(self.signature_image),
                       x, y,
                       width=sig_width,
                       height=sig_height,
                       mask='auto')  # Preserve PNG transparency

        c.save()
        packet.seek(0)
        return packet

    def add_signature_to_pdf(self, input_pdf_path, output_pdf_path=None):
        """
        Sign a single PDF with page filtering.

        Args:
            input_pdf_path: Path to input PDF
            output_pdf_path: Path for output PDF (defaults to input_signed.pdf)

        Returns:
            dict: Processing result with success status and details
        """
        result = {
            'input_path': input_pdf_path,
            'output_path': output_pdf_path,
            'success': False,
            'total_pages': 0,
            'pages_signed': 0,
            'error': None
        }

        try:
            # Validate input
            if not os.path.exists(input_pdf_path):
                raise ValueError(f"Input PDF not found: {input_pdf_path}")

            # Determine output path
            if output_pdf_path is None:
                input_path = Path(input_pdf_path)
                output_pdf_path = str(input_path.parent / f"{input_path.stem}_signed.pdf")

            result['output_path'] = output_pdf_path

            # Read input PDF
            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()

            total_pages = len(reader.pages)
            result['total_pages'] = total_pages
            pages_signed = 0

            # Process each page
            for page_num, page in enumerate(reader.pages, start=1):
                # Check if this page should be signed
                if self._should_sign_page(page_num, total_pages):
                    # Get page dimensions
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)

                    # Create signature overlay
                    overlay_pdf = self._create_signature_overlay(page_width, page_height)
                    overlay_reader = PdfReader(overlay_pdf)

                    # Merge signature with page
                    page.merge_page(overlay_reader.pages[0])
                    pages_signed += 1

                # Add page to output (signed or unsigned)
                writer.add_page(page)

            # Write output PDF
            os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)

            result['pages_signed'] = pages_signed
            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def batch_sign_pdfs(self, pdf_directory, output_directory=None):
        """
        Sign all PDFs in a directory.

        Args:
            pdf_directory: Directory containing PDFs to sign
            output_directory: Output directory (defaults to pdf_directory/signed/)

        Returns:
            dict: Batch processing results
        """
        # Validate input directory
        if not os.path.isdir(pdf_directory):
            raise ValueError(f"Input directory not found: {pdf_directory}")

        # Determine output directory
        if output_directory is None:
            output_directory = os.path.join(pdf_directory, 'signed')

        os.makedirs(output_directory, exist_ok=True)

        # Find all PDFs
        pdf_files = []
        for root, dirs, files in os.walk(pdf_directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))

        # Process each PDF
        results = {
            'total_pdfs': len(pdf_files),
            'successful': 0,
            'failed': 0,
            'files': [],
            'log_path': None
        }

        for pdf_path in pdf_files:
            # Determine output path (maintain relative structure)
            rel_path = os.path.relpath(pdf_path, pdf_directory)
            output_path = os.path.join(output_directory, rel_path)

            # Process PDF
            result = self.add_signature_to_pdf(pdf_path, output_path)

            # Track results
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['files'].append(result)

        # Write log file
        log_path = os.path.join(output_directory, 'signature_log.json')
        self._write_log(results['files'], log_path)
        results['log_path'] = log_path

        return results

    def _write_log(self, file_results, log_path):
        """Write processing log to JSON file"""
        log_data = {
            'signed_files': []
        }

        # Load existing log if it exists
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                pass  # Start fresh if log is corrupted

        # Add new entries
        for result in file_results:
            if result['success']:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'input_path': result['input_path'],
                    'output_path': result['output_path'],
                    'signature': self.signature_path,
                    'pages_filter': self.pages,
                    'position': self.position,
                    'scale': self.scale,
                    'x_offset': self.x_offset / 72,  # Convert back to inches
                    'y_offset': self.y_offset / 72,
                    'opacity': self.opacity,
                    'rotation': self.rotation,
                    'total_pages': result['total_pages'],
                    'pages_signed': result['pages_signed'],
                    'success': True
                }
                log_data['signed_files'].append(log_entry)

        # Write log
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    try:
        import PIL
    except ImportError:
        missing.append('pillow')

    try:
        import reportlab
    except ImportError:
        missing.append('reportlab')

    try:
        import pypdf
    except ImportError:
        missing.append('pypdf')

    return missing
