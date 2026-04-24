## 🌐 Web Interface Guide

# PDF Organizer - Web Interface

This guide documents the legacy PDF web interface inside the broader `pyPDFLibrarianSort` Python tools workspace.

A modern, beautiful web interface for organizing PDFs with drag & drop functionality, real-time categorization, and library browsing.

## 🚀 Quick Start

### Launch the Web Interface

**Option 1: Batch File (Windows)**
```bash
START_WEB_INTERFACE.bat
```

**Option 2: Python Command**
```bash
python web_interface.py
```

**Option 3: Direct Python**
```python
from web_interface import app
app.run(host='0.0.0.0', port=5000)
```

Then open your browser and go to:
```
http://localhost:5000
```

## 📋 Features

### 1. **Drag & Drop Upload**
- Drag PDF files directly into the browser
- Or click to browse and select files
- Upload multiple PDFs at once
- Real-time upload progress

### 2. **AI-Powered Categorization**
- Automatic category suggestions
- Smart filename analysis
- Content-based classification
- Confidence scoring (High/Medium/Low)

### 3. **Interactive Review**
- See all suggestions before organizing
- Edit categories manually
- Edit suggested filenames
- Approve or reject individual files
- Batch approve/reject all

### 4. **Library Browser**
- Browse organized PDFs
- Hierarchical folder view
- File size information
- Category statistics

### 5. **Statistics Dashboard**
- Total PDFs organized
- Category breakdown
- Last run date
- Visual charts

### 6. **Provider Selection**
- Choose between Gemini, Anthropic, or DeepSeek
- Configure API keys
- Set ebooks folder path

## 🎯 How to Use

### Step 1: Configure Settings

First time using the web interface:

1. Click **⚙️ Settings** button
2. Enter your **Ebooks Folder** path (e.g., `F:\ebooks`)
3. Select your **AI Provider** (Gemini, Anthropic, or DeepSeek)
4. Enter your **API Key**
5. Click **Save Settings**

### Step 2: Upload PDFs

1. **Drag & drop** PDFs into the upload area
   - OR click **Choose Files** to browse
2. See uploaded files listed with sizes
3. Click **🤖 Analyze & Categorize**

### Step 3: Review Suggestions

The AI will analyze each PDF and suggest:
- **Category**: Where to organize it
- **Rename**: Better filename (if current is gibberish)
- **Confidence**: How confident the AI is

For each PDF, you can:
- ✅ **Approve**: Include in organization
- ❌ **Reject**: Skip this file
- ✏️ **Edit**: Change category or filename
- Use **Approve All** or **Reject All** for batch actions

### Step 4: Organize

1. Review all suggestions
2. Click **📦 Organize Approved Files**
3. Confirm the action
4. Watch as PDFs are moved and renamed!

### Step 5: Browse Library

Click **📁 Browse Library** to:
- See your organized PDFs
- Navigate folder structure
- View statistics

## 📸 Interface Overview

### Main Upload Screen
```
┌─────────────────────────────────────────┐
│   📚 PDF Organizer                      │
│   AI-Powered Library Management         │
│   [Settings] [Browse] [Statistics]      │
├─────────────────────────────────────────┤
│                                         │
│   ┌───────────────────────────────┐    │
│   │       📄                       │    │
│   │   Drag & Drop PDFs Here       │    │
│   │   or click to browse          │    │
│   │   [Choose Files]              │    │
│   └───────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

### Review Screen
```
┌─────────────────────────────────────────┐
│   📋 Categorization Results             │
│   [✓ Approve All] [✗ Reject All]       │
│   [📦 Organize Approved Files]          │
├─────────────────────────────────────────┤
│   ┌─────────────────────────────┐      │
│   │ Document.pdf  🔍 Gibberish   │      │
│   │ Category: Science/Biology    │      │
│   │ Rename: Study of Rabbits     │      │
│   │ Confidence: HIGH              │      │
│   │              [✓ Approve] [✗] │      │
│   └─────────────────────────────┘      │
│                                         │
│   ✅ APPROVED                           │
│   ┌─────────────────────────────┐      │
│   │ Python Guide.pdf             │      │
│   │ Category: Programming/Python │      │
│   │ Confidence: HIGH              │      │
│   └─────────────────────────────┘      │
└─────────────────────────────────────────┘
```

## 🎨 Visual Features

### Color Coding

- **Green border**: Approved files
- **Red opacity**: Rejected files
- **Blue badge**: Gibberish filename detected
- **Green badge**: High confidence
- **Yellow badge**: Medium confidence
- **Red badge**: Low confidence

### Real-time Updates

- Upload progress spinner
- Analysis loading indicator
- Organization progress overlay
- Toast notifications for all actions

## ⚙️ Configuration

### Settings Page

```javascript
{
  "ebooks_folder": "F:/ebooks",      // Where PDFs are organized
  "provider": "gemini",              // AI provider
  "api_key": "your-api-key-here",   // API key
  "batch_delay": 10                  // Not used in web interface
}
```

### API Provider Links

- **Gemini**: https://aistudio.google.com/app/apikey
- **Anthropic**: https://console.anthropic.com/
- **DeepSeek**: https://platform.deepseek.com/

## 🔧 Advanced Usage

### Custom Port

Run on a different port:

```bash
python web_interface.py --port 8080
```

Or modify the code:
```python
app.run(host='0.0.0.0', port=8080)
```

### Access from Other Devices

If running on your local network:

1. Find your computer's IP address
2. Access from another device: `http://YOUR_IP:5000`
3. Make sure firewall allows port 5000

