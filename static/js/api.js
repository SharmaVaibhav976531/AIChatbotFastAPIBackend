// static/js/api.js

class ApiClient {
    constructor() {
        this.baseURL = '';
        this.refreshPromise = null; // Prevents multiple simultaneous refresh calls
    }

    getAccessToken() {
        return localStorage.getItem('access_token');
    }

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    setTokens(access, refresh) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    }

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('current_session_id');
    }

    /**
     * Core fetch wrapper with automatic JWT refresh handling.
     */
    async request(endpoint, options = {}) {
        const token = this.getAccessToken();
        
        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // First attempt
        let response = await fetch(`${this.baseURL}${endpoint}`, { ...options, headers });

        // Handle 401 Unauthorized (Token Expired)
        if (response.status === 401 && this.getRefreshToken()) {
            console.warn('[API] Access token expired. Attempting refresh...');
            
            // If a refresh is already in progress, wait for it
            if (this.refreshPromise) {
                await this.refreshPromise;
            } else {
                this.refreshPromise = this._refreshTokens();
                const success = await this.refreshPromise;
                this.refreshPromise = null; // Reset

                if (!success) {
                    this.clearTokens();
                    window.location.reload(); // Force back to login
                    throw new Error('Authentication failed');
                }
            }

            // Retry the original request with the new token
            headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
            response = await fetch(`${this.baseURL}${endpoint}`, { ...options, headers });
        }

        // Parse JSON safely
        let data = null;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        }

        if (!response.ok) {
            const error = new Error(data?.detail || `HTTP Error: ${response.status}`);
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    }

    /**
     * Internal method to refresh tokens.
     */
    async _refreshTokens() {
        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: this.getRefreshToken() })
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access_token, data.refresh_token);
                console.log('[API] ✅ Tokens refreshed successfully');
                return true;
            }
            return false;
        } catch (error) {
            console.error('[API] ❌ Token refresh failed:', error);
            return false;
        }
    }

    // --- API Endpoints Wrappers ---

    async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async signup(username, email, password) {
        return this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    }

    async logout() {
        const token = this.getAccessToken();
        if (token) {
            // Fire and forget
            fetch(`${this.baseURL}/auth/logout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            }).catch(() => {});
        }
        this.clearTokens();
    }

    async getProfile() {
        return this.request('/auth/me');
    }

    async getSessions() {
        return this.request('/sessions');
    }

    async createSession(title = 'New Chat') {
        return this.request('/sessions', {
            method: 'POST',
            body: JSON.stringify({ title })
        });
    }

    async getSessionMessages(sessionId) {
        return this.request(`/sessions/${sessionId}/messages`);
    }

    async updateSession(sessionId, title) {
        return this.request(`/sessions/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify({ title })
        });
    }

    async deleteSession(sessionId) {
        return this.request(`/sessions/${sessionId}`, { method: 'DELETE' });
    }

    async sendMessage(message, sessionId) {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({ message, session_id: sessionId })
        });
    }

    async getDocuments() {
        return this.request('/documents/');
    }

    async deleteDocument(documentId) {
        return this.request(`/documents/${documentId}`, { method: 'DELETE' });
    }

    // --- Phase 6: Vector Search & Retrieval API Endpoints ---

    async search(query, topK = null, threshold = null, metric = null, filters = null) {
        return this.request('/search', {
            method: 'POST',
            body: JSON.stringify({
                query,
                top_k: topK,
                similarity_threshold: threshold,
                distance_metric: metric,
                filters
            })
        });
    }

    async vectorSearch(searchPayload) {
        return this.request('/vector-search', {
            method: 'POST',
            body: JSON.stringify(searchPayload)
        });
    }

    async retrieveContext(query, topK = null, threshold = null) {
        return this.request('/retrieve', {
            method: 'POST',
            body: JSON.stringify({
                query,
                top_k: topK,
                similarity_threshold: threshold
            })
        });
    }

    async getDocumentChunks(documentId, skip = 0, limit = 100) {
        return this.request(`/documents/${documentId}/chunks?skip=${skip}&limit=${limit}`);
    }

    async getDocumentMetadata(documentId) {
        return this.request(`/documents/${documentId}/metadata`);
    }
}

// Export a singleton instance
export const api = new ApiClient();