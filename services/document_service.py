# services/document_service.py
import hashlib
import uuid
import logging
from database.repositories.document_repository import DocumentRepository
from services.storage_service import StorageService

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, doc_repo: DocumentRepository, storage_service: StorageService):
        self.doc_repo = doc_repo
        self.storage_service = storage_service

    def upload_document(
        self, 
        user_id: uuid.UUID, 
        file_content: bytes, 
        original_filename: str, 
        extension: str, 
        mime_type: str,
        session_id: uuid.UUID | None = None
    ):
        logger.info(f"[DOC-SERVICE] Processing upload for: {original_filename} (session: {session_id})")
        
        # 1. Calculate SHA-256 hash for duplicate detection
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # 2. Check for exact duplicate within the same session
        existing = self.doc_repo.get_by_hash(file_hash, session_id=session_id)
        if existing and existing.status == "COMPLETED":
            logger.warning(f"[DOC-SERVICE] Duplicate document detected in session {session_id}: {original_filename}")
            raise ValueError("This exact document has already been uploaded and processed for this chat session.")
            
        # 3. Generate internal filename and storage path
        internal_filename = f"{uuid.uuid4()}{extension}"
        storage_path = f"{user_id}/{internal_filename}"
        
        # 4. Save to storage (Local or S3)
        full_path = self.storage_service.save_file(storage_path, file_content)
        
        # 5. Create DB record with session_id
        document = self.doc_repo.create(
            user_id=user_id,
            session_id=session_id,
            filename=internal_filename,
            original_filename=original_filename,
            extension=extension,
            mime_type=mime_type,
            file_size=len(file_content),
            file_hash=file_hash,
            storage_path=full_path,
            status="UPLOADED"
        )
        
        logger.info(f"[DOC-SERVICE] ✅ Document saved to DB: {original_filename} (ID: {document.id}, Session: {session_id})")
        return document