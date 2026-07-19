# services/hyde_service.py

"""
HyDE (Hypothetical Document Embeddings) Service — Advanced RAG Component

Generates a hypothetical ideal passage/answer using LLM, then embeds
the hypothetical document to perform dense semantic retrieval.
"""

import time
import logging
from openai import OpenAI
from core.settings import get_settings
from schemas.rag import HyDEResponse
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class HyDEService:
    """
    Generates a hypothetical document answering the user's query.
    Embedding a hypothetical answer bridges the semantic gap between a short user question
    and long factual document passages in the vector space.
    """

    def __init__(self, client: OpenAI | None = None):
        self.settings = get_settings()
        self.client = client or OpenAI(
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.base_url
        )

    def generate_hypothetical_document(self, query: str) -> HyDEResponse:
        """
        Calls LLM to generate a hypothetical passage answering the query.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/hyde_service.py",
            class_name="HyDEService",
            func_name="generate_hypothetical_document",
            purpose="Generate a hypothetical answer passage for HyDE vector retrieval.",
            input_params={"query": f"'{query[:30]}...'"}
        )

        t0 = time.time()
        prompt = (
            f"Please write a short, informative hypothetical document snippet or passage that directly "
            f"answers the following question. Do not state that this is hypothetical or add meta-commentary.\n\n"
            f"Question: {query}\n\n"
            f"Hypothetical Answer Passage:"
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=self.settings.hyde_max_tokens
            )
            hypothetical_doc = (completion.choices[0].message.content or "").strip()
            duration_ms = round((time.time() - t0) * 1000, 2)

            # Log REAL execution details
            EducationalLogger.log_rag_step(
                step_num=2,
                step_name="HyDE Passage Generation",
                why_needed="Map short user question to dense passage vector space via hypothetical answer generation.",
                input_data=f"Query: '{query}'",
                output_data=f"Hypothetical Doc: '{hypothetical_doc[:80]}...'",
                duration_ms=duration_ms
            )

            res = HyDEResponse(
                query=query,
                hypothetical_document=hypothetical_doc,
                token_count=len(hypothetical_doc.split())
            )

            EducationalLogger.log_function_exit(
                file_name="services/hyde_service.py",
                class_name="HyDEService",
                func_name="generate_hypothetical_document",
                returned_value=f"Hypothetical passage ({len(hypothetical_doc)} chars)",
                start_time=start_time
            )
            return res

        except Exception as e:
            EducationalLogger.log_educational_error(
                file_name="services/hyde_service.py",
                func_name="generate_hypothetical_document",
                line_no=65,
                error=e,
                input_data=query,
                expected="HyDEResponse with passage",
                fix_suggestion="Check LLM API availability; falling back to original query."
            )
            logger.warning(f"[HyDE] Generation failed: {e}. Falling back to original query.")
            res = HyDEResponse(
                query=query,
                hypothetical_document=query,
                token_count=len(query.split())
            )
            EducationalLogger.log_function_exit(
                file_name="services/hyde_service.py",
                class_name="HyDEService",
                func_name="generate_hypothetical_document",
                returned_value="Fallback to query text",
                start_time=start_time,
                status="FAILED"
            )
            return res
