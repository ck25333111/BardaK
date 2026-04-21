# ────────────────────────────────────────────────────────────────
# Путь: backend/alembic/env.py
# Описание: Конфигурация Alembic для миграций проекта BardaK.
#           Подключает настройки приложения и metadata ORM-моделей.
# ────────────────────────────────────────────────────────────────

"""Alembic environment configuration for BardaK."""

from __future__ import annotations

# Импорт Path для добавления backend в sys.path
from pathlib import Path

# Импорт sys для настройки путей импорта
import sys

# Импорт fileConfig для настройки логирования Alembic
from logging.config import fileConfig

# Импорт Alembic config/context
from alembic import context

# Импорт engine_from_config и pool для sync-подключения Alembic
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# ────────────────────────────────────────────────────────────────
# Добавляем backend в sys.path, чтобы работали импорты app.*
# ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Импорт настроек приложения
from app.core.settings import get_settings

# Импорт metadata всех моделей
from app.models import Base

# ────────────────────────────────────────────────────────────────
# Alembic config object
# ────────────────────────────────────────────────────────────────
config = context.config

# Настраиваем логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Получаем настройки приложения
settings = get_settings()

# Подставляем sync-URL для Alembic
config.set_main_option("sqlalchemy.url", settings.alembic_database_url)

# Metadata ORM-моделей для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запустить миграции в offline-режиме."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запустить миграции в online-режиме."""

    connectable = engine_from_config(
        configuration=config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()