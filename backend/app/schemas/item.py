# ────────────────────────────────────────────────────────────────
# Путь: backend/app/schemas/item.py
# Описание: Pydantic-схемы Item.
#           Контракты запросов и ответов API.
# ────────────────────────────────────────────────────────────────

"""Pydantic-схемы Item для проекта BardaK.

Назначение:
- валидировать входящие данные API
- формировать ответы наружу
- разделять ORM и HTTP слой
"""

from __future__ import annotations

# Импорт datetime для временных полей ответа
from datetime import datetime

# Импорт инструментов Pydantic
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ItemBase(BaseModel):
    """Базовая схема общих полей Item."""

    # Название предмета
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название предмета",
    )

    # ID текущей локации хранения
    location_id: int = Field(
        ...,
        description="ID локации хранения",
    )

    # Необязательная категория предмета
    category_id: int | None = Field(
        default=None,
        description="ID категории предмета",
    )

    # Описание предмета
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Описание предмета",
    )

    # Количество одинаковых предметов
    quantity: int = Field(
        default=1,
        ge=1,
        description="Количество предметов",
    )

    # Состояние предмета
    condition: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Состояние предмета",
    )

    # Дополнительный комментарий
    comment: str | None = Field(
        default=None,
        max_length=1000,
        description="Комментарий к предмету",
    )

    # Размеры предмета в миллиметрах
    width_mm: int | None = Field(
        default=None,
        ge=1,
        description="Ширина предмета в мм",
    )

    depth_mm: int | None = Field(
        default=None,
        ge=1,
        description="Глубина предмета в мм",
    )

    height_mm: int | None = Field(
        default=None,
        ge=1,
        description="Высота предмета в мм",
    )


class ItemCreate(ItemBase):
    """Схема создания нового Item."""


class ItemUpdate(BaseModel):
    """Схема частичного обновления Item."""

    # Все поля optional для PATCH
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location_id: int | None = None
    category_id: int | None = None
    description: str | None = Field(default=None, max_length=1000)
    quantity: int | None = Field(default=None, ge=1)
    condition: str | None = Field(default=None, min_length=1, max_length=100)
    comment: str | None = Field(default=None, max_length=1000)
    width_mm: int | None = Field(default=None, ge=1)
    depth_mm: int | None = Field(default=None, ge=1)
    height_mm: int | None = Field(default=None, ge=1)


class ItemRead(ItemBase):
    """Схема ответа Item наружу."""

    # Разрешаем создание схемы из ORM-объекта
    model_config = ConfigDict(from_attributes=True)

    # Системные поля
    id: int
    created_at: datetime
    updated_at: datetime