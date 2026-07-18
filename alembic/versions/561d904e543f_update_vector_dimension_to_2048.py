"""update_vector_dimension_to_2000

Revision ID: 561d904e543f
Revises: 291fa939d79c
Create Date: 2026-07-18

Note: pgvector HNSW and IVFFlat indexes are limited to 2000 dimensions.
The nvidia/nemotron-3-embed-1b model returns 2048-dim vectors which are
truncated to 2000 dims in the embedding service before storage.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '561d904e543f'
down_revision: Union[str, Sequence[str], None] = '291fa939d79c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade vector column from 1024 to 2000 dimensions.
    
    Uses 2000 (pgvector's max indexable dimension) instead of 2048
    (the model's native output). Embeddings are truncated and
    re-normalized in the embedding service before storage.
    """
    # 1. Drop the existing HNSW index
    op.drop_index(
        op.f('ix_embeddings_vector_hnsw'),
        table_name='embeddings',
        postgresql_ops={'vector': 'vector_cosine_ops'},
        postgresql_with={'m': '16', 'ef_construction': '64'},
        postgresql_using='hnsw'
    )

    # 2. Alter the vector column to 2000 dimensions
    op.alter_column('embeddings', 'vector', type_=Vector(2000))

    # 3. Recreate the HNSW index (2000 is within the 2000-dim limit)
    op.create_index(
        op.f('ix_embeddings_vector_hnsw'),
        'embeddings',
        ['vector'],
        unique=False,
        postgresql_ops={'vector': 'vector_cosine_ops'},
        postgresql_with={'m': '16', 'ef_construction': '64'},
        postgresql_using='hnsw'
    )


def downgrade() -> None:
    """Downgrade vector column back to 1024 dimensions."""
    # 1. Drop the HNSW index
    op.drop_index(
        op.f('ix_embeddings_vector_hnsw'),
        table_name='embeddings',
        postgresql_ops={'vector': 'vector_cosine_ops'},
        postgresql_with={'m': '16', 'ef_construction': '64'},
        postgresql_using='hnsw'
    )

    # 2. Revert the vector column back to 1024
    op.alter_column('embeddings', 'vector', type_=Vector(1024))

    # 3. Recreate the HNSW index
    op.create_index(
        op.f('ix_embeddings_vector_hnsw'),
        'embeddings',
        ['vector'],
        unique=False,
        postgresql_ops={'vector': 'vector_cosine_ops'},
        postgresql_with={'m': '16', 'ef_construction': '64'},
        postgresql_using='hnsw'
    )
