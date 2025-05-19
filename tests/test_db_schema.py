# tests/test_db_schema.py
import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

from app.core.config import settings

# URL подключения берём из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL', settings.DATABASE_URL)

@pytest.fixture(scope="module")
def engine():
    try:
        engine = create_engine(DATABASE_URL)
        # Проверим подключение
        conn = engine.connect()
        conn.close()
        return engine
    except OperationalError as e:
        pytest.skip(f"Cannot connect to database: {e}")


def test_tables_exist(engine):
    inspector = inspect(engine)
    expected_tables = {
        'users',
        'books',
        'readers',
        'borrowed_books',
        'alembic_version'
    }
    existing = set(inspector.get_table_names())
    missing = expected_tables - existing
    assert not missing, f"Missing tables: {missing}"


def test_reader_phone_column(engine):
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('readers')}
    assert 'phone' in columns, "Column 'phone' not found in 'readers' table"
    # Проверяем, что столбец обязательный (nullable=False)
    assert not columns['phone']['nullable'], "Column 'phone' should be NOT NULL"
    # Проверяем тип данных (примерно String)
    col_type = columns['phone']['type']
    assert hasattr(col_type, 'length') or str(col_type).startswith('VARCHAR'), \
        f"Unexpected type for 'phone': {col_type}"
