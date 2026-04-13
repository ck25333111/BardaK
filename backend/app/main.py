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

#────────────────────────────────────────
# Импорты
#────────────────────────────────────────

import logging  # # чтобы писать лог о загрузке настроек

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.logging import configure_logging
from app.core.request_id import RequestContextMiddleware
from app.core.settings import get_settings  # # наш Settings (env/.env)


from app.db.session import check_db_connection  # # проверка доступности БД

#────────────────────────────────────────
# Settings: читаем env/.env ОДИН РАЗ
#────────────────────────────────────────

settings = get_settings()  # # создаём единый объект настроек (кэшируется)


#────────────────────────────────────────
# Логи: включаем ДО создания app, чтобы всё писалось одинаково
#────────────────────────────────────────

configure_logging(log_level=settings.log_level, json_logs=True)  # # уровень логов берём из env

logger = logging.getLogger("app")  # # используем ваш единый логгер "app"
logger.info(
    "settings loaded",
    extra={
        "app_env": settings.app_env,  # # dev/test/prod
        "log_level": settings.log_level,  # # INFO/DEBUG/...
        "database_url_set": bool(settings.database_url),  # # чтобы не светить пароль, просто факт
    },
)

app = FastAPI(title="BardaK API", version="0.1.0")


#────────────────────────────────────────
# CORS: разрешаем фронту обращаться к API
#────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # # фронт Vite
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


#────────────────────────────────────────
@app.get("/health")
async def health() -> dict[str, str]:
    """Simple healthcheck endpoint."""
    return {"status": "ok"}
    
#────────────────────────────────────────
# Healthcheck: DB
#────────────────────────────────────────

@app.get("/health/db")
async def health_db() -> dict[str, str]:
    """Healthcheck для базы данных.

    Возвращает:
    - ok    → если БД доступна
    - error → если БД недоступна
    """
    is_ok = await check_db_connection()  # # пробуем SELECT 1

    if is_ok:
        return {"status": "ok"}  # # БД жива

    return {"status": "error"}  # # БД недоступна