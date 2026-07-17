// static/js/documents.js
import { api } from './api.js';
import { ui } from './ui.js';

export const documents = {
    // ═══════════════════════════════════════════════════
    // DOM REFERENCES
    // ═══════════════════════════════════════════════════
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    attachBtn: document.getElementById('attach-file-btn'), // <-- ADDED
    uploadProgress: document.getElementById('upload-progress-container'),
    uploadFilename: document.getElementById('upload-filename'),
    uploadPercentage: document.getElementById('upload-percentage'),
    progressFill: document.getElementById('progress-fill'),
    uploadStatus: document.getElementById('upload-status'),
    documentList: document.getElementById('document-list'),
    refreshBtn: document.getElementById('refresh-docs-btn'),

    // ═══════════════════════════════════════════════════
    // STATE & CONFIGURATION
    // ═══════════════════════════════════════════════════
    pollingInterval: null,
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_EXTENSIONS: ['.pdf', '.docx', '.txt', '.csv', '.md'],

    // ═══════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════
    init() {
        this.setupDropZone();
        this.setupFileInput();
        this.setupAttachButton(); // <-- ADDED
        this.setupRefreshButton();
        this.startPolling();
        console.log('[DOCUMENTS] ✅ Module initialized');
    },

    // ═══════════════════════════════════════════════════
    // EVENT LISTENERS SETUP
    // ═══════════════════════════════════════════════════
    setupDropZone() {
        if (!this.dropZone) return;

        this.dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.dropZone.classList.remove('drag-over');
            });
        });

        this.dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFiles(files);
            }
        });
    },

    setupFileInput() {
        if (!this.fileInput) return;

        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files);
                e.target.value = ''; // Reset so same file can be re-uploaded
            }
        });
    },

    setupAttachButton() {
        // Wire up the paperclip icon in the chat input area
        if (this.attachBtn && this.fileInput) {
            this.attachBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.fileInput.click();
            });
        }
    },

    setupRefreshButton() {
        if (!this.refreshBtn) return;
        this.refreshBtn.addEventListener('click', () => {
            this.loadDocuments();
            ui.toast.show('Documents refreshed', 'info', 2000);
        });
    },

    // ═══════════════════════════════════════════════════
    // FILE VALIDATION & UPLOAD
    // ═══════════════════════════════════════════════════
    handleFiles(fileList) {
        const files = Array.from(fileList);
        
        for (const file of files) {
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (!this.ALLOWED_EXTENSIONS.includes(ext)) {
                ui.toast.show(`Unsupported file type: ${ext}`, 'error');
                continue;
            }

            if (file.size > this.MAX_FILE_SIZE) {
                const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
                ui.toast.show(`File too large: ${sizeMB}MB (max 50MB)`, 'error');
                continue;
            }

            this.uploadFile(file);
        }
    },

    uploadFile(file) {
        console.log(`[DOCUMENTS] Uploading: ${file.name}`);
        this.showProgress(file.name, 'Uploading...');
        
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        const token = api.getAccessToken();

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                this.updateProgress(percent, 'Uploading...');
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                this.updateProgress(100, 'Processing...');
                ui.toast.show(`${file.name} uploaded successfully`, 'success');
                setTimeout(() => this.hideProgress(), 1500);
                this.loadDocuments();
            } else {
                let errorMsg = 'Upload failed';
                try {
                    const data = JSON.parse(xhr.responseText);
                    errorMsg = data.detail || errorMsg;
                } catch (e) {}
                
                ui.toast.show(`${file.name}: ${errorMsg}`, 'error');
                this.hideProgress();
            }
        };

        xhr.onerror = () => {
            ui.toast.show(`Network error uploading ${file.name}`, 'error');
            this.hideProgress();
        };

        xhr.open('POST', '/documents/upload');
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        xhr.send(formData);
    },

    // ═══════════════════════════════════════════════════
    // PROGRESS UI HELPERS
    // ═══════════════════════════════════════════════════
    showProgress(filename, status) {
        if (!this.uploadProgress) return;
        this.uploadFilename.textContent = filename;
        this.uploadStatus.textContent = status;
        this.progressFill.style.width = '0%';
        this.uploadPercentage.textContent = '0%';
        this.uploadProgress.classList.remove('hidden');
    },

    updateProgress(percent, status) {
        if (!this.progressFill) return;
        this.progressFill.style.width = `${percent}%`;
        this.uploadPercentage.textContent = `${percent}%`;
        if (status) this.uploadStatus.textContent = status;
    },

    hideProgress() {
        if (!this.uploadProgress) return;
        this.uploadProgress.classList.add('hidden');
    },

    // ═══════════════════════════════════════════════════
    // DOCUMENT LIST & STATUS POLLING
    // ═══════════════════════════════════════════════════
    async loadDocuments() {
        try {
            const data = await api.getDocuments();
            this.renderDocumentList(data.documents || []);
        } catch (error) {
            console.error('[DOCUMENTS] Failed to load:', error);
        }
    },

    renderDocumentList(documents) {
        if (!this.documentList) return;
        
        if (documents.length === 0) {
            this.documentList.innerHTML = `
                <div class="empty-state">
                    <p>No documents uploaded yet.</p>
                </div>
            `;
            return;
        }

        this.documentList.innerHTML = documents.map(doc => {
            const statusClass = this.getStatusClass(doc.status);
            const statusLabel = doc.status.charAt(0).toUpperCase() + doc.status.slice(1).toLowerCase();
            const sizeMB = (doc.file_size / (1024 * 1024)).toFixed(2);
            const date = new Date(doc.created_at).toLocaleDateString();
            
            return `
                <div class="document-item" data-id="${doc.id}">
                    <div class="doc-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                    </div>
                    <div class="doc-info">
                        <div class="doc-name" title="${this.escapeHtml(doc.original_filename)}">
                            ${this.escapeHtml(doc.original_filename)}
                        </div>
                        <div class="doc-meta">${sizeMB} MB • ${date}</div>
                    </div>
                    <span class="doc-status ${statusClass}">${statusLabel}</span>
                    <button class="btn btn-ghost btn-xs delete-doc-btn" data-id="${doc.id}" title="Delete">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            `;
        }).join('');

        this.documentList.querySelectorAll('.delete-doc-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteDocument(btn.dataset.id);
            });
        });
    },

    getStatusClass(status) {
        const map = {
            'UPLOADED': 'status-processing',
            'PROCESSING': 'status-processing',
            'COMPLETED': 'status-completed',
            'FAILED': 'status-failed'
        };
        return map[status] || 'status-processing';
    },

    async deleteDocument(docId) {
        if (!confirm('Delete this document and all its processed data?')) return;
        try {
            await api.deleteDocument(docId);
            ui.toast.show('Document deleted', 'success');
            this.loadDocuments();
        } catch (error) {
            ui.toast.show(error.message || 'Failed to delete document', 'error');
        }
    },

    startPolling() {
        this.stopPolling();
        this.pollingInterval = setInterval(async () => {
            const rightSidebar = document.getElementById('right-sidebar');
            if (rightSidebar && rightSidebar.classList.contains('hidden')) return;
            await this.loadDocuments();
        }, 3000);
    },

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};