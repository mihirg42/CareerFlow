import pytest

from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatus,
)

from app.exceptions import (
    ApplicationNotFoundError,
    InvalidStatusTransitionError,
)

from app.services.application_service import ApplicationService

ALLOWED_TRANSITIONS = ApplicationService.ALLOWED_TRANSITIONS


PATHS_TO_STATUS = {
    ApplicationStatus.APPLIED: [],
    ApplicationStatus.SHORTLISTED: [ApplicationStatus.SHORTLISTED],
    ApplicationStatus.INTERVIEW: [
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW,
    ],
    ApplicationStatus.OFFERED: [
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.OFFERED,
    ],
    ApplicationStatus.REJECTED: [ApplicationStatus.REJECTED],
    ApplicationStatus.WITHDRAWN: [ApplicationStatus.WITHDRAWN],
}


def create_application_at_status(service, application_data, target_status):
    app = service.create(ApplicationCreate(**application_data))

    app_id = app["id"]

    for next_status in PATHS_TO_STATUS[target_status]:
        service.update_status(app_id, ApplicationStatus(next_status))

    return service.get_by_id(app_id)


@pytest.mark.parametrize("current", list(ApplicationStatus))
@pytest.mark.parametrize("target", list(ApplicationStatus))
def test_status_transitions(service, application_data, current, target):
    app = create_application_at_status(service, application_data, current.value)

    app_id = app["id"]

    allowed = current == target or target.value in ALLOWED_TRANSITIONS[current.value]

    if allowed:
        result = service.update_status(app_id, target)

        assert result["status"] == target
        assert service.get_by_id(app_id)["status"] == target

    else:
        with pytest.raises(InvalidStatusTransitionError):
            service.update_status(app_id, target)

        assert service.get_by_id(app_id) == app


@pytest.mark.parametrize("current", list(ApplicationStatus))
@pytest.mark.parametrize("target", list(ApplicationStatus))
def test_put_status_transitions(service, application_data, current, target):
    app = create_application_at_status(service, application_data, current.value)

    app_id = app["id"]

    update = ApplicationUpdate(
        **{**application_data, "company_name": "Updated Company", "status": target}
    )

    allowed = current == target or target.value in ALLOWED_TRANSITIONS[current.value]

    if allowed:
        result = service.update(app_id, update)

        assert result["status"] == target
        assert result["company_name"] == "Updated Company"

    else:
        with pytest.raises(InvalidStatusTransitionError):
            service.update(app_id, update)

        assert service.get_by_id(app_id) == app


def test_service_create(service, application_data):
    result = service.create(ApplicationCreate(**application_data))

    assert result["id"] == 1
    assert result["company_name"] == "Microsoft"
    assert result["status"] == ApplicationStatus.APPLIED


def test_service_get_all(service, application_data):
    service.create(ApplicationCreate(**application_data))
    service.create(ApplicationCreate(**application_data))

    result = service.get_all()

    assert len(result) == 2
    assert {app["id"] for app in result} == {1, 2}


def test_service_missing_application(service):
    with pytest.raises(ApplicationNotFoundError):
        service.get_by_id(999)


def test_service_update_missing_application(service, application_data):
    update = ApplicationUpdate(**application_data, status=ApplicationStatus.APPLIED)

    with pytest.raises(ApplicationNotFoundError):
        service.update(999, update)


def test_service_patch_missing_application(service):
    with pytest.raises(ApplicationNotFoundError):
        service.update_status(999, ApplicationStatus.SHORTLISTED)


def test_service_delete_missing_application(service):
    with pytest.raises(ApplicationNotFoundError):
        service.delete(999)


def test_service_delete(service, application_data):
    app = service.create(ApplicationCreate(**application_data))

    service.delete(app["id"])

    with pytest.raises(ApplicationNotFoundError):
        service.get_by_id(app["id"])
