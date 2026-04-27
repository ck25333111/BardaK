# ────────────────────────────────────────────────────────────────
# Путь: backend/app/models/location.py
# Описание: ORM-модель Location.
#           Описывает универсальный узел хранения:
#           дом, комнату, шкаф, секцию, ящик, полку, ячейку и т.д.
# ────────────────────────────────────────────────────────────────

"""ORM-модель места хранения для проекта BardaK.

Идея модели:
- Location — это универсальная сущность хранения
- одна и та же модель описывает любой физический узел хранения
- вложенность строится через self-reference по parent_id

Примеры:
- Дом
- Спальня
- Стол
- Ящик 1
- Ячейка A1
- Шкаф
- Верхний отсек
"""

from __future__ import annotations

# Импорт datetime для хранения временных меток записи
from datetime import datetime

# Импорт функций и типов SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# Импорт базового класса всех ORM-моделей проекта
from app.models.base import Base


class Location(Base):
    """ORM-модель универсального места хранения.

    Назначение:
    - хранить любую структуру мест хранения в виде дерева
    - позволять описывать мебель и вложенные контейнеры
    - быть фундаментом для дальнейшей привязки предметов

    Важно:
    - сама модель описывает только узел дерева
    - параметры внутренней раскладки будут вынесены
      в отдельную сущность LocationLayout

    Примеры узлов:
    - дом
    - комната
    - шкаф
    - секция
    - ящик
    - полка
    - ячейка
    - коробка
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
    # - "house"
    # - "room"
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
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Ширина места хранения в миллиметрах.
    # Пока nullable, потому что не для всех узлов размеры
    # будут известны на старте.
    width_mm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Глубина места хранения в миллиметрах.
    depth_mm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Высота места хранения в миллиметрах.
    height_mm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Необязательное текстовое описание.
    # Можно хранить заметки:
    # - "верхние ячейки длиннее нижних"
    # - "внутри стоят перегородки"
    description: Mapped[str | None] = mapped_column(
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

    # Время последнего обновления записи.
    # Обновляется на стороне БД автоматически при изменении строки.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ORM-ссылка на родительский узел дерева.
    # Нужна для удобной навигации вверх по иерархии.
    parent: Mapped[Location | None] = relationship(
        "Location",
        remote_side="Location.id",
        back_populates="children",
    )

    # ORM-ссылка на дочерние узлы дерева.
    # Нужна для построения структуры хранения вниз по иерархии.
    children: Mapped[list[Location]] = relationship(
        "Location",
        back_populates="parent",
    )