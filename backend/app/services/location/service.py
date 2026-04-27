# ────────────────────────────────────────────────────────────────
# Путь: backend/app/services/location/service.py
# Описание: Service-слой для сущности Location.
# ────────────────────────────────────────────────────────────────

"""Сервис бизнес-сценариев для Location."""

from __future__ import annotations

# Импорт асинхронной сессии SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

# Импорт ORM-модели Location
from app.models.location import Location

# Импорт repository слоя
from app.repositories.location_repository import LocationRepository

# Импорт входных схем Location
from app.schemas.location import LocationCreate
from app.schemas.location import LocationUpdate

# Импорт доменных ошибок
from app.services.location.exceptions import LocationNotFoundError

# Импорт бизнес-валидаторов
from app.services.location.validators import validate_location_can_be_deleted
from app.services.location.validators import validate_not_self_parent
from app.services.location.validators import validate_parent_exists


class LocationService:
    """Service-слой сценариев работы с Location."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализировать сервис.

        Args:
            session: Активная асинхронная сессия БД.
        """
        # Сохраняем сессию для управления транзакцией
        self._session = session

        # Создаём repository для доступа к данным
        self._repository = LocationRepository(session)

    async def create(self, payload: LocationCreate) -> Location:
        """Создать новую локацию."""
        # Проверяем существование родителя, если он указан
        await validate_parent_exists(self._repository, payload.parent_id)

        try:
            # Создаём локацию через repository
            location = await self._repository.create(payload)

            # Фиксируем транзакцию
            await self._session.commit()

            # Возвращаем созданную сущность
            return location
        except Exception:
            # При ошибке откатываем транзакцию
            await self._session.rollback()
            raise

    async def get_by_id(self, location_id: int) -> Location:
        """Получить локацию по id."""
        # Загружаем локацию из БД
        location = await self._repository.get_by_id(location_id)

        # Если локация не найдена — поднимаем доменную ошибку
        if location is None:
            raise LocationNotFoundError(
                f"Локация с id={location_id} не найдена.",
            )

        # Возвращаем найденную локацию
        return location

    async def get_all(self) -> list[Location]:
        """Получить список всех локаций."""
        # Возвращаем все локации из repository
        return await self._repository.get_all()

    async def update(self, location_id: int, payload: LocationUpdate) -> Location:
        """Обновить существующую локацию."""
        # Сначала убеждаемся, что локация существует
        location = await self.get_by_id(location_id)

        # Берём только реально переданные поля
        update_data = payload.model_dump(exclude_unset=True)

        # Если parent_id передан явно — валидируем его
        if "parent_id" in update_data:
            parent_id = update_data["parent_id"]
            validate_not_self_parent(location_id, parent_id)
            await validate_parent_exists(self._repository, parent_id)

        try:
            # Обновляем запись через repository
            updated_location = await self._repository.update(location, update_data)

            # Фиксируем изменения
            await self._session.commit()

            # Возвращаем обновлённую сущность
            return updated_location
        except Exception:
            # При ошибке откатываем транзакцию
            await self._session.rollback()
            raise

    async def delete(self, location_id: int) -> None:
        """Удалить локацию по id."""
        # Убеждаемся, что локация существует
        location = await self.get_by_id(location_id)

        # Проверяем, что удаление допустимо
        await validate_location_can_be_deleted(self._repository, location_id)

        try:
            # Удаляем сущность через repository
            await self._repository.delete(location)

            # Фиксируем удаление
            await self._session.commit()
        except Exception:
            # При ошибке откатываем транзакцию
            await self._session.rollback()
            raise