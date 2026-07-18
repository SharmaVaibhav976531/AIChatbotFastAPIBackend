# celery_app/tasks.py
import logging
import time
from celery_app.celery import celery_app
from core.settings import get_settings
import uuid
from database.session import SessionLocal
from core.settings import get_settings
# Import Repositories
from database.repositories.document_repository import DocumentRepository
from database.repositories.chunk_repository import ChunkRepository
from database.repositories.metadata_repository import MetadataRepository
from database.repositories.embedding_repository import EmbeddingRepository

# Import Services (Instantiate directly to avoid FastAPI circular imports)
from services.loader_service import LoaderService
from services.chunking_service import ChunkingService
from services.metadata_service import MetadataService
from services.embedding_service import EmbeddingService, embedding_provider

settings = get_settings()
loader_svc = LoaderService()
chunking_svc = ChunkingService()
metadata_svc = MetadataService()
embedding_svc = EmbeddingService(embedding_provider)

logger = logging.getLogger(__name__)


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


@celery_app.task(bind=True, name="process_document_task", max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: str):
    """
    The master RAG pipeline task.
    Orchestrates: Load -> Clean -> Chunk -> Metadata -> Embed -> Save.
    """
    db = SessionLocal()
    try:
        doc_repo = DocumentRepository(db)
        chunk_repo = ChunkRepository(db)
        meta_repo = MetadataRepository(db)
        emb_repo = EmbeddingRepository(db)
        
        doc = doc_repo.get_by_id(uuid.UUID(document_id))
        if not doc:
            logger.error(f"[CELERY] Document {document_id} not found.")
            return
            
        doc_repo.update_status(doc.id, "PROCESSING")
        logger.info(f"[CELERY] 🚀 Starting pipeline for: {doc.original_filename}")
        
        # 1. LOAD TEXT
        text = loader_svc.extract_text(doc.storage_path, doc.extension)
        
        # 2. CLEAN & CHUNK
        clean_text = chunking_svc.clean_text(text)
        raw_chunks = chunking_svc.chunk_text(clean_text)
        
        if not raw_chunks:
            raise ValueError("Document resulted in zero chunks after processing.")
        
        # 3. PREPARE & SAVE CHUNKS
        chunks_data = [{
            "document_id": doc.id,
            "chunk_index": rc["chunk_index"],
            "content": rc["content"],
            "token_count": len(rc["content"].split()),
            "embedding_status": "PENDING"
        } for rc in raw_chunks]
        
        created_chunks = chunk_repo.create_chunks(chunks_data)
        
        # 4. EXTRACT METADATA & PREPARE EMBEDDINGS
        doc_info = {"original_filename": doc.original_filename}
        chunk_texts = []
        metadata_data = []
        
        for chunk in created_chunks:
            meta = metadata_svc.extract_metadata(chunk.content, doc_info)
            metadata_data.append({
                "chunk_id": chunk.id, "page_number": meta["page_number"],
                "section": meta["section"], "heading": meta["heading"],
                "source": meta["source"], "language": meta["language"],
                "keywords": meta["keywords"]
            })
            chunk_texts.append(chunk.content)
            
        meta_repo.create_metadata(metadata_data)
        
        # 5. GENERATE & SAVE EMBEDDINGS
        vectors = embedding_svc.generate_embeddings(chunk_texts)
        
        embeddings_data = [{
            "chunk_id": chunk.id,
            "embedding_model": settings.embedding_model,
            "embedding_dimension": len(vectors[i]),
            "vector": vectors[i]
        } for i, chunk in enumerate(created_chunks)]
        
        emb_repo.create_embeddings(embeddings_data)
        
        # 6. FINALIZE STATUS
        for chunk in created_chunks:
            chunk.embedding_status = "COMPLETED"
        db.commit()
        
        doc_repo.update_status(doc.id, "COMPLETED")
        logger.info(f"[CELERY] ✅ Pipeline completed for: {doc.original_filename} ({len(created_chunks)} chunks)")
        
    except Exception as e:
        logger.error(f"[CELERY] ❌ Pipeline failed for {document_id}: {e}")
        db.rollback()
        try:
            doc_repo = DocumentRepository(db)
            doc_repo.update_status(uuid.UUID(document_id), "FAILED")
        except Exception as db_err:
            logger.error(f"[CELERY] Failed to update status to FAILED: {db_err}")
        raise self.retry(exc=e)
    finally:
        db.close()