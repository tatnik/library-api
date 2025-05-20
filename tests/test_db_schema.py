import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

from app.core.config import settings

DATABASE_URL = os.getenv('DATABASE_URL', settings.DATABASE_URL)

@pytest.fixture(scope="session")
def engine():
    """Фикстура создаёт engine на всё тестовое окружение и проверяет подключение."""
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        yield engine
        engine.dispose()
    except OperationalError as e:
        pytest.skip(f"Cannot connect to database: {e}")

def test_tables_exist(engine):
    """Проверяем наличие всех ключевых таблиц в БД после миграций."""
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
        f"Следующие таблицы отсутствуют: {missing}. "
        "Возможно, не выполнены миграции Alembic."
    )

def test_reader_phone_column(engine):
    """Проверяем, что в таблице readers есть NOT NULL-столбец phone типа String/VARCHAR."""
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('readers')}
    assert 'phone' in columns, "Нет столбца 'phone' в таблице readers"
    assert not columns['phone']['nullable'], "Столбец 'phone' должен быть NOT NULL"
    col_type = columns['phone']['type']
    # Проверка на строковый тип (универсально для разных диалектов)
    assert (
        hasattr(col_type, 'length') or str(col_type).lower().startswith('varchar')
    ), f"Неожиданный тип столбца phone: {col_type}"
