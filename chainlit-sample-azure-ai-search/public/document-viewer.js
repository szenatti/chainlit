// Document Viewer Components
// This module provides client-side document viewing functionality

class DocumentViewer {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8001';  // API server URL
        this.token = localStorage.getItem('auth_token');
    }

    async authenticate(username, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                localStorage.setItem('auth_token', this.token);
                return true;
            } else {
                throw new Error('Authentication failed');
            }
        } catch (error) {
            console.error('Authentication error:', error);
            return false;
        }
    }

    async getDocumentInfo(docId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/document/${docId}/info`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get document info: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error getting document info:', error);
            return null;
        }
    }

    async createDocumentViewer(docId, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Show loading state
        container.innerHTML = '<div class="loading">Loading document...</div>';

        try {
            const docInfo = await this.getDocumentInfo(docId);
            if (!docInfo) {
                container.innerHTML = '<div class="error">Failed to load document information</div>';
                return;
            }

            const fileExtension = docInfo.file_extension.toLowerCase();
            const fileUrl = `${this.apiBaseUrl}/api/file?doc_id=${docId}`;

            switch (fileExtension) {
                case '.pdf':
                    await this.createPDFViewer(container, fileUrl, docInfo);
                    break;
                case '.docx':
                case '.doc':
                    await this.createDocxViewer(container, fileUrl, docInfo);
                    break;
                case '.md':
                    await this.createMarkdownViewer(container, fileUrl, docInfo);
                    break;
                case '.txt':
                    await this.createTextViewer(container, fileUrl, docInfo);
                    break;
                case '.csv':
                    await this.createCSVViewer(container, fileUrl, docInfo);
                    break;
                case '.xlsx':
                case '.xls':
                    await this.createExcelViewer(container, fileUrl, docInfo);
                    break;
                case '.jpg':
                case '.jpeg':
                case '.png':
                case '.gif':
                    await this.createImageViewer(container, fileUrl, docInfo);
                    break;
                case '.mp4':
                case '.avi':
                    await this.createVideoViewer(container, fileUrl, docInfo);
                    break;
                default:
                    this.createDownloadViewer(container, fileUrl, docInfo);
            }
        } catch (error) {
            console.error('Error creating document viewer:', error);
            container.innerHTML = '<div class="error">Error loading document</div>';
        }
    }

    async createPDFViewer(container, fileUrl, docInfo) {
        // Create PDF viewer using PDF.js
        container.innerHTML = `
            <div class="document-viewer pdf-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button id="prev-page">Previous</button>
                    <span id="page-info">Page 1 of ?</span>
                    <button id="next-page">Next</button>
                    <button onclick="window.open('${fileUrl}', '_blank')">Open in New Tab</button>
                </div>
                <canvas id="pdf-canvas" style="border: 1px solid #ccc; width: 100%; max-width: 800px;"></canvas>
            </div>
        `;

        // Load PDF.js if needed
        if (typeof pdfjsLib === 'undefined') {
            await this.loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js');
        }

        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

        try {
            const pdf = await pdfjsLib.getDocument(fileUrl).promise;
            let currentPage = 1;
            const canvas = document.getElementById('pdf-canvas');
            const ctx = canvas.getContext('2d');

            const renderPage = async (pageNumber) => {
                const page = await pdf.getPage(pageNumber);
                const viewport = page.getViewport({ scale: 1.5 });
                
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                
                await page.render({
                    canvasContext: ctx,
                    viewport: viewport
                }).promise;

                document.getElementById('page-info').textContent = `Page ${pageNumber} of ${pdf.numPages}`;
            };

            await renderPage(currentPage);

            document.getElementById('prev-page').onclick = async () => {
                if (currentPage > 1) {
                    currentPage--;
                    await renderPage(currentPage);
                }
            };

            document.getElementById('next-page').onclick = async () => {
                if (currentPage < pdf.numPages) {
                    currentPage++;
                    await renderPage(currentPage);
                }
            };

        } catch (error) {
            console.error('Error loading PDF:', error);
            container.innerHTML = `<div class="error">Error loading PDF: ${error.message}</div>`;
        }
    }

    async createDocxViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer docx-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')">Download Original</button>
                </div>
                <div id="docx-content" style="border: 1px solid #ccc; padding: 20px; background: white;"></div>
            </div>
        `;

        if (typeof mammoth === 'undefined') {
            await this.loadScript('https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.4.2/mammoth.browser.min.js');
        }

        try {
            const response = await fetch(fileUrl, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });

            if (response.ok) {
                const arrayBuffer = await response.arrayBuffer();
                const result = await mammoth.convertToHtml({ arrayBuffer });
                document.getElementById('docx-content').innerHTML = result.value;
            } else {
                throw new Error('Failed to fetch document');
            }
        } catch (error) {
            console.error('Error loading DOCX:', error);
            container.innerHTML = `<div class="error">Error loading document: ${error.message}</div>`;
        }
    }

    async createMarkdownViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer markdown-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')">View Raw</button>
                </div>
                <div id="markdown-content" style="border: 1px solid #ccc; padding: 20px; background: white;"></div>
            </div>
        `;

        if (typeof marked === 'undefined') {
            await this.loadScript('https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js');
        }

        try {
            const response = await fetch(fileUrl, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });

            if (response.ok) {
                const text = await response.text();
                document.getElementById('markdown-content').innerHTML = marked.parse(text);
            } else {
                throw new Error('Failed to fetch document');
            }
        } catch (error) {
            console.error('Error loading Markdown:', error);
            container.innerHTML = `<div class="error">Error loading document: ${error.message}</div>`;
        }
    }

    async createTextViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer text-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')">Download</button>
                </div>
                <pre id="text-content" style="border: 1px solid #ccc; padding: 20px; background: white; white-space: pre-wrap; overflow: auto; max-height: 500px;"></pre>
            </div>
        `;

        try {
            const response = await fetch(fileUrl, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const text = await response.text();
                document.getElementById('text-content').textContent = text;
            } else {
                throw new Error('Failed to fetch document');
            }
        } catch (error) {
            console.error('Error loading text:', error);
            container.innerHTML = `<div class="error">Error loading document: ${error.message}</div>`;
        }
    }

    async createCSVViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer csv-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')">Download</button>
                </div>
                <div id="csv-table" style="border: 1px solid #ccc; padding: 10px; background: white; overflow: auto; max-height: 500px;"></div>
            </div>
        `;

        try {
            const response = await fetch(fileUrl, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const text = await response.text();
                const rows = text.split('\n').map(row => row.split(','));
                
                let tableHTML = '<table style="border-collapse: collapse; width: 100%;">';
                rows.forEach((row, index) => {
                    const tag = index === 0 ? 'th' : 'td';
                    tableHTML += '<tr>';
                    row.forEach(cell => {
                        tableHTML += `<${tag} style="border: 1px solid #ddd; padding: 8px;">${cell.trim()}</${tag}>`;
                    });
                    tableHTML += '</tr>';
                });
                tableHTML += '</table>';
                
                document.getElementById('csv-table').innerHTML = tableHTML;
            } else {
                throw new Error('Failed to fetch document');
            }
        } catch (error) {
            console.error('Error loading CSV:', error);
            container.innerHTML = `<div class="error">Error loading document: ${error.message}</div>`;
        }
    }

    async createImageViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer image-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')">View Full Size</button>
                </div>
                <img src="${fileUrl}" alt="${docInfo.filename}" style="max-width: 100%; height: auto; border: 1px solid #ccc;" />
            </div>
        `;
    }

    async createVideoViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer video-viewer">
                <h3>${docInfo.filename}</h3>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')">Download</button>
                </div>
                <video controls style="max-width: 100%; height: auto;">
                    <source src="${fileUrl}" type="${docInfo.content_type}">
                    Your browser does not support the video tag.
                </video>
            </div>
        `;
    }

    createDownloadViewer(container, fileUrl, docInfo) {
        container.innerHTML = `
            <div class="document-viewer download-viewer">
                <h3>${docInfo.filename}</h3>
                <p>File type: ${docInfo.content_type}</p>
                <p>Size: ${this.formatFileSize(docInfo.size)}</p>
                <div class="viewer-controls">
                    <button onclick="window.open('${fileUrl}', '_blank')" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer;">
                        Download File
                    </button>
                </div>
            </div>
        `;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
}

// Global instance
window.documentViewer = new DocumentViewer();

// CSS Styles
const styles = `
    .document-viewer {
        margin: 20px 0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        background: #f9f9f9;
    }
    
    .document-viewer h3 {
        margin-top: 0;
        color: #333;
    }
    
    .viewer-controls {
        margin: 10px 0;
        padding: 10px 0;
        border-bottom: 1px solid #eee;
    }
    
    .viewer-controls button {
        margin-right: 10px;
        padding: 8px 16px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .viewer-controls button:hover {
        background: #0056b3;
    }
    
    .loading, .error {
        padding: 20px;
        text-align: center;
        border-radius: 4px;
    }
    
    .loading {
        background: #e3f2fd;
        color: #1976d2;
    }
    
    .error {
        background: #ffebee;
        color: #c62828;
    }
`;

// Inject CSS
const styleSheet = document.createElement("style");
styleSheet.textContent = styles;
document.head.appendChild(styleSheet); 