# services/parent_child_service.py

"""
Parent-Child Retrieval Service — Advanced RAG Component

Expands retrieved child chunks to their larger parent context (or adjacent chunk context)
to supply full section awareness to the LLM.
"""

import uuid
import time
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models.chunk import DocumentChunk
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class ParentChildService:
    """
    Looks up parent chunks or adjacent chunks for retrieved child chunks
    to rebuild original document sections.
    """

    def __init__(self, db: Session):
        self.db = db

    def expand_to_parent_context(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes retrieved child chunk dicts, checks if parent chunks or adjacent chunks exist in DB,
        and expands the content to full parent context.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/parent_child_service.py",
            class_name="ParentChildService",
            func_name="expand_to_parent_context",
            purpose="Resolve parent chunk hierarchy and assemble expanded section context.",
            input_params={"child_chunks_count": len(chunks)}
        )

        if not chunks:
            EducationalLogger.log_function_exit(
                file_name="services/parent_child_service.py",
                class_name="ParentChildService",
                func_name="expand_to_parent_context",
                returned_value="Empty list",
                start_time=start_time
            )
            return []

        t0 = time.time()
        expanded_list = []
        child_ids = []
        parent_ids = []

        for c in chunks:
            chunk_id_str = c.get("document_id")
            chunk_idx = c.get("chunk_index", 0)
            doc_id_str = c.get("document_id")

            child_ids.append(f"doc:{doc_id_str[:6]}_chk:{chunk_idx}")

            try:
                doc_uuid = uuid.UUID(doc_id_str)
                # Fetch adjacent chunks (index - 1, index, index + 1) for the document to form parent context window
                adjacent_db_chunks = (
                    self.db.query(DocumentChunk)
                    .filter(
                        DocumentChunk.document_id == doc_uuid,
                        DocumentChunk.chunk_index >= max(0, chunk_idx - 1),
                        DocumentChunk.chunk_index <= chunk_idx + 1
                    )
                    .order_by(DocumentChunk.chunk_index.asc())
                    .all()
                )

                if adjacent_db_chunks and len(adjacent_db_chunks) > 1:
                    parent_text = "\n".join([ac.content for ac in adjacent_db_chunks])
                    p_id = f"parent_sec_{adjacent_db_chunks[0].chunk_index}-{adjacent_db_chunks[-1].chunk_index}"
                    parent_ids.append(p_id)

                    expanded_c = dict(c)
                    expanded_c["content"] = parent_text
                    expanded_c["is_parent_expanded"] = True
                    expanded_c["parent_id"] = p_id
                    expanded_list.append(expanded_c)
                else:
                    expanded_list.append(c)

            except Exception as ex:
                logger.debug(f"[PARENT-CHILD] Expansion skip for chunk {c.get('document_id')}: {ex}")
                expanded_list.append(c)

        duration_ms = round((time.time() - t0) * 1000, 2)

        EducationalLogger.log_rag_step(
            step_num=4,
            step_name="Parent-Child Context Expansion",
            why_needed="Map granular child vector matches to complete parent section text.",
            input_data=f"Child Chunks ({len(chunks)}): {child_ids[:2]}",
            output_data=f"Expanded Parent Sections ({len(parent_ids)} parents resolved)",
            duration_ms=duration_ms
        )

        EducationalLogger.log_function_exit(
            file_name="services/parent_child_service.py",
            class_name="ParentChildService",
            func_name="expand_to_parent_context",
            returned_value=f"Expanded {len(expanded_list)} chunks",
            start_time=start_time
        )
        return expanded_list
