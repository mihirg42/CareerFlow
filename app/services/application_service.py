from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatus,
)

from app.repositories.application_repository import (
    ApplicationRepository,
)

from app.exceptions import InvalidStatusTransitionError


class ApplicationService:

    ALLOWED_TRANSITIONS = {
        ApplicationStatus.APPLIED: {
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.SHORTLISTED: {
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.INTERVIEW: {
            ApplicationStatus.OFFERED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.OFFERED: {
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.REJECTED: set(),
        ApplicationStatus.WITHDRAWN: set(),
    }

    def __init__(self, repository: ApplicationRepository):
        self.repository = repository

    def get_all(self) -> list[dict]:
        return self.repository.get_all()

    def get_by_id(self, app_id: int) -> dict:
        return self.repository.get_by_id(app_id)

    def create(self, application: ApplicationCreate) -> dict:
        return self.repository.create(application)

    def update(self, app_id: int, application: ApplicationUpdate) -> dict:

        existing = self.repository.get_by_id(app_id)

        self._validate_status_transition(
            existing["status"],
            application.status,
        )

        return self.repository.update(app_id, application)

    def update_status(self, app_id: int, status: ApplicationStatus) -> dict:

        existing = self.repository.get_by_id(app_id)

        self._validate_status_transition(
            existing["status"],
            status,
        )

        return self.repository.update_status(app_id, status)

    def delete(self, app_id: int) -> None:
        self.repository.delete(app_id)

    def _validate_status_transition(
        self,
        current_status: ApplicationStatus,
        new_status: ApplicationStatus,
    ) -> None:

        if current_status == new_status:
            return

        if new_status not in self.ALLOWED_TRANSITIONS[current_status]:
            raise InvalidStatusTransitionError(
                f"Cannot change application status from "
                f"{current_status.value} to {new_status.value}"
            )
