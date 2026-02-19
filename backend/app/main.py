#────────────────────────────────────────
# backend/app/main.py
# FastAPI приложение + тестовый endpoint echo для проверки связки фронт↔бэк
#────────────────────────────────────────

"""FastAPI app entrypoint and simple API endpoints for development."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="BardaK API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EchoPayload(BaseModel):
    """Incoming payload from frontend test form."""

    first: str = Field(default="", max_length=500)
    second: str = Field(default="", max_length=500)
    third: str = Field(default="", max_length=500)


@app.get("/health")
async def health() -> dict[str, str]:
    """Healthcheck endpoint."""
    return {"status": "ok"}


@app.post("/api/v1/echo")
async def echo(payload: EchoPayload) -> dict[str, object]:
    """Echo back received payload to confirm frontend-backend connectivity."""
    return {"ok": True, "received": payload.model_dump()}
