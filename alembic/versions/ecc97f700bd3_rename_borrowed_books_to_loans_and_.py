

"""Rename borrowed_books to loans and refactor fields

Revision ID: ecc97f700bd3
Revises: 8f36fdcbf3c5
Create Date: 2025-05-19 18:24:30.551774

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ecc97f700bd3'
down_revision = '8f36fdcbf3c5'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Rename table
    op.rename_table('borrowed_books', 'loans')

    # 2) Rename column borrow_date -> loan_date and add new check constraint
    with op.batch_alter_table('loans', schema=None) as batch:
        batch.alter_column(
            'borrow_date',
            new_column_name='loan_date',
            existing_type=sa.TIMESTAMP(timezone=True)
        )
        batch.create_check_constraint(
            'ck_loans_return_date',
            '(return_date IS NULL) OR (return_date >= loan_date)'
        )

    # 3) Add constraints on books if not present
    with op.batch_alter_table('books', schema=None) as batch:
        batch.create_check_constraint(
            'ck_books_copies_non_negative',
            'copies >= 0'
        )
        batch.create_unique_constraint(
            'uq_books_isbn', ['isbn']
        )


def downgrade():
    # 1) Remove added constraints on books
    with op.batch_alter_table('books', schema=None) as batch:
        batch.drop_constraint('uq_books_isbn', type_='unique')
        batch.drop_constraint('ck_books_copies_non_negative', type_='check')

    # 2) Drop new check constraint & rename column loan_date -> borrow_date
    with op.batch_alter_table('loans', schema=None) as batch:
        batch.drop_constraint('ck_loans_return_date', type_='check')
        batch.alter_column(
            'loan_date',
            new_column_name='borrow_date',
            existing_type=sa.TIMESTAMP(timezone=True)
        )
        batch.create_check_constraint(
            'ck_borrowedbook_return_date',
            '(return_date IS NULL) OR (return_date >= borrow_date)'
        )

    # 3) Rename table back
    op.rename_table('loans', 'borrowed_books')