### Production Deployment

For production use, use a proper WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_interface:app
```

## 📊 API Endpoints

The web interface provides a RESTful API:

### GET `/`
Main page (HTML)

### GET/POST `/api/settings`
Get or update settings

### POST `/api/upload`
Upload PDF files
- Body: `FormData` with files
- Returns: List of uploaded files with IDs

### POST `/api/analyze`
Analyze PDFs and get categorization
- Body: `{ files: [...] }`
- Returns: Categorization results

### POST `/api/organize`
Move approved files to ebooks folder
- Body: `{ files: [...] }`
- Returns: Success/failure status

### GET `/api/browse`
Browse organized library
- Returns: File tree and statistics

### GET `/api/stats`
Get organization statistics
- Returns: Total organized, categories, last run

### GET `/api/categories`
Get available categories
- Returns: List of existing categories

## 🐛 Troubleshooting

### Port Already in Use

```
Error: Address already in use
```

**Solution**: Change the port:
```python
app.run(port=5001)  # Use different port
```

### Can't Access from Browser

1. Check firewall settings
2. Try `http://127.0.0.1:5000` instead of `localhost`
3. Make sure server is running

### Upload Fails

1. Check file size (max 100MB per file)
2. Ensure files are PDFs
3. Check browser console for errors

### Analysis Fails

1. Verify API key is correct
2. Check ebooks folder exists
3. Ensure API provider is selected

### Files Not Organizing

1. Make sure files are approved (green border)
2. Check ebooks folder permissions
3. Verify category paths are valid

## 💡 Tips & Best Practices

### Performance

- Upload in batches of 20-50 files for best results
- Large PDFs (>10MB) may take longer to process
- Analysis is batched - multiple PDFs = one API call

### Workflow

1. **Daily Use**: Leave web interface open, drag PDFs as they arrive
2. **Bulk Organization**: Upload many PDFs, review all at once
3. **Careful Review**: Always check suggestions before organizing

### Category Management

- Edit categories to match your structure
- Use existing categories when possible
- Create subcategories with `/` (e.g., `Science/Biology/Zoology`)

### Filename Editing

- AI suggests better names for gibberish files
- Edit names before organizing
- Keep names descriptive but concise

## 🔐 Security Notes

### Local Use Only (Default)

By default, the web interface is accessible only from your computer:
```python
app.run(host='127.0.0.1')  # Local only
```

### Network Access

If you enable network access (`host='0.0.0.0'`):
- Anyone on your network can access it
- API keys are stored in session (not secure for production)
- Use HTTPS in production
- Add authentication for sensitive use

### API Key Storage

- API keys stored in Flask session
- Not persisted to disk
- Lost when browser session ends
- Re-enter after restarting browser

## 📈 Future Enhancements

Potential improvements:
- [ ] User authentication
- [ ] Multiple user accounts
- [ ] Persistent settings storage
- [ ] OCR for scanned PDFs
- [ ] PDF preview thumbnails
- [ ] Advanced search
- [ ] Category templates
- [ ] Undo functionality
- [ ] Dark mode
- [ ] Mobile-responsive design
- [ ] Batch operations history

## 🆘 Support

Having issues? Check:

1. **Console Output**: Look for error messages in terminal
2. **Browser Console**: Check for JavaScript errors (F12)
3. **Network Tab**: Inspect API calls
4. **Log Files**: Check Flask logs

## 🎉 Enjoy!

The web interface makes PDF organization beautiful and intuitive. Drag, drop, review, organize!

Happy organizing! 📚✨
