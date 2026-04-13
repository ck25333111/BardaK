# ────────────────────────────────────────────────────────────────
# Путь: backend/app/models/location.py
# Описание: ORM-модель Location.
#           Описывает универсальный узел хранения:
#           мебель, секцию, ящик, ячейку, полку, коробку и т.д.
# ────────────────────────────────────────────────────────────────

"""ORM-модель места хранения для проекта BardaK.

Идея модели:
- Location — это универсальная сущность хранения
- одна и та же модель описывает шкаф, стол, ящик, ячейку, полку и т.д.
- вложенность строится через parent_id

Примеры:
- Стол
- Ящик 1
- Ячейка A1
- Шкаф
- Верхний отсек
"""

from __future__ import annotations

# Импорт datetime для хранения времени создания записи
from datetime import datetime

# Импорт Optional для nullable-ссылок
from typing import Optional

# Импорт функций и типов SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# Импорт базового класса всех ORM-моделей проекта
from app.models.base import Base


class Location(Base):
    """ORM-модель универсального места хранения.

    Назначение:
    - хранить любую структуру мест хранения в виде дерева
    - позволять описывать мебель и вложенные контейнеры
    - быть фундаментом для дальнейшей привязки предметов

    Примеры узлов:
    - шкаф
    - секция
    - ящик
    - ячейка
    - коробка
    - полка
    """

    # Явное имя таблицы в БД
    __tablename__ = "locations"

    # Первичный ключ записи
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Человекочитаемое имя места хранения
    # Примеры:
    # - "Стол"
    # - "Ящик 1"
    # - "Ячейка A1"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Тип узла хранения.
    # Пока строкой, без Enum, чтобы не зацементировать
    # набор значений слишком рано.
    # Примеры:
    # - "table"
    # - "drawer"
    # - "cell"
    # - "wardrobe"
    # - "shelf"
    location_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Ссылка на родительский Location.
    # Нужна для построения дерева хранения.
    # Если parent_id = None, значит это корневой узел.
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Ширина места хранения в миллиметрах.
    # Пока nullable, потому что не для всех узлов размеры
    # будут известны на старте.
    width_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Глубина места хранения в миллиметрах.
    depth_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Высота места хранения в миллиметрах.
    height_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Необязательное текстовое описание.
    # Можно хранить заметки:
    # - "верхние ячейки длиннее нижних"
    # - "внутри стоят перегородки"
    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Время создания записи.
    # Выставляется на стороне БД автоматически.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )