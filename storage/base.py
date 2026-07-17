# storage/base.py
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    """
    Abstract Base Class for file storage.
    Follows the Strategy Pattern to allow seamless switching between 
    Local, S3, Azure Blob, or GCS in the future without changing business logic.
    """
    
    @abstractmethod
    def save(self, destination_path: str, file_content: bytes) -> str:
        """Saves file content and returns the absolute path or URL."""
        pass

    @abstractmethod
    def delete(self, file_path: str) -> bool:
        """Deletes a file. Returns True if successful, False otherwise."""
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """Checks if a file exists at the given path."""
        pass