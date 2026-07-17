# services/chunking_service.py
import re
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ChunkingService:
    """
    Handles text cleaning and semantic chunking.
    Uses LangChain's RecursiveCharacterTextSplitter for production-grade chunking.
    """
    
    def __init__(self):
        # Initialize the LangChain text splitter with settings from .env
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            # Order matters! It tries to split by paragraphs first, then newlines, 
            # then sentences, then words, and finally characters as a last resort.
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logger.info(
            f"[CHUNKING] Initialized with chunk_size={settings.chunk_size}, "
            f"overlap={settings.chunk_overlap}"
        )

    def clean_text(self, raw_text: str) -> str:
        """
        Cleans and normalizes the raw extracted text before chunking.
        This removes formatting artifacts that could confuse the LLM or chunker.
        """
        logger.debug("[CHUNKING] Starting text cleaning pipeline...")
        original_length = len(raw_text)
        
        # 1. Normalize newlines (convert Windows \r\n to Unix \n)
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        
        # 2. Remove excessive empty lines (3 or more newlines become 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 3. Remove leading/trailing whitespace from each line, but preserve line breaks
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # 4. Remove excessive horizontal spaces (2 or more spaces become 1)
        text = re.sub(r' {2,}', ' ', text)
        
        # 5. Remove non-printable control characters (except newlines and tabs)
        text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', '', text)
        
        cleaned_length = len(text)
        logger.debug(
            f"[CHUNKING] ✅ Text cleaning completed. "
            f"Original: {original_length} chars -> Cleaned: {cleaned_length} chars."
        )
        
        return text

    def chunk_text(self, text: str) -> list[dict]:
        """
        Splits the cleaned text into semantic chunks.
        
        Args:
            text: The cleaned text to be chunked.
            
        Returns:
            list[dict]: A list of dictionaries containing 'chunk_index' and 'content'.
        """
        logger.info(f"[CHUNKING] Starting chunking process for text of length {len(text)}...")
        
        if not text or not text.strip():
            logger.warning("[CHUNKING] Input text is empty. Returning empty chunks list.")
            return []
        
        # Split the text using LangChain's recursive splitter
        raw_chunks = self.text_splitter.split_text(text)
        
        # Format the output with sequential chunk indices
        chunks = []
        for i, chunk_content in enumerate(raw_chunks):
            # Ensure no chunk is completely empty after stripping
            clean_chunk = chunk_content.strip()
            if clean_chunk:
                chunks.append({
                    "chunk_index": i,
                    "content": clean_chunk
                })
                
        logger.info(f"[CHUNKING] ✅ Chunking completed. Generated {len(chunks)} chunks.")
        return chunks
