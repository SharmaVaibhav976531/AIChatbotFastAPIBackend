// static/js/markdown.js

export const md = {
    /**
     * Renders a string of Markdown into safe HTML.
     * Supports: Bold, Italic, Inline Code, Code Blocks, Lists, and Line Breaks.
     */
    render(text) {
        if (!text) return '';

        // 1. Escape HTML to prevent XSS attacks
        let html = this.escapeHtml(text);

        // 2. Code Blocks (```language\ncode\n```)
        // We use a placeholder to protect code blocks from other regex replacements
        const codeBlocks = [];
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const index = codeBlocks.length;
            codeBlocks.push(`<pre class="code-block"><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`);
            return `%%CODEBLOCK_${index}%%`;
        });

        // 3. Inline Code (`code`)
        html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

        // 4. Bold (**text**)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // 5. Italic (*text*)
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // 6. Unordered Lists (- item)
        // Split by newlines and wrap consecutive '-' items in <ul>
        const lines = html.split('\n');
        let inList = false;
        let processedLines = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line.trim().startsWith('- ')) {
                if (!inList) {
                    processedLines.push('<ul class="markdown-list">');
                    inList = true;
                }
                processedLines.push(`<li>${line.trim().substring(2)}</li>`);
            } else {
                if (inList) {
                    processedLines.push('</ul>');
                    inList = false;
                }
                // Handle regular line breaks
                if (line.trim() !== '') {
                    processedLines.push(line);
                } else {
                    processedLines.push('<br>');
                }
            }
        }
        if (inList) processedLines.push('</ul>');

        html = processedLines.join('\n');

        // 7. Restore Code Blocks
        codeBlocks.forEach((block, index) => {
            html = html.replace(`%%CODEBLOCK_${index}%%`, block);
        });

        return html;
    },

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
};