import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.db import Base, get_db
from app.main import app

# Конфиг для тестовой БД (in-memory, изоляция через StaticPool)
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture(autouse=True)
def prepare_database():
    """Полная изоляция: пересоздаём таблицы перед каждым тестом."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """TestClient с отдельной тестовой БД."""
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = _get_test_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def make_auth_header(client):
    """Фабрика для генерации JWT заголовка для нового пользователя."""
    def _make_auth_header(email=None, password="secret123"):
        if email is None:
            email = f"user_{uuid.uuid4().hex}@example.com"
        # Регистрация
        resp = client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )
        assert resp.status_code == 201
        # Логин
        resp = client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _make_auth_header
