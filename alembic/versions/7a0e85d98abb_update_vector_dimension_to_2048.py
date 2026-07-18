"""update_vector_dimension_to_768

Revision ID: 7a0e85d98abb
Revises: 83531a4fbc7e
Create Date: 2026-07-18 02:43:26.744475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '7a0e85d98abb'
down_revision: Union[str, Sequence[str], None] = '83531a4fbc7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade: Change vector column from 1536 to 768 dimensions.
    
    Switched from nvidia/nemotron-3-embed-1b:free (2048 dims, incompatible 
    with OpenAI SDK + exceeds HNSW 2000 dim limit) to thenlper/gte-base 
    (768 dims, SDK compatible, HNSW compatible).
    """
    # Drop the HNSW index first (it depends on the vector column type)
    op.drop_index('ix_embeddings_vector_hnsw', table_name='embeddings')
    
    # Alter the vector column dimension
    op.alter_column('embeddings', 'vector',
               existing_type=Vector(1536),
               type_=Vector(768),
               existing_nullable=False,
               postgresql_using='vector::vector(768)')
    
    # Recreate the HNSW index with the new dimension
    op.create_index(
        'ix_embeddings_vector_hnsw',
        'embeddings',
        ['vector'],
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'vector': 'vector_cosine_ops'}
    )


def downgrade() -> None:
    """Downgrade: Revert vector column from 768 back to 1536 dimensions."""
    op.drop_index('ix_embeddings_vector_hnsw', table_name='embeddings')
    
    op.alter_column('embeddings', 'vector',
               existing_type=Vector(768),
               type_=Vector(1536),
               existing_nullable=False,
               postgresql_using='vector::vector(1536)')
    
    op.create_index(
        'ix_embeddings_vector_hnsw',
        'embeddings',
        ['vector'],
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'vector': 'vector_cosine_ops'}
    )
