from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatus,
)
from app.exceptions import (
    ApplicationNotFoundError,
)
from itertools import count
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class ApplicationRepository:
    IST = ZoneInfo("Asia/Kolkata")

    def __init__(self):
        self._applications = {}
        self._counter = count(start=1)

    def get_all(self):
        return [dict(app) for app in self._applications.values()]

    def get_by_id(self, app_id: int):
        if app_id in self._applications:
            return dict(self._applications.get(app_id))
        else:
            raise ApplicationNotFoundError(f"Application with ID {app_id} not found")

    def create(self, app1: ApplicationCreate):
        app = app1.model_dump()
        app["id"] = next(self._counter)
        app["status"] = ApplicationStatus.APPLIED
        now = datetime.now(self.IST)
        app["created_at"] = now
        app["updated_at"] = now
        self._applications[app["id"]] = app
        return app.copy()

    def update(self, app_id: int, app1: ApplicationUpdate):
        if app_id in self._applications:
            app = dict(self._applications.get(app_id))
            app2 = app1.model_dump()
            app.update(app2)
            now = datetime.now(self.IST)
            app["updated_at"] = now

            self._applications[app_id] = app
            return app.copy()
        else:
            raise ApplicationNotFoundError(f"Application with ID {app_id} not found")

    def delete(self, app_id: int):
        if app_id in self._applications:
            self._applications.pop(app_id, None)
        else:
            raise ApplicationNotFoundError(f"Application with ID {app_id} not found")

    def update_status(self, app_id: int, status: ApplicationStatus):
        if app_id in self._applications:
            self._applications[app_id]["status"] = status
            now = datetime.now(self.IST)
            self._applications[app_id]["updated_at"] = now
            return self._applications[app_id].copy()
        else:
            raise ApplicationNotFoundError(f"Application with ID {app_id} not found")
