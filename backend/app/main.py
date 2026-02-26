#────────────────────────────────────────
# backend/app/main.py
# Точка входа FastAPI:
# - configure_logging() один раз при старте
# - CORS для фронта
# - RequestIdMiddleware для request_id
# - подключение router v1
#────────────────────────────────────────

"""FastAPI application entry point for BardaK backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.logging import configure_logging
from app.core.request_id import RequestContextMiddleware



#────────────────────────────────────────
# Логи: включаем ДО создания app, чтобы всё писалось одинаково
#────────────────────────────────────────


configure_logging(log_level="INFO", json_logs=True)
app = FastAPI(title="BardaK API", version="0.1.0")


#────────────────────────────────────────
# CORS: разрешаем фронту обращаться к API
#────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # фронт Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#────────────────────────────────────────
# RequestIdMiddleware: request_id на каждый запрос + заголовок X-Request-ID
#────────────────────────────────────────
app.add_middleware(RequestContextMiddleware)

#────────────────────────────────────────
# API v1
#────────────────────────────────────────
app.include_router(v1_router, prefix="/api/v1")



@app.get("/health")
async def health() -> dict[str, str]:
    """Simple healthcheck endpoint."""
    return {"status": "ok"}

