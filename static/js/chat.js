// static/js/chat.js
import { md } from './markdown.js';

export const chat = {
    messagesList: document.getElementById('messages-list'),
    welcomeScreen: document.getElementById('welcome-screen'),
    typingIndicator: document.getElementById('typing-indicator'),
    userInput: document.getElementById('user-input'),
    sendBtn: document.getElementById('send-btn'),
    chatForm: document.getElementById('chat-form'),

    init() {
        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = Math.min(this.userInput.scrollHeight, 200) + 'px';
            
            // Enable/disable send button based on content
            this.sendBtn.disabled = !this.userInput.value.trim();
        });

        // Handle Enter (send) and Shift+Enter (newline)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (this.userInput.value.trim()) {
                    if (typeof this.chatForm.requestSubmit === 'function') {
                        this.chatForm.requestSubmit();
                    } else {
                        this.chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                    }
                }
            }
        });

        // Focus input on load
        this.userInput.focus();
    },

    clear() {
        this.messagesList.innerHTML = '';
        this.welcomeScreen.classList.remove('hidden');
    },

    appendMessage(role, text, sourcesData = null) {
        this.welcomeScreen.classList.add('hidden');
        
        const row = document.createElement('div');
        row.className = `message-row ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = `avatar ${role}-avatar`;
        avatar.textContent = role === 'user' ? 'You' : 'AI';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        // Use our secure markdown renderer
        content.innerHTML = md.render(text);
        
        // Add copy button and Sources Used badge list for bot messages
        if (role === 'bot') {
            const footerDiv = document.createElement('div');
            footerDiv.className = 'message-footer-actions';
            footerDiv.style.marginTop = '10px';
            footerDiv.style.display = 'flex';
            footerDiv.style.alignItems = 'center';
            footerDiv.style.gap = '8px';
            footerDiv.style.flexWrap = 'wrap';

            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-ghost btn-xs';
            copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(text);
                copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Copied!';
                setTimeout(() => {
                    copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy';
                }, 2000);
            };
            footerDiv.appendChild(copyBtn);

            // Add Sources Used indicator if search results exist
            if (sourcesData && sourcesData.results && sourcesData.results.length > 0) {
                const sourcesPill = document.createElement('button');
                sourcesPill.className = 'btn btn-outline btn-xs sources-used-pill';
                sourcesPill.innerHTML = `📚 Sources Used (${sourcesData.results.length})`;
                sourcesPill.onclick = () => {
                    const rightSidebar = document.getElementById('right-sidebar');
                    const tabSourcesBtn = document.getElementById('tab-sources-btn');
                    if (rightSidebar) rightSidebar.classList.remove('hidden');
                    if (tabSourcesBtn) tabSourcesBtn.click();
                };
                footerDiv.appendChild(sourcesPill);
            }

            content.appendChild(footerDiv);
        }

        row.appendChild(avatar);
        row.appendChild(content);
        this.messagesList.appendChild(row);
        
        this.scrollToBottom();
    },

    showTyping() {
        this.welcomeScreen.classList.add('hidden');
        this.typingIndicator.classList.remove('hidden');
        this.scrollToBottom();
    },

    hideTyping() {
        this.typingIndicator.classList.add('hidden');
    },

    scrollToBottom() {
        const container = document.getElementById('chat-container');
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
        });
    }
};