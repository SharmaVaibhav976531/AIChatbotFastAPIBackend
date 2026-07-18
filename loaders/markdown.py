# loaders/markdown.py
import logging
from loaders.base import DocumentLoader

logger = logging.getLogger(__name__)

class MarkdownLoader(DocumentLoader):
    def load(self, file_path: str) -> str:
        logger.info(f"[LOADER] Extracting text from Markdown: {file_path}")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()