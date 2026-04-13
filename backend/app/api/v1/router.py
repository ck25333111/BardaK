#────────────────────────────────────────
# backend/app/api/v1/router.py
# Сборщик роутов API v1 (подключаем модули и выдаём один общий APIRouter)
#────────────────────────────────────────

"""API v1 router aggregator."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.dev import router as dev_router

router = APIRouter()

#────────────────────────────────────────
# Dev endpoints (временные/отладочные)
#────────────────────────────────────────
router.include_router(dev_router, prefix="/dev")
