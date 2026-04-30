# ────────────────────────────────────────────────────────────────
# Путь: backend/app/services/category/service.py
# Описание: Service-слой для сущности Category.
#           Содержит сценарии и бизнес-правила работы с категориями.
# ────────────────────────────────────────────────────────────────

"""Service для работы с Category в проекте BardaK.

Назначение:
- выполнять сценарии приложения для категорий
- проверять доменные правила
- отделять бизнес-логику от API и repository

Важно:
- service не знает про FastAPI и HTTP
- service не строит SQL-запросы напрямую
- repository отвечает за доступ к данным
"""

from __future__ import annotations

# Импорт последовательностей для типизации списков результатов
from collections.abc import Sequence

# Импорт SQLAlchemy-сессии
from sqlalchemy.ext.asyncio import AsyncSession

# Импорт ORM-модели Category
from app.models.category import Category

# Импорт repository-слоя
from app.repositories.category_repository import CategoryRepository

# Импорт схем Category
from app.schemas.category import CategoryCreate
from app.schemas.category import CategoryUpdate

# Импорт доменных исключений
from app.services.category.exceptions import CategoryNameAlreadyExistsError
from app.services.category.exceptions import CategoryNotFoundError


class CategoryService:
    """Service для сценариев Category."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализировать service.

        Args:
            session: Асинхронная SQLAlchemy-сессия.
        """

        # Создаём repository для работы с таблицей categories
        self._repository = CategoryRepository(session)

    async def create(self, payload: CategoryCreate) -> Category:
        """Создать новую категорию.

        Args:
            payload: Данные для создания категории.

        Returns:
            Созданная ORM-модель Category.

        Raises:
            CategoryNameAlreadyExistsError: Если категория с таким названием уже есть.
        """

        # Проверяем уникальность названия категории
        existing_category = await self._repository.get_by_name(payload.name)

        # Если категория с таким названием уже есть — запрещаем создание дубля
        if existing_category is not None:
            raise CategoryNameAlreadyExistsError(payload.name)

        # Создаём категорию через repository
        return await self._repository.create(payload)

    async def get_all(self) -> Sequence[Category]:
        """Получить список всех категорий.

        Returns:
            Последовательность ORM-моделей Category.
        """

        # Делегируем получение списка repository-слою
        return await self._repository.get_all()

    async def get_by_id(self, category_id: int) -> Category:
        """Получить категорию по id.

        Args:
            category_id: ID категории.

        Returns:
            ORM-модель Category.

        Raises:
            CategoryNotFoundError: Если категория не найдена.
        """

        # Ищем категорию по id
        category = await self._repository.get_by_id(category_id)

        # Если записи нет — выбрасываем доменную ошибку
        if category is None:
            raise CategoryNotFoundError(category_id)

        # Возвращаем найденную категорию
        return category

    async def update(
        self,
        category_id: int,
        payload: CategoryUpdate,
    ) -> Category:
        """Обновить категорию.

        Args:
            category_id: ID категории.
            payload: Данные частичного обновления.

        Returns:
            Обновлённая ORM-модель Category.

        Raises:
            CategoryNotFoundError: Если категория не найдена.
            CategoryNameAlreadyExistsError: Если новое имя уже занято.
        """

        # Получаем текущую категорию или падаем с доменной ошибкой
        category = await self.get_by_id(category_id)

        # Если меняется имя — проверяем уникальность нового имени
        if payload.name is not None and payload.name != category.name:
            existing_category = await self._repository.get_by_name(payload.name)

            # Если такое имя уже занято другой категорией — запрещаем обновление
            if existing_category is not None and existing_category.id != category.id:
                raise CategoryNameAlreadyExistsError(payload.name)

        # Обновляем категорию через repository
        return await self._repository.update(category, payload)

    async def delete(self, category_id: int) -> None:
        """Удалить категорию.

        Args:
            category_id: ID категории.

        Raises:
            CategoryNotFoundError: Если категория не найдена.
        """

        # Получаем категорию или падаем с доменной ошибкой
        category = await self.get_by_id(category_id)

        # Удаляем категорию через repository
        await self._repository.delete(category)