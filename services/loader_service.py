# services/loader_service.py
import logging
from loaders.base import DocumentLoader
from loaders.pdf import PDFLoader
from loaders.docx import DOCXLoader
from loaders.txt import TXTLoader
from loaders.csv import CSVLoader
from loaders.markdown import MarkdownLoader

logger = logging.getLogger(__name__)

class LoaderService:
    """
    Facade for document text extraction.
    Routes file extraction requests to the appropriate DocumentLoader 
    based on the file extension.
    """
    
    def __init__(self):
        # Registry of supported loaders
        self.loaders: dict[str, DocumentLoader] = {
            ".pdf": PDFLoader(),
            ".docx": DOCXLoader(),
            ".txt": TXTLoader(),
            ".csv": CSVLoader(),
            ".md": MarkdownLoader(),
        }
        logger.info(f"[LOADER-SERVICE] Initialized with loaders: {list(self.loaders.keys())}")

    def get_loader(self, file_extension: str) -> DocumentLoader:
        """Retrieves the correct loader for a given file extension."""
        ext = file_extension.lower()
        if ext not in self.loaders:
            raise ValueError(f"Unsupported file type for loading: {ext}")
        return self.loaders[ext]

    def extract_text(self, file_path: str, file_extension: str) -> str:
        """
        Main entry point for text extraction.
        
        Args:
            file_path: Absolute path to the saved file.
            file_extension: The file extension (e.g., '.pdf').
            
        Returns:
            str: The extracted raw text.
        """
        loader = self.get_loader(file_extension)
        logger.info(f"[LOADER-SERVICE] Routing {file_path} to {loader.__class__.__name__}")
        
        extracted_text = loader.load(file_path)
        
        if not extracted_text or not extracted_text.strip():
            logger.warning(f"[LOADER-SERVICE] Extracted text is empty for {file_path}")
            
        logger.info(f"[LOADER-SERVICE] Successfully extracted {len(extracted_text)} characters from {file_path}")
        return extracted_text