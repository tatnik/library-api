import pytest
from fastapi import status
import uuid

@pytest.fixture
def setup_entities(client, make_auth_header):
    """Creates a book and a reader with unique data for testing."""
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
    """Test the loan limit for the number of books."""
    initial_book_id, reader_id, auth_header = setup_entities
    book_ids = [initial_book_id]

    # Create additional books
    for i in range(extra_books):
        resp = client.post(
            "/books/",
            json={"title": f"Book{i}_{uuid.uuid4().hex}", "author": "Author", "copies": 1},
            headers=auth_header
        )
        assert resp.status_code == status.HTTP_201_CREATED
        book_ids.append(resp.json()["id"])

    # Loan books
    actual_statuses = []
    for bid in book_ids:
        resp = client.post(
            "/loans/", json={"book_id": bid, "reader_id": reader_id}, headers=auth_header
        )
        actual_statuses.append(resp.status_code)

    assert actual_statuses == expected_statuses

def test_return_book_and_copy_increment(client, setup_entities):
    """Test returning a book and restoring the number of copies."""
    book_id, reader_id, auth_header = setup_entities
    # Loan a book
    resp = client.post(
        "/loans/", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # Return the book
    resp = client.post(
        "/loans/return", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == status.HTTP_200_OK

    # Check that copies are restored
    book = client.get(f"/books/{book_id}")
    assert book.json()["copies"] == 1

def test_return_not_loaned(client, setup_entities):
    """Test attempting to return a book that was not loaned."""
    book_id, reader_id, auth_header = setup_entities
    resp = client.post(
        "/loans/return", json={"book_id": book_id, "reader_id": reader_id}, headers=auth_header
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
