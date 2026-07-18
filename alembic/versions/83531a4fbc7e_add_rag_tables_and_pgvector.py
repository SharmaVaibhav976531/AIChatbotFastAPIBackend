"""add rag tables and pgvector

Revision ID: 83531a4fbc7e
Revises: cefc8cffeb8d
Create Date: 2026-07-15 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector  # ← CRITICAL: Import pgvector


# revision identifiers, used by Alembic.
revision: str = '83531a4fbc7e'
down_revision: Union[str, Sequence[str], None] = 'cefc8cffeb8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with RAG tables and pgvector extension."""
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Enable pgvector extension FIRST
    # ═══════════════════════════════════════════════════════════════
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Create documents table
    # ═══════════════════════════════════════════════════════════════
    op.create_table(
        'documents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('extension', sa.String(length=20), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_file_hash'), 'documents', ['file_hash'], unique=False)
    op.create_index(op.f('ix_documents_status'), 'documents', ['status'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Create document_chunks table
    # ═══════════════════════════════════════════════════════════════
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('document_id', sa.Uuid(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('embedding_status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_embedding_status'), 'document_chunks', ['embedding_status'], unique=False)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 4: Create chunk_metadata table
    # ═══════════════════════════════════════════════════════════════
    op.create_table(
        'chunk_metadata',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chunk_id', sa.Uuid(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('section', sa.String(length=255), nullable=True),
        sa.Column('heading', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chunk_id')
    )
    op.create_index(op.f('ix_chunk_metadata_chunk_id'), 'chunk_metadata', ['chunk_id'], unique=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Create embeddings table (with pgvector)
    # ═══════════════════════════════════════════════════════════════
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chunk_id', sa.Uuid(), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('embedding_dimension', sa.Integer(), nullable=False),
        sa.Column('vector', Vector(1536), nullable=False),  # ← pgvector column
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embeddings_chunk_id'), 'embeddings', ['chunk_id'], unique=False)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 6: Create HNSW index for fast vector similarity search
    # ═══════════════════════════════════════════════════════════════
    op.create_index(
        'ix_embeddings_vector_hnsw',
        'embeddings',
        ['vector'],
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'vector': 'vector_cosine_ops'}
    )


def downgrade() -> None:
    """Downgrade schema - reverse all changes."""
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Drop HNSW index FIRST
    # ═══════════════════════════════════════════════════════════════
    op.drop_index('ix_embeddings_vector_hnsw', table_name='embeddings')
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Drop tables in reverse order
    # ═══════════════════════════════════════════════════════════════
    op.drop_index(op.f('ix_embeddings_chunk_id'), table_name='embeddings')
    op.drop_table('embeddings')
    
    op.drop_index(op.f('ix_chunk_metadata_chunk_id'), table_name='chunk_metadata')
    op.drop_table('chunk_metadata')
    
    op.drop_index(op.f('ix_document_chunks_embedding_status'), table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_document_id'), table_name='document_chunks')
    op.drop_table('document_chunks')
    
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_status'), table_name='documents')
    op.drop_index(op.f('ix_documents_file_hash'), table_name='documents')
    op.drop_table('documents')
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Drop pgvector extension LAST
    # ═══════════════════════════════════════════════════════════════
    op.execute("DROP EXTENSION IF EXISTS vector")