# pyPDFLibrarianSort - Project Brief

## 30-Second Overview

**Modern web-based PDF management platform** with two powerful tools: (1) AI-powered organization with 98% cost savings, and (2) digital signature tool requiring no AI credits. Drag & drop interface, batch processing, and automated workflows.

## Key Innovations

1. **Batch Processing**: Organize 200 PDFs in one API call ($0.10) vs individual processing ($10). **98% cost savings**.
2. **Zero-Cost Signatures**: Add signatures to PDFs with no AI credits required.

## Core Capabilities

### PDF Organization (AI-Powered)
1. **Three AI Providers**: Gemini, Anthropic, DeepSeek
2. **Batch Mode**: Process all PDFs in single API call
3. **Watch Mode**: Auto-organize PDFs as they arrive (24/7)
4. **Smart Renaming**: Detects gibberish filenames, reads content, suggests meaningful names

### PDF Signatures (No AI Required)
1. **Flexible Positioning**: 4 corner positions with adjustable margins
2. **Page Selection**: Sign all, first, last, odd, even, or custom ranges
3. **Full Customization**: Size, opacity (10-100%), rotation (0-360°)
4. **Batch Processing**: Sign multiple PDFs at once

### Web Interface
- **Drag & Drop**: Upload signatures and PDFs easily
- **Real-Time Preview**: See signature placement before applying
- **Visual Approval**: Review AI categorization before organizing
- **Browse Library**: Explore organized PDF collection

## Target Users

- Professionals managing document libraries (organization + signatures)
- Legal firms needing document signing and organization
- Researchers with hundreds of PDFs to categorize
- Students organizing study materials
- Businesses requiring signed contracts and organized files
- Anyone needing PDF management without expensive tools

## Technical Stack

- **Language**: Python 3.x
- **AI Providers**: Google Gemini, Anthropic Claude, DeepSeek (for organization)
- **PDF Processing**: pypdf, ReportLab, Pillow (for signatures)
- **File Monitoring**: watchdog
- **Web Framework**: Flask with RESTful API
- **Deployment**: Cross-platform (Windows, macOS, Linux)

## Project Status

**Active Development** | **v2.0** with web interface, watch mode, and multi-provider support

## Quick Links

- **Setup**: See `docs/guides/QUICK_START.md`
- **Features**: See `docs/features/FEATURES_SUMMARY.md`
- **Web Interface**: See `docs/guides/WEB_INTERFACE_GUIDE.md`
- **PDF Signatures**: See `docs/guides/SIGNATURE_GUIDE.md`
- **Watch Mode**: See `docs/guides/WATCH_MODE_README.md`
- **Claude Instructions**: See `CLAUDE.md`

## Repository

**GitHub**: [pyPDFLibrarianSort](https://github.com/yourusername/pyPDFLibrarianSort)

---

**Maintained by**: Peter Bamuhigire
**Last Updated**: January 2026
**License**: MIT
