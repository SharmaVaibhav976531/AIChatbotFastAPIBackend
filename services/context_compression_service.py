# services/context_compression_service.py

"""
Context Compression Service — Advanced RAG Component

Compresses assembled document context by removing redundant, duplicated sentences
and irrelevant padding prior to LLM prompt injection.
"""

import time
import logging
from typing import List, Dict, Any
from core.settings import get_settings
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class ContextCompressionService:
    """
    Analyzes retrieved text chunks and removes duplicated sentences, filler tokens,
    and redundant lines to maximize prompt efficiency.
    """

    def __init__(self):
        self.settings = get_settings()

    def compress_chunks(self, chunks: List[Dict[str, Any]], target_ratio: float = 0.7) -> List[Dict[str, Any]]:
        """
        Deduplicates sentences across chunks and truncates redundant text while preserving sources.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/context_compression_service.py",
            class_name="ContextCompressionService",
            func_name="compress_chunks",
            purpose="Compress context window by eliminating sentence redundancy.",
            input_params={"chunks_count": len(chunks), "target_ratio": target_ratio}
        )

        if not chunks:
            EducationalLogger.log_function_exit(
                file_name="services/context_compression_service.py",
                class_name="ContextCompressionService",
                func_name="compress_chunks",
                returned_value="Empty list",
                start_time=start_time
            )
            return []

        t0 = time.time()
        seen_sentences = set()
        compressed_chunks = []

        total_orig_tokens = 0
        total_comp_tokens = 0

        for chunk in chunks:
            content = chunk.get("content", "")
            orig_tokens = len(content.split())
            total_orig_tokens += orig_tokens

            sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip()]
            filtered_sentences = []

            for s in sentences:
                s_lower = s.lower()
                if s_lower not in seen_sentences:
                    seen_sentences.add(s_lower)
                    filtered_sentences.append(s)

            compressed_text = ". ".join(filtered_sentences)
            if filtered_sentences:
                compressed_text += "."

            comp_tokens = len(compressed_text.split())
            total_comp_tokens += comp_tokens

            c_copy = dict(chunk)
            c_copy["content"] = compressed_text if compressed_text else content
            compressed_chunks.append(c_copy)

        duration_ms = round((time.time() - t0) * 1000, 2)
        saved_tokens = max(0, total_orig_tokens - total_comp_tokens)
        comp_percent = round((saved_tokens / max(1, total_orig_tokens)) * 100, 1)

        EducationalLogger.log_rag_step(
            step_num=5,
            step_name="Context Compression",
            why_needed="Remove duplicate sentences and fluff to reduce LLM prompt token overhead.",
            input_data=f"Original Context Tokens: {total_orig_tokens}",
            output_data=f"Compressed Tokens: {total_comp_tokens} (Saved {saved_tokens} tokens, {comp_percent}% reduction)",
            duration_ms=duration_ms
        )

        EducationalLogger.log_function_exit(
            file_name="services/context_compression_service.py",
            class_name="ContextCompressionService",
            func_name="compress_chunks",
            returned_value=f"Compressed from {total_orig_tokens} -> {total_comp_tokens} tokens ({comp_percent}% reduction)",
            start_time=start_time
        )
        return compressed_chunks
