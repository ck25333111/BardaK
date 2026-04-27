# ────────────────────────────────────────────────────────────────
# Путь: backend/app/models/category.py
# Описание: ORM-модель Category.
#           Описывает категорию предметов для группировки Item.
# ────────────────────────────────────────────────────────────────

"""ORM-модель категории предметов для проекта BardaK."""

from __future__ import annotations

# Импорт datetime для временных меток
from datetime import datetime

# Импорт SQLAlchemy типов и функций
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

# Импорт ORM-инструментов
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# Импорт базового класса ORM-моделей
from app.models.base import Base


class Category(Base):
    """ORM-модель категории предметов."""

    # Явное имя таблицы в БД
    __tablename__ = "categories"

    # Первичный ключ
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Название категории
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # Необязательное описание категории
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Время создания записи
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Время последнего обновления записи
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Обратная ORM-связь на предметы этой категории
    items = relationship(
        "Item",
        back_populates="category",
    )