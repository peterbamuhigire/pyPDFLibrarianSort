# 📚 pyPDFLibrarianSort

**Modern web-based PDF management platform** - AI-powered organization with 98% cost savings + digital signatures with zero AI credits.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Multi-AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Anthropic%20%7C%20DeepSeek-blueviolet)](https://ai.google.dev/)

> **Complete PDF management: AI organization + digital signatures, all in one modern web interface**

## 🎯 Key Features

- 🤖 **Three AI Providers** - Choose Gemini, Anthropic (Claude), or DeepSeek
- 💰 **98% Cost Savings** - Batch processing: $0.10 for 200 PDFs vs $10 individual
- 🌐 **Modern Web Interface** - Drag & drop, real-time preview, visual approval
- ✍️ **PDF Signature Tool** - Add signatures to PDFs with NO AI credits (web + CLI)
- 👀 **Watch Mode** - Auto-organize PDFs as they arrive (24/7 background mode)
- 🔍 **Smart Renaming** - Detects gibberish filenames, reads content, suggests better names
- 🌲 **Deep Hierarchy** - Preserves multi-level folder structures (3+ levels)
- 📊 **Content Analysis** - Reads PDF content for accurate categorization
- 🎒 **Cross-Platform** - Works on Windows, macOS, Linux
- 🔒 **Privacy-First** - Only filenames/metadata sent to API, never PDF content

## 💰 Cost Comparison

| PDFs | Single Mode | Batch Mode | **Savings** |
|------|------------|------------|-------------|
| 50   | $2.50      | $0.05      | **98%** ✅  |
| 200  | $10.00     | $0.10      | **99%** ✅  |
| 500  | $25.00     | $0.15      | **99%** ✅  |

**Why such huge savings?** Batch mode processes ALL PDFs in a single API call instead of one call per PDF!

## 📖 Documentation

### Getting Started
- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Get running in 5 minutes
- **[Project Brief](PROJECT_BRIEF.md)** - 30-second overview
- **[Get Started](docs/guides/GET_STARTED.md)** - Detailed setup guide

### User Guides
- **[Web Interface Guide](docs/guides/WEB_INTERFACE_GUIDE.md)** - Using the web UI
- **[PDF Signature Guide](docs/guides/SIGNATURE_GUIDE.md)** - Sign PDFs with no AI credits
- **[Watch Mode](docs/guides/WATCH_MODE_README.md)** - Auto-organization setup
- **[Smart Renaming](docs/guides/SMART_RENAMING_GUIDE.md)** - How gibberish detection works
- **[Features Summary](docs/features/FEATURES_SUMMARY.md)** - Complete feature list

### Reference
- **[Error Handling](docs/reference/ERROR_HANDLING.md)** - Troubleshooting guide
- **[Portable Usage](docs/reference/PORTABLE_USAGE.md)** - Cross-platform usage
- **[Hierarchical Categories](docs/reference/HIERARCHICAL_CATEGORIES.md)** - Category system explained

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance
- **[Skills Directory](skills/)** - Reusable development skills

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Modes](#-usage-modes)
- [Cost Comparison](#-cost-comparison)
- [Contributing](#-contributing)
- [License](#-license)

## 🔧 Installation

```bash
git clone https://github.com/peterbamuhigire/pyPDFLibrarianSort.git
cd pyPDFLibrarianSort
pip install -r requirements.txt
```

**Get an API key:**
- **Gemini**: https://aistudio.google.com/app/apikey
- **Anthropic**: https://console.anthropic.com/
- **DeepSeek**: https://platform.deepseek.com/

See [docs/guides/GET_STARTED.md](docs/guides/GET_STARTED.md) for detailed setup instructions.

## 🚀 Quick Start

**Web Interface (Recommended - All Features):**
```bash
python web_interface.py
# Opens http://localhost:5000 automatically
# Access: PDF Organization + PDF Signatures
```

**PDF Organization:**
- **Batch Mode**: `python organize_batch.py` (cost-effective)
- **Watch Mode**: `python watch_setup.py` (auto-organize 24/7)

**PDF Signatures (No AI Credits):**
```bash
python sign_setup.py  # Interactive wizard
# OR
python sign_batch.py --signature sig.png --input document.pdf
```

See [docs/guides/QUICK_START.md](docs/guides/QUICK_START.md) for detailed usage.

## 📖 Features & Usage Modes

### PDF Organization (AI-Powered)

| Mode | Best For | Cost (200 PDFs) | Command |
|------|----------|-----------------|---------|
| **Web Interface** | Interactive use, visual review | $0.10 | `python web_interface.py` |
| **Watch Mode** | Auto-organize 24/7 | $0.10-0.20 | `python watch_setup.py` |
| **Batch Mode** | One-time organization | $0.10 | `python organize_batch.py` |
| **Single Mode** | Maximum accuracy | $10.00 | `python organize_simple.py` |

### PDF Signatures (No AI Credits)

| Mode | Best For | Cost | Command |
|------|----------|------|---------|
| **Web Interface** | Interactive signing with preview | $0 | `python web_interface.py` |
| **Interactive CLI** | Step-by-step configuration | $0 | `python sign_setup.py` |
| **Direct CLI** | Scripting & automation | $0 | `python sign_batch.py` |

**Signature Features**: 4 corner positions • Page selection (all/first/last/odd/even/ranges) • Size control (10-100%) • Opacity (10-100%) • Rotation (0-360°) • Batch processing

See [docs/features/FEATURES_SUMMARY.md](docs/features/FEATURES_SUMMARY.md) for detailed comparisons.

See comprehensive documentation in [docs/](docs/) directory for detailed guides on configuration, troubleshooting, and advanced usage.

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute!

## 🙏 Credits

- **AI Organization**: Powered by [Google Gemini](https://ai.google.dev/), [Anthropic Claude](https://www.anthropic.com/), and [DeepSeek](https://www.deepseek.com/)
- **PDF Processing**: ReportLab, PyPDF, Pillow
- Built with ❤️ for PDF management needs
- Thanks to all contributors!

## 🔗 Links

- [Documentation](docs/)
- [Issue Tracker](https://github.com/yourusername/pyPDFLibrarianSort/issues)
- [Discussions](https://github.com/yourusername/pyPDFLibrarianSort/discussions)
- [Gemini API](https://ai.google.dev/)

---

⭐ **Star this repo if it helped you organize your PDF library!**

💡 **Have questions?** Open a [Discussion](https://github.com/yourusername/pyPDFLibrarianSort/discussions)

🐛 **Found a bug?** Report an [Issue](https://github.com/yourusername/pyPDFLibrarianSort/issues)
