# services/metadata_service.py
import re
import logging

logger = logging.getLogger(__name__)

class MetadataService:
    """
    Extracts contextual metadata from document chunks.
    Uses regex to parse delimiters injected by the Document Loaders.
    """
    
    def extract_metadata(self, chunk_content: str, document_info: dict) -> dict:
        """
        Analyzes a chunk of text and extracts metadata.
        
        Args:
            chunk_content: The raw text of the chunk.
            document_info: Dict containing document-level info (e.g., original_filename).
            
        Returns:
            dict: A dictionary matching the ChunkMetadata model fields.
        """
        logger.debug("[METADATA] Extracting metadata from chunk...")
        
        # 1. Extract Page Number from the delimiter (e.g., "--- Page 3 ---")
        # This regex is flexible with whitespace: r'---\s*Page\s+(\d+)\s*---'
        page_match = re.search(r'---\s*Page\s+(\d+)\s*---', chunk_content)
        page_number = int(page_match.group(1)) if page_match else None
        
        # 2. Calculate basic statistics for analytics and filtering
        word_count = len(chunk_content.split())
        char_count = len(chunk_content)
        
        # 3. Extract Heading (Placeholder for future NLP/Markdown header extraction)
        heading = None 
        
        metadata = {
            "page_number": page_number,
            "section": None,
            "heading": heading,
            "source": document_info.get("original_filename", "Unknown Document"),
            "language": "en",  # Default to English; future: integrate langdetect
            "keywords": [],    # Placeholder for future keyword extraction (e.g., YAKE/KeyBERT)
            "word_count": word_count,
            "char_count": char_count
        }
        
        logger.debug(f"[METADATA] ✅ Extracted: Page={page_number}, Words={word_count}")
        return metadata