# ────────────────────────────────────────────────────────────────
# Путь: backend/app/repositories/category_repository.py
# Описание: Repository-слой для сущности Category.
#           Содержит только операции доступа к данным без
#           бизнес-логики и HTTP-логики.
# ────────────────────────────────────────────────────────────────

"""Repository для работы с Category в проекте BardaK.

Назначение:
- инкапсулировать SQLAlchemy-запросы к таблице categories
- отделить доступ к данным от service-слоя
- дать предсказуемый API для CRUD-операций

Важно:
- repository не содержит бизнес-правил
- repository не работает с HTTP-слоем
- repository не принимает решений о сценариях приложения
"""

from __future__ import annotations

# Импорт последовательностей для типизации списков результатов
from collections.abc import Sequence

# Импорт SQLAlchemy-запросов
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Импорт ORM-модели Category
from app.models.category import Category

# Импорт Pydantic-схем
from app.schemas.category import CategoryCreate
from app.schemas.category import CategoryUpdate


class CategoryRepository:
    """Repository для доступа к данным Category."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализировать repository.

        Args:
            session: Асинхронная SQLAlchemy-сессия.
        """

        # Сохраняем сессию для запросов к БД
        self._session = session

    async def create(self, payload: CategoryCreate) -> Category:
        """Создать новую категорию.

        Args:
            payload: Данные для создания категории.

        Returns:
            Созданная ORM-модель Category.
        """

        # Создаём ORM-объект из входной схемы
        category = Category(**payload.model_dump())

        # Добавляем объект в текущую сессию
        self._session.add(category)

        # Сохраняем изменения в БД
        await self._session.commit()

        # Обновляем объект, чтобы получить id и timestamps
        await self._session.refresh(category)

        # Возвращаем созданную категорию
        return category

    async def get_all(self) -> Sequence[Category]:
        """Получить список всех категорий.

        Returns:
            Последовательность ORM-моделей Category.
        """

        # Формируем SELECT-запрос с сортировкой по id
        statement = select(Category).order_by(Category.id)

        # Выполняем запрос
        result = await self._session.execute(statement)

        # Возвращаем ORM-объекты
        return result.scalars().all()

    async def get_by_id(self, category_id: int) -> Category | None:
        """Получить категорию по id.

        Args:
            category_id: ID категории.

        Returns:
            Category, если запись найдена, иначе None.
        """

        # Формируем SELECT-запрос по первичному ключу
        statement = select(Category).where(Category.id == category_id)

        # Выполняем запрос
        result = await self._session.execute(statement)

        # Возвращаем один объект или None
        return result.scalar_one_or_none()
    

    async def get_by_name(self, name: str) -> Category | None:
        """Получить категорию по названию.

        Args:
            name: Название категории.

        Returns:
            Category, если запись найдена, иначе None.
        """

        # Формируем SELECT-запрос по уникальному имени категории
        statement = select(Category).where(Category.name == name)

        # Выполняем запрос
        result = await self._session.execute(statement)

        # Возвращаем одну запись или None
        return result.scalar_one_or_none()


    async def update(
        self,
        category: Category,
        payload: CategoryUpdate,
    ) -> Category:
        """Обновить категорию.

        Args:
            category: ORM-объект категории.
            payload: Данные частичного обновления.

        Returns:
            Обновлённая ORM-модель Category.
        """

        # Берём только реально переданные поля PATCH-запроса
        update_data = payload.model_dump(exclude_unset=True)

        # Применяем изменения к ORM-объекту
        for field_name, field_value in update_data.items():
            setattr(category, field_name, field_value)

        # Сохраняем изменения в БД
        await self._session.commit()

        # Обновляем объект из БД
        await self._session.refresh(category)

        # Возвращаем обновлённую категорию
        return category

    async def delete(self, category: Category) -> None:
        """Удалить категорию.

        Args:
            category: ORM-объект категории для удаления.
        """

        # Помечаем объект на удаление
        await self._session.delete(category)

        # Фиксируем удаление в БД
        await self._session.commit()