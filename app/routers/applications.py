from fastapi import APIRouter, HTTPException, status

from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatusUpdate,
    ApplicationResponse,
)

from app.services.application_service import ApplicationService

from app.exceptions import (
    ApplicationNotFoundError,
    InvalidStatusTransitionError,
)

router = APIRouter(prefix="/applications", tags=["Applications"])

service = ApplicationService()


@router.get("", response_model=list[ApplicationResponse])
def get_applications():
    return service.get_all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int):
    try:
        return service.get_by_id(application_id)

    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
def create_application(application: ApplicationCreate):
    return service.create(application)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(application_id: int, application: ApplicationUpdate):
    try:
        return service.update(application_id, application)

    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int, application: ApplicationStatusUpdate
):
    try:
        return service.update_status(application_id, application.status)

    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int):
    try:
        service.delete(application_id)

    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
