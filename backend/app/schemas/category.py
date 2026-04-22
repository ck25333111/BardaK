# ────────────────────────────────────────────────────────────────
# Путь: backend/app/schemas/category.py
# Описание: Pydantic-схемы Category.
#           Контракты запросов и ответов API.
# ────────────────────────────────────────────────────────────────

"""Pydantic-схемы Category для проекта BardaK."""

from __future__ import annotations

# Импорт datetime для временных полей ответа
from datetime import datetime

# Импорт инструментов Pydantic
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class CategoryBase(BaseModel):
    """Базовая схема общих полей Category."""

    # Название категории
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название категории",
    )

    # Необязательное описание категории
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Описание категории",
    )


class CategoryCreate(CategoryBase):
    """Схема создания новой категории."""


class CategoryUpdate(BaseModel):
    """Схема частичного обновления Category."""

    # Новое название категории
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    # Новое описание категории
    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class CategoryRead(CategoryBase):
    """Схема ответа Category наружу."""

    # Разрешаем создание схемы из ORM-объекта
    model_config = ConfigDict(from_attributes=True)

    # Системные поля
    id: int
    created_at: datetime
    updated_at: datetime