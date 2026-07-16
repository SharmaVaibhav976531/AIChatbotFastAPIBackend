# celery_app/tasks.py
import logging
import time
from celery_app.celery import celery_app
from core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_expired_sessions_task(self):
    """
    Example Task: Cleanup expired or orphaned data.
    Uses bind=True to access self for retry logic.
    """
    try:
        logger.info("[CELERY-TASK] Starting cleanup of expired sessions...")
        # Future: Add DB query here to delete old sessions
        time.sleep(1) # Simulate work
        logger.info("[CELERY-TASK] ✅ Cleanup completed successfully.")
        return {"status": "success", "message": "Cleanup done"}
    except Exception as exc:
        logger.error(f"[CELERY-TASK] ❌ Cleanup failed: {exc}. Retrying...")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, queue="heavy_queue")
def simulate_heavy_rag_processing_task(self, document_id: str):
    """
    Example Task: Heavy processing (e.g., PDF parsing, chunking, embedding).
    Routed to 'heavy_queue' to prevent blocking lightweight tasks.
    """
    try:
        logger.info(f"[CELERY-TASK] Starting heavy RAG processing for doc: {document_id}")
        time.sleep(3) # Simulate heavy CPU/IO work
        
        # Future: 
        # 1. Download PDF from S3
        # 2. Chunk text (LangChain)
        # 3. Generate embeddings (OpenAI)
        # 4. Save to pgvector
        
        logger.info(f"[CELERY-TASK] ✅ RAG processing completed for doc: {document_id}")
        return {"status": "success", "document_id": document_id}
    except Exception as exc:
        logger.error(f"[CELERY-TASK] ❌ RAG processing failed for {document_id}: {exc}")
        # For heavy tasks, we might not want to retry indefinitely
        raise self.retry(exc=exc, countdown=120)