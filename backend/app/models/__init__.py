# ────────────────────────────────────────────────────────────────
# Путь: backend/app/models/__init__.py
# Описание: Пакет ORM-моделей проекта BardaK.
#           Центральная точка импорта моделей.
# ────────────────────────────────────────────────────────────────

"""Пакет ORM-моделей проекта BardaK."""

from __future__ import annotations

from app.models.base import Base
from app.models.category import Category
from app.models.item import Item
from app.models.location import Location

__all__: list[str] = [
    "Base",
    "Category",
    "Item",
    "Location",
]