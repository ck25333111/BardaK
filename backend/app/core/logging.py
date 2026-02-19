#────────────────────────────────────────
# backend/app/core/logging.py
# Единый конфиг логирования: JSON/текст, уровни, формат, request_id из contextvars
#────────────────────────────────────────

"""Centralized logging configuration.

Цели:
- Один конфиг на всё приложение (не размазываем logging.basicConfig по файлам)
- Структурные JSON-логи (проще читать/парсить, позже можно писать в БД/ELK)
- request_id подтягивается автоматически из contextvars
"""

from __future__ import annotations

import json
import logging
import sys
from logging.config import dictConfig
from typing import Any

from app.core.request_context import REQUEST_ID


class RequestIdFilter(logging.Filter):
    """Inject request_id into each log record.

    request_id берём из contextvars (REQUEST_ID). Это работает и в async.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        request_id: str | None = REQUEST_ID.get()  # request_id текущего запроса или None
        record.request_id = request_id  # type: ignore[attr-defined]  # добавляем поле в record
        return True


class JsonFormatter(logging.Formatter):
    """Formats log records as compact JSON.

    Это удобно:
    - читать в консоли
    - складывать в файл
    - позже грузить в Postgres/Elastic и т.д.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }

        # Если есть exception — добавим stacktrace
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(*, log_level: str = "INFO", json_logs: bool = True) -> None:
    """Configure logging once, at application startup.

    Args:
        log_level: Уровень логов ("DEBUG", "INFO", "WARNING"...).
        json_logs: True -> JSON формат, False -> человекочитаемый текст.
    """
    #────────────────────────────────────────
    # Handlers: куда пишем логи (пока только консоль)
    #────────────────────────────────────────
    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": log_level,
            "filters": ["request_id"],  # request_id добавится в каждый лог
            "formatter": "json" if json_logs else "text",
        }
    }

    #────────────────────────────────────────
    # Formatters: как выглядят логи
    #────────────────────────────────────────
    formatters: dict[str, Any] = {
        "text": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | %(message)s"
        },
        "json": {
            "()": "app.core.logging.JsonFormatter",
        },
    }

    #────────────────────────────────────────
    # dictConfig: единая точка конфигурации logging
    #────────────────────────────────────────
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id": {
                    "()": "app.core.logging.RequestIdFilter",
                }
            },
            "formatters": formatters,
            "handlers": handlers,
            "root": {"level": log_level, "handlers": ["console"]},
            "loggers": {
                # uvicorn.* тоже логируем, но не даём им жить отдельно от общей системы
                "uvicorn": {"level": log_level},
                "uvicorn.error": {"level": log_level},
                "uvicorn.access": {"level": log_level},
            },
        }
    )
