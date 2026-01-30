#!/usr/bin/env python3
"""
PDF Organizer - Web Interface
Modern web UI for PDF organization with drag & drop
"""

import os
import json
import shutil
import webbrowser
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from pdf_organizer_batch import BatchPDFOrganizer
from pdf_content_analyzer import PDFContentAnalyzer

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = Path.home() / 'pdf_organizer_uploads'
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# In-memory storage for session data (use Redis in production)
pending_pdfs = {}
analysis_results = {}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    if request.method == 'POST':
        data = request.json
        session['ebooks_folder'] = data.get('ebooks_folder')
        session['provider'] = data.get('provider', 'gemini')
        session['api_key'] = data.get('api_key')
        session['batch_delay'] = data.get('batch_delay', 10)

        return jsonify({'success': True, 'message': 'Settings saved'})

    return jsonify({
        'ebooks_folder': session.get('ebooks_folder', ''),
        'provider': session.get('provider', 'gemini'),
        'api_key': session.get('api_key', ''),
        'batch_delay': session.get('batch_delay', 10)
    })


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    uploaded = []

    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER'] / filename
            file.save(filepath)

            # Generate unique ID
            file_id = f"{datetime.now().timestamp()}_{filename}"

            uploaded.append({
                'id': file_id,
                'filename': filename,
                'path': str(filepath),
                'size': filepath.stat().st_size
            })

    return jsonify({
        'success': True,
        'files': uploaded
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_pdfs():
    """Analyze uploaded PDFs and suggest categorization"""
    data = request.json
    file_paths = data.get('files', [])

    if not session.get('api_key'):
        return jsonify({'error': 'API key not configured'}), 400

    if not session.get('ebooks_folder'):
        return jsonify({'error': 'Ebooks folder not configured'}), 400

    try:
        # Create temporary organizer
        organizer = BatchPDFOrganizer(
            downloads_folder=app.config['UPLOAD_FOLDER'],
            ebooks_folder=session.get('ebooks_folder'),
            api_key=session.get('api_key'),
            provider=session.get('provider', 'gemini'),
            use_content_analysis=True
        )

        # Get PDF info
        pdf_list = []
        for file_info in file_paths:
            pdf_path = Path(file_info['path'])
            if pdf_path.exists():
                info = organizer.get_pdf_info(pdf_path)
                info['id'] = file_info['id']
                pdf_list.append(info)

        # Load categories
        categories = organizer.load_or_analyze_categories()

        # Batch categorize
        categorizations = organizer.batch_categorize_all(pdf_list, categories)

        # Match results
        results = []
        categorization_map = {cat['number']: cat for cat in categorizations}

        for i, pdf_info in enumerate(pdf_list, 1):
            cat_result = categorization_map.get(i, {
                'category': 'Uncategorized',
                'confidence': 'low',
                'rename': None
            })

            results.append({
                'id': pdf_info['id'],
                'filename': pdf_info['filename'],
                'path': pdf_info['path'],
                'category': cat_result.get('category', 'Uncategorized'),
                'confidence': cat_result.get('confidence', 'low'),
                'rename': cat_result.get('rename'),
                'is_gibberish': pdf_info.get('is_gibberish', False),
                'has_content': pdf_info.get('has_content', False),
                'approved': False  # User needs to approve
            })

        # Store results for later use
        session_id = session.get('session_id', str(datetime.now().timestamp()))
        session['session_id'] = session_id
        analysis_results[session_id] = results

        organizer.cleanup()

        return jsonify({
            'success': True,
            'results': results,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/organize', methods=['POST'])
def organize_pdfs():
    """Organize approved PDFs"""
    data = request.json
    approved_files = data.get('files', [])

    if not session.get('api_key'):
        return jsonify({'error': 'API key not configured'}), 400

    try:
        organizer = BatchPDFOrganizer(
            downloads_folder=app.config['UPLOAD_FOLDER'],
            ebooks_folder=session.get('ebooks_folder'),
            api_key=session.get('api_key'),
            provider=session.get('provider', 'gemini')
        )

        organized = []
        failed = []

        for file_info in approved_files:
            try:
                result = {
                    'source': file_info['path'],
                    'filename': file_info['filename'],
                    'category': file_info['category'],
                    'rename_to': file_info.get('rename')
                }

                organizer.move_pdf(result)
                organized.append(file_info['filename'])

                # Clean up upload
                Path(file_info['path']).unlink(missing_ok=True)

            except Exception as e:
                failed.append({
                    'filename': file_info['filename'],
                    'error': str(e)
                })

        organizer.save_log()
        organizer.cleanup()

        return jsonify({
            'success': True,
            'organized': organized,
            'failed': failed
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/browse')
def browse_library():
    """Browse organized PDF library"""
    ebooks_folder = session.get('ebooks_folder')

    if not ebooks_folder or not Path(ebooks_folder).exists():
        return jsonify({'error': 'Ebooks folder not configured or does not exist'}), 400

    ebooks_path = Path(ebooks_folder)

    # Build file tree
    def build_tree(path, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return None

        items = []
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    children = build_tree(item, max_depth, current_depth + 1)
                    pdf_count = len(list(item.rglob('*.pdf')))
                    items.append({
                        'name': item.name,
                        'type': 'folder',
                        'path': str(item.relative_to(ebooks_path)),
                        'pdf_count': pdf_count,
                        'children': children or []
                    })
                elif item.suffix.lower() == '.pdf':
                    items.append({
                        'name': item.name,
                        'type': 'file',
                        'path': str(item.relative_to(ebooks_path)),
                        'size': item.stat().st_size
                    })
        except PermissionError:
            pass

        return items

    tree = build_tree(ebooks_path)

    # Get statistics
    total_pdfs = len(list(ebooks_path.rglob('*.pdf')))
    total_folders = len([d for d in ebooks_path.rglob('*') if d.is_dir()])

    return jsonify({
        'success': True,
        'tree': tree,
        'stats': {
            'total_pdfs': total_pdfs,
            'total_folders': total_folders,
            'ebooks_folder': str(ebooks_path)
        }
    })


@app.route('/api/stats')
def get_stats():
    """Get organization statistics"""
    ebooks_folder = session.get('ebooks_folder')

    if not ebooks_folder:
        return jsonify({'error': 'Ebooks folder not configured'}), 400

    ebooks_path = Path(ebooks_folder)
    log_file = ebooks_path / 'organization_log.json'

    if not log_file.exists():
        return jsonify({
            'total_organized': 0,
            'last_run': None,
            'categories': {}
        })

    with open(log_file, 'r', encoding='utf-8') as f:
        log = json.load(f)

    # Count by category
    category_counts = {}
    for item in log.get('organized_files', []):
        cat = item.get('category', 'Uncategorized')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return jsonify({
        'total_organized': len(log.get('organized_files', [])),
        'last_run': log.get('last_run'),
        'categories': category_counts
    })


@app.route('/api/categories')
def get_categories():
    """Get available categories"""
    ebooks_folder = session.get('ebooks_folder')

    if not ebooks_folder:
        return jsonify([])

    try:
        organizer = BatchPDFOrganizer(
            downloads_folder=app.config['UPLOAD_FOLDER'],
            ebooks_folder=ebooks_folder,
            api_key='dummy',  # Not needed for category analysis
            provider='gemini'
        )

        categories = organizer.load_or_analyze_categories()

        category_list = [
            {
                'path': path,
                'count': info['count'],
                'depth': info['depth']
            }
            for path, info in sorted(categories.items())
        ]

        organizer.cleanup()

        return jsonify(category_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    """Open browser after a short delay to ensure server is ready"""
    import time
    time.sleep(1.5)  # Wait for server to start
    webbrowser.open('http://localhost:5000')


def main():
    """Run the web interface"""
    print("="*70)
    print("  PDF Organizer - Web Interface")
    print("="*70)
    print()
    print("Starting web server...")
    print()
    print("Your browser will open automatically to:")
    print("  → http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)
    print()

    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == '__main__':
    main()
