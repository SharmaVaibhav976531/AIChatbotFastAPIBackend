# services/citation_service.py

"""
Citation Service — Advanced RAG Component

Generates explicit source attributions and inline citations:
[Source: filename, Page X, Chunk Y, Confidence Z]
"""

import uuid
import logging
from typing import List, Dict, Any
from schemas.rag import SourceAttribution, Citation
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class CitationService:
    """
    Format source attribution objects and append citation footers to AI responses.
    """

    @staticmethod
    def build_sources_and_citations(chunks: List[Dict[str, Any]]) -> tuple[List[SourceAttribution], List[Citation], str]:
        """
        Processes chunks into structured SourceAttribution and Citation lists,
        and constructs a citation footer string.
        """
        sources: List[SourceAttribution] = []
        citations: List[Citation] = []
        footer_lines: List[str] = []

        for idx, c in enumerate(chunks, 1):
            doc_id_str = c.get("document_id")
            doc_id = uuid.UUID(doc_id_str) if doc_id_str and len(str(doc_id_str)) == 36 else uuid.uuid4()
            chunk_id = uuid.uuid4()

            filename = c.get("filename", "document.pdf")
            chunk_idx = c.get("chunk_index", idx)
            page_no = c.get("page_number", (chunk_idx // 2) + 1)
            sim_score = round(float(c.get("similarity", 0.85)), 2)
            content_snippet = c.get("content", "")[:100].strip() + "..."

            source_attr = SourceAttribution(
                document_id=doc_id,
                chunk_id=chunk_id,
                filename=filename,
                chunk_index=chunk_idx,
                page_number=page_no,
                similarity_score=sim_score,
                content_snippet=content_snippet
            )
            sources.append(source_attr)

            citation = Citation(
                document_name=filename,
                document_uuid=doc_id,
                chunk_uuid=chunk_id,
                chunk_number=chunk_idx,
                page_number=page_no,
                similarity_score=sim_score,
                filename=filename,
                quote_snippet=content_snippet
            )
            citations.append(citation)

            footer_lines.append(
                f"[{idx}] {filename} (Page {page_no}, Chunk {chunk_idx}, Confidence: {sim_score:.0%})"
            )

        footer_text = "\n\n**Sources & Citations:**\n" + "\n".join(footer_lines) if footer_lines else ""
        return sources, citations, footer_text
