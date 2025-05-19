import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db, Base
import app.models as models

client = TestClient(app)

# Тестовая БД для borrow
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/tests/test_borrow.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Создаём схему БД один раз для всего модуля
@pytest.fixture(scope="module", autouse=True)
def override_db():
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

# Очищаем только таблицу выдач и восстанавливаем количество копий перед каждым тестом
@pytest.fixture(autouse=True)
def clear_borrow_table():
    db = TestingSessionLocal()
    try:
        # Удаляем все записи о займах
        db.query(models.BorrowedBook).delete()
        # Восстанавливаем изначальное количество копий (1) для всех книг
        db.query(models.Book).update({models.Book.copies: 1})
        db.commit()
    finally:
        db.close()

# Фикстура для авторизации библиотекаря
@pytest.fixture(scope="module")
def auth_header():
    resp = client.post(
        "/auth/register", json={"email": "lib@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    login_resp = client.post(
        "/auth/login", data={"username": "lib@example.com", "password": "secret123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Фикстура для создания книги и читателя один раз за модуль
@pytest.fixture(scope="module")
def setup_entities(auth_header):
    book_resp = client.post(
        "/books/", json={"title": "B", "author": "A", "copies": 1}, headers=auth_header
    )
    reader_resp = client.post(
        "/readers/", json={"name": "R", "email": "r@example.com", "phone": "9513219876"}, headers=auth_header
    )
    assert book_resp.status_code == 201
    assert reader_resp.status_code == 201
    return book_resp.json()["id"], reader_resp.json()["id"]


def test_borrow_success(setup_entities, auth_header):
    book_id, reader_id = setup_entities
    resp = client.post(
        "/borrow/",
        json={"book_id": book_id, "reader_id": reader_id},
        headers=auth_header
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["book_id"] == book_id
    assert data["reader_id"] == reader_id


def test_read_borrowed_books(setup_entities, auth_header):
    book_id, reader_id = setup_entities
    # Предварительная выдача
    borrow_resp = client.post(
        "/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert borrow_resp.status_code == 200
    response = client.get(f"/borrowed/{reader_id}", headers=auth_header)
    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    assert any(b["id"] == book_id for b in books)


def test_borrow_no_copies(setup_entities, auth_header):
    book_id, reader_id = setup_entities
    # Первая выдача
    first = client.post(
        "/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert first.status_code == 200
    # Вторая выдача
    second = client.post(
        "/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert second.status_code == 400


def test_return_success(setup_entities, auth_header):
    book_id, reader_id = setup_entities
    # Выдаём
    borrow_resp = client.post(
        "/borrow/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert borrow_resp.status_code == 200
    # Возвращаем
    return_resp = client.post(
        "/return/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert return_resp.status_code == 200
    # Проверяем копии
    book = client.get(f"/books/{book_id}", headers=auth_header).json()
    assert book["copies"] == 1


def test_return_not_borrowed(setup_entities, auth_header):
    book_id, reader_id = setup_entities
    # Попытка возврата без займов
    resp = client.post(
        "/return/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == 400


def test_borrow_limit_exceeded(setup_entities, auth_header):
    """Один читатель не может взять более 3-х книг одновременно"""
    _, reader_id = setup_entities
    book_ids = []
    # Создаем 4 книги
    for i in range(4):
        resp = client.post(
            "/books/",
            json={"title": f"Limit Book {i}", "author": "Author", "copies": 1},
            headers=auth_header
        )
        assert resp.status_code == 201
        book_ids.append(resp.json()["id"])
    # Выдаем первые три книги
    for bid in book_ids[:3]:
        resp = client.post(
            "/borrow/", json={"book_id": bid, "reader_id": reader_id}, headers=auth_header
        )
        assert resp.status_code == 200
    # Попытка взять четвертую книгу -> ошибка
    resp = client.post(
        "/borrow/", json={"book_id": book_ids[3], "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Loan limit exceeded"
