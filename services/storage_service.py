# services/storage_service.py
import logging
from storage.base import StorageProvider

logger = logging.getLogger(__name__)

class StorageService:
    """
    Facade for storage operations. 
    Routes calls to the configured StorageProvider (Local, S3, etc.).
    Keeps the rest of the application decoupled from the actual storage mechanism.
    """
    def __init__(self, provider: StorageProvider):
        self.provider = provider

    def save_file(self, destination_path: str, file_content: bytes) -> str:
        logger.info(f"[STORAGE-SERVICE] Saving file to {destination_path}")
        return self.provider.save(destination_path, file_content)

    def delete_file(self, file_path: str) -> bool:
        logger.info(f"[STORAGE-SERVICE] Deleting file {file_path}")
        return self.provider.delete(file_path)
        
    def file_exists(self, file_path: str) -> bool:
        return self.provider.exists(file_path)