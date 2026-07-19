"""add_parent_id_to_document_chunks

Revision ID: 7f920a1b8e43
Revises: c56ae6eebc1f
Create Date: 2026-07-19 21:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f920a1b8e43'
down_revision: Union[str, None] = 'c56ae6eebc1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add optional parent_id foreign key column to document_chunks
    op.add_column('document_chunks', sa.Column('parent_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_document_chunks_parent_id'), 'document_chunks', ['parent_id'], unique=False)
    op.create_foreign_key(
        'fk_document_chunks_parent_id_document_chunks',
        'document_chunks', 'document_chunks',
        ['parent_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_document_chunks_parent_id_document_chunks', 'document_chunks', type_='foreignkey')
    op.drop_index(op.f('ix_document_chunks_parent_id'), table_name='document_chunks')
    op.drop_column('document_chunks', 'parent_id')
