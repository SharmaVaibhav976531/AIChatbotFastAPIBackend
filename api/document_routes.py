# api/document_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from uuid import UUID
from database.models.user import User
from app.dependencies import get_current_active_user, get_document_service, get_document_repository
from services.document_service import DocumentService
from database.repositories.document_repository import DocumentRepository
from schemas.document import DocumentResponse, DocumentListResponse
from core.settings import get_settings
from celery_app.tasks import process_document_task
import logging

logger = logging.getLogger(__name__)
settings = get_settings()
document_router = APIRouter(prefix="/documents", tags=["Documents"])


@document_router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    session_id: UUID | None = Form(None),
    user: User = Depends(get_current_active_user),
    doc_service: DocumentService = Depends(get_document_service)
):
    content = await file.read()
    
    # 1. Validate Size
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File size exceeds {settings.max_file_size_mb}MB limit")
        
    # 2. Validate Extension
    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in settings.supported_file_types.split(","):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        
    try:
        document = doc_service.upload_document(
            user_id=user.id,
            session_id=session_id,
            file_content=content, 
            original_filename=file.filename,
            extension=ext, 
            mime_type=file.content_type or "application/octet-stream"
        )
        
        # 3. Trigger Background Task
        process_document_task.delay(str(document.id))
        logger.info(f"[API] Triggered Celery task for document: {document.id} (Session: {session_id})")
        
        return document
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@document_router.get("/", response_model=DocumentListResponse)
async def list_documents(
    session_id: UUID | None = Query(None),
    user: User = Depends(get_current_active_user),
    doc_repo: DocumentRepository = Depends(get_document_repository)
):
    """List all documents for the authenticated user, optionally filtered by session_id."""
    docs = doc_repo.get_by_user(user.id, session_id=session_id)
    return DocumentListResponse(documents=docs, total=len(docs))


@document_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user: User = Depends(get_current_active_user),
    doc_repo: DocumentRepository = Depends(get_document_repository)
):
    """Delete a document and its associated storage file."""
    from storage.local import LocalStorageProvider
    
    doc = doc_repo.get_by_id(document_id)
    
    if not doc: 
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != user.id: 
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete from storage
    provider = LocalStorageProvider(settings.upload_directory)
    provider.delete(doc.storage_path)
    
    # Delete from DB (Cascades to chunks, metadata, embeddings automatically)
    doc_repo.delete(doc.id)
    
    return None