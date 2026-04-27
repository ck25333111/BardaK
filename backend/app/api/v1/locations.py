#────────────────────────────────────────
# backend/app/api/v1/locations.py
# HTTP endpoints для сущности Location.
#────────────────────────────────────────

"""API v1 endpoints для Location."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.location import LocationCreate
from app.schemas.location import LocationRead
from app.schemas.location import LocationUpdate
from app.services.location.exceptions import LocationHasChildrenError
from app.services.location.exceptions import LocationNotFoundError
from app.services.location.exceptions import LocationParentNotFoundError
from app.services.location.exceptions import LocationSelfParentError
from app.services.location.service import LocationService


router = APIRouter(
    prefix="/locations",
    tags=["locations"],
)


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    """Создать новую локацию."""
    service = LocationService(session)

    try:
        location = await service.create(payload)
        return LocationRead.model_validate(location)
    except LocationParentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get("", response_model=list[LocationRead])
async def get_locations(
    session: AsyncSession = Depends(get_session),
) -> list[LocationRead]:
    """Получить список всех локаций."""
    service = LocationService(session)
    locations = await service.get_all()
    return [LocationRead.model_validate(location) for location in locations]


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: int,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    """Получить локацию по id."""
    service = LocationService(session)

    try:
        location = await service.get_by_id(location_id)
        return LocationRead.model_validate(location)
    except LocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    payload: LocationUpdate,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    """Обновить локацию по id."""
    service = LocationService(session)

    try:
        location = await service.update(location_id, payload)
        return LocationRead.model_validate(location)
    except LocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (LocationParentNotFoundError, LocationSelfParentError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Удалить локацию по id."""
    service = LocationService(session)

    try:
        await service.delete(location_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except LocationHasChildrenError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error