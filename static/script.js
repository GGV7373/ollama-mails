// DOM Elements
const emailForm = document.getElementById('email-form');
const contextInput = document.getElementById('context');
const emailStyleSelect = document.getElementById('email-style');
const fileInput = document.getElementById('file-input');
const fileUploadArea = document.getElementById('file-upload-area');
const fileInfo = document.getElementById('file-info');
const generateBtn = document.getElementById('generate-btn');
const outputArea = document.getElementById('output-area');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const clearBtn = document.getElementById('clear-btn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const ollamaStatus = document.getElementById('ollama-status');
const emailStats = document.getElementById('email-stats');
const wordCountSpan = document.getElementById('word-count');
const charCountSpan = document.getElementById('char-count');

let selectedFile = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkOllamaStatus();
    setupEventListeners();
    setInterval(checkOllamaStatus, 30000); // Check every 30 seconds
});

// Event Listeners
emailForm.addEventListener('submit', handleEmailGeneration);
copyBtn.addEventListener('click', copyToClipboard);
downloadBtn.addEventListener('click', downloadEmail);
clearBtn.addEventListener('click', clearOutput);

// File Upload Handling
fileUploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        updateFileInfo();
    }
});

// Drag and Drop
fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        selectedFile = files[0];
        updateFileInfo();
    }
});

// Setup event listeners
function setupEventListeners() {
    // Add enter key support for quick generation (Ctrl+Enter)
    contextInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            emailForm.dispatchEvent(new Event('submit'));
        }
    });
}

// Update file info display
function updateFileInfo() {
    if (selectedFile) {
        const fileSize = (selectedFile.size / 1024).toFixed(2);
        fileInfo.innerHTML = `
            <strong>${selectedFile.name}</strong> (${fileSize} KB)
            <span style="margin-left: auto; cursor: pointer; color: #999;" onclick="clearFile()">x</span>
        `;
        fileInfo.classList.remove('hidden');
    }
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
}

// Check Ollama status
async function checkOllamaStatus() {
    try {
        const response = await fetch('/api/check-ollama', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.available) {
            ollamaStatus.textContent = `[OK] Ollama Connected (${data.models.join(', ')})`;
            ollamaStatus.classList.add('connected');
            ollamaStatus.classList.remove('disconnected');
            generateBtn.disabled = false;
        } else {
            ollamaStatus.textContent = '[OFFLINE] Ollama Disconnected';
            ollamaStatus.classList.add('disconnected');
            ollamaStatus.classList.remove('connected');
            generateBtn.disabled = true;
        }
    } catch (error) {
        ollamaStatus.textContent = '[ERROR] Ollama Unavailable';
        ollamaStatus.classList.add('disconnected');
        ollamaStatus.classList.remove('connected');
        generateBtn.disabled = true;
    }
}

// Handle email generation
async function handleEmailGeneration(e) {
    e.preventDefault();

    const context = contextInput.value.trim();
    const emailStyle = emailStyleSelect.value;

    if (!context) {
        showError('Please provide email context');
        return;
    }

    showLoading(true);
    clearError();

    try {
        const formData = new FormData();
        formData.append('context', context);
        formData.append('email_style', emailStyle);

        if (selectedFile) {
            formData.append('file', selectedFile);
        }

        const response = await fetch('/api/generate-email', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate email');
        }

        const data = await response.json();
        displayEmail(data.email);
        updateStats(data.email);

    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Display generated email
function displayEmail(email) {
    if (!email || email.startsWith('Error:')) {
        showError(email);
        return;
    }

    outputArea.innerHTML = `<pre>${escapeHtml(email)}</pre>`;
    emailStats.classList.remove('hidden');
    copyBtn.disabled = false;
    downloadBtn.disabled = false;
}

// Update word and character count
function updateStats(email) {
    const text = email.trim();
    const charCount = text.length;
    const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;

    wordCountSpan.textContent = `Words: ${wordCount}`;
    charCountSpan.textContent = `Characters: ${charCount}`;
}

// Copy to clipboard
async function copyToClipboard() {
    const text = outputArea.innerText;

    if (!text || text.includes('Generated email')) {
        showError('No email to copy');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '[Copied]';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    } catch (error) {
        showError('Failed to copy to clipboard');
    }
}

// Download email
async function downloadEmail() {
    const email = outputArea.innerText;

    if (!email || email.includes('Generated email')) {
        showError('No email to download');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('email_content', email);

        const response = await fetch('/api/download-email', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to download file');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'email.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        showError(`Download failed: ${error.message}`);
    }
}

// Clear output
function clearOutput() {
    outputArea.innerHTML = '<p class="placeholder">Generated email will appear here...</p>';
    emailStats.classList.add('hidden');
    clearError();
    copyBtn.disabled = true;
    downloadBtn.disabled = true;
}

// Show/hide loading spinner
function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
        generateBtn.disabled = true;
    } else {
        loading.classList.add('hidden');
        generateBtn.disabled = false;
    }
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// Clear error message
function clearError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
