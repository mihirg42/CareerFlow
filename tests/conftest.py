import pytest

from fastapi.testclient import TestClient
from app.main import app

from app.services.application_service import ApplicationService
from app.repositories.application_repository import ApplicationRepository
from app.routers import applications as application_router

# conftest.py is a special local plugin file in pytest used to share fixtures, hooks, and configuration across multiple test files without needing explicit imports.
# When you run pytest, it automatically discovers any conftest.py file in your test directory and makes its contents available to all tests in that directory and its subdirectories.


@pytest.fixture
def repository():
    return ApplicationRepository()


@pytest.fixture
def service():
    return ApplicationService()


@pytest.fixture
def client(monkeypatch, service):
    # temporarily replaces application_router's service with the service fixture
    # after the test runs application_router's service resets to its original value
    # thos provides test isolation
    monkeypatch.setattr(application_router, "service", service)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def application_data():
    return {
        "company_name": "Microsoft",
        "job_title": "Software Engineer",
        "job_url": "https://example.com/jobs/123",
        "applied_date": "2026-11-26",
        "salary_expected": 1500000,
        "notes": "Applied through company website",
    }


@pytest.fixture
def created_application(client, application_data):
    response = client.post("/applications", json=application_data)

    assert response.status_code == 201

    return response.json()
