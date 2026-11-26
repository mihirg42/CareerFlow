from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_repository

from app.repositories.application_repository import (
    ApplicationRepository,
)

from app.services.application_service import (
    ApplicationService,
)

from app.schemas.application import ApplicationCreate


# Test 1: Verify constructor dependency injection
def test_service_uses_injected_repository(repository):

    service = ApplicationService(repository=repository)

    assert service.repository is repository


# Test 2: Verify shared repository state
def test_services_with_shared_repository(repository, application_data):

    service1 = ApplicationService(repository=repository)
    service2 = ApplicationService(repository=repository)

    created = service1.create(ApplicationCreate(**application_data))

    retrieved = service2.get_by_id(created["id"])

    assert service1 is not service2
    assert service1.repository is service2.repository
    assert retrieved == created


# Test 3: Verify isolated repository state
def test_services_with_separate_repositories(application_data):

    repo1 = ApplicationRepository()
    repo2 = ApplicationRepository()

    service1 = ApplicationService(repository=repo1)
    service2 = ApplicationService(repository=repo2)

    service1.create(ApplicationCreate(**application_data))

    assert service1.repository is not service2.repository
    assert len(service1.get_all()) == 1
    assert service2.get_all() == []


# Test 4: Verify persistence across real HTTP requests
def test_repository_persists_across_requests(application_data):

    assert app.dependency_overrides == {}

    assert get_repository() is get_repository()

    with TestClient(app) as real_client:

        response = real_client.post("/applications", json=application_data)

        assert response.status_code == 201

        created = response.json()
        app_id = created["id"]

        try:
            response = real_client.get(f"/applications/{app_id}")

            assert response.status_code == 200
            assert response.json() == created

        finally:
            get_repository().delete(app_id)


# Test 5: Verify FastAPI dependency substitution
def test_repository_dependency_override(client, repository, application_data):

    original_repository = get_repository()
    original_state = original_repository.get_all()

    assert repository is not original_repository

    response = client.post("/applications", json=application_data)

    assert response.status_code == 201

    created = response.json()

    stored = repository.get_by_id(created["id"])

    assert stored["id"] == created["id"]
    assert stored["company_name"] == created["company_name"]
    assert stored["job_title"] == created["job_title"]

    assert original_repository.get_all() == original_state
