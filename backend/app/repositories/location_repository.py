# ────────────────────────────────────────────────────────────────
# Путь: backend/app/repositories/location_repository.py
# Описание: Repository-слой для сущности Location.
#           Содержит только операции доступа к данным без
#           бизнес-логики и HTTP-логики.
# ────────────────────────────────────────────────────────────────

"""Repository для работы с Location в проекте BardaK.

Назначение:
- инкапсулировать SQLAlchemy-запросы к таблице locations
- отделить доступ к данным от service-слоя
- дать предсказуемый API для CRUD-операций

Важно:
- repository не содержит бизнес-правил
- repository не валидирует сценарии домена
- repository не работает с HTTP-слоем
"""

from __future__ import annotations

# Импорт последовательностей для типизации списков результатов
from collections.abc import Sequence

# Импорт SQLAlchemy-конструкций для запросов
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Импорт ORM-модели Location
from app.models.location import Location

# Импорт Pydantic-схемы создания
from app.schemas.location import LocationCreate


class LocationRepository:
    """Repository для доступа к данным Location.

    Этот класс отвечает только за:
    - создание записи
    - получение одной записи
    - получение списка записей
    - обновление уже загруженной записи
    - удаление записи
    - технические проверки существования и наличия детей
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализировать repository.

        Args:
            session: Асинхронная SQLAlchemy-сессия.
        """
        # Сохраняем сессию для дальнейших запросов к БД
        self._session = session

    async def create(self, payload: LocationCreate) -> Location:
        """Создать новую локацию в БД.

        Args:
            payload: Данные для создания Location.

        Returns:
            Location: Созданная ORM-модель.
        """
        # Создаём ORM-объект из входной Pydantic-схемы
        location = Location(**payload.model_dump())

        # Добавляем объект в текущую сессию
        self._session.add(location)

        # Выполняем flush, чтобы запись ушла в БД и получила id
        await self._session.flush()

        # Обновляем объект из БД, чтобы подтянуть server_default поля
        await self._session.refresh(location)

        # Возвращаем созданную запись
        return location

    async def get_by_id(self, location_id: int) -> Location | None:
        """Получить Location по идентификатору.

        Args:
            location_id: ID локации.

        Returns:
            Location | None: Найденная запись или None.
        """
        # Формируем SELECT по первичному ключу
        statement = select(Location).where(Location.id == location_id)

        # Выполняем запрос
        result = await self._session.execute(statement)

        # Возвращаем один объект или None
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Location]:
        """Получить список всех локаций.

        Returns:
            list[Location]: Список ORM-объектов Location.
        """
        # Формируем запрос на получение всех локаций
        statement = select(Location).order_by(Location.id)

        # Выполняем запрос
        result = await self._session.execute(statement)

        # Получаем все объекты из результата
        locations: Sequence[Location] = result.scalars().all()

        # Приводим к обычному list и возвращаем
        return list(locations)

    async def update(self, location: Location, data: dict[str, object]) -> Location:
        """Обновить уже загруженный объект Location.

        Args:
            location: ORM-объект, который нужно обновить.
            data: Словарь полей для изменения.

        Returns:
            Location: Обновлённый ORM-объект.
        """
        # Последовательно обновляем только переданные поля
        for field_name, value in data.items():
            setattr(location, field_name, value)

        # Выполняем flush, чтобы изменения ушли в БД
        await self._session.flush()

        # Обновляем объект из БД, чтобы подтянуть актуальные значения
        await self._session.refresh(location)

        # Возвращаем обновлённый объект
        return location

    async def delete(self, location: Location) -> None:
        """Удалить объект Location из БД.

        Args:
            location: ORM-объект для удаления.
        """
        # Помечаем объект на удаление в текущей сессии
        await self._session.delete(location)

        # Выполняем flush, чтобы удаление ушло в БД
        await self._session.flush()

    async def exists_by_id(self, location_id: int) -> bool:
        """Проверить существование Location по ID.

        Args:
            location_id: ID локации.

        Returns:
            bool: True если запись существует, иначе False.
        """
        # Получаем объект по идентификатору
        location = await self.get_by_id(location_id)

        # Возвращаем факт существования записи
        return location is not None

    async def has_children(self, location_id: int) -> bool:
        """Проверить, есть ли у Location дочерние узлы.

        Args:
            location_id: ID родительской локации.

        Returns:
            bool: True если дочерние записи существуют, иначе False.
        """
        # Формируем запрос на поиск хотя бы одного дочернего узла
        statement = select(Location.id).where(Location.parent_id == location_id).limit(1)

        # Выполняем запрос
        result = await self._session.execute(statement)

        # Если нашли хотя бы одну строку — дети существуют
        child_id = result.scalar_one_or_none()

        # Возвращаем результат проверки
        return child_id is not None