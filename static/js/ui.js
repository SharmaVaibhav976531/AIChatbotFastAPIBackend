// static/js/ui.js

export const ui = {
    /**
     * Toast Notification System
     * Displays non-blocking, auto-dismissing messages.
     */
    toast: {
        container: document.getElementById('toast-container'),
        
        show(message, type = 'info', duration = 4000) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            
            // Icons based on type
            const icons = {
                success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
                error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
                warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
                info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
            };

            toast.innerHTML = `
                <div class="toast-icon">${icons[type] || icons.info}</div>
                <div class="toast-message">${this.escapeHtml(message)}</div>
                <button class="toast-close" aria-label="Close">&times;</button>
            `;

            this.container.appendChild(toast);

            // Trigger animation
            requestAnimationFrame(() => toast.classList.add('show'));

            // Auto dismiss
            const timeoutId = setTimeout(() => this.dismiss(toast), duration);

            // Manual dismiss
            toast.querySelector('.toast-close').addEventListener('click', () => {
                clearTimeout(timeoutId);
                this.dismiss(toast);
            });
        },

        dismiss(toast) {
            toast.classList.remove('show');
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300); // Wait for animation
        },

        escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    },

    /**
     * Theme Management (Dark / Light / System)
     */
    theme: {
        init() {
            const savedTheme = localStorage.getItem('theme') || 'system';
            this.apply(savedTheme);
            
            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (localStorage.getItem('theme') === 'system') {
                    this.apply('system');
                }
            });
        },

        apply(theme) {
            const html = document.documentElement;
            const sunIcon = document.querySelector('.icon-sun');
            const moonIcon = document.querySelector('.icon-moon');

            let effectiveTheme = theme;
            if (theme === 'system') {
                effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            }

            html.setAttribute('data-theme', effectiveTheme);
            localStorage.setItem('theme', theme);

            // Update icons
            if (sunIcon && moonIcon) {
                if (effectiveTheme === 'dark') {
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                } else {
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                }
            }
        },

        toggle() {
            const current = localStorage.getItem('theme') || 'system';
            const htmlTheme = document.documentElement.getAttribute('data-theme');
            
            // Cycle: dark -> light -> system
            let next = 'light';
            if (current === 'light') next = 'system';
            else if (current === 'system' && htmlTheme === 'light') next = 'dark';
            else if (current === 'system' && htmlTheme === 'dark') next = 'dark'; // Force dark if system was light
            
            this.apply(next);
            ui.toast.show(`Theme set to ${next.charAt(0).toUpperCase() + next.slice(1)}`, 'info', 2000);
        }
    },

    /**
     * Utility: Toggle loading state on buttons
     */
    setLoading(buttonId, isLoading, defaultText = '') {
        const btn = document.getElementById(buttonId);
        if (!btn) return;
        
        const textSpan = btn.querySelector('.btn-text');
        const loaderSpan = btn.querySelector('.btn-loader');

        if (isLoading) {
            btn.disabled = true;
            if (textSpan) textSpan.classList.add('hidden');
            if (loaderSpan) {
                loaderSpan.classList.remove('hidden');
                loaderSpan.innerHTML = '<svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>';
            }
        } else {
            btn.disabled = false;
            if (textSpan) textSpan.classList.remove('hidden');
            if (loaderSpan) loaderSpan.classList.add('hidden');
        }
    }
};

// Initialize theme on load
ui.theme.init();