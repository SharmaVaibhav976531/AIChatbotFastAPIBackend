// static/js/app.js
import { api } from './api.js';
import { ui } from './ui.js';
import { chat } from './chat.js';
import { documents } from './documents.js'; 
import { shortcuts } from './shortcuts.js'; 
import { initRetrievalPanel } from './retrieval_panel.js';
import { retrievalState } from './retrieval_state.js';

const app = {
    currentSessionId: localStorage.getItem('current_session_id') || null,
    
    // DOM Elements
    authView: document.getElementById('auth-view'),
    appView: document.getElementById('app-view'),
    loginForm: document.getElementById('login-form'),
    signupForm: document.getElementById('signup-form'),
    sessionList: document.getElementById('session-list'),
    currentSessionTitle: document.getElementById('current-session-title'),
    
    init() {
        // 1. Check Auth State
        if (api.getAccessToken()) {
            this.loadApp();
        } else {
            this.showAuth();
        }

        // 2. Setup Auth Listeners
        this.setupAuthListeners();
        
        // 3. Setup App Listeners (will be attached when app loads)
        this.setupAppListeners();
    },

    showAuth() {
        this.authView.classList.remove('hidden');
        this.appView.classList.add('hidden');
    },

    async loadApp() {
        this.authView.classList.add('hidden');
        this.appView.classList.remove('hidden');
        
        try {
            // Load User Profile
            const user = await api.getProfile();
            document.getElementById('user-display-name').textContent = user.username;
            document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();
            
            // Initialize Modules
            chat.init();
            documents.init(); 
            initRetrievalPanel();
            
            // Load Sessions
            await this.loadSessions();
            
        } catch (error) {
            console.error('Failed to load app:', error);
            api.clearTokens();
            this.showAuth();
            ui.toast.show('Session expired. Please log in again.', 'warning');
        }
    },

    setupAuthListeners() {
        // Toggle Login/Signup
        document.getElementById('toggle-auth-btn').addEventListener('click', () => {
            const isLogin = !this.loginForm.classList.contains('hidden');
            this.loginForm.classList.toggle('hidden');
            this.signupForm.classList.toggle('hidden');
            document.getElementById('toggle-auth-btn').textContent = isLogin ? 'Sign In' : 'Sign Up';
            document.getElementById('toggle-text').textContent = isLogin ? 'Already have an account?' : "Don't have an account?";
            document.getElementById('auth-title').textContent = isLogin ? 'Create Account' : 'Welcome to Nexus AI';
            document.getElementById('login-error').classList.add('hidden');
            document.getElementById('signup-error').classList.add('hidden');
        });

        // Login Handler
        this.loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            ui.setLoading('login-btn', true);
            document.getElementById('login-error').classList.add('hidden');

            try {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;
                
                const data = await api.login(username, password);
                api.setTokens(data.access_token, data.refresh_token);
                
                ui.toast.show('Login successful!', 'success');
                this.loginForm.reset();
                this.loadApp();
            } catch (error) {
                document.getElementById('login-error').textContent = error.message;
                document.getElementById('login-error').classList.remove('hidden');
                ui.toast.show(error.message, 'error');
            } finally {
                ui.setLoading('login-btn', false, 'Sign In');
            }
        });

        // Signup Handler
        this.signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            ui.setLoading('signup-btn', true);
            document.getElementById('signup-error').classList.add('hidden');

            try {
                const username = document.getElementById('signup-username').value;
                const email = document.getElementById('signup-email').value;
                const password = document.getElementById('signup-password').value;
                
                const data = await api.signup(username, email, password);
                api.setTokens(data.access_token, data.refresh_token);
                
                ui.toast.show('Account created successfully!', 'success');
                this.signupForm.reset();
                this.loadApp();
            } catch (error) {
                document.getElementById('signup-error').textContent = error.message;
                document.getElementById('signup-error').classList.remove('hidden');
                ui.toast.show(error.message, 'error');
            } finally {
                ui.setLoading('signup-btn', false, 'Create Account');
            }
        });
    },

    setupAppListeners() {
        // Theme Toggle
        document.getElementById('theme-toggle-btn').addEventListener('click', () => {
            ui.theme.toggle();
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            api.logout();
            this.currentSessionId = null;
            chat.clear();
            ui.toast.show('Logged out successfully', 'info');
            this.showAuth();
        });

        // New Chat
        document.getElementById('new-chat-btn').addEventListener('click', () => {
            this.createNewSession();
        });

        // Chat Form Submit
        chat.chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chat.userInput.value.trim();
            if (!message) return;

            // 1. Ensure we have a session
            if (!this.currentSessionId) {
                await this.createNewSession();
            }

            // 2. UI Updates
            chat.userInput.value = '';
            chat.userInput.style.height = 'auto';
            chat.sendBtn.disabled = true;
            chat.appendMessage('user', message);
            chat.showTyping();

            try {
                // 3. Vector Context Retrieval + Chat API Call
                let searchResult = null;
                try {
                    searchResult = await api.retrieveContext(message, null, null, this.currentSessionId);
                    retrievalState.setSearchResult(searchResult);
                } catch (searchErr) {
                    console.warn('[APP] Retrieval context failed:', searchErr);
                }

                const data = await api.sendMessage(message, this.currentSessionId);
                
                // 4. Success UI
                chat.hideTyping();
                chat.appendMessage('bot', data.reply, searchResult);
                
                // 5. Refresh sessions to update message counts/titles
                await this.loadSessions();
                
            } catch (error) {
                chat.hideTyping();
                chat.appendMessage('bot', `⚠️ Error: ${error.message}`);
                ui.toast.show('Failed to send message', 'error');
            } finally {
                chat.userInput.focus();
            }
        });

        // Rename Session
        document.getElementById('rename-session-btn').addEventListener('click', async () => {
            if (!this.currentSessionId) return;
            const newTitle = prompt('Enter new session title:', this.currentSessionTitle.textContent);
            if (!newTitle || !newTitle.trim() || newTitle === this.currentSessionTitle.textContent) return;

            try {
                await api.updateSession(this.currentSessionId, newTitle.trim());
                this.currentSessionTitle.textContent = newTitle.trim();
                await this.loadSessions();
                ui.toast.show('Session renamed', 'success');
            } catch (error) {
                ui.toast.show(error.message, 'error');
            }
        });

        // Delete Session
        document.getElementById('delete-session-btn').addEventListener('click', async () => {
            if (!this.currentSessionId) return;
            if (!confirm('Are you sure you want to delete this session and all its messages?')) return;

            try {
                await api.deleteSession(this.currentSessionId);
                this.currentSessionId = null;
                localStorage.removeItem('current_session_id');
                this.currentSessionTitle.textContent = 'New Conversation';
                chat.clear();
                await this.loadSessions();
                ui.toast.show('Session deleted', 'success');
            } catch (error) {
                ui.toast.show(error.message, 'error');
            }
        });

        // Right Sidebar Toggle (with smart polling)
        document.getElementById('toggle-right-sidebar').addEventListener('click', () => {
            const rightSidebar = document.getElementById('right-sidebar');
            rightSidebar.classList.toggle('hidden');
            
            // Start polling when sidebar opens, stop when closed
            if (rightSidebar.classList.contains('hidden')) {
                documents.stopPolling();
            } else {
                documents.loadDocuments(); // Immediate refresh
                documents.startPolling();
            }
        });

        document.getElementById('close-right-sidebar').addEventListener('click', () => {
            document.getElementById('right-sidebar').classList.add('hidden');
            documents.stopPolling();
        });

        // Mobile backdrop & Desktop Collapse for left sidebar
        const backdrop = document.getElementById('sidebar-backdrop');
        const leftSidebar = document.getElementById('left-sidebar');
        const collapseBtn = document.getElementById('collapse-sidebar-btn');

        // Restore initial sidebar state
        const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
        if (isCollapsed && window.innerWidth > 768) {
            leftSidebar?.classList.add('collapsed');
        }
        
        if (collapseBtn && leftSidebar) {
            collapseBtn.addEventListener('click', () => {
                const collapsed = leftSidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebar_collapsed', collapsed);
            });
        }

        document.getElementById('toggle-left-sidebar')?.addEventListener('click', () => {
            leftSidebar?.classList.toggle('collapsed');
            if (leftSidebar && !leftSidebar.classList.contains('collapsed')) {
                backdrop?.classList.add('active');
            } else {
                backdrop?.classList.remove('active');
            }
        });

        if (backdrop) {
            backdrop.addEventListener('click', () => {
                leftSidebar?.classList.add('collapsed');
                backdrop.classList.remove('active');
            });
        }

        // Debounced search for sessions
        const searchInput = document.getElementById('search-chats');
        if (searchInput) {
            const debouncedFilter = this.debounce((query) => {
                this.filterSessions(query);
            }, 300);
            
            searchInput.addEventListener('input', (e) => {
                debouncedFilter(e.target.value.toLowerCase());
            });
        }

        // Initialize shortcuts module
        shortcuts.init();
    },

    filterSessions(query) {
        const items = document.querySelectorAll('.session-item');
        if (!query) {
            items.forEach(item => item.classList.remove('filtered-out'));
            return;
        }
        
        items.forEach(item => {
            const title = item.querySelector('.session-item-title')?.textContent.toLowerCase() || '';
            if (title.includes(query)) {
                item.classList.remove('filtered-out');
            } else {
                item.classList.add('filtered-out');
            }
        });
    
    },

    async loadSessions() {
        try {
            const data = await api.getSessions();
            const userSessions = data.sessions || [];
            
            // Validate if stored currentSessionId belongs to user's sessions
            const sessionExists = userSessions.some(s => s.id === this.currentSessionId);
            if (!sessionExists) {
                if (userSessions.length > 0) {
                    this.currentSessionId = userSessions[0].id;
                    localStorage.setItem('current_session_id', userSessions[0].id);
                    this.currentSessionTitle.textContent = userSessions[0].title;
                } else {
                    this.currentSessionId = null;
                    localStorage.removeItem('current_session_id');
                    this.currentSessionTitle.textContent = 'New Conversation';
                }
            }

            this.renderSessionList(userSessions);
            
            // Load messages if active session exists
            if (this.currentSessionId) {
                await this.loadSessionMessages(this.currentSessionId);
            }
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    },

    renderSessionList(sessions) {
        this.sessionList.innerHTML = '';
        
        if (sessions.length === 0) {
            this.sessionList.innerHTML = '<div class="empty-state" style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 0.875rem;">No conversations yet.</div>';
            return;
        }

        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = `session-item ${session.id === this.currentSessionId ? 'active' : ''}`;
            item.title = session.title;
            item.innerHTML = `
                <svg class="session-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                <span class="session-item-title">${this.escapeHtml(session.title)}</span>
            `;
            item.addEventListener('click', () => this.switchSession(session.id, session.title));
            this.sessionList.appendChild(item);
        });
    },

    async switchSession(sessionId, title) {
        this.currentSessionId = sessionId;
        localStorage.setItem('current_session_id', sessionId);
        this.currentSessionTitle.textContent = title;
        
        // Update active state in UI
        document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
        await this.loadSessionMessages(sessionId);
        await documents.loadDocuments();
    },

    async loadSessionMessages(sessionId) {
        chat.clear();
        try {
            const data = await api.getSessionMessages(sessionId);
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    if (msg.role !== 'system') {
                        chat.appendMessage(msg.role === 'user' ? 'user' : 'bot', msg.content);
                    }
                });
            } else {
                chat.appendMessage('bot', 'New session started! How can I help you?');
            }
        } catch (error) {
            chat.appendMessage('bot', '⚠️ Failed to load conversation history.');
            ui.toast.show('Failed to load messages', 'error');
        }
    },

    async createNewSession() {
        try {
            const data = await api.createSession('New Chat');
            this.currentSessionId = data.id;
            localStorage.setItem('current_session_id', data.id);
            this.currentSessionTitle.textContent = data.title;
            chat.clear();
            chat.appendMessage('bot', 'New session created! How can I help you?');
            await this.loadSessions();
            await documents.loadDocuments();
            return data.id;
        } catch (error) {
            ui.toast.show('Failed to create new session', 'error');
            return null;
        }
    },

    // Debounce utility for search
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

window.app = app;

// Start the application
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});