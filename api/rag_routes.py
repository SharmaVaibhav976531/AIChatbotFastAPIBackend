# api/rag_routes.py

"""
Phase 7: Optional RAG Debug & Inspection Router

Exposes endpoints for testing individual RAG pipeline stages:
/rag/debug, /rag/context, /rag/prompt, /rag/rerank.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.rag import RAGResponse, BuiltContext, PromptPayload, RerankedResult
from schemas.search import VectorSearchRequest
from services.rag_service import RAGService
from services.vector_search_service import VectorSearchService
from services.reranking_service import RerankingService
from services.context_builder_service import ContextBuilderService
from services.prompt_builder_service import PromptBuilderService
from app.dependencies import (
    get_current_active_user,
    get_rag_service,
    get_vector_search_service,
    get_reranking_service,
    get_context_builder_service,
    get_prompt_builder_service
)
from database.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG Debug & Inspection"])


@router.post("/debug", response_model=RAGResponse, summary="Execute full RAG pipeline for inspection")
async def debug_rag_pipeline(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        return await rag_service.execute_rag(
            user_id=current_user.id,
            query=request.query,
            session_id=request.session_id,
            top_k=request.top_k,
            threshold=request.similarity_threshold,
            filters=request.filters
        )
    except Exception as e:
        logger.error(f"[RAG-DEBUG-API] Error executing RAG debug pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG execution failed: {str(e)}"
        )


@router.post("/context", response_model=BuiltContext, summary="Build context block without LLM generation")
async def debug_build_context(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    vector_search_service: VectorSearchService = Depends(get_vector_search_service),
    reranking_service: RerankingService = Depends(get_reranking_service),
    context_builder_service: ContextBuilderService = Depends(get_context_builder_service)
):
    try:
        search_res = vector_search_service.search(
            request=request,
            user_id=current_user.id
        )
        reranked, _ = reranking_service.rerank(search_res.results, request.query)
        return context_builder_service.build_context(reranked)
    except Exception as e:
        logger.error(f"[RAG-DEBUG-API] Error building context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context building failed: {str(e)}"
        )


@router.post("/prompt", response_model=PromptPayload, summary="Inspect constructed system prompt and messages")
async def debug_build_prompt(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    vector_search_service: VectorSearchService = Depends(get_vector_search_service),
    reranking_service: RerankingService = Depends(get_reranking_service),
    context_builder_service: ContextBuilderService = Depends(get_context_builder_service),
    prompt_builder_service: PromptBuilderService = Depends(get_prompt_builder_service)
):
    try:
        search_res = vector_search_service.search(
            request=request,
            user_id=current_user.id
        )
        reranked, _ = reranking_service.rerank(search_res.results, request.query)
        built_ctx = context_builder_service.build_context(reranked)
        return prompt_builder_service.build_rag_prompt(request.query, built_ctx)
    except Exception as e:
        logger.error(f"[RAG-DEBUG-API] Error building prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prompt building failed: {str(e)}"
        )


@router.post("/rerank", response_model=list[RerankedResult], summary="Inspect candidate reranking")
async def debug_rerank(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    vector_search_service: VectorSearchService = Depends(get_vector_search_service),
    reranking_service: RerankingService = Depends(get_reranking_service)
):
    try:
        search_res = vector_search_service.search(
            request=request,
            user_id=current_user.id
        )
        reranked, _ = reranking_service.rerank(search_res.results, request.query)
        return reranked
    except Exception as e:
        logger.error(f"[RAG-DEBUG-API] Error during reranking debug: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reranking failed: {str(e)}"
        )
