"""add regulation model

Revision ID: 63a521b349d0
Revises: 002
Create Date: 2026-02-25 13:44:26.884881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '63a521b349d0'
down_revision: Union[str, Sequence[str], None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Create regulation table and its index."""
    # 1. Criar a tabela Regulation
    op.create_table(
        'regulation',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('modality_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['modality_id'], ['modalities.modality.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='modalities'
    )

    op.create_index(
        op.f('ix_modalities_regulation_modality_id'), 
        'regulation', 
        ['modality_id'], 
        unique=False, 
        schema='modalities'
    )


def downgrade() -> None:
    """Downgrade schema: Drop regulation table and its index."""
    op.drop_index(
        op.f('ix_modalities_regulation_modality_id'), 
        table_name='regulation', 
        schema='modalities'
    )
    op.drop_table('regulation', schema='modalities')