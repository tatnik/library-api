

"""add created_at and updated_at to all tables

Revision ID: 1141611fe825
Revises: ecc97f700bd3
Create Date: 2025-05-20 10:54:24.261758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1141611fe825'
down_revision: Union[str, None] = 'ecc97f700bd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('books', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('books', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('readers', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('readers', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('loans', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('loans', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

def downgrade():
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'updated_at')
    op.drop_column('books', 'created_at')
    op.drop_column('books', 'updated_at')
    op.drop_column('readers', 'created_at')
    op.drop_column('readers', 'updated_at')
    op.drop_column('loans', 'created_at')
    op.drop_column('loans', 'updated_at')
