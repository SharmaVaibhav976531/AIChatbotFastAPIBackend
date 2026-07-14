// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('%c═══════════════════════════════════════════════════', 'color: #6366f1; font-weight: bold');
    console.log('%c  FRONTEND INITIALIZED — Phase 3: Auth + Multi-User', 'color: #22c55e; font-weight: bold');
    console.log('%c═══════════════════════════════════════════════════', 'color: #6366f1; font-weight: bold');

    // ═══════════════════════════════════════════════════
    // DOM REFERENCES
    // ═══════════════════════════════════════════════════
    const authContainer = document.getElementById('auth-container');
    const appContainer = document.getElementById('app-container');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const loginError = document.getElementById('login-error');
    const signupError = document.getElementById('signup-error');
    const toggleAuthBtn = document.getElementById('toggle-auth-btn');
    const toggleText = document.getElementById('toggle-text');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userDisplay = document.getElementById('user-display');
    const sessionList = document.getElementById('session-list');
    const newSessionBtn = document.getElementById('new-session-btn');
    const sessionTitle = document.getElementById('session-title');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const renameSessionBtn = document.getElementById('rename-session-btn');
    const deleteSessionBtn = document.getElementById('delete-session-btn');

    // ═══════════════════════════════════════════════════
    // AUTH MANAGER — Token storage & authenticated fetch
    // ═══════════════════════════════════════════════════
    const Auth = {
        getAccessToken() { return localStorage.getItem('access_token'); },
        getRefreshToken() { return localStorage.getItem('refresh_token'); },
        
        setTokens(access, refresh) {
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
        },
        
        clearTokens() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('current_session_id');
        },

        isLoggedIn() {
            return !!this.getAccessToken();
        },

        /**
         * Authenticated fetch wrapper.
         * Automatically attaches the access token and handles 401 → refresh flow.
         */
        async apiFetch(url, options = {}) {
            const token = this.getAccessToken();
            if (!options.headers) options.headers = {};
            if (token) {
                options.headers['Authorization'] = `Bearer ${token}`;
            }
            if (options.body && !options.headers['Content-Type']) {
                options.headers['Content-Type'] = 'application/json';
            }

            let response = await fetch(url, options);

            // If 401, try to refresh the token
            if (response.status === 401 && this.getRefreshToken()) {
                console.log('[AUTH] Access token expired, attempting refresh...');
                const refreshed = await this.refreshTokens();
                if (refreshed) {
                    // Retry the original request with the new token
                    options.headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
                    response = await fetch(url, options);
                } else {
                    // Refresh failed → force logout
                    this.logout();
                    return response;
                }
            }

            return response;
        },

        async refreshTokens() {
            try {
                const response = await fetch('/auth/refresh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: this.getRefreshToken() })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.setTokens(data.access_token, data.refresh_token);
                    console.log('[AUTH] ✅ Tokens refreshed successfully');
                    return true;
                }
                console.log('[AUTH] ❌ Token refresh failed');
                return false;
            } catch (error) {
                console.error('[AUTH] ❌ Refresh error:', error);
                return false;
            }
        },

        logout() {
            // Fire-and-forget the logout API call (for server-side logging)
            const token = this.getAccessToken();
            if (token) {
                fetch('/auth/logout', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                }).catch(() => {});
            }
            this.clearTokens();
            showAuthScreen();
            console.log('[AUTH] User logged out');
        }
    };

    // State
    let currentSessionId = localStorage.getItem('current_session_id') || null;


    // ═══════════════════════════════════════════════════
    // AUTH UI — Login / Signup Form Handlers
    // ═══════════════════════════════════════════════════

    let isLoginMode = true;

    toggleAuthBtn.addEventListener('click', () => {
        isLoginMode = !isLoginMode;
        if (isLoginMode) {
            loginForm.style.display = 'flex';
            signupForm.style.display = 'none';
            authTitle.textContent = 'Welcome Back';
            authSubtitle.textContent = 'Sign in to continue chatting';
            toggleText.textContent = "Don't have an account?";
            toggleAuthBtn.textContent = 'Sign Up';
        } else {
            loginForm.style.display = 'none';
            signupForm.style.display = 'flex';
            authTitle.textContent = 'Create Account';
            authSubtitle.textContent = 'Start chatting with AI';
            toggleText.textContent = 'Already have an account?';
            toggleAuthBtn.textContent = 'Sign In';
        }
        loginError.style.display = 'none';
        signupError.style.display = 'none';
    });

    // LOGIN
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.style.display = 'none';
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        
        const btn = document.getElementById('login-btn');
        btn.disabled = true;
        btn.textContent = 'Signing in...';

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                Auth.setTokens(data.access_token, data.refresh_token);
                console.log('[AUTH] ✅ Login successful');
                loginForm.reset();
                await initApp();
            } else {
                loginError.textContent = data.detail || 'Login failed';
                loginError.style.display = 'block';
            }
        } catch (error) {
            loginError.textContent = 'Network error. Please try again.';
            loginError.style.display = 'block';
            console.error('[AUTH] Login error:', error);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Sign In';
        }
    });

    // SIGNUP
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        signupError.style.display = 'none';
        const username = document.getElementById('signup-username').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value;

        const btn = document.getElementById('signup-btn');
        btn.disabled = true;
        btn.textContent = 'Creating account...';

        try {
            const response = await fetch('/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                Auth.setTokens(data.access_token, data.refresh_token);
                console.log('[AUTH] ✅ Signup successful');
                signupForm.reset();
                await initApp();
            } else {
                signupError.textContent = data.detail || 'Signup failed';
                signupError.style.display = 'block';
            }
        } catch (error) {
            signupError.textContent = 'Network error. Please try again.';
            signupError.style.display = 'block';
            console.error('[AUTH] Signup error:', error);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Create Account';
        }
    });

    // LOGOUT
    logoutBtn.addEventListener('click', () => {
        Auth.logout();
    });


    // ═══════════════════════════════════════════════════
    // SCREEN MANAGEMENT
    // ═══════════════════════════════════════════════════

    function showAuthScreen() {
        authContainer.style.display = 'flex';
        appContainer.style.display = 'none';
    }

    function showAppScreen() {
        authContainer.style.display = 'none';
        appContainer.style.display = 'flex';
    }


    // ═══════════════════════════════════════════════════
    // APP INITIALIZATION
    // ═══════════════════════════════════════════════════

    async function initApp() {
        showAppScreen();

        // Load user profile
        try {
            const response = await Auth.apiFetch('/auth/me');
            if (response.ok) {
                const user = await response.json();
                userDisplay.textContent = `👤 ${user.username}`;
                console.log(`[APP] User loaded: ${user.username}`);
            } else {
                Auth.logout();
                return;
            }
        } catch (error) {
            Auth.logout();
            return;
        }

        // Load sessions
        await loadSessions();

        // If we have a current session, load it
        if (currentSessionId) {
            await loadSessionMessages(currentSessionId);
        } else {
            chatBox.innerHTML = '';
            appendMessage('bot', 'Hello! How can I help you today? Create a new session or select one from the sidebar.');
        }
    }


    // ═══════════════════════════════════════════════════
    // SESSION MANAGEMENT
    // ═══════════════════════════════════════════════════

    async function loadSessions() {
        try {
            const response = await Auth.apiFetch('/sessions');
            if (!response.ok) return;
            const data = await response.json();
            renderSessionList(data.sessions);
        } catch (error) {
            console.error('[SESSIONS] Failed to load:', error);
        }
    }

    function renderSessionList(sessions) {
        sessionList.innerHTML = '';
        if (sessions.length === 0) {
            sessionList.innerHTML = '<div style="padding:16px; color:var(--text-muted); font-size:0.85rem; text-align:center;">No sessions yet.<br>Click "+ New" to start chatting!</div>';
            return;
        }

        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = `session-item ${session.id === currentSessionId ? 'active' : ''}`;
            item.innerHTML = `
                <span class="session-item-title">${escapeHtml(session.title)}</span>
                <span class="session-item-meta">${session.message_count} msgs</span>
            `;
            item.addEventListener('click', () => switchSession(session.id, session.title));
            sessionList.appendChild(item);
        });
    }

    async function switchSession(sessionId, title) {
        currentSessionId = sessionId;
        localStorage.setItem('current_session_id', sessionId);
        sessionTitle.textContent = title || 'AI Assistant';
        
        // Update active state in sidebar
        document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
        event.currentTarget?.classList?.add('active');

        await loadSessionMessages(sessionId);
    }

    async function loadSessionMessages(sessionId) {
        chatBox.innerHTML = '';
        try {
            const response = await Auth.apiFetch(`/sessions/${sessionId}/messages`);
            if (!response.ok) {
                appendMessage('bot', 'Failed to load messages.');
                return;
            }
            const data = await response.json();
            sessionTitle.textContent = data.session_title;

            if (data.messages.length === 0) {
                appendMessage('bot', 'New session started! How can I help you?');
            } else {
                data.messages.forEach(msg => {
                    if (msg.role !== 'system') {
                        const sender = msg.role === 'user' ? 'user' : 'bot';
                        appendMessage(sender, msg.content);
                    }
                });
            }
        } catch (error) {
            console.error('[SESSIONS] Failed to load messages:', error);
            appendMessage('bot', 'Error loading conversation.');
        }
    }

    // NEW SESSION
    newSessionBtn.addEventListener('click', async () => {
        try {
            const response = await Auth.apiFetch('/sessions', {
                method: 'POST',
                body: JSON.stringify({ title: 'New Chat' })
            });
            if (response.ok) {
                const session = await response.json();
                currentSessionId = session.id;
                localStorage.setItem('current_session_id', session.id);
                sessionTitle.textContent = session.title;
                chatBox.innerHTML = '';
                appendMessage('bot', 'New session created! How can I help you?');
                await loadSessions();
            }
        } catch (error) {
            console.error('[SESSIONS] Failed to create:', error);
        }
    });

    // RENAME SESSION
    renameSessionBtn.addEventListener('click', async () => {
        if (!currentSessionId) return;
        const newTitle = prompt('Enter new session title:', sessionTitle.textContent);
        if (!newTitle || !newTitle.trim()) return;

        try {
            const response = await Auth.apiFetch(`/sessions/${currentSessionId}`, {
                method: 'PUT',
                body: JSON.stringify({ title: newTitle.trim() })
            });
            if (response.ok) {
                sessionTitle.textContent = newTitle.trim();
                await loadSessions();
            }
        } catch (error) {
            console.error('[SESSIONS] Rename failed:', error);
        }
    });

    // DELETE SESSION
    deleteSessionBtn.addEventListener('click', async () => {
        if (!currentSessionId) return;
        if (!confirm('Delete this session and all its messages?')) return;

        try {
            const response = await Auth.apiFetch(`/sessions/${currentSessionId}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                currentSessionId = null;
                localStorage.removeItem('current_session_id');
                sessionTitle.textContent = 'AI Assistant';
                chatBox.innerHTML = '';
                appendMessage('bot', 'Session deleted. Create a new one to start chatting!');
                await loadSessions();
            }
        } catch (error) {
            console.error('[SESSIONS] Delete failed:', error);
        }
    });

    // SIDEBAR TOGGLE
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });


    // ═══════════════════════════════════════════════════
    // CHAT — Send message, receive AI reply
    // ═══════════════════════════════════════════════════

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        // Auto-create a session if none is selected
        if (!currentSessionId) {
            try {
                const response = await Auth.apiFetch('/sessions', {
                    method: 'POST',
                    body: JSON.stringify({ title: 'New Chat' })
                });
                if (response.ok) {
                    const session = await response.json();
                    currentSessionId = session.id;
                    localStorage.setItem('current_session_id', session.id);
                    sessionTitle.textContent = session.title;
                    chatBox.innerHTML = '';
                    await loadSessions();
                }
            } catch (error) {
                appendMessage('bot', '⚠️ Failed to create session.');
                return;
            }
        }

        // ── UI Updates ──
        appendMessage('user', message);
        userInput.value = '';
        showTypingIndicator();
        toggleInputState(true);

        console.log('%c════════════════════════════════════════════════', 'color: #6366f1');
        console.log('%c          FRONTEND  →  BACKEND', 'color: #6366f1; font-weight: bold');
        console.log(`  Method   : POST /chat`);
        console.log(`  Session  : ${currentSessionId}`);
        console.log(`  Message  : "${message}"`);
        console.log('%c════════════════════════════════════════════════', 'color: #6366f1');

        try {
            const startTime = performance.now();

            const response = await Auth.apiFetch('/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: message,
                    session_id: currentSessionId
                })
            });

            const duration = (performance.now() - startTime).toFixed(1);

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();

            console.log('%c════════════════════════════════════════════════', 'color: #a855f7');
            console.log('%c          BACKEND  →  FRONTEND', 'color: #a855f7; font-weight: bold');
            console.log(`  Status   : ${response.status} OK ✅`);
            console.log(`  Duration : ${duration}ms`);
            console.log(`  Model    : ${data.model}`);
            console.log('%c════════════════════════════════════════════════', 'color: #a855f7');

            removeTypingIndicator();
            appendMessage('bot', data.reply);

            // Refresh session list (updates message count)
            await loadSessions();

        } catch (error) {
            removeTypingIndicator();
            appendMessage('bot', `⚠️ ${error.message || 'Sorry, I encountered an error.'}`);
            console.error('[CHAT] Error:', error);
        } finally {
            toggleInputState(false);
            userInput.focus();
        }
    });


    // ═══════════════════════════════════════════════════
    // HELPER FUNCTIONS
    // ═══════════════════════════════════════════════════

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        let formattedText = text.replace(/\n/g, '<br>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        messageDiv.innerHTML = formattedText;
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.classList.add('typing-indicator');
        indicator.innerHTML = '<span></span><span></span><span></span>';
        chatBox.appendChild(indicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    function toggleInputState(isDisabled) {
        userInput.disabled = isDisabled;
        sendBtn.disabled = isDisabled;
    }

    function scrollToBottom() {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }


    // ═══════════════════════════════════════════════════
    // STARTUP — Check if user is already authenticated
    // ═══════════════════════════════════════════════════

    if (Auth.isLoggedIn()) {
        console.log('[AUTH] Existing tokens found, initializing app...');
        initApp();
    } else {
        console.log('[AUTH] No tokens found, showing login screen');
        showAuthScreen();
    }

    console.log('[FRONTEND] ✅ All event listeners attached — ready!');
});