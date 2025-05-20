import pytest
from fastapi import status
import uuid

@pytest.fixture
def setup_entities(client, make_auth_header):
    """Создаёт книгу и читателя с уникальными данными для теста."""
    auth_header = make_auth_header()
    unique_email = f"reader_{uuid.uuid4().hex}@example.com"
    book_resp = client.post(
        "/books/",
        json={"title": f"Initial Book {uuid.uuid4().hex}", "author": "Author", "copies": 1},
        headers=auth_header
    )
    reader_resp = client.post(
        "/readers/",
        json={"name": "Reader", "email": unique_email, "phone": "9513219876"},
        headers=auth_header
    )
    assert book_resp.status_code == status.HTTP_201_CREATED
    assert reader_resp.status_code == status.HTTP_201_CREATED
    return book_resp.json()["id"], reader_resp.json()["id"], auth_header

@pytest.mark.parametrize("extra_books, expected_statuses", [
    (0, [status.HTTP_201_CREATED]),
    (2, [status.HTTP_201_CREATED] * 3),
    (3, [status.HTTP_201_CREATED] * 3 + [status.HTTP_400_BAD_REQUEST]),
])
def test_loan_and_limits(client, setup_entities, extra_books, expected_statuses):
    """Тест лимита на количество выдач книг."""
    initial_book_id, reader_id, auth_header = setup_entities
    book_ids = [initial_book_id]

    # Создаём дополнительные книги
    for i in range(extra_books):
        resp = client.post(
            "/books/",
            json={"title": f"Book{i}_{uuid.uuid4().hex}", "author": "Author", "copies": 1},
            headers=auth_header
        )
        assert resp.status_code == status.HTTP_201_CREATED
        book_ids.append(resp.json()["id"])

    # Выдаём книги
    actual_statuses = []
    for bid in book_ids:
        resp = client.post(
            "/loans/", json={"book_id": bid, "reader_id": reader_id}, headers=auth_header
        )
        actual_statuses.append(resp.status_code)

    assert actual_statuses == expected_statuses

def test_return_book_and_copy_increment(client, setup_entities):
    """Тест возврата книги и восстановления количества экземпляров."""
    book_id, reader_id, auth_header = setup_entities
    # Выдача книги
    resp = client.post(
        "/loans/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # Возврат книги
    resp = client.post(
        "/loans/return", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == status.HTTP_200_OK

    # Проверка восстановления копий
    book = client.get(f"/books/{book_id}")
    assert book.json()["copies"] == 1

def test_return_not_loaned(client, setup_entities):
    """Тест попытки вернуть невыданную книгу."""
    book_id, reader_id, auth_header = setup_entities
    resp = client.post(
        "/loans/return", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
