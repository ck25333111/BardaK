# ────────────────────────────────────────────────────────────────
# Путь: backend/app/services/location/validators.py
# Описание: Валидаторы бизнес-правил для сущности Location.
# ────────────────────────────────────────────────────────────────

"""Валидаторы service-слоя для Location.

Назначение:
- вынести бизнес-проверки из service.py
- держать проверки маленькими и переиспользуемыми
- не смешивать use-case и валидацию
"""

from __future__ import annotations

# Импорт репозитория для проверок существования и связей
from app.repositories.location_repository import LocationRepository

# Импорт доменных исключений Location
from app.services.location.exceptions import LocationHasChildrenError
from app.services.location.exceptions import LocationParentNotFoundError
from app.services.location.exceptions import LocationSelfParentError

 
async def validate_parent_exists(
    repository: LocationRepository,
    parent_id: int | None,
) -> None:
    """Проверить, что родительская локация существует.

    Args:
        repository: Репозиторий Location.
        parent_id: Идентификатор родительской локации или None.

    Raises:
        LocationParentNotFoundError: Если parent_id указан,
            но такой локации нет в БД.
    """
    # Если parent_id не передан, значит создаётся корневой узел
    if parent_id is None:
        return

    # Проверяем существование родительской локации
    exists = await repository.exists_by_id(parent_id)

    # Если родитель не найден, поднимаем доменную ошибку
    if not exists:
        raise LocationParentNotFoundError(
            f"Родительская локация с id={parent_id} не найдена.",
        )


def validate_not_self_parent(
    location_id: int,
    parent_id: int | None,
) -> None:
    """Проверить, что локация не назначена родителем самой себе.

    Args:
        location_id: Идентификатор текущей локации.
        parent_id: Новый идентификатор родителя или None.

    Raises:
        LocationSelfParentError: Если parent_id совпадает с location_id.
    """
    # Если родитель не задан, проверка не нужна
    if parent_id is None:
        return

    # Нельзя указывать саму локацию как родителя самой себе
    if location_id == parent_id:
        raise LocationSelfParentError(
            f"Локация с id={location_id} не может быть родителем самой себе.",
        )


async def validate_location_can_be_deleted(
    repository: LocationRepository,
    location_id: int,
) -> None:
    """Проверить, что локацию можно удалить.

    Args:
        repository: Репозиторий Location.
        location_id: Идентификатор удаляемой локации.

    Raises:
        LocationHasChildrenError: Если у локации есть дочерние узлы.
    """
    # Проверяем, есть ли у локации дочерние элементы
    has_children = await repository.has_children(location_id)

    # Если дочерние локации существуют, удаление запрещено
    if has_children:
        raise LocationHasChildrenError(
            f"Нельзя удалить локацию с id={location_id}, "
            "потому что у неё есть дочерние локации.",
        )