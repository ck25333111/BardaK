#────────────────────────────────────────
# backend/app/api/v1/router.py
# Сборщик роутов API v1 (подключаем модули и выдаём один общий APIRouter)
#────────────────────────────────────────

"""API v1 router aggregator."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.categories import router as categories_router
from app.api.v1.dev import router as dev_router
from app.api.v1.locations import router as locations_router

router = APIRouter()

#────────────────────────────────────────
# Dev endpoints (временные/отладочные)
#────────────────────────────────────────
router.include_router(dev_router, prefix="/dev")

#────────────────────────────────────────
# Location endpoints
#────────────────────────────────────────
router.include_router(locations_router)

#────────────────────────────────────────
# Category endpoints
#────────────────────────────────────────
router.include_router(categories_router)