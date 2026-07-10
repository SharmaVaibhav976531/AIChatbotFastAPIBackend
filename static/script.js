// Wait until the HTML is fully loaded before running JS
document.addEventListener('DOMContentLoaded', () => {
    // 1. Grab references to our HTML elements
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const resetBtn = document.getElementById('reset-btn');
    const sendBtn = document.getElementById('send-btn');

    // 2. Load previous conversation history when the page opens
    loadHistory();

    // 3. Listen for the form submission (when user clicks Send or presses Enter)
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // CRITICAL: Prevents the browser from refreshing the page
        
        const message = userInput.value.trim();
        if (!message) return; // Don't send empty messages

        // --- UI UPDATES ---
        appendMessage('user', message); // Show user's message immediately
        userInput.value = '';           // Clear the input box
        showTypingIndicator();          // Show the bouncing dots
        toggleInputState(true);         // Disable input while waiting for AI

        try {
            // --- NETWORK REQUEST ---
            // This is the exact same POST request you tested in Swagger!
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json(); // Parse the JSON response
            
            // --- UI UPDATES ---
            removeTypingIndicator();
            appendMessage('bot', data.reply); // Show the AI's reply

        } catch (error) {
            removeTypingIndicator();
            appendMessage('bot', "⚠️ Sorry, I encountered a network error.");
            console.error('Fetch error:', error);
        } finally {
            toggleInputState(false); // Re-enable input
            userInput.focus();       // Put cursor back in the input box
        }
    });

    // 4. Listen for the Reset button click
    resetBtn.addEventListener('click', async () => {
        if (!confirm('Clear conversation history?')) return;

        try {
            const response = await fetch('/reset', { method: 'POST' });
            if (response.ok) {
                chatBox.innerHTML = ''; // Clear the UI
                appendMessage('bot', "Conversation reset! How can I help you?");
            }
        } catch (error) {
            console.error('Reset error:', error);
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
        scrollToBottom(); // Auto-scroll to the newest message
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
        // Smoothly scrolls the chat box to the very bottom
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }

    async function loadHistory() {
        try {
            // Fetches the GET /history endpoint we built in the backend
            const response = await fetch('/history');
            if (response.ok) {
                const data = await response.json();
                if (data.history && data.history.length > 0) {
                    data.history.forEach(msg => {
                        const sender = msg.role === 'user' ? 'user' : 'bot';
                        appendMessage(sender, msg.content);
                    });
                } else {
                    appendMessage('bot', "Hello! How can I help you today?");
                }
            }
        } catch (error) {
            appendMessage('bot', "Hello! How can I help you today?");
        }
    }
});