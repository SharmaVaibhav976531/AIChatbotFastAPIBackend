// static/js/config.js

/**
 * Phase 6 Frontend Configuration Settings
 */
export const RETRIEVAL_CONFIG = {
    DEFAULT_TOP_K: 5,
    DEFAULT_SIMILARITY_THRESHOLD: 0.05,
    DEFAULT_DISTANCE_METRIC: "cosine",
    
    // Similarity Score Threshold Colors & Badges
    SIMILARITY_THRESHOLDS: [
        { min: 0.90, color: "green", label: "High Confidence", badgeClass: "badge-success" },
        { min: 0.70, color: "blue", label: "Moderate Match", badgeClass: "badge-info" },
        { min: 0.50, color: "orange", label: "Fair Match", badgeClass: "badge-warning" },
        { min: 0.00, color: "gray", label: "Low Match", badgeClass: "badge-neutral" }
    ],

    // Feature Flags & Debug Mode
    DEBUG_MODE: true,
    MAX_PREVIEW_LENGTH: 200,
    AUTO_OPEN_SOURCES_PANEL: true
};

/**
 * Helper to determine badge properties based on similarity score (0.0 to 1.0)
 */
export function getSimilarityBadgeProps(score) {
    for (const t of RETRIEVAL_CONFIG.SIMILARITY_THRESHOLDS) {
        if (score >= t.min) {
            return t;
        }
    }
    return RETRIEVAL_CONFIG.SIMILARITY_THRESHOLDS[RETRIEVAL_CONFIG.SIMILARITY_THRESHOLDS.length - 1];
}
