"""make regulations independent

Revision ID: 1217187ea5c2
Revises: 63a521b349d0
Create Date: 2026-02-25 14:12:24.651639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1217187ea5c2'
down_revision: Union[str, Sequence[str], None] = '63a521b349d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Remove modality dependency from regulations."""
    # 1. Remover o índice associado à coluna
    op.drop_index(op.f('ix_modalities_regulation_modality_id'), table_name='regulation', schema='modalities')
    
    # 2. Remover a Foreign Key constraint
    op.drop_constraint('regulation_modality_id_fkey', 'regulation', schema='modalities', type_='foreignkey')
    
    # 3. Remover a coluna modality_id
    op.drop_column('regulation', 'modality_id', schema='modalities')


def downgrade() -> None:
    """Downgrade schema: Restore modality dependency."""
    op.add_column('regulation', sa.Column('modality_id', postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True), schema='modalities')
    
    op.create_foreign_key(
        'regulation_modality_id_fkey', 
        'regulation', 'modality', 
        ['modality_id'], ['id'], 
        source_schema='modalities', 
        referent_schema='modalities'
    )
    
    op.create_index(
        op.f('ix_modalities_regulation_modality_id'), 
        'regulation', 
        ['modality_id'], 
        unique=False, 
        schema='modalities'
    )