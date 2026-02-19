#────────────────────────────────────────
# backend/app/schemas/dev.py
# Pydantic-схемы для dev-эндпоинтов (тестовые запросы/ответы)
#────────────────────────────────────────

"""Schemas for development endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EchoPayload(BaseModel):
    """Payload for echo endpoint.

    Используется для проверки связи фронт ↔ бэкенд и CORS.
    """

    first: str = Field(default="", max_length=500)
    second: str = Field(default="", max_length=500)
    third: str = Field(default="", max_length=500)
