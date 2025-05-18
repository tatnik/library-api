import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db
from app.database import Base

client = TestClient(app)

# Настройка тестовой БД SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_books.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Переопределяем зависимость get_db для тестов
@pytest.fixture(scope="module", autouse=True)
def override_get_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()



# Фикстура для авторизации: регистрируем и логинимся, возвращаем заголовок
@pytest.fixture(scope="module")
def auth_header():
    # Регистрация пользователя
    resp = client.post(
        "/auth/register",
        json={"email": "bookuser@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    # Логин и получение токена
    login_resp = client.post(
        "/auth/login",
        data={"username": "bookuser@example.com", "password": "secret123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_read_books(auth_header):
    # Создание книги
    book_data = {
        "title": "Test Book",
        "author": "Author A",
        "published_year": 2025,
        "isbn": "123-4567890123",
        "copies": 5,
        "description": "A test book"
    }
    response = client.post(
        "/books/", json=book_data, headers=auth_header
    )
    assert response.status_code == 201
    created = response.json()
    for key in book_data:
        assert created[key] == book_data[key]
    assert "id" in created

    # Получение списка книг
    response = client.get("/books/", headers=auth_header)
    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    assert len(books) == 1
    assert books[0]["title"] == "Test Book"
