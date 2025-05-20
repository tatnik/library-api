

"""change is_active to Boolean in users

Revision ID: 4edb48a7f35d
Revises: 1141611fe825
Create Date: 2025-05-20 11:19:38.903736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4edb48a7f35d'
down_revision: Union[str, None] = '1141611fe825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'is_active',
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        postgresql_using='is_active::boolean',
        existing_nullable=False  # если у тебя nullable=True, то ставь True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'is_active',
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        postgresql_using='is_active::integer',
        existing_nullable=False
    )
