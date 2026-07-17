# storage/local.py
import logging
from pathlib import Path
from storage.base import StorageProvider

logger = logging.getLogger(__name__)

class LocalStorageProvider(StorageProvider):
    """
    Local filesystem implementation of the StorageProvider.
    """
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[STORAGE] Local storage initialized at: {self.base_dir.resolve()}")

    def save(self, destination_path: str, file_content: bytes) -> str:
        full_path = self.base_dir / destination_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(file_content)
            
        logger.info(f"[STORAGE] File saved successfully: {full_path}")
        return str(full_path)

    def delete(self, file_path: str) -> bool:
        full_path = self.base_dir / file_path
        if full_path.exists():
            full_path.unlink()
            logger.info(f"[STORAGE] File deleted: {full_path}")
            return True
            
        logger.warning(f"[STORAGE] File not found for deletion: {full_path}")
        return False

    def exists(self, file_path: str) -> bool:
        return (self.base_dir / file_path).exists()