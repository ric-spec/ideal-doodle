"""add api_key table

Revision ID: a1b2c3d4e5f6
Revises: d72211cd3dde
Create Date: 2026-03-02 22:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd72211cd3dde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'api_key',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.AutoString(length=255), nullable=False),
        sa.Column('description', sqlmodel.AutoString(), nullable=True),
        sa.Column('prefix', sqlmodel.AutoString(length=8), nullable=False),
        sa.Column('key_hash', sqlmodel.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash'),
    )
    op.create_index(op.f('ix_api_key_is_active'), 'api_key', ['is_active'], unique=False)
    op.create_index(op.f('ix_api_key_prefix'), 'api_key', ['prefix'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_api_key_prefix'), table_name='api_key')
    op.drop_index(op.f('ix_api_key_is_active'), table_name='api_key')
    op.drop_table('api_key')
