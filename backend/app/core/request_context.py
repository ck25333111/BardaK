#────────────────────────────────────────
# backend/app/core/request_context.py
# Контекст запроса: request_id через contextvars для логов и трассировки
#────────────────────────────────────────

"""Request-scoped context variables.

Здесь хранится request_id, чтобы:
- не прокидывать его руками по всем функциям
- логирование могло автоматически подхватывать request_id
"""

from __future__ import annotations

from contextvars import ContextVar


# request_id живёт в контексте текущего запроса (async-friendly)
REQUEST_ID: ContextVar[str | None] = ContextVar("REQUEST_ID", default=None)
