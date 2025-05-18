import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db, Base

client = TestClient(app)

# Тестовая БД для borrow
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_borrow.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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



@pytest.fixture(scope="module")
def auth_header():
    # Регистрация и логин пользователя-библиотекаря
    resp = client.post("/auth/register", json={"email": "lib@example.com", "password": "secret123"})
    assert resp.status_code == 200
    login = client.post("/auth/login", data={"username": "lib@example.com", "password": "secret123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def setup_book_and_reader(auth_header):
    # Создаём книгу и читателя для тестов
    book_resp = client.post(
        "/books/", json={"title":"B","author":"A","copies":1}, headers=auth_header
    )
    reader_resp = client.post(
        "/readers/", json={"name":"R","email":"r@example.com"}, headers=auth_header
    )
    assert book_resp.status_code == 201 and reader_resp.status_code == 201
    return book_resp.json()["id"], reader_resp.json()["id"]


def test_borrow_success(setup_book_and_reader, auth_header):
    book_id, reader_id = setup_book_and_reader
    # Успешная выдача
    resp = client.post("/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["book_id"] == book_id and data["reader_id"] == reader_id
    # Количество копий уменьшилось
    book = client.get(f"/books/{book_id}", headers=auth_header).json()
    assert book["copies"] == 0


def test_borrow_no_copies(setup_book_and_reader, auth_header):
    book_id, reader_id = setup_book_and_reader
    # Нет копий
    resp = client.post("/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header)
    assert resp.status_code == 400


def test_return_success(setup_book_and_reader, auth_header):
    book_id, reader_id = setup_book_and_reader
    # Сначала выдаём книгу
    client.post("/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header)
    # Возврат
    resp = client.post("/return/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header)
    assert resp.status_code == 200
    # Копии увеличились
    book = client.get(f"/books/{book_id}", headers=auth_header).json()
    assert book["copies"] == 1


def test_return_not_borrowed(setup_book_and_reader, auth_header):
    book_id, reader_id = setup_book_and_reader
    # Попытка вернуть невыданную книгу
    resp = client.post("/return/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header)
    assert resp.status_code == 400
