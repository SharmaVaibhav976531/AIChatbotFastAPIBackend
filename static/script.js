// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c═══════════════════════════════════════════════════', 'color: #00bcd4; font-weight: bold');
    console.log('%c  FRONTEND INITIALIZED — DOM fully loaded', 'color: #4caf50; font-weight: bold');
    console.log('%c═══════════════════════════════════════════════════', 'color: #00bcd4; font-weight: bold');

    // 1. Grab references to our HTML elements
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const resetBtn = document.getElementById('reset-btn');
    const sendBtn = document.getElementById('send-btn');
    console.log('[FRONTEND] ✅ All DOM elements referenced');

    // 2. Load previous conversation history when the page opens
    loadHistory();

    // 3. Listen for the form submission (when user clicks Send or presses Enter)
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // CRITICAL: Prevents the browser from refreshing the page

        const message = userInput.value.trim();
        if (!message) {
            console.log('[FRONTEND] ⚠️ Empty message ignored');
            return;
        }

        // ── FRONTEND → BACKEND ──
        console.log('%c════════════════════════════════════════════════', 'color: #00bcd4');
        console.log('%c          FRONTEND  →  BACKEND', 'color: #00bcd4; font-weight: bold; font-size: 14px');
        console.log('%c════════════════════════════════════════════════', 'color: #00bcd4');
        console.log(`  Method   : POST /chat`);
        console.log(`  Message  : "${message}"`);
        console.log(`  Length   : ${message.length} chars`);
        console.log(`  Payload  :`, JSON.stringify({ message: message }, null, 2));
        console.log('%c════════════════════════════════════════════════', 'color: #00bcd4');

        // --- UI UPDATES ---
        appendMessage('user', message);
        userInput.value = '';
        showTypingIndicator();
        toggleInputState(true);

        try {
            const startTime = performance.now();

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
            });

            const duration = (performance.now() - startTime).toFixed(1);

            if (!response.ok) {
                console.error(`[FRONTEND] ❌ Server responded with error: ${response.status}`);
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            // ── BACKEND → FRONTEND ──
            const replyPreview = data.reply.length > 200 ? data.reply.substring(0, 200) + '...' : data.reply;
            console.log('%c════════════════════════════════════════════════', 'color: #e040fb');
            console.log('%c          BACKEND  →  FRONTEND', 'color: #e040fb; font-weight: bold; font-size: 14px');
            console.log('%c════════════════════════════════════════════════', 'color: #e040fb');
            console.log(`  Status   : ${response.status} OK ✅`);
            console.log(`  Duration : ${duration}ms`);
            console.log(`  Model    : ${data.model}`);
            console.log(`  Reply    : "${replyPreview}"`);
            console.log(`  Length   : ${data.reply.length} chars`);
            console.log(`  Full response:`, data);
            console.log('%c════════════════════════════════════════════════', 'color: #e040fb');

            removeTypingIndicator();
            appendMessage('bot', data.reply);

        } catch (error) {
            removeTypingIndicator();
            appendMessage('bot', "⚠️ Sorry, I encountered a network error.");
            console.error('[FRONTEND] ❌ Fetch error:', error.message);
        } finally {
            toggleInputState(false);
            userInput.focus();
            console.log('[FRONTEND] Input re-enabled — ready for next message');
        }
    });

    // 4. Listen for the Reset button click
    resetBtn.addEventListener('click', async () => {
        console.log('[FRONTEND] 🗑️ Reset button clicked');
        if (!confirm('Clear conversation history?')) {
            console.log('[FRONTEND] Reset cancelled by user');
            return;
        }

        try {
            console.log('[FRONTEND] Sending POST /reset...');
            const response = await fetch('/reset', { method: 'POST' });
            console.log(`[FRONTEND] Reset response: ${response.status}`);

            if (response.ok) {
                chatBox.innerHTML = '';
                appendMessage('bot', "Conversation reset! How can I help you?");
                console.log('[FRONTEND] ✅ UI cleared, conversation reset');
            }
        } catch (error) {
            console.error('[FRONTEND] ❌ Reset error:', error.message);
        }
    });

    // =====================================================================
    // Helper Functions (The "Utility" layer of the frontend)
    // =====================================================================

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        // Basic formatting: Convert newlines to <br> and **text** to <b>text</b>
        let formattedText = text.replace(/\n/g, '<br>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        messageDiv.innerHTML = formattedText;
        chatBox.appendChild(messageDiv);
        scrollToBottom();

        const icon = sender === 'user' ? '→' : '←';
        const preview = text.length > 80 ? text.substring(0, 80) + '...' : text;
        console.log(`[FRONTEND] 💬 ${icon} [${sender}] "${preview}"`);
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.classList.add('typing-indicator');
        indicator.innerHTML = '<span></span><span></span><span></span>';
        chatBox.appendChild(indicator);
        scrollToBottom();
        console.log('[FRONTEND] ⏳ Typing indicator shown — waiting for AI...');
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
            console.log('[FRONTEND] Typing indicator removed');
        }
    }

    function toggleInputState(isDisabled) {
        userInput.disabled = isDisabled;
        sendBtn.disabled = isDisabled;
        console.log(`[FRONTEND] Input: ${isDisabled ? '🔒 DISABLED' : '🔓 ENABLED'}`);
    }

    function scrollToBottom() {
        // Smoothly scrolls the chat box to the very bottom
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }

    async function loadHistory() {
        try {
            console.log('[FRONTEND] 📋 Loading history: GET /history...');
            const response = await fetch('/history');

            if (response.ok) {
                const data = await response.json();
                if (data.history && data.history.length > 0) {
                    console.log(`[FRONTEND] ✅ Loaded ${data.history.length} messages from server`);
                    data.history.forEach((msg, i) => {
                        const sender = msg.role === 'user' ? 'user' : 'bot';
                        const preview = msg.content.length > 60 ? msg.content.substring(0, 60) + '...' : msg.content;
                        console.log(`  Message ${i + 1}: [${msg.role}] "${preview}"`);
                        appendMessage(sender, msg.content);
                    });
                } else {
                    console.log('[FRONTEND] No history — showing welcome message');
                    appendMessage('bot', "Hello! How can I help you today?");
                }
            }
        } catch (error) {
            console.error('[FRONTEND] ❌ Failed to load history:', error.message);
            appendMessage('bot', "Hello! How can I help you today?");
        }
    }

    console.log('[FRONTEND] ✅ All event listeners attached — chat ready!');
});