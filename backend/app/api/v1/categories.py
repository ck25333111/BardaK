# ────────────────────────────────────────────────────────────────
# Путь: backend/app/api/v1/categories.py
# Описание: HTTP endpoints для сущности Category.
#           API-слой не содержит бизнес-логику.
# ────────────────────────────────────────────────────────────────

"""API v1 endpoints для Category.

Назначение:
- принять HTTP-запрос
- вызвать service-слой
- преобразовать доменные ошибки в HTTP-ответы
- вернуть Pydantic-схему наружу
"""

from __future__ import annotations

# Импорт FastAPI-инструментов
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status

# Импорт async SQLAlchemy session
from sqlalchemy.ext.asyncio import AsyncSession

# Импорт dependency получения DB-сессии
from app.db.session import get_session

# Импорт API-схем Category
from app.schemas.category import CategoryCreate
from app.schemas.category import CategoryRead
from app.schemas.category import CategoryUpdate

# Импорт доменных ошибок Category
from app.services.category.exceptions import CategoryNameAlreadyExistsError
from app.services.category.exceptions import CategoryNotFoundError

# Импорт service-слоя Category
from app.services.category.service import CategoryService


# Роутер категорий
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_session),
) -> CategoryRead:
    """Создать новую категорию.

    Args:
        payload: Данные для создания категории.
        session: Асинхронная DB-сессия.

    Returns:
        Созданная категория.
    """

    # Создаём service для сценария Category
    service = CategoryService(session)

    try:
        # Создаём категорию через service-слой
        category = await service.create(payload)

        # Возвращаем API-схему наружу
        return CategoryRead.model_validate(category)

    except CategoryNameAlreadyExistsError as error:
        # Дублирующееся имя категории — конфликт данных
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get("", response_model=list[CategoryRead])
async def get_categories(
    session: AsyncSession = Depends(get_session),
) -> list[CategoryRead]:
    """Получить список всех категорий.

    Args:
        session: Асинхронная DB-сессия.

    Returns:
        Список категорий.
    """

    # Создаём service для сценария Category
    service = CategoryService(session)

    # Получаем список категорий
    categories = await service.get_all()

    # Преобразуем ORM-объекты в Pydantic-схемы
    return [CategoryRead.model_validate(category) for category in categories]


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
) -> CategoryRead:
    """Получить категорию по id.

    Args:
        category_id: ID категории.
        session: Асинхронная DB-сессия.

    Returns:
        Найденная категория.
    """

    # Создаём service для сценария Category
    service = CategoryService(session)

    try:
        # Получаем категорию по id
        category = await service.get_by_id(category_id)

        # Возвращаем API-схему наружу
        return CategoryRead.model_validate(category)

    except CategoryNotFoundError as error:
        # Если категории нет — возвращаем 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
) -> CategoryRead:
    """Обновить категорию по id.

    Args:
        category_id: ID категории.
        payload: Данные частичного обновления.
        session: Асинхронная DB-сессия.

    Returns:
        Обновлённая категория.
    """

    # Создаём service для сценария Category
    service = CategoryService(session)

    try:
        # Обновляем категорию через service-слой
        category = await service.update(category_id, payload)

        # Возвращаем API-схему наружу
        return CategoryRead.model_validate(category)

    except CategoryNotFoundError as error:
        # Если категории нет — возвращаем 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except CategoryNameAlreadyExistsError as error:
        # Если имя уже занято — возвращаем 409
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Удалить категорию по id.

    Args:
        category_id: ID категории.
        session: Асинхронная DB-сессия.

    Returns:
        Пустой ответ 204.
    """

    # Создаём service для сценария Category
    service = CategoryService(session)

    try:
        # Удаляем категорию через service-слой
        await service.delete(category_id)

        # Возвращаем пустой успешный ответ
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except CategoryNotFoundError as error:
        # Если категории нет — возвращаем 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error