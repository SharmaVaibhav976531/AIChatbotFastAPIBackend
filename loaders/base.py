# loaders/base.py
from abc import ABC, abstractmethod

class DocumentLoader(ABC):
    """
    Abstract Base Class for document text extraction.
    All specific loaders (PDF, DOCX, etc.) must implement the `load` method.
    """
    
    @abstractmethod
    def load(self, file_path: str) -> str:
        """
        Extracts text from the file at the given path.
        
        Args:
            file_path: Absolute path to the file.
            
        Returns:
            str: The extracted raw text, ideally with page/section delimiters.
        """
        pass