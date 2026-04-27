# ────────────────────────────────────────────────────────────────
# Путь: backend/app/models/__init__.py
# Описание: Пакет ORM-моделей проекта BardaK.
#           Центральная точка импорта моделей.
# ────────────────────────────────────────────────────────────────

"""Пакет ORM-моделей проекта BardaK.

Назначение:
- собрать модели в одном месте
- упростить импорт в Alembic и других модулях
- зафиксировать структуру слоя models
"""

from __future__ import annotations

# Базовый класс всех ORM-моделей
from app.models.base import Base

# Модель категории предметов
from app.models.category import Category

# Модель предмета
from app.models.item import Item

# Модель места хранения
from app.models.location import Location

# Экспортируем публичный интерфейс пакета
__all__: list[str] = [
    "Base",
    "Category",
    "Item",
    "Location",
]
