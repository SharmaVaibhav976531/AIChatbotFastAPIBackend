# api/search_routes.py

"""
Phase 6: Vector Search & Retrieval API Routes

Defines endpoints for vector similarity search, document chunk retrieval,
and document chunk metadata inspection. All endpoints require JWT authentication
and enforce strict user data isolation.
"""

import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query

from database.models.user import User
from app.dependencies import (
    get_current_active_user,
    get_vector_search_service,
    get_search_repository
)
from services.vector_search_service import VectorSearchService
from database.repositories.search_repository import SearchRepository
from schemas.search import (
    VectorSearchRequest, 
    SearchResponse, 
    DocumentChunkDetailResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Search & Retrieval"])


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Primary Vector Similarity Search",
    description="Embeds query text and returns top-k matching document chunks filtered by metadata and user ownership."
)
def search_documents(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    search_service: VectorSearchService = Depends(get_vector_search_service)
) -> SearchResponse:
    try:
        return search_service.search(request=request, user_id=current_user.id)
    except Exception as e:
        logger.error(f"[API] ❌ Vector search failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(e)}"
        )


@router.post(
    "/vector-search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Explicit Vector Similarity Search Endpoint",
    description="Alias endpoint for vector similarity search."
)
def vector_search(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    search_service: VectorSearchService = Depends(get_vector_search_service)
) -> SearchResponse:
    return search_service.search(request=request, user_id=current_user.id)


@router.post(
    "/retrieve",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Context Retrieval Endpoint",
    description="Retrieves ranked context chunks without sending to LLM."
)
def retrieve_context(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_active_user),
    search_service: VectorSearchService = Depends(get_vector_search_service)
) -> SearchResponse:
    return search_service.search(request=request, user_id=current_user.id)


@router.get(
    "/documents/{document_id}/chunks",
    response_model=list[DocumentChunkDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List Document Chunks",
    description="Returns all extracted text chunks for a specific document owned by the current user."
)
def list_document_chunks(
    document_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    search_repo: SearchRepository = Depends(get_search_repository)
) -> list[DocumentChunkDetailResponse]:
    chunks = search_repo.get_chunks_by_document(
        document_id=document_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or has no chunks"
        )
    return chunks


@router.get(
    "/documents/{document_id}/metadata",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
    summary="Get Document Chunk Metadata",
    description="Fetches associated chunk metadata for a specific document owned by the current user."
)
def get_document_metadata(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    search_repo: SearchRepository = Depends(get_search_repository)
) -> list[dict]:
    metadata_list = search_repo.get_metadata_by_document(
        document_id=document_id,
        user_id=current_user.id
    )
    return metadata_list
