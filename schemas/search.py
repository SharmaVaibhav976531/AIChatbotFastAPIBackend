# schemas/search.py

"""
Phase 6: Search & Retrieval Schemas

Defines Pydantic V2 models for vector similarity search requests, 
metadata filtering options, ranked result items, and search responses.
"""

from __future__ import annotations
import uuid
import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class MetadataFilter(BaseModel):
    """
    Filtering criteria applied to document chunks before/during vector search.
    Supports filtering by document identity, extension, mime type, date range, etc.
    """
    model_config = ConfigDict(extra="ignore")

    session_id: uuid.UUID | None = Field(
        default=None,
        description="Filter search to specific chat session UUID"
    )
    document_ids: list[uuid.UUID] | None = Field(
        default=None, 
        description="Filter search to specific document UUIDs"
    )
    filenames: list[str] | None = Field(
        default=None, 
        description="Filter by original file names (e.g. ['Resume.pdf'])"
    )
    extensions: list[str] | None = Field(
        default=None, 
        description="Filter by file extensions (e.g. ['.pdf', '.docx'])"
    )
    mime_types: list[str] | None = Field(
        default=None, 
        description="Filter by MIME types (e.g. ['application/pdf'])"
    )
    created_after: datetime.datetime | None = Field(
        default=None, 
        description="Only include documents uploaded after this timestamp"
    )
    created_before: datetime.datetime | None = Field(
        default=None, 
        description="Only include documents uploaded before this timestamp"
    )
    min_token_count: int | None = Field(
        default=None, 
        ge=0, 
        description="Minimum token count for chunk inclusion"
    )
    max_token_count: int | None = Field(
        default=None, 
        ge=0, 
        description="Maximum token count for chunk inclusion"
    )


class VectorSearchRequest(BaseModel):
    """
    Request model for POST /search, POST /vector-search, and POST /retrieve endpoints.
    """
    model_config = ConfigDict(extra="ignore")

    query: str = Field(
        ..., 
        min_length=1, 
        max_length=4000, 
        description="Natural language user query to embed and search"
    )
    session_id: uuid.UUID | None = Field(
        default=None,
        description="Chat session ID to isolate document context"
    )
    top_k: int | None = Field(
        default=None, 
        ge=1, 
        le=100, 
        description="Maximum number of top chunks to return"
    )
    similarity_threshold: float | None = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Minimum similarity score threshold (0.0 to 1.0)"
    )
    distance_metric: Literal["cosine", "l2", "inner_product"] | None = Field(
        default=None, 
        description="Vector distance metric algorithm"
    )
    filters: MetadataFilter | None = Field(
        default=None, 
        description="Metadata filtering criteria"
    )
    use_cache: bool = Field(
        default=True, 
        description="Whether to check Redis search cache"
    )


class MultiQuerySearchRequest(BaseModel):
    """
    Request model for POST /rag/multi-query debugging endpoint.
    """
    model_config = ConfigDict(extra="ignore")

    queries: list[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of query variations to execute in parallel"
    )
    session_id: uuid.UUID | None = Field(default=None, description="Chat session ID filter")
    top_k: int | None = Field(default=None, ge=1, le=100)
    similarity_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    filters: MetadataFilter | None = Field(default=None)


class RankedChunkResult(BaseModel):
    """
    Individual ranked chunk returned by the vector search engine.
    """
    model_config = ConfigDict(from_attributes=True)

    rank: int = Field(..., description="1-based rank position in search results")
    score: float = Field(..., description="Calculated similarity score (higher = more relevant)")
    distance: float = Field(..., description="Raw vector distance score (lower = nearer)")
    chunk_id: uuid.UUID = Field(..., description="UUID of the document chunk")
    document_id: uuid.UUID = Field(..., description="UUID of the parent document")
    filename: str = Field(..., description="Original filename of the parent document")
    chunk_index: int = Field(..., description="Sequential position index of the chunk in the document")
    content: str = Field(..., description="Text content snippet of the chunk")
    token_count: int | None = Field(default=None, description="Token length of the chunk content")
    metadata: dict | None = Field(default=None, description="Associated chunk metadata key-values")


class SearchResponse(BaseModel):
    """
    Standard response wrapper for vector search API endpoints.
    """
    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Submitted search query string")
    total_found: int = Field(..., description="Number of matching chunks retrieved above threshold")
    distance_metric: str = Field(..., description="Distance metric algorithm used")
    search_strategy: str = Field(..., description="Search strategy executed (e.g. 'vector', 'hybrid_prepared')")
    latency_ms: float = Field(..., description="Total retrieval latency in milliseconds")
    cache_hit: bool = Field(..., description="Whether result was served from Redis cache")
    results: list[RankedChunkResult] = Field(default_factory=list, description="Ranked list of matching chunks")


class DocumentChunkDetailResponse(BaseModel):
    """
    Detailed listing model for GET /documents/{id}/chunks.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    token_count: int | None
    embedding_status: str
    created_at: datetime.datetime
