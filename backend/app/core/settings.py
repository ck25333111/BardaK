#────────────────────────────────────────
# backend/app/core/settings.py
# Настройки приложения через pydantic-settings:
# - единый источник конфигурации
# - чтение env и backend/.env
# - валидация обязательных параметров на старте
#────────────────────────────────────────

"""Настройки приложения BardaK.

Задачи этого модуля:
- хранить все настройки в одном месте
- читать переменные окружения и backend/.env
- валидировать конфиг сразу при старте приложения
- не допускать размазывания os.getenv() по проекту
"""

from __future__ import annotations

#────────────────────────────────────────
# Импорты
#────────────────────────────────────────

# # Path нужен, чтобы жёстко и стабильно найти backend/.env
from pathlib import Path

# # lru_cache нужен, чтобы объект settings создавался один раз
from functools import lru_cache

# # Final для констант, Literal для ограничения допустимых значений APP_ENV
from typing import Final, Literal

# # Field описывает поля настроек
from pydantic import Field

# # BaseSettings и SettingsConfigDict дают чтение env/.env
from pydantic_settings import BaseSettings, SettingsConfigDict


#────────────────────────────────────────
# Константы
#────────────────────────────────────────

# # Дефолтный уровень логов
DEFAULT_LOG_LEVEL: Final[str] = "INFO"

# # Абсолютный путь до backend/.env
ENV_FILE_PATH: Final[Path] = Path(__file__).resolve().parents[2] / ".env"


#────────────────────────────────────────
# Основной класс настроек
#────────────────────────────────────────

class Settings(BaseSettings):
    """Единый источник настроек приложения.

    Правила:
    - настройки читаются из переменных окружения и файла backend/.env
    - обязательные параметры должны быть заданы явно
    - проект не использует os.getenv() напрямую в бизнес-коде
    """

    #────────────────────────────────────────
    # Конфиг pydantic-settings
    #────────────────────────────────────────

    model_config = SettingsConfigDict(
        # # Жёстко указываем путь до backend/.env,
        # # чтобы запуск работал одинаково из разных директорий
        env_file=str(ENV_FILE_PATH),

        # # Кодировка .env
        env_file_encoding="utf-8",

        # # APP_ENV и app_env считаем одинаковыми
        case_sensitive=False,

        # # Лишние переменные не должны ломать запуск
        extra="ignore",
    )

    #────────────────────────────────────────
    # Базовые настройки приложения
    #────────────────────────────────────────

    # # Среда запуска приложения
    app_env: Literal["dev", "test", "prod"] = Field(
        default="dev",
        alias="APP_ENV",
        description="Среда запуска приложения: dev/test/prod",
    )

    # # Уровень логирования
    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        alias="LOG_LEVEL",
        description="Уровень логирования: DEBUG/INFO/WARNING/ERROR",
    )

    #────────────────────────────────────────
    # Настройки БД
    #────────────────────────────────────────

    # # DATABASE_URL обязателен.
    # # Если его нет, приложение должно упасть сразу при старте.
    database_url: str = Field(
        alias="DATABASE_URL",
        description="DSN для БД. Ожидается формат: postgresql+asyncpg://...",
    )

    #────────────────────────────────────────
    # Удобные вычисляемые свойства
    #────────────────────────────────────────

    @property
    def is_prod(self) -> bool:
        """Проверить, запущено ли приложение в production.

        Returns:
            bool: True, если APP_ENV == "prod", иначе False.
        """
        # # Простая проверка окружения
        return self.app_env == "prod"

    @property
    def alembic_database_url(self) -> str:
        """Получить sync DSN для Alembic.

        Приложение использует asyncpg:
        - postgresql+asyncpg://...

        Для миграций Alembic удобнее использовать psycopg:
        - postgresql+psycopg://...

        Returns:
            str: строка подключения для Alembic.
        """
        # # Преобразуем asyncpg DSN в psycopg DSN для миграций
        return self.database_url.replace(
            "postgresql+asyncpg://",
            "postgresql+psycopg://",
        )


#────────────────────────────────────────
# Фабрика настроек
#────────────────────────────────────────

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Создать и вернуть единый экземпляр настроек.

    Почему через кэш:
    - настройки читаются один раз
    - все импорты получают один и тот же объект
    - нет лишнего повторного создания Settings()

    Returns:
        Settings: объект конфигурации приложения.

    Raises:
        ValueError: если DATABASE_URL имеет неверный формат.
    """
    # # Создаём объект настроек
    settings = Settings()

    # # Проверяем, что DSN подходит для async SQLAlchemy
    if not settings.database_url.startswith("postgresql+asyncpg://"):
        raise ValueError(
            "DATABASE_URL должен начинаться с 'postgresql+asyncpg://'. "
            "Пример: postgresql+asyncpg://user:pass@localhost:5432/bardak"
        )

    # # Возвращаем кэшируемый объект
    return settings