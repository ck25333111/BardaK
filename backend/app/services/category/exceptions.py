# ────────────────────────────────────────────────────────────────
# Путь: backend/app/services/category/exceptions.py
# Описание: Доменные исключения service-слоя для Category.
#           Не зависят от FastAPI и HTTP.
# ────────────────────────────────────────────────────────────────

"""Доменные исключения для Category service.

Назначение:
- описывать ошибки сценариев работы с категориями
- не привязывать service-слой к HTTP-статусам
- позволить API-слою самому решать, какой HTTP-ответ вернуть
"""

from __future__ import annotations


class CategoryError(Exception):
    """Базовое исключение для ошибок Category."""


class CategoryNotFoundError(CategoryError):
    """Категория не найдена."""

    def __init__(self, category_id: int) -> None:
        """Создать ошибку отсутствующей категории.

        Args:
            category_id: ID категории, которую не удалось найти.
        """

        # Формируем человекочитаемое сообщение ошибки
        message = f"Категория с id={category_id} не найдена"

        # Передаём сообщение в базовый Exception
        super().__init__(message)


class CategoryNameAlreadyExistsError(CategoryError):
    """Категория с таким названием уже существует."""

    def __init__(self, name: str) -> None:
        """Создать ошибку дублирующегося названия категории.

        Args:
            name: Название категории, которое уже занято.
        """

        # Формируем человекочитаемое сообщение ошибки
        message = f"Категория с названием '{name}' уже существует"

        # Передаём сообщение в базовый Exception
        super().__init__(message)