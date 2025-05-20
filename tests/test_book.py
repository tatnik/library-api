from fastapi import status
import pytest

@pytest.fixture
def book_payload():
    return {
        "title": "Test Book",
        "author": "Alice",
        "published_year": 2021,
        "isbn": "123-4567890123",
        "copies": 2,
        "description": "Sample description"
    }

def test_crud_books(client, make_auth_header, book_payload):
    auth_header = make_auth_header()
    # Create
    resp = client.post("/books/", json=book_payload, headers=auth_header)
    assert resp.status_code == status.HTTP_201_CREATED
    book = resp.json()
    assert book["title"] == book_payload["title"]
    book_id = book["id"]

    # Read
    resp = client.get(f"/books/{book_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["author"] == book_payload["author"]

    # Update
    resp = client.put(
        f"/books/{book_id}",
        json={"title": "Updated Title"},
        headers=auth_header
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["title"] == "Updated Title"

    # Delete
    resp = client.delete(f"/books/{book_id}", headers=auth_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Not found afterwards
    resp = client.get(f"/books/{book_id}")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
