import pytest

from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatus,
)

from app.exceptions import ApplicationNotFoundError
from app.repositories.application_repository import ApplicationRepository


def test_repository_isolation(application_data):
    repo1 = ApplicationRepository()
    repo2 = ApplicationRepository()

    repo1.create(ApplicationCreate(**application_data))

    assert len(repo1.get_all()) == 1
    assert repo2.get_all() == []


def test_create_returns_copy(repository, application_data):
    result = repository.create(ApplicationCreate(**application_data))

    result["company_name"] = "Modified Company"

    saved = repository.get_by_id(result["id"])

    assert saved["company_name"] == "Microsoft"


def test_get_by_id_returns_copy(repository, application_data):
    result = repository.create(ApplicationCreate(**application_data))

    app_id = result["id"]

    retrieved = repository.get_by_id(app_id)
    retrieved["company_name"] = "Modified Company"

    assert repository.get_by_id(app_id)["company_name"] == "Microsoft"


def test_get_all_returns_copies(repository, application_data):
    result = repository.create(ApplicationCreate(**application_data))

    applications = repository.get_all()

    applications[0]["company_name"] = "Modified Company"
    applications.clear()

    saved = repository.get_by_id(result["id"])

    assert saved["company_name"] == "Microsoft"
    assert len(repository.get_all()) == 1


def test_update_returns_copy(repository, application_data):
    result = repository.create(ApplicationCreate(**application_data))

    app_id = result["id"]

    update = ApplicationUpdate(
        **{
            **application_data,
            "company_name": "Google",
            "status": ApplicationStatus.APPLIED,
        }
    )

    updated = repository.update(app_id, update)

    assert updated["company_name"] == "Google"

    updated["company_name"] = "Modified Company"

    assert repository.get_by_id(app_id)["company_name"] == "Google"


def test_update_status_returns_copy(repository, application_data):
    result = repository.create(ApplicationCreate(**application_data))

    app_id = result["id"]

    updated = repository.update_status(app_id, ApplicationStatus.SHORTLISTED)

    assert updated["status"] == ApplicationStatus.SHORTLISTED

    updated["status"] = ApplicationStatus.REJECTED

    assert repository.get_by_id(app_id)["status"] == ApplicationStatus.SHORTLISTED


def test_repository_get_missing(repository):
    with pytest.raises(ApplicationNotFoundError):
        repository.get_by_id(999)


def test_repository_update_missing(repository, application_data):
    update = ApplicationUpdate(**application_data, status=ApplicationStatus.APPLIED)

    with pytest.raises(ApplicationNotFoundError):
        repository.update(999, update)


def test_repository_delete_missing(repository):
    with pytest.raises(ApplicationNotFoundError):
        repository.delete(999)


def test_repository_patch_missing(repository):
    with pytest.raises(ApplicationNotFoundError):
        repository.update_status(999, ApplicationStatus.SHORTLISTED)
