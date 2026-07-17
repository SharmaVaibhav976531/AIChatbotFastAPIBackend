# loaders/docx.py
import logging
from docx import Document as DocxDocument
from loaders.base import DocumentLoader

logger = logging.getLogger(__name__)

class DOCXLoader(DocumentLoader):
    """Extracts text from Microsoft Word DOCX files."""
    
    def load(self, file_path: str) -> str:
        logger.info(f"[LOADER] Extracting text from DOCX: {file_path}")
        try:
            doc = DocxDocument(file_path)
            full_text = [para.text for para in doc.paragraphs]
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"[LOADER] Error reading DOCX {file_path}: {e}")
            raise