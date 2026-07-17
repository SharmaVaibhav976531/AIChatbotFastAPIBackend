import uuid, logging
from sqlalchemy.orm import Session
from database.models.document import Document

logger = logging.getLogger(__name__)

class DocumentRepository:
    def __init__(self, db: Session): self.db = db

    def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_user(self, user_id: uuid.UUID) -> list[Document]:
        return self.db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).all()

    def get_by_hash(self, file_hash: str) -> Document | None:
        return self.db.query(Document).filter(Document.file_hash == file_hash).first()

    def update_status(self, document_id: uuid.UUID, status: str):
        doc = self.get_by_id(document_id)
        if doc:
            doc.status = status
            self.db.commit()

    def delete(self, document_id: uuid.UUID):
        doc = self.get_by_id(document_id)
        if doc:
            self.db.delete(doc)
            self.db.commit()