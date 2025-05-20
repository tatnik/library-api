import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

from app.core.config import settings

DATABASE_URL = os.getenv('DATABASE_URL', settings.DATABASE_URL)

@pytest.fixture(scope="session")
def engine():
    """Fixture creates engine for the entire test session and checks connection."""
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        yield engine
        engine.dispose()
    except OperationalError as e:
        pytest.skip(f"Cannot connect to database: {e}")

def test_tables_exist(engine):
    """Check that all main tables exist in DB after migrations."""
    inspector = inspect(engine)
    expected_tables = {
        'users',
        'books',
        'readers',
        'loans',
        'alembic_version',
    }
    existing = set(inspector.get_table_names())
    missing = expected_tables - existing
    assert not missing, (
        f"Missing tables: {missing}. "
        "Maybe Alembic migrations are not applied."
    )

def test_reader_phone_column(engine):
    """Check that the 'readers' table has a NOT NULL 'phone' column of type String/VARCHAR."""
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('readers')}
    assert 'phone' in columns, "No 'phone' column in 'readers' table"
    assert not columns['phone']['nullable'], "'phone' column must be NOT NULL"
    col_type = columns['phone']['type']
    # Universal check for string type (different dialects)
    assert (
        hasattr(col_type, 'length') or str(col_type).lower().startswith('varchar')
    ), f"Unexpected column type for 'phone': {col_type}"
