#────────────────────────────────────────
# backend/app/api/v1/echo.py
# API endpoint для проверки связки фронт↔бэк (приём/валидация/ответ)
#────────────────────────────────────────

"""Echo endpoint for frontend-backend connectivity tests."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.form import ThreeFieldsPayload

router = APIRouter(prefix="/echo", tags=["dev"])


@router.post("")
async def echo(payload: ThreeFieldsPayload) -> dict[str, object]:
    """Return received payload back to the client."""
    return {"ok": True, "received": payload.model_dump()}
