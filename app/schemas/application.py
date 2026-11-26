from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW = "INTERVIEW"
    OFFERED = "OFFERED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class ApplicationBase(BaseModel):
    company_name: str
    job_title: str
    job_url: HttpUrl | None = None
    applied_date: date
    salary_expected: int | None = Field(default=None, ge=0)
    notes: str | None = None

    @field_validator("company_name", "job_title")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be blank")

        return value.strip()


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    status: ApplicationStatus


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(ApplicationBase):
    id: int
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
