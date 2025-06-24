// Authentication and Document Viewer Integration for Chainlit
// This script manages user authentication and document viewing

class ChainlitDocumentIntegration {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8001';
        this.token = localStorage.getItem('auth_token');
        this.authenticated = !!this.token;
        this.init();
    }

    init() {
        // Add authentication status to UI
        this.addAuthUI();
        
        // Check if user is already authenticated
        if (this.token) {
            this.verifyToken();
        }
        
        // Add global function for opening document viewer
        window.openDocumentViewer = (docId) => this.openDocumentViewer(docId);
        
        // Add modal for document viewing
        this.createDocumentModal();
    }

    addAuthUI() {
        // Create authentication UI
        const authContainer = document.createElement('div');
        authContainer.id = 'auth-container';
        authContainer.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;

        if (this.authenticated) {
            authContainer.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: green;">✓ Authenticated</span>
                    <button onclick="documentIntegration.logout()" style="padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;">
                        Logout
                    </button>
                </div>
            `;
        } else {
            authContainer.innerHTML = `
                <div id="login-form">
                    <div style="margin-bottom: 10px; font-weight: bold;">Document Access</div>
                    <div style="margin-bottom: 10px;">
                        <input type="text" id="username" placeholder="Username" style="width: 120px; padding: 5px; border: 1px solid #ccc; border-radius: 4px;">
                    </div>
                    <div style="margin-bottom: 10px;">
                        <input type="password" id="password" placeholder="Password" style="width: 120px; padding: 5px; border: 1px solid #ccc; border-radius: 4px;">
                    </div>
                    <button onclick="documentIntegration.login()" style="width: 100%; padding: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Login
                    </button>
                    <div style="font-size: 11px; color: #666; margin-top: 5px;">
                        Demo: testuser / secret
                    </div>
                </div>
            `;
        }

        document.body.appendChild(authContainer);
    }

    async login() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            alert('Please enter username and password');
            return;
        }

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
                this.authenticated = true;
                
                // Update UI
                document.getElementById('auth-container').remove();
                this.addAuthUI();
                
                // Initialize document viewer with token
                if (window.documentViewer) {
                    window.documentViewer.token = this.token;
                }
                
                alert('Authentication successful! You can now view documents.');
            } else {
                alert('Authentication failed. Please check your credentials.');
            }
        } catch (error) {
            console.error('Authentication error:', error);
            alert('Authentication error. Please try again.');
        }
    }

    logout() {
        this.token = null;
        this.authenticated = false;
        localStorage.removeItem('auth_token');
        
        // Update UI
        document.getElementById('auth-container').remove();
        this.addAuthUI();
        
        alert('Logged out successfully.');
    }

    async verifyToken() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                // Token is invalid
                this.logout();
            }
        } catch (error) {
            console.error('Token verification error:', error);
            this.logout();
        }
    }

    createDocumentModal() {
        const modal = document.createElement('div');
        modal.id = 'document-modal';
        modal.style.cssText = `
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            overflow: auto;
        `;

        modal.innerHTML = `
            <div style="position: relative; margin: 2% auto; width: 90%; max-width: 1200px; background: white; border-radius: 8px; padding: 20px;">
                <button onclick="documentIntegration.closeDocumentViewer()" style="position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
                <div id="document-viewer-container"></div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    async openDocumentViewer(docId) {
        if (!this.authenticated) {
            alert('Please login first to view documents.');
            return;
        }

        const modal = document.getElementById('document-modal');
        const container = document.getElementById('document-viewer-container');
        
        modal.style.display = 'block';
        container.innerHTML = '<div style="text-align: center; padding: 50px;">Loading document...</div>';

        try {
            // Load document viewer script if not already loaded
            if (!window.documentViewer) {
                await this.loadScript('/public/document-viewer.js');
                // Set the token for the document viewer
                if (window.documentViewer) {
                    window.documentViewer.token = this.token;
                }
            }

            // Create the document viewer
            if (window.documentViewer) {
                await window.documentViewer.createDocumentViewer(docId, 'document-viewer-container');
            } else {
                container.innerHTML = '<div style="color: red; text-align: center; padding: 50px;">Error: Document viewer not available</div>';
            }
        } catch (error) {
            console.error('Error opening document viewer:', error);
            container.innerHTML = '<div style="color: red; text-align: center; padding: 50px;">Error loading document</div>';
        }
    }

    closeDocumentViewer() {
        const modal = document.getElementById('document-modal');
        modal.style.display = 'none';
        
        // Clear the container
        document.getElementById('document-viewer-container').innerHTML = '';
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script already exists
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
}

// Auto-inject and initialize
(function() {
    // Function to initialize the integration
    function initializeIntegration() {
        if (window.documentIntegration) {
            return; // Already initialized
        }
        window.documentIntegration = new ChainlitDocumentIntegration();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeIntegration);
    } else {
        initializeIntegration();
    }

    // Also try to initialize after a short delay for Chainlit's dynamic loading
    setTimeout(initializeIntegration, 1000);
})(); 