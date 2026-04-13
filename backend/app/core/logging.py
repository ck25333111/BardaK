#────────────────────────────────────────
# backend/app/core/logging.py
# Единый конфиг логирования: JSON/текст, уровни, формат, request_id из contextvars
# + запись в файл (RotatingFileHandler) с ротацией
# + отдельный access-лог (запросы) в logs/access.log
#────────────────────────────────────────

"""Centralized logging configuration.

Цели:
- Один конфиг на всё приложение (не размазываем logging.basicConfig по файлам)
- Структурные JSON-логи
- request_id подтягивается автоматически из contextvars
- Логи пишутся в консоль и в файл (с ротацией)
- Отдельный access-лог для запросов (method/path/status/duration/request_id)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from logging.config import dictConfig
from typing import Any

from app.core.request_context import REQUEST_ID


class RequestIdFilter(logging.Filter):
    """Inject request_id into each log record via contextvars."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = REQUEST_ID.get()  # type: ignore[attr-defined]
        return True


class JsonFormatter(logging.Formatter):
    """Formats log records as compact JSON (including extra fields)."""

    _STANDARD_ATTRS: set[str] = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }

        # stacktrace если есть exception
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        # ВАЖНО: добавляем любые extra-поля (method/path/status/duration и т.д.)
        for key, value in record.__dict__.items():
            if key in self._STANDARD_ATTRS:
                continue
            if key in payload:
                continue
            payload[key] = value

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(
    *,
    log_level: str = "INFO",
    json_logs: bool = True,
    log_to_file: bool = True,
    log_file_path: str = "logs/app.log",
    access_log_path: str = "logs/access.log",
) -> None:
    """Configure logging once, at application startup."""
    if log_to_file:
        os.makedirs(os.path.dirname(log_file_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(access_log_path) or ".", exist_ok=True)

    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": log_level,
            "filters": ["request_id"],
            "formatter": "json" if json_logs else "text",
        }
    }

    if log_to_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file_path,
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": log_level,
            "filters": ["request_id"],
            "formatter": "json" if json_logs else "text",
        }
        # отдельный файл под access (запросы)
        handlers["access_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": access_log_path,
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": log_level,
            "filters": ["request_id"],
            "formatter": "json" if json_logs else "text",
        }

    formatters: dict[str, Any] = {
        "text": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | %(message)s"
        },
        "json": {"()": "app.core.logging.JsonFormatter"},
    }

    root_handlers: list[str] = ["console"]
    if log_to_file:
        root_handlers.append("file")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": "app.core.logging.RequestIdFilter"}},
            "formatters": formatters,
            "handlers": handlers,
            "root": {"level": log_level, "handlers": root_handlers},
            "loggers": {
                # Отдельный логгер для access-логов (чтобы не мешать с app.log)
                "app.access": {
                    "level": log_level,
                    "handlers": (["access_file"] if log_to_file else []),
                    "propagate": True,  # в консоль тоже уйдёт через root
                },
                "uvicorn": {"level": log_level},
                "uvicorn.error": {"level": log_level},
                "uvicorn.access": {"level": log_level},
            },
        }
    )