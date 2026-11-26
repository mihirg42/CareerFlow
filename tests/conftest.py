import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.services.application_service import ApplicationService
from app.repositories.application_repository import ApplicationRepository
from app.routers import applications as application_router
from app.dependencies import get_repository, get_service

# conftest.py is a special local plugin file in pytest used to share fixtures, hooks, and configuration across multiple test files without needing explicit imports.
# When you run pytest, it automatically discovers any conftest.py file in your test directory and makes its contents available to all tests in that directory and its subdirectories.


@pytest.fixture
def repository() -> ApplicationRepository:
    return ApplicationRepository()


@pytest.fixture
def service(repository: ApplicationRepository) -> ApplicationService:
    return get_service(repository)


@pytest.fixture
def client(repository: ApplicationRepository):
    app.dependency_overrides[get_repository] = lambda: repository
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


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
