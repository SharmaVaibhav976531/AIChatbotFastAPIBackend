# loaders/csv.py
import logging
import csv
from loaders.base import DocumentLoader

logger = logging.getLogger(__name__)

class CSVLoader(DocumentLoader):
    """
    Extracts text from CSV files. 
    Formats it as a readable text block so the LLM can understand the tabular data.
    """
    def load(self, file_path: str) -> str:
        logger.info(f"[LOADER] Extracting text from CSV: {file_path}")
        text_lines = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                # Join columns with ' | ' for better LLM readability
                text_lines.append(" | ".join(row))
        return "\n".join(text_lines)