import pytest
from fastapi import status
import uuid

@pytest.fixture
def reader_payload():
    """Always unique email for the reader."""
    return {
        "name": "John Doe",
        "email": f"john_{uuid.uuid4().hex}@example.com",
        "phone": "9513219876"
    }

def test_crud_readers(client, make_auth_header, reader_payload):
    auth_header = make_auth_header()
    # Create
    resp = client.post("/readers/", json=reader_payload, headers=auth_header)
    assert resp.status_code == status.HTTP_201_CREATED
    reader = resp.json()
    rid = reader["id"]

    # List
    resp = client.get("/readers/", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    assert any(r["id"] == rid for r in resp.json())

    # Get
    resp = client.get(f"/readers/{rid}", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == reader_payload["name"]

    # Update
    resp = client.put(
        f"/readers/{rid}",
        json={"name": "Jane Doe"},
        headers=auth_header
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "Jane Doe"

    # Delete
    resp = client.delete(f"/readers/{rid}", headers=auth_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Not found
    resp = client.get(f"/readers/{rid}", headers=auth_header)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    