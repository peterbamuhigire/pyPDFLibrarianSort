// PDF Organizer Web Interface - Main JavaScript

let uploadedFiles = [];
let analysisResults = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    setupDragDrop();
    setupFileInput();
    loadSettings();
    updateAPIKeyLink();
}

// Drag & Drop Setup
function setupDragDrop() {
    const dropZone = document.getElementById('dropZone');

    dropZone.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files).filter(f =>
            f.name.toLowerCase().endsWith('.pdf')
        );

        if (files.length > 0) {
            handleFiles(files);
        } else {
            showToast('Please drop PDF files only', 'warning');
        }
    });
}

function setupFileInput() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
}

// File Handling
async function handleFiles(files) {
    if (files.length === 0) return;

    showProgress('Uploading files...', `Uploading ${files.length} file(s)`);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadedFiles = uploadedFiles.concat(data.files);
            updateFileList();
            showToast(`Uploaded ${data.files.length} file(s)`, 'success');
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Upload error: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function updateFileList() {
    const fileList = document.getElementById('fileList');
    const filesContainer = document.getElementById('files');
    const fileCount = document.getElementById('fileCount');

    if (uploadedFiles.length === 0) {
        fileList.style.display = 'none';
        return;
    }

    fileList.style.display = 'block';
    fileCount.textContent = uploadedFiles.length;

    filesContainer.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-icon">📄</div>
                <div class="file-details">
                    <h4>${file.filename}</h4>
                    <div class="file-size">${formatBytes(file.size)}</div>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-danger" onclick="removeFile(${index})">✗</button>
            </div>
        </div>
    `).join('');
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileList();
}

function clearFiles() {
    if (confirm('Clear all uploaded files?')) {
        uploadedFiles = [];
        updateFileList();
    }
}

// Analysis
async function analyzeFiles() {
    if (uploadedFiles.length === 0) {
        showToast('No files to analyze', 'warning');
        return;
    }

    // Check settings
    const settings = await getSettings();
    if (!settings.api_key || !settings.ebooks_folder) {
        showToast('Please configure settings first', 'warning');
        showSettings();
        return;
    }

    showProgress('Analyzing PDFs...', 'This may take a moment');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: uploadedFiles })
        });

        const data = await response.json();

        if (data.success) {
            analysisResults = data.results;
            showResults();
            showToast('Analysis complete!', 'success');
        } else {
            showToast(data.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        showToast('Analysis error: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function showResults() {
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';

    const resultsContainer = document.getElementById('results');

    resultsContainer.innerHTML = analysisResults.map((result, index) => `
        <div class="result-card ${result.approved ? 'approved' : ''}" id="result-${index}">
            <div class="result-header">
                <div class="result-filename">
                    ${result.filename}
                    ${result.is_gibberish ? '<span class="gibberish-badge">🔍 Gibberish Name</span>' : ''}
                </div>
                <div class="result-actions">
                    <button class="btn btn-success" onclick="approveResult(${index})">✓</button>
                    <button class="btn btn-danger" onclick="rejectResult(${index})">✗</button>
                </div>
            </div>
            <div class="result-body">
                <div class="result-field">
                    <span class="result-label">Category:</span>
                    <input type="text" class="input result-value" value="${result.category}"
                           onchange="updateCategory(${index}, this.value)">
                </div>
                ${result.rename ? `
                    <div class="result-field">
                        <span class="result-label">Rename to:</span>
                        <input type="text" class="input result-value" value="${result.rename}"
                               onchange="updateRename(${index}, this.value)">
                    </div>
                ` : ''}
                <div class="result-field">
                    <span class="result-label">Confidence:</span>
                    <span class="confidence-badge confidence-${result.confidence}">
                        ${result.confidence.toUpperCase()}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

function approveResult(index) {
    analysisResults[index].approved = true;
    document.getElementById(`result-${index}`).classList.add('approved');
    showToast('Approved', 'success');
}

function rejectResult(index) {
    analysisResults[index].approved = false;
    document.getElementById(`result-${index}`).classList.remove('approved');
    document.getElementById(`result-${index}`).classList.add('rejected');
    showToast('Rejected', 'warning');
}

function approveAll() {
    analysisResults.forEach((_, index) => approveResult(index));
}

function rejectAll() {
    analysisResults.forEach((_, index) => rejectResult(index));
}

function updateCategory(index, value) {
    analysisResults[index].category = value;
}

function updateRename(index, value) {
    analysisResults[index].rename = value;
}

// Organize
async function organizeApproved() {
    const approved = analysisResults.filter(r => r.approved);

    if (approved.length === 0) {
        showToast('No files approved', 'warning');
        return;
    }

    if (!confirm(`Organize ${approved.length} approved file(s)?`)) {
        return;
    }

    showProgress('Organizing PDFs...', `Moving ${approved.length} file(s)`);

    try {
        const response = await fetch('/api/organize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: approved })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Organized ${data.organized.length} file(s)!`, 'success');

            if (data.failed.length > 0) {
                showToast(`${data.failed.length} file(s) failed`, 'error');
            }

            // Reset
            uploadedFiles = [];
            analysisResults = [];
            showUpload();
        } else {
            showToast(data.error || 'Organization failed', 'error');
        }
    } catch (error) {
        showToast('Organization error: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

// Settings
async function saveSettings() {
    const settings = {
        ebooks_folder: document.getElementById('ebooksFolder').value,
        provider: document.getElementById('provider').value,
        api_key: document.getElementById('apiKey').value
    };

    if (!settings.ebooks_folder || !settings.api_key) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        const data = await response.json();

        if (data.success) {
            showToast('Settings saved!', 'success');
            showUpload();
        } else {
            showToast(data.error || 'Failed to save settings', 'error');
        }
    } catch (error) {
        showToast('Error saving settings: ' + error.message, 'error');
    }
}

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();

        if (settings.ebooks_folder) {
            document.getElementById('ebooksFolder').value = settings.ebooks_folder;
        }
        if (settings.provider) {
            document.getElementById('provider').value = settings.provider;
        }
        if (settings.api_key) {
            document.getElementById('apiKey').value = settings.api_key;
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

async function getSettings() {
    const response = await fetch('/api/settings');
    return await response.json();
}

function updateAPIKeyLink() {
    const provider = document.getElementById('provider').value;
    const link = document.getElementById('apiKeyLink');

    const links = {
        'gemini': 'https://aistudio.google.com/app/apikey',
        'anthropic': 'https://console.anthropic.com/',
        'deepseek': 'https://platform.deepseek.com/'
    };

    link.href = links[provider];
    link.textContent = links[provider];
}

document.getElementById('provider').addEventListener('change', updateAPIKeyLink);

// Navigation
function showUpload() {
    hideAllSections();
    document.getElementById('uploadSection').style.display = 'block';
}

function showSettings() {
    hideAllSections();
    document.getElementById('settingsSection').style.display = 'block';
}

async function showBrowser() {
    hideAllSections();
    document.getElementById('browserSection').style.display = 'block';

    showProgress('Loading library...', '');

    try {
        const response = await fetch('/api/browse');
        const data = await response.json();

        if (data.success) {
            renderLibraryTree(data.tree, data.stats);
        } else {
            showToast(data.error || 'Failed to load library', 'error');
        }
    } catch (error) {
        showToast('Error loading library: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

async function showStats() {
    hideAllSections();
    document.getElementById('statsSection').style.display = 'block';

    showProgress('Loading statistics...', '');

    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        renderStats(stats);
    } catch (error) {
        showToast('Error loading stats: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function hideAllSections() {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
}

// Render Functions
function renderLibraryTree(tree, stats) {
    const statsBar = document.getElementById('libraryStats');
    statsBar.innerHTML = `
        <div><strong>Total PDFs:</strong> ${stats.total_pdfs}</div>
        <div><strong>Folders:</strong> ${stats.total_folders}</div>
        <div><strong>Location:</strong> ${stats.ebooks_folder}</div>
    `;

    const treeContainer = document.getElementById('libraryTree');
    treeContainer.innerHTML = renderTreeItems(tree);
}

function renderTreeItems(items) {
    if (!items || items.length === 0) return '<p>No files found</p>';

    return items.map(item => {
        if (item.type === 'folder') {
            return `
                <div class="folder-item">
                    📁 ${item.name} (${item.pdf_count} PDFs)
                    <div class="folder-children">
                        ${renderTreeItems(item.children)}
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="file-item-tree">
                    📄 ${item.name} (${formatBytes(item.size)})
                </div>
            `;
        }
    }).join('');
}

function renderStats(stats) {
    const container = document.getElementById('statsContent');

    const categoryList = Object.entries(stats.categories || {})
        .sort((a, b) => b[1] - a[1])
        .map(([cat, count]) => `<div><strong>${cat}:</strong> ${count} PDFs</div>`)
        .join('');

    container.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${stats.total_organized}</div>
            <div class="stat-label">Total Organized</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${Object.keys(stats.categories || {}).length}</div>
            <div class="stat-label">Categories Used</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.last_run ? new Date(stats.last_run).toLocaleDateString() : 'Never'}</div>
            <div class="stat-label">Last Run</div>
        </div>
        <div class="section">
            <h3>Category Breakdown</h3>
            ${categoryList || '<p>No data yet</p>'}
        </div>
    `;
}

// UI Helpers
function showProgress(message, detail) {
    document.getElementById('progressMessage').textContent = message;
    document.getElementById('progressDetail').textContent = detail;
    document.getElementById('progressOverlay').style.display = 'flex';
}

function hideProgress() {
    document.getElementById('progressOverlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
