from app.repositories.application_repository import ApplicationRepository
from app.services.application_service import ApplicationService
from typing import Annotated
from fastapi import Depends

repository = ApplicationRepository()


def get_repository() -> ApplicationRepository:
    return repository


def get_service(
    repo: Annotated[ApplicationRepository, Depends(get_repository)],
) -> ApplicationService:
    return ApplicationService(repository=repo)
