# Skip Pages Feature

## Overview

The PDF signature tool now supports skipping specific pages or ranges when signing PDFs. This feature is available in all interfaces: web GUI, CLI tools, and interactive setup.

## How It Works

The `skip_pages` parameter allows you to exclude specific pages from signing, **applied after the main page selection**. This gives you fine-grained control over which pages get signed.

### Examples

1. **Sign all pages except page 5**
   - Pages: `all`
   - Skip: `5`
   - Result: Pages 1-4, 6-10 signed (assuming 10-page PDF)

2. **Sign all pages except pages 2-4**
   - Pages: `all`
   - Skip: `2-4`
   - Result: Pages 1, 5-10 signed

3. **Sign odd pages except 1 and 5-7**
   - Pages: `odd`
   - Skip: `1,5-7`
   - Result: Pages 3, 9 signed (assuming 10-page PDF)

## Usage

### Web Interface

1. Navigate to the **Sign PDFs** section
2. Configure your signature settings
3. Under "Pages to Sign", select your page option (all, first, last, odd, even, or custom range)
4. In the **"Skip Pages (Optional)"** field, enter pages to exclude:
   - Single page: `5`
   - Multiple pages: `2,5,8`
   - Range: `2-4`
   - Mixed: `1,3-5,10,15-20`
5. Upload PDFs and sign

### CLI - sign_batch.py

```bash
# Sign all pages except page 2
python sign_batch.py --signature sig.png --input doc.pdf --pages all --skip-pages "2"

# Sign odd pages except first and last
python sign_batch.py --signature sig.png --input doc.pdf --pages odd --skip-pages "1,10"

# Sign all pages except pages 2, 5-7, and 15
python sign_batch.py --signature sig.png --input doc.pdf --skip-pages "2,5-7,15"
```

### Interactive Setup - sign_setup.py

When running the interactive setup, you'll be prompted at Step 10:

```
==================================================
STEP 10: Skip Pages (Optional)
==================================================
Enter pages to exclude from signing (applied after page selection).
Examples: '2,5' or '1-3,10' or leave empty to skip none

Skip pages (press Enter to skip none): 2,5-7,15
```

### Python API

```python
from pdf_signature import PDFSignature

# Create signer with skip_pages
signer = PDFSignature(
    signature_image_path='signature.png',
    pages='all',
    skip_pages='2,5-7,15',  # Skip these pages
    position='bottom-left',
    scale=0.25
)

# Sign PDF
result = signer.add_signature_to_pdf('input.pdf', 'output.pdf')
print(f"Signed {result['pages_signed']} of {result['total_pages']} pages")
```

## Format

The skip_pages parameter uses the same range format as the pages parameter:

- **Single page**: `5`
- **Multiple pages**: `2,5,8,10`
- **Range**: `1-5` (pages 1 through 5)
- **Mixed**: `1-3,7,10,15-20`

## Validation

- Invalid format will raise a `ValueError`
- Empty string `''` means no pages are skipped
- Pages are 1-indexed (first page is 1, not 0)

## Implementation Details

1. Skip pages are checked **first** before the main page filter
2. If a page is in the skip list, it's excluded regardless of the pages filter
3. This allows complex combinations like "sign odd pages except pages 1 and 5-7"

## Testing

Run the test suite to verify the skip_pages functionality:

```bash
python test_signature.py
```

The test suite includes:
- Skip single page
- Skip range of pages
- Skip pages combined with page filters (e.g., odd pages except specific ones)

All tests pass successfully! ✅
