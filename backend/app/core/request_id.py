#────────────────────────────────────────
# backend/app/core/request_id.py
# Middleware: request_id (contextvars) + access лог + логирование unhandled exceptions
#────────────────────────────────────────

"""Request context middleware.

- Генерирует/берёт X-Request-ID
- Кладёт request_id в contextvars (работает в async)
- Пишет access-лог (method/path/status/duration/request_id)
- Ловит unhandled exceptions и пишет их в app.log через logger.exception
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import REQUEST_ID


_APP_LOGGER = logging.getLogger("app")
_ACCESS_LOGGER = logging.getLogger("app.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware для request_id + access-log + exception-log."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:

        #────────────────────────────────────────
        # 0) Фиксируем время начала запроса
        #────────────────────────────────────────
        started: float = time.perf_counter()

        #────────────────────────────────────────
        # 1) Берём request_id из header'а (если клиент/прокси уже прислал)
        #    Иначе генерируем новый UUID
        #────────────────────────────────────────
        incoming: str | None = request.headers.get("X-Request-ID")
        request_id: str = incoming or str(uuid.uuid4())

        #────────────────────────────────────────
        # 2) Кладём request_id в contextvars
        #    (дальше он будет автоматически попадать в логи)
        #────────────────────────────────────────
        token = REQUEST_ID.set(request_id)

        try:
            #────────────────────────────────────────
            # 3) Передаём управление дальше (в роуты)
            #────────────────────────────────────────
            response: Response = await call_next(request)

            #────────────────────────────────────────
            # 4) Считаем длительность запроса
            #────────────────────────────────────────
            duration_ms: int = int((time.perf_counter() - started) * 1000)

            #────────────────────────────────────────
            # 5) Пишем access-лог (method, path, status, duration)
            #────────────────────────────────────────
            _ACCESS_LOGGER.info(
                "request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )

            #────────────────────────────────────────
            # 6) Возвращаем request_id клиенту в header
            #────────────────────────────────────────
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception:
            #────────────────────────────────────────
            # 7) Если произошла необработанная ошибка —
            #    логируем её со stacktrace
            #────────────────────────────────────────
            duration_ms: int = int((time.perf_counter() - started) * 1000)

            _APP_LOGGER.exception(
                "unhandled exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

        finally:
            #────────────────────────────────────────
            # 8) Чистим contextvars
            #────────────────────────────────────────
            REQUEST_ID.reset(token)