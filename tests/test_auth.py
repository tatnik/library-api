import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database import Base
from app.main import app
import app.db as db_module

client = TestClient(app)

# Создаём временную БД SQLite для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Переопределяем зависимость get_db для тестов
import app.auth_utils as auth_utils

@pytest.fixture(autouse=True)
def override_get_db():
    # Сбрасываем и создаём таблицы в тестовой БД
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Функция для замены зависимости
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Используем dependency_overrides для подмены get_db
    app.dependency_overrides[db_module.get_db] = _get_test_db
    yield
    # После тестов очищаем overrides
    app.dependency_overrides.clear()


def test_register_and_login_and_me_and_logout():
    # Регистрация
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"

    # Повторная регистрация -> 400
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret123"}
    )
    assert response.status_code == 400

    # Логин
    response = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    # GET /auth/me
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"

    # Logout
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 204

    # Повторный GET /auth/me -> 401
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
