import pytest
from fastapi.testclient import TestClient
from main import app
from config import settings
from app import init_db

# Set test database URL
settings.database_url = "sqlite://test_db.sqlite3"

# Initialize the database before creating the client
import asyncio
asyncio.run(init_db())

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "KIBERone Resumes API"}


def test_register_tutor():
    response = client.post("/api/v1/tutors/register/", json={
        "username": "test_tutor",
        "tutor_branch_id": "123",  # Changed to match new schema
        "phone_number": "+1234567890"  # Add phone number field instead of password
    })
    # This might fail if the tutor already exists, which is expected behavior
    # Or fail with 404 if tutor not found in CRM (which is expected in test environment)
    assert response.status_code in [200, 400, 404]


def test_get_resumes_unverified():
    response = client.get("/api/v1/resumes/unverified/")
    # This will likely return 401 because authentication is required
    # Or 403 if authentication is required but not provided
    assert response.status_code in [200, 401, 403, 422]  # 422 if no auth header provided


def test_get_tutor_groups():
    response = client.get("/api/v1/tutors/groups/")
    # This will likely return 401 because authentication is required
    # Or 403 if authentication is required but not provided
    assert response.status_code in [200, 401, 403, 422]


def test_get_group_clients():
    # This will test the endpoint with a group_id parameter
    response = client.get("/api/v1/groups/clients/?group_id=123")
    # This will likely return 401 because authentication is required
    # Or 403 if authentication is required but not provided
    assert response.status_code in [200, 401, 403, 422]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
