// static/js/shortcuts.js
import { ui } from './ui.js';

export const shortcuts = {
    modal: document.getElementById('shortcuts-modal'),
    isMac: navigator.platform.toUpperCase().indexOf('MAC') >= 0,
    
    init() {
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Close modal button
        const closeBtn = document.getElementById('close-shortcuts-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideModal());
        }
        
        // Click outside modal to close
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.hideModal();
            });
        }
        
        console.log('[SHORTCUTS] ✅ Module initialized');
    },
    
    handleKeydown(e) {
        // Don't trigger shortcuts when typing in inputs (except Escape)
        const target = e.target;
        const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';
        
        // Escape always works
        if (e.key === 'Escape') {
            e.preventDefault();
            this.hideModal();
            this.closeSidebars();
            return;
        }
        
        // Skip other shortcuts if in input
        if (isInput) return;
        
        const ctrlOrCmd = this.isMac ? e.metaKey : e.ctrlKey;
        
        // Ctrl/Cmd + N: New chat
        if (ctrlOrCmd && e.key === 'n') {
            e.preventDefault();
            document.getElementById('new-chat-btn')?.click();
        }
        // Ctrl/Cmd + K: Focus search
        else if (ctrlOrCmd && e.key === 'k') {
            e.preventDefault();
            document.getElementById('search-chats')?.focus();
        }
        // Ctrl/Cmd + /: Show shortcuts
        else if (ctrlOrCmd && e.key === '/') {
            e.preventDefault();
            this.showModal();
        }
        // Ctrl/Cmd + Shift + L: Toggle theme
        else if (ctrlOrCmd && e.shiftKey && e.key === 'L') {
            e.preventDefault();
            ui.theme.toggle();
        }
        // Ctrl/Cmd + B: Toggle left sidebar
        else if (ctrlOrCmd && e.key === 'b') {
            e.preventDefault();
            document.getElementById('toggle-left-sidebar')?.click();
        }
        // Ctrl/Cmd + D: Toggle documents
        else if (ctrlOrCmd && e.key === 'd') {
            e.preventDefault();
            document.getElementById('toggle-right-sidebar')?.click();
        }
        // Ctrl/Cmd + J: Focus chat input
        else if (ctrlOrCmd && e.key === 'j') {
            e.preventDefault();
            document.getElementById('user-input')?.focus();
        }
    },
    
    showModal() {
        if (this.modal) {
            this.modal.classList.add('active');
            // Focus trap: focus the close button
            document.getElementById('close-shortcuts-btn')?.focus();
        }
    },
    
    hideModal() {
        if (this.modal) {
            this.modal.classList.remove('active');
        }
    },
    
    closeSidebars() {
        const leftSidebar = document.getElementById('left-sidebar');
        const rightSidebar = document.getElementById('right-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');
        
        if (leftSidebar && !leftSidebar.classList.contains('collapsed')) {
            leftSidebar.classList.add('collapsed');
        }
        if (rightSidebar && !rightSidebar.classList.contains('hidden')) {
            rightSidebar.classList.add('hidden');
        }
        if (backdrop) {
            backdrop.classList.remove('active');
        }
    }
};