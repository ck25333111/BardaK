#────────────────────────────────────────
# backend/app/schemas/form.py
# Pydantic-схемы для приёма данных с тестовой формы фронтенда
#────────────────────────────────────────

"""Pydantic schemas for frontend form payload."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ThreeFieldsPayload(BaseModel):
    """Payload with three input fields from the frontend."""

    first: str = Field(default="", max_length=500)
    second: str = Field(default="", max_length=500)
    third: str = Field(default="", max_length=500)
