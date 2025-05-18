import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db


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

def test_read_update_delete_book(auth_header):
    # Создание книги для тестов CRUD по ID
    book_data = {
        "title": "Another Book",
        "author": "Author B",
        "published_year": 2021,
        "isbn": "987-6543210987",
        "copies": 3,
        "description": "Another test book"
    }
    resp = client.post("/books/", json=book_data, headers=auth_header)
    assert resp.status_code == 201
    book = resp.json()
    book_id = book["id"]

    # GET /books/{id}
    resp = client.get(f"/books/{book_id}", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["id"] == book_id

    # PUT /books/{id}
    update_data = {"title": "Updated Title"}
    resp = client.put(f"/books/{book_id}", json=update_data, headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"

    # DELETE /books/{id}
    resp = client.delete(f"/books/{book_id}", headers=auth_header)
    assert resp.status_code == 204

    # GET после удаления -> 404
    resp = client.get(f"/books/{book_id}", headers=auth_header)
    assert resp.status_code == 404
