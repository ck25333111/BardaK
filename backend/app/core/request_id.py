#────────────────────────────────────────
# backend/app/core/request_id.py
# Middleware: создаёт/принимает request_id и кладёт в contextvars + в header ответа
#────────────────────────────────────────

"""Request ID middleware.

Что делает:
- Берёт X-Request-ID из заголовков, если пришёл (например, прокси/клиент прислал)
- Если не пришёл — генерит UUID
- Кладёт request_id:
  - в request.state (удобно читать из обработчиков)
  - в contextvars (чтобы логирование подхватывало автоматически)
- Возвращает request_id в заголовке ответа X-Request-ID
"""

from __future__ import annotations

import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.request_context import REQUEST_ID


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware, добавляющий request_id к каждому HTTP-запросу."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and ensure request_id is available everywhere."""
        #────────────────────────────────────────
        # 1) Берём request_id из header'а (если клиент/прокси уже прислал)
        #────────────────────────────────────────
        incoming_request_id: str | None = request.headers.get("x-request-id")

        #────────────────────────────────────────
        # 2) Если нет — генерим новый UUID
        #────────────────────────────────────────
        request_id: str = incoming_request_id or str(uuid.uuid4())  # UUID для корреляции логов

        #────────────────────────────────────────
        # 3) Сохраняем в request.state (чтобы можно было читать в роуте)
        #────────────────────────────────────────
        request.state.request_id = request_id  # type: ignore[attr-defined]

        #────────────────────────────────────────
        # 4) Сохраняем в contextvar (чтобы логгер подхватывал автоматически)
        #────────────────────────────────────────
        token = REQUEST_ID.set(request_id)  # token нужен, чтобы корректно вернуть старое значение

        try:
            #────────────────────────────────────────
            # 5) Пускаем запрос дальше по цепочке
            #────────────────────────────────────────
            response: Response = await call_next(request)

            #────────────────────────────────────────
            # 6) Добавляем request_id в заголовки ответа
            #────────────────────────────────────────
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            #────────────────────────────────────────
            # 7) Чистим контекст (ВАЖНО для корректной работы в async)
            #────────────────────────────────────────
            REQUEST_ID.reset(token)
