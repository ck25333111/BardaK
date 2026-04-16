# ────────────────────────────────────────────────────────────────
# Путь: backend/app/schemas/location.py
# Описание: Pydantic-схемы Location.
#           Контракты запросов и ответов API.
# ────────────────────────────────────────────────────────────────

"""Pydantic-схемы Location для проекта BardaK.

Назначение:
- валидация входящих данных API
- формирование ответов наружу
- разделение ORM и HTTP слоя

Важно:
- ORM-модель = app.models.location
- API-схемы = app.schemas.location
"""

from __future__ import annotations

# Импорт datetime для временных полей ответа
from datetime import datetime

# Импорт Pydantic инструментов
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class LocationBase(BaseModel):
    """Базовая схема общих полей Location."""

    # Название места хранения
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название места хранения",
    )

    # Тип узла хранения
    location_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Тип локации",
    )

    # Родительская локация
    parent_id: int | None = Field(
        default=None,
        description="ID родительской локации",
    )

    # Размеры в миллиметрах
    width_mm: int | None = None
    depth_mm: int | None = None
    height_mm: int | None = None

    # Описание / заметки
    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class LocationCreate(LocationBase):
    """Схема создания новой локации."""


class LocationUpdate(BaseModel):
    """Схема частичного обновления Location."""

    # Все поля optional для PATCH/PUT обновления
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location_type: str | None = Field(default=None, min_length=1, max_length=100)
    parent_id: int | None = None

    width_mm: int | None = None
    depth_mm: int | None = None
    height_mm: int | None = None

    description: str | None = Field(default=None, max_length=1000)


class LocationRead(LocationBase):
    """Схема ответа Location наружу."""

    # Разрешаем создание схемы из ORM объекта
    model_config = ConfigDict(from_attributes=True)

    # Системные поля
    id: int
    created_at: datetime
    updated_at: datetime