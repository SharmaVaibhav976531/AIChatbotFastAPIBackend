// static/js/components/retrieval_components.js

import { getSimilarityBadgeProps } from '../config.js';

/**
 * Renders Similarity Score Badge (Color-coded)
 */
export function renderSimilarityBadge(score) {
    const percent = Math.round(score * 100);
    const props = getSimilarityBadgeProps(score);
    
    return `
        <span class="badge ${props.badgeClass}" title="${props.label} (${percent}%)">
            ${percent}% Match
        </span>
    `;
}

/**
 * Renders an Individual Ranked Source Chunk Card
 */
export function renderChunkCard(chunk) {
    const percent = Math.round(chunk.score * 100);
    const props = getSimilarityBadgeProps(chunk.score);

    const meta = chunk.metadata || {};
    const heading = meta.heading || meta.section || 'General Content';
    const pageNum = meta.page_number ? `Page ${meta.page_number}` : '';

    return `
        <div class="source-chunk-card" data-chunk-id="${chunk.chunk_id}">
            <div class="chunk-card-header">
                <div class="chunk-title-group">
                    <span class="rank-pill">#${chunk.rank}</span>
                    <span class="chunk-filename" title="${chunk.filename}">${chunk.filename}</span>
                    ${pageNum ? `<span class="chunk-page-tag">${pageNum}</span>` : ''}
                </div>
                <div class="chunk-score-group">
                    ${renderSimilarityBadge(chunk.score)}
                    <button class="btn btn-ghost btn-xs copy-chunk-btn" title="Copy Chunk Content" data-content="${encodeURIComponent(chunk.content)}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                    </button>
                </div>
            </div>

            <!-- Score Progress Bar -->
            <div class="score-progress-container">
                <div class="score-progress-bar ${props.color}" style="width: ${percent}%"></div>
            </div>

            <div class="chunk-heading-label">📍 ${heading}</div>

            <div class="chunk-preview-body">
                <div class="chunk-text collapsed">${escapeHtml(chunk.content)}</div>
                <button class="btn-link btn-xs toggle-expand-btn">Show More</button>
            </div>

            <div class="chunk-card-footer">
                <span class="chunk-meta-item">Index: #${chunk.chunk_index}</span>
                ${chunk.token_count ? `<span class="chunk-meta-item">Tokens: ${chunk.token_count}</span>` : ''}
                <button class="btn-link btn-xs view-metadata-btn" data-chunk-id="${chunk.chunk_id}">View Metadata</button>
            </div>
        </div>
    `;
}

/**
 * Renders the Search Debug Panel
 */
export function renderSearchDebugPanel(response) {
    if (!response) return '';

    const cacheStatus = response.cache_hit ? '⚡ HIT (Redis)' : '🔍 MISS (DB Query)';
    
    return `
        <div class="search-debug-panel">
            <div class="debug-header">
                <span>🛠 Search Debug Metrics</span>
                <span class="badge badge-neutral">${response.latency_ms} ms</span>
            </div>
            <div class="debug-grid">
                <div class="debug-item">
                    <span class="debug-label">Strategy</span>
                    <span class="debug-value">${response.search_strategy}</span>
                </div>
                <div class="debug-item">
                    <span class="debug-label">Distance Metric</span>
                    <span class="debug-value">${response.distance_metric}</span>
                </div>
                <div class="debug-item">
                    <span class="debug-label">Cache Status</span>
                    <span class="debug-value">${cacheStatus}</span>
                </div>
                <div class="debug-item">
                    <span class="debug-label">Chunks Retrieved</span>
                    <span class="debug-value">${response.total_found}</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Helper to escape HTML tags in chunk text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
