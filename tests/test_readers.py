import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db, Base


client = TestClient(app)

# Тестовая БД SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/tests/test_readers.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Override get_db
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



# Авторизация для тестов
@pytest.fixture(scope="module")
def auth_header():
    resp = client.post("/auth/register", json={"email": "reader@example.com", "password": "secret123"})
    assert resp.status_code == 200
    login = client.post("/auth/login", data={"username": "reader@example.com", "password": "secret123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_readers(auth_header):
    data = {"name": "John Doe", "email": "john@example.com", "phone": "9513219876"}
    resp = client.post("/readers/", json=data, headers=auth_header)
    assert resp.status_code == 201
    reader = resp.json()
    assert reader["name"] == data["name"]
    assert reader["email"] == data["email"]
    assert reader["phone"] == data["phone"]

    resp = client.get("/readers/", headers=auth_header)
    assert resp.status_code == 200
    readers = resp.json()
    assert isinstance(readers, list)
    assert any(r["email"] == data["email"] for r in readers)


def test_crud_reader_by_id(auth_header):
    # Создать
    data = {"name": "Jane Doe", "email": "jane@example.com", "phone": "9513219876"}
    resp = client.post("/readers/", json=data, headers=auth_header)
    reader = resp.json()
    rid = reader["id"]
    # GET
    resp = client.get(f"/readers/{rid}", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["id"] == rid
    # PUT
    update = {"name": "Jane Smith"}
    resp = client.put(f"/readers/{rid}", json=update, headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Jane Smith"
    # DELETE
    resp = client.delete(f"/readers/{rid}", headers=auth_header)
    assert resp.status_code == 204
    # GET после удаления
    resp = client.get(f"/readers/{rid}", headers=auth_header)
    assert resp.status_code == 404
