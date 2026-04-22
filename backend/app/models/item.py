# ────────────────────────────────────────────────────────────────
# Путь: backend/app/models/item.py
# Описание: ORM-модель Item.
#           Описывает предмет или группу одинаковых предметов,
#           находящихся в конкретной локации.
# ────────────────────────────────────────────────────────────────

"""ORM-модель предмета для проекта BardaK.

Идея модели:
- Item описывает предмет или группу одинаковых предметов
- предмет всегда относится к одной текущей локации
- предмет может быть привязан к категории
- часть полей остаётся optional, чтобы не перегружать ввод

Примеры:
- Отвёртка крестовая
- Кабель USB-C 2м
- Батарейки AAA
- Куртка зимняя
"""

from __future__ import annotations

# Импорт datetime для временных меток
from datetime import datetime

# Импорт SQLAlchemy типов и функций
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

# Импорт ORM-инструментов
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# Импорт базового класса ORM-моделей
from app.models.base import Base


class Item(Base):
    """ORM-модель предмета склада."""

    # Явное имя таблицы в БД
    __tablename__ = "items"

    # Первичный ключ
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Название предмета
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Текущая локация хранения предмета
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Необязательная категория предмета
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Необязательное описание предмета
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Количество одинаковых предметов в записи
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    # Состояние предмета
    condition: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Дополнительный комментарий
    comment: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Размеры предмета в миллиметрах
    width_mm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    depth_mm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height_mm: Mapped[int | None] = mapped_column(
        Integer,
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

    # ORM-связь на текущую локацию предмета
    location = relationship("Location")

    # ORM-связь на категорию предмета
    category = relationship(
        "Category",
        back_populates="items",
    )