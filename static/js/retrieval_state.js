// static/js/retrieval_state.js

import { RETRIEVAL_CONFIG } from './config.js';

/**
 * Event-Driven State Store for Vector Search & Context Retrieval
 */
class RetrievalStateStore {
    constructor() {
        this.lastSearchResult = null;
        this.selectedChunk = null;
        this.activeFilters = {
            filenames: null,
            extensions: null,
            created_after: null
        };
        this.debugMode = RETRIEVAL_CONFIG.DEBUG_MODE;
        this.listeners = [];
    }

    setSearchResult(result) {
        this.lastSearchResult = result;
        this.notify('SEARCH_RESULT_UPDATED', result);
    }

    setSelectedChunk(chunk) {
        this.selectedChunk = chunk;
        this.notify('CHUNK_SELECTED', chunk);
    }

    setFilters(filters) {
        this.activeFilters = { ...this.activeFilters, ...filters };
        this.notify('FILTERS_CHANGED', this.activeFilters);
    }

    toggleDebugMode(enabled) {
        this.debugMode = enabled !== undefined ? enabled : !this.debugMode;
        this.notify('DEBUG_MODE_TOGGLED', this.debugMode);
    }

    subscribe(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    notify(event, data) {
        this.listeners.forEach(callback => {
            try {
                callback(event, data);
            } catch (err) {
                console.error('[RetrievalState] Error in listener:', err);
            }
        });
    }
}

export const retrievalState = new RetrievalStateStore();
