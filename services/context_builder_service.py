# services/context_builder_service.py

"""
Phase 7: Context Builder Service

Constructs clean, deduplicated, token-bounded context blocks for LLM prompt injection.
Preserves source metadata and enforces MAX_CONTEXT_TOKENS limits.
"""

import logging
from core.settings import get_settings
from schemas.rag import RerankedResult, BuiltContext, SourceAttribution

logger = logging.getLogger(__name__)


class ContextBuilderService:
    def __init__(self):
        self.settings = get_settings()

    def build_context(
        self, 
        reranked_chunks: list[RerankedResult],
        max_tokens: int | None = None
    ) -> BuiltContext:
        """
        Deduplicates chunks, formats source headers, and bounds total context tokens.
        
        Args:
            reranked_chunks: List of RerankedResult chunks
            max_tokens: Maximum token budget (defaults to settings.max_context_tokens)
            
        Returns:
            BuiltContext object containing assembled context string, token count, and source list.
        """
        token_budget = max_tokens or self.settings.max_context_tokens
        
        if not reranked_chunks:
            return BuiltContext(
                context_text="",
                total_tokens=0,
                chunk_count=0,
                sources=[]
            )

        seen_contents = set()
        context_blocks = []
        sources = []
        current_token_count = 0

        for chunk in reranked_chunks:
            # 1. Deduplication by content hash / string match
            clean_text = chunk.content.strip()
            if clean_text in seen_contents:
                continue
            seen_contents.add(clean_text)

            # 2. Estimate token count (standard 1 token ≈ 4 chars or word count * 1.3)
            estimated_chunk_tokens = chunk.token_count or int(len(clean_text.split()) * 1.3)

            # 3. Check Token Budget
            if current_token_count + estimated_chunk_tokens > token_budget and context_blocks:
                logger.info(f"[CONTEXT-BUILDER] Token budget reached ({current_token_count}/{token_budget} tokens). Stopping context addition.")
                break

            meta = chunk.metadata or {}
            heading = meta.get("heading") or meta.get("section") or ""
            page = meta.get("page_number")
            page_str = f" Page {page}" if page else ""

            # 4. Format Document Header
            header = f"--- SOURCE [{chunk.new_rank}]: {chunk.filename}{page_str} {f'({heading})' if heading else ''} ---"
            block = f"{header}\n{clean_text}\n"

            context_blocks.append(block)
            current_token_count += estimated_chunk_tokens

            # 5. Build Source Attribution object
            sources.append(
                SourceAttribution(
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    filename=chunk.filename,
                    chunk_index=chunk.new_rank,
                    page_number=page,
                    section=meta.get("section"),
                    heading=meta.get("heading"),
                    similarity_score=chunk.reranked_score,
                    content_snippet=clean_text[:150] + "..." if len(clean_text) > 150 else clean_text
                )
            )

        full_context_text = "\n".join(context_blocks)
        
        logger.info(
            f"[CONTEXT-BUILDER] Built context window with {len(sources)} chunks | "
            f"Total Tokens: ~{current_token_count} (Budget: {token_budget})"
        )

        return BuiltContext(
            context_text=full_context_text,
            total_tokens=current_token_count,
            chunk_count=len(sources),
            sources=sources
        )
