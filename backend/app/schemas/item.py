# ────────────────────────────────────────────────────────────────
# Путь: backend/app/schemas/item.py
# Описание: Pydantic-схемы Item.
#           Контракты запросов и ответов API.
# ────────────────────────────────────────────────────────────────

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location_id: int
    category_id: int | None = None
    description: str | None = Field(default=None, max_length=1000)
    quantity: int = Field(default=1, ge=1)
    condition: str | None = Field(default=None, min_length=1, max_length=100)
    comment: str | None = Field(default=None, max_length=1000)
    width_mm: int | None = Field(default=None, ge=1)
    depth_mm: int | None = Field(default=None, ge=1)
    height_mm: int | None = Field(default=None, ge=1)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime