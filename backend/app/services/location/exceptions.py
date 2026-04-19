# ────────────────────────────────────────────────────────────────
# Путь: backend/app/services/location/exceptions.py
# Описание: Доменные исключения для service-слоя Location.
# ────────────────────────────────────────────────────────────────

"""Исключения бизнес-логики Location.

Назначение:
- отделить доменные ошибки от HTTP-слоя
- не использовать голые ValueError
- дать API-слою понятные типы ошибок
"""

from __future__ import annotations


class LocationServiceError(Exception):
    """Базовая ошибка service-слоя Location."""


class LocationNotFoundError(LocationServiceError):
    """Локация не найдена."""


class LocationParentNotFoundError(LocationServiceError):
    """Родительская локация не найдена."""


class LocationSelfParentError(LocationServiceError):
    """Локация не может быть родителем самой себе."""


class LocationHasChildrenError(LocationServiceError):
    """Нельзя удалить локацию с дочерними узлами."""