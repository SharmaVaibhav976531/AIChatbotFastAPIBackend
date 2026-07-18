// static/js/retrieval_panel.js

import { retrievalState } from './retrieval_state.js';
import { renderChunkCard, renderSearchDebugPanel } from './components/retrieval_components.js';

export function initRetrievalPanel() {
    const tabDocsBtn = document.getElementById('tab-documents-btn');
    const tabSourcesBtn = document.getElementById('tab-sources-btn');
    const paneDocs = document.getElementById('documents-tab-pane');
    const paneSources = document.getElementById('sources-tab-pane');
    const sourcesList = document.getElementById('retrieved-sources-list');
    const debugContainer = document.getElementById('debug-panel-container');
    const badgeCount = document.getElementById('sources-badge-count');

    if (!tabDocsBtn || !tabSourcesBtn) return;

    // 1. Tab Navigation Handlers
    tabDocsBtn.addEventListener('click', () => {
        tabDocsBtn.classList.add('active');
        tabSourcesBtn.classList.remove('active');
        paneDocs.classList.remove('hidden');
        paneDocs.classList.add('active');
        paneSources.classList.add('hidden');
        paneSources.classList.remove('active');
    });

    tabSourcesBtn.addEventListener('click', () => {
        tabSourcesBtn.classList.add('active');
        tabDocsBtn.classList.remove('active');
        paneSources.classList.remove('hidden');
        paneSources.classList.add('active');
        paneDocs.classList.add('hidden');
        paneDocs.classList.remove('active');
    });

    // 2. Subscribe to Search Result State Updates
    retrievalState.subscribe((event, data) => {
        if (event === 'SEARCH_RESULT_UPDATED' && data) {
            renderSearchResults(data);
        }
    });

    function renderSearchResults(searchResponse) {
        // Render Debug Panel
        if (debugContainer) {
            debugContainer.innerHTML = renderSearchDebugPanel(searchResponse);
        }

        // Render Badge Count
        if (badgeCount) {
            const count = searchResponse.results?.length || 0;
            badgeCount.textContent = count;
            badgeCount.classList.toggle('hidden', count === 0);
        }

        // Render Ranked Chunk Cards
        if (!searchResponse.results || searchResponse.results.length === 0) {
            sourcesList.innerHTML = `
                <div class="empty-state">
                    <p>No matching chunks retrieved above similarity threshold.</p>
                </div>
            `;
            return;
        }

        const cardsHtml = searchResponse.results.map(chunk => renderChunkCard(chunk)).join('');
        sourcesList.innerHTML = cardsHtml;

        // Attach Expand/Collapse and Copy Listeners
        attachCardEventListeners();
    }

    function attachCardEventListeners() {
        // Expand/Collapse text toggle
        sourcesList.querySelectorAll('.toggle-expand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const textDiv = e.target.previousElementSibling;
                if (textDiv) {
                    const isCollapsed = textDiv.classList.toggle('collapsed');
                    e.target.textContent = isCollapsed ? 'Show More' : 'Show Less';
                }
            });
        });

        // Copy Chunk Content
        sourcesList.querySelectorAll('.copy-chunk-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const content = decodeURIComponent(e.currentTarget.getAttribute('data-content') || '');
                try {
                    await navigator.clipboard.writeText(content);
                    const originalTitle = e.currentTarget.getAttribute('title');
                    e.currentTarget.setAttribute('title', 'Copied!');
                    setTimeout(() => e.currentTarget.setAttribute('title', originalTitle), 1500);
                } catch (err) {
                    console.error('Failed to copy chunk content:', err);
                }
            });
        });
    }
}
