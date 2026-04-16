#────────────────────────────────────────
# backend/app/api/v1/dev.py
# Dev-эндпоинты: быстрые проверки (echo, health-checkи и т.п.)
#────────────────────────────────────────

"""Development endpoints (non-business API).

Важно:
- dev-роуты НЕ должны мешать бизнес-API (blueprints/items/etc.)
- поэтому они живут в /api/v1/dev/*
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.schemas.dev import EchoPayload

router = APIRouter(tags=["dev"])
logger = logging.getLogger("app")  # общий логгер приложения


@router.post("/echo")
async def echo(payload: EchoPayload, request: Request) -> dict[str, object]:
    """Echo back received payload and log it.

    Args:
        payload: Данные из фронта (3 поля).
        request: Объект запроса (тут можно читать request.state.request_id при необходимости).

    Returns:
        JSON с тем, что получили (для отладки).
    """
    # request_id уже внутри логов автоматически (через contextvars + filter)
    logger.info("dev.echo: payload received")  # простая отметка, что запрос дошёл

    # Можно достать request_id руками (иногда полезно в отладке)
    # request_id: str | None = getattr(request.state, "request_id", None)

    return {"ok": True, "received": payload.model_dump()}
