#────────────────────────────────────────
# backend/app/main.py
# Точка входа FastAPI приложения + CORS + подключение роутов v1
#────────────────────────────────────────

"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.echo import router as echo_router

app = FastAPI(title="BardaK API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(echo_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Healthcheck endpoint."""
    return {"status": "ok"}
