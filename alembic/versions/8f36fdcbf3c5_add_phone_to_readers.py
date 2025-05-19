

"""add phone to readers 

Revision ID: 8f36fdcbf3c5
Revises: 78a9946d7d62
Create Date: 2025-05-19 10:19:54.506882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f36fdcbf3c5'
down_revision: Union[str, None] = '78a9946d7d62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем обязательную колонку phone в таблицу readers с дефолтным значением для существующих записей
    op.add_column(
        'readers',
        sa.Column('phone', sa.String(), nullable=False, server_default='')
    )
    # Убираем серверный default, т.к. он нужен был только для миграции
    op.alter_column('readers', 'phone', server_default=None)


def downgrade() -> None:
    """Downgrade schema. """
    op.drop_column('readers', 'phone')
