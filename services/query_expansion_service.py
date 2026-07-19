# services/query_expansion_service.py

"""
Query Expansion Service — Advanced RAG Component

Generates semantic variations of user questions using LLM inference
to improve recall during vector retrieval.
"""

import time
import logging
from openai import OpenAI
from core.settings import get_settings
from schemas.rag import ExpandedQueryResponse
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class QueryExpansionService:
    """
    Generates multiple semantically diverse variations of a user query
    to overcome vocabulary mismatch in vector similarity search.
    """

    def __init__(self, client: OpenAI | None = None):
        self.settings = get_settings()
        self.client = client or OpenAI(
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.base_url
        )

    def expand_query(self, query: str, max_variations: int = 3) -> ExpandedQueryResponse:
        """
        Calls LLM to generate expanded query variations.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/query_expansion_service.py",
            class_name="QueryExpansionService",
            func_name="expand_query",
            purpose="Generate semantic variations of user query for query expansion.",
            input_params={"query": f"'{query[:30]}...'", "max_variations": max_variations}
        )

        t0 = time.time()
        prompt = (
            f"You are an expert AI search optimizer. Generate {max_variations} alternative, "
            f"semantically diverse rephrasings or expanded versions of the following query to help search a vector database.\n"
            f"Return ONLY the variations, one per line, with no numbering, bullets, or extra commentary.\n\n"
            f"Original Query: {query}"
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            raw_output = completion.choices[0].message.content or ""
            variations = [line.strip() for line in raw_output.split("\n") if line.strip()]
            # Ensure variations do not exceed max_variations and exclude duplicates
            unique_variations = []
            for v in variations:
                if v.lower() != query.lower() and v not in unique_variations:
                    unique_variations.append(v)
                if len(unique_variations) >= max_variations:
                    break

            # Always include the original query as variation #0
            all_queries = [query] + unique_variations
            duration_ms = round((time.time() - t0) * 1000, 2)

            # Log REAL execution details
            EducationalLogger.log_rag_step(
                step_num=1,
                step_name="Query Expansion",
                why_needed="Overcome vocabulary mismatch by generating semantically diverse query reformulations.",
                input_data=f"Original Query: '{query}'",
                output_data=f"Expanded Queries ({len(all_queries)}): {all_queries}",
                duration_ms=duration_ms
            )

            res = ExpandedQueryResponse(
                original_query=query,
                expanded_queries=all_queries,
                total_variations=len(all_queries)
            )

            EducationalLogger.log_function_exit(
                file_name="services/query_expansion_service.py",
                class_name="QueryExpansionService",
                func_name="expand_query",
                returned_value=f"Expanded to {len(all_queries)} queries",
                start_time=start_time
            )
            return res

        except Exception as e:
            EducationalLogger.log_educational_error(
                file_name="services/query_expansion_service.py",
                func_name="expand_query",
                line_no=70,
                error=e,
                input_data=query,
                expected="ExpandedQueryResponse with variations",
                fix_suggestion="Check LLM API availability; falling back to original query."
            )
            logger.warning(f"[QUERY-EXPANSION] LLM query expansion failed: {e}. Using original query.")
            res = ExpandedQueryResponse(
                original_query=query,
                expanded_queries=[query],
                total_variations=1
            )
            EducationalLogger.log_function_exit(
                file_name="services/query_expansion_service.py",
                class_name="QueryExpansionService",
                func_name="expand_query",
                returned_value="Fallback to original query",
                start_time=start_time,
                status="FAILED"
            )
            return res
