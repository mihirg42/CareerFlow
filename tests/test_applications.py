import pytest
from datetime import datetime, timedelta
from app.schemas.application import ApplicationStatus

# conftest.py is a special local plugin file in pytest used to share fixtures, hooks, and configuration across multiple test files without needing explicit imports.
# When you run pytest, it automatically discovers any conftest.py file in your test directory and makes its contents available to all tests in that directory and its subdirectories.


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_empty_applications(client):
    response = client.get("/applications")

    assert response.status_code == 200
    assert response.json() == []


def test_create_application(client, application_data):
    response = client.post("/applications", json=application_data)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["status"] == ApplicationStatus.APPLIED

    for key, value in application_data.items():
        assert data[key] == value

    assert data["created_at"] == data["updated_at"]

    created_at = datetime.fromisoformat(data["created_at"])
    assert created_at.utcoffset() == timedelta(hours=5, minutes=30)


def test_get_all_applications(client, application_data, created_application):
    second_application = {**application_data, "company_name": "Google"}

    response = client.post("/applications", json=second_application)
    assert response.status_code == 201

    response = client.get("/applications")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert {item["company_name"] for item in data} == {"Microsoft", "Google"}


def test_get_application_by_id(client, created_application):
    app_id = created_application["id"]

    response = client.get(f"/applications/{app_id}")

    assert response.status_code == 200
    assert response.json() == created_application


def test_get_missing_application(client):
    response = client.get("/applications/999")

    assert response.status_code == 404
    assert response.json()["detail"]


def test_update_application(client, application_data, created_application):
    app_id = created_application["id"]

    updated_data = {
        **application_data,
        "job_title": "Backend Engineer",
        "salary_expected": 1800000,
        "status": "SHORTLISTED",
    }

    response = client.put(f"/applications/{app_id}", json=updated_data)

    assert response.status_code == 200

    data = response.json()

    for key, value in updated_data.items():
        assert data[key] == value

    assert data["id"] == app_id
    assert data["created_at"] == created_application["created_at"]

    assert datetime.fromisoformat(data["updated_at"]) >= datetime.fromisoformat(
        created_application["updated_at"]
    )

    saved = client.get(f"/applications/{app_id}")

    assert saved.status_code == 200
    assert saved.json() == data


def test_update_missing_application(client, application_data):
    response = client.put(
        "/applications/999", json={**application_data, "status": "APPLIED"}
    )

    assert response.status_code == 404


def test_put_invalid_status_transition(client, application_data, created_application):
    app_id = created_application["id"]

    response = client.put(
        f"/applications/{app_id}",
        json={
            **application_data,
            "company_name": "Changed Company",
            "status": "OFFERED",
        },
    )

    assert response.status_code == 409

    saved = client.get(f"/applications/{app_id}")

    assert saved.status_code == 200
    assert saved.json() == created_application


def test_patch_status(client, created_application):
    app_id = created_application["id"]

    response = client.patch(
        f"/applications/{app_id}/status", json={"status": "SHORTLISTED"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "SHORTLISTED"
    assert data["id"] == app_id
    assert data["created_at"] == created_application["created_at"]

    assert datetime.fromisoformat(data["updated_at"]) >= datetime.fromisoformat(
        created_application["updated_at"]
    )

    for key in (
        "company_name",
        "job_title",
        "job_url",
        "applied_date",
        "salary_expected",
        "notes",
    ):
        assert data[key] == created_application[key]

    saved = client.get(f"/applications/{app_id}")
    assert saved.json() == data


def test_patch_invalid_status_transition(client, created_application):
    app_id = created_application["id"]

    response = client.patch(
        f"/applications/{app_id}/status", json={"status": "OFFERED"}
    )

    assert response.status_code == 409

    saved = client.get(f"/applications/{app_id}")
    assert saved.json() == created_application


def test_patch_missing_application(client):
    response = client.patch("/applications/999/status", json={"status": "SHORTLISTED"})

    assert response.status_code == 404


def test_delete_application(client, created_application):
    app_id = created_application["id"]

    response = client.delete(f"/applications/{app_id}")

    assert response.status_code == 204
    assert response.content == b""

    response = client.get(f"/applications/{app_id}")

    assert response.status_code == 404


def test_delete_missing_application(client):
    response = client.delete("/applications/999")

    assert response.status_code == 404


@pytest.mark.parametrize("field", ["company_name", "job_title", "applied_date"])
def test_missing_required_field(client, application_data, field):
    invalid_data = application_data.copy()
    del invalid_data[field]

    response = client.post("/applications", json=invalid_data)

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["company_name", "job_title"])
@pytest.mark.parametrize("value", ["", "   ", "\n\t"])
def test_blank_fields(client, application_data, field, value):
    response = client.post("/applications", json={**application_data, field: value})

    assert response.status_code == 422


@pytest.mark.parametrize("url", ["invalid-url", "ftp://example.com", "example.com"])
def test_invalid_job_url(client, application_data, url):
    response = client.post("/applications", json={**application_data, "job_url": url})

    assert response.status_code == 422


@pytest.mark.parametrize("salary", [-1, -10000])
def test_negative_salary(client, application_data, salary):
    response = client.post(
        "/applications", json={**application_data, "salary_expected": salary}
    )

    assert response.status_code == 422


def test_optional_fields(client):
    response = client.post(
        "/applications",
        json={
            "company_name": "Google",
            "job_title": "Backend Engineer",
            "applied_date": "2026-11-26",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["job_url"] is None
    assert data["salary_expected"] is None
    assert data["notes"] is None


def test_invalid_status_value(client, created_application):
    app_id = created_application["id"]

    response = client.patch(
        f"/applications/{app_id}/status", json={"status": "INVALID_STATUS"}
    )

    assert response.status_code == 422


def test_invalid_application_id(client):
    response = client.get("/applications/abc")

    assert response.status_code == 422


def test_unique_ids(client, application_data):
    ids = []

    for _ in range(100):
        response = client.post("/applications", json=application_data)

        assert response.status_code == 201
        ids.append(response.json()["id"])

    assert len(ids) == 100
    assert len(set(ids)) == 100

    response = client.get("/applications")

    assert response.status_code == 200
    assert len(response.json()) == 100


def test_deleted_id_not_reused(client, application_data, created_application):
    old_id = created_application["id"]

    response = client.delete(f"/applications/{old_id}")
    assert response.status_code == 204

    response = client.post("/applications", json=application_data)

    assert response.status_code == 201
    assert response.json()["id"] > old_id


def test_server_generated_fields(client, application_data):
    response = client.post(
        "/applications",
        json={
            **application_data,
            "id": 999,
            "status": "OFFERED",
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
        },
    )

    # Pydantic may reject extra fields if extra="forbid".
    if response.status_code == 422:
        return

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["status"] == "APPLIED"
    assert datetime.fromisoformat(data["created_at"]).year != 2000
    assert datetime.fromisoformat(data["updated_at"]).year != 2000
