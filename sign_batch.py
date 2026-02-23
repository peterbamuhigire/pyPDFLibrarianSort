"""
PDF Signature Batch Tool - Direct CLI

Command-line tool for signing PDFs with PNG signatures.
Designed for scripting and automation.

Usage:
    python sign_batch.py --signature sig.png --input docs/ --output signed/
    python sign_batch.py --signature sig.png --input doc.pdf --pages "1,3,5-10" --opacity 0.8
"""

import argparse
import sys
import os

try:
    from pdf_signature import PDFSignature, check_dependencies
except ImportError:
    print("ERROR: pdf_signature.py not found!")
    print("Make sure you're running this from the correct directory.")
    sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Sign PDFs with PNG signature images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign single PDF with default settings
  python sign_batch.py --signature sig.png --input document.pdf

  # Sign all PDFs in directory with custom position and size
  python sign_batch.py --signature sig.png --input docs/ --output signed/ --position top-right --scale 0.2

  # Sign only first and last pages with transparency
  python sign_batch.py --signature sig.png --input doc.pdf --pages "1,last" --opacity 0.5

  # Sign odd pages with rotation
  python sign_batch.py --signature sig.png --input doc.pdf --pages odd --rotation 15

  # Sign page range with custom margins
  python sign_batch.py --signature sig.png --input doc.pdf --pages "1-5,10,15-20" --x-offset 0.3 --y-offset 0.3

  # Sign all pages except specific pages
  python sign_batch.py --signature sig.png --input doc.pdf --pages all --skip-pages "2,5-7,15"
        """
    )

    # Required arguments
    parser.add_argument('--signature', required=True,
                       help='Path to signature PNG image')
    parser.add_argument('--input', required=True,
                       help='PDF file or directory to sign')

    # Optional arguments
    parser.add_argument('--output',
                       help='Output file/directory (default: input_signed.pdf or input/signed/)')
    parser.add_argument('--pages', default='all',
                       help='Pages to sign: all, first, last, odd, even, or range like "1-5,10" (default: all)')
    parser.add_argument('--skip-pages', default='',
                       help='Pages to skip (applied after --pages filter), range like "2,5-7,15" (default: none)')
    parser.add_argument('--position', default='bottom-right',
                       choices=['bottom-right', 'bottom-left', 'top-right', 'top-left'],
                       help='Signature position (default: bottom-right)')
    parser.add_argument('--scale', type=float, default=0.25,
                       help='Signature size as fraction of page width, 0.1-1.0 (default: 0.25)')
    parser.add_argument('--x-offset', type=float, default=0.5,
                       help='Horizontal margin from edge in inches (default: 0.5)')
    parser.add_argument('--y-offset', type=float, default=0.5,
                       help='Vertical margin from edge in inches (default: 0.5)')
    parser.add_argument('--opacity', type=float, default=1.0,
                       help='Signature opacity, 0.1-1.0 (default: 1.0 = opaque)')
    parser.add_argument('--rotation', type=int, default=0,
                       help='Rotation angle in degrees, 0-360 (default: 0)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress progress output')

    args = parser.parse_args()

    # Check dependencies
    if not args.quiet:
        print("Checking dependencies...")
    missing = check_dependencies()
    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)

    # Validate inputs
    if not os.path.exists(args.signature):
        print(f"ERROR: Signature file not found: {args.signature}")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"ERROR: Input not found: {args.input}")
        sys.exit(1)

    # Determine if batch mode
    is_directory = os.path.isdir(args.input)

    # Validate output
    output_path = args.output
    if output_path is None:
        if is_directory:
            output_path = os.path.join(args.input, 'signed')
        else:
            from pathlib import Path
            input_file = Path(args.input)
            output_path = str(input_file.parent / f"{input_file.stem}_signed.pdf")

    # Print configuration
    if not args.quiet:
        print()
        print("=" * 60)
        print("PDF SIGNATURE TOOL")
        print("=" * 60)
        print(f"Signature:  {args.signature}")
        print(f"Input:      {args.input}")
        print(f"Output:     {output_path}")
        print(f"Pages:      {args.pages}")
        if args.skip_pages:
            print(f"Skip pages: {args.skip_pages}")
        print(f"Position:   {args.position}")
        print(f"Scale:      {args.scale}")
        print(f"X Offset:   {args.x_offset}\"")
        print(f"Y Offset:   {args.y_offset}\"")
        print(f"Opacity:    {args.opacity}")
        print(f"Rotation:   {args.rotation}°")
        print("=" * 60)
        print()

    try:
        # Create signer
        signer = PDFSignature(
            signature_image_path=args.signature,
            position=args.position,
            scale=args.scale,
            x_offset=args.x_offset,
            y_offset=args.y_offset,
            opacity=args.opacity,
            rotation=args.rotation,
            pages=args.pages,
            skip_pages=args.skip_pages
        )

        if is_directory:
            # Batch mode
            if not args.quiet:
                print("Processing directory...")
                print()

            results = signer.batch_sign_pdfs(args.input, output_path)

            if not args.quiet:
                print()
                print("=" * 60)
                print("RESULTS")
                print("=" * 60)
                print(f"Total PDFs:  {results['total_pdfs']}")
                print(f"Successful:  {results['successful']}")
                print(f"Failed:      {results['failed']}")
                print(f"Log file:    {results['log_path']}")
                print()

            if results['failed'] > 0:
                print("Failed files:")
                for file_result in results['files']:
                    if not file_result['success']:
                        print(f"  - {file_result['input_path']}: {file_result['error']}")
                sys.exit(1)

        else:
            # Single file mode
            if not args.quiet:
                print("Processing file...")
                print()

            result = signer.add_signature_to_pdf(args.input, output_path)

            if not args.quiet:
                print()
                print("=" * 60)
                print("RESULT")
                print("=" * 60)

            if result['success']:
                if not args.quiet:
                    print(f"✓ Success!")
                    print(f"  Total pages:  {result['total_pages']}")
                    print(f"  Pages signed: {result['pages_signed']}")
                    print(f"  Output file:  {result['output_path']}")
            else:
                print(f"✗ Failed: {result['error']}")
                sys.exit(1)

        if not args.quiet:
            print()
            print("Done!")

    except Exception as e:
        print(f"\nERROR: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
