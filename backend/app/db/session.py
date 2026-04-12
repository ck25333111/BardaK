#────────────────────────────────────────
# backend/app/core/db.py
# Подключение к БД (PostgreSQL):
# - async SQLAlchemy engine
# - фабрика async-сессий
# - dependency для FastAPI
#────────────────────────────────────────

"""Database module for BardaK backend.

Этот модуль отвечает за:
- создание async engine (один на приложение)
- создание фабрики сессий (AsyncSession)
- dependency get_session() для FastAPI

Правила:
- не создаём engine в каждом запросе
- не держим сессии глобально “навсегда” — выдаём на запрос и закрываем
"""

from __future__ import annotations

#────────────────────────────────────────
# Импорты
#────────────────────────────────────────

from collections.abc import AsyncGenerator  # # правильный тип для yield dependency
from functools import lru_cache  # # кэшируем engine/sessionmaker, чтобы не плодить
import logging  # # логирование событий БД (коннект/ошибки)
import asyncio # # для async/await в SQLAlchemy

from sqlalchemy.ext.asyncio import (  # # async SQLAlchemy API
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text  # # для простого "SELECT 1" в проверке соединения

from app.core.settings import get_settings  # # тянем DATABASE_URL из единого settings


#────────────────────────────────────────
# Логгер
#────────────────────────────────────────

logger = logging.getLogger("app")  # # единый логгер приложения


#────────────────────────────────────────
# Engine / Sessionmaker (singleton через cache)
#────────────────────────────────────────

@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Создать и вернуть async engine (один на приложение).

    Почему через функцию + кэш:
    - engine тяжёлый объект
    - должен быть один, а не на каждый импорт/запрос

    Returns:
        AsyncEngine: асинхронный engine SQLAlchemy.
    """
    settings = get_settings()  # # читаем настройки (кэшируется)
    database_url = settings.database_url  # # DSN вида postgresql+asyncpg://...

    # # Создаём engine:
    # # pool_pre_ping=True — проверяет соединения в пуле, чтобы не отдавать “мертвые”
    # # echo=False — не спамим SQL в консоль (потом можно включать в dev через env)
    engine = create_async_engine(
        database_url,            # # строка подключения
        pool_pre_ping=True,      # # защита от протухших коннектов
        echo=False,              # # SQL-эхо (лучше управлять через конфиг позже)
    )

    logger.info("db engine created", extra={"database_url_set": True})  # # лог без пароля
    return engine  # # возвращаем engine


@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Создать и вернуть фабрику async-сессий.

    Returns:
        async_sessionmaker[AsyncSession]: фабрика сессий.
    """
    engine = get_engine()  # # берём singleton engine

    # # expire_on_commit=False:
    # # после commit объекты не “протухают” и не требуют повторного запроса
    session_maker = async_sessionmaker(
        bind=engine,             # # к какому engine привязана сессия
        class_=AsyncSession,     # # тип сессии
        expire_on_commit=False,  # # удобнее для API
        autoflush=False,         # # меньше неожиданных flush; вручную/commit
        autocommit=False,        # # autocommit нам не нужен
    )

    logger.info("db sessionmaker created")  # # лог
    return session_maker  # # возвращаем фабрику


#────────────────────────────────────────
# Dependency: выдаём сессию на запрос и закрываем
#────────────────────────────────────────

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: получить AsyncSession на время запроса.

    Работает так:
    - создаём сессию
    - отдаём её через yield
    - после запроса закрываем (даже если упали с ошибкой)

    Yields:
        AsyncSession: активная сессия.
    """
    session_maker = get_sessionmaker()  # # берём фабрику

    async with session_maker() as session:  # # создаём сессию и гарантируем закрытие
        try:
            yield session  # # отдаём сессию вызывающему коду (repo/service)
        finally:
            # # async with сам закроет, но пусть будет очевидно по логике
            # # (тут не делаем commit/rollback — это ответственность сервиса/репозитория)
            pass


#────────────────────────────────────────
# Проверка соединения (для дебага/healthcheck, опционально)
#────────────────────────────────────────

async def check_db_connection() -> bool:
    """Проверить, что БД доступна (SELECT 1) с коротким таймаутом.

    Returns:
        bool: True если всё ок, иначе False.
    """
    engine = get_engine()  # # singleton engine

    async def _probe() -> None:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    try:
        await asyncio.wait_for(_probe(), timeout=1.0)
        logger.info("db connection check: ok")
        return True
    except (TimeoutError, OSError):
        # # OSError сюда попадает при "connection refused" и прочей сетевой хуйне
        logger.warning("db connection check: unavailable")
        return False
    except Exception:
        # # остальное — реально неожиданное, пусть будет stacktrace
        logger.exception("db connection check: failed")
        return False


