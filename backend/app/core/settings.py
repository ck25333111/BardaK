#────────────────────────────────────────
# backend/app/core/settings.py
# Настройки приложения (env/.env) через pydantic-settings.
#────────────────────────────────────────

"""Модуль настроек приложения.

- все конфиги в одном месте (а не os.getenv() по всему проекту)
- типы и валидация (чтобы ловить херню сразу при старте)
- загрузка из .env без костылей

"""

#────────────────────────────────────────
# Импорты
#────────────────────────────────────────

from __future__ import annotations  # noqa: D401 
from pathlib import Path
from functools import lru_cache  # # кэшируем settings(), чтобы не пересоздавать объект на каждый импорт
from typing import Final, Literal  # # Literal — чтобы ограничить APP_ENV; Final — константы

from pydantic import Field  # # Field — задаём дефолты/описания/алиасы
from pydantic_settings import BaseSettings, SettingsConfigDict  # # BaseSettings читает env/.env автоматически


#────────────────────────────────────────
# Константы
#────────────────────────────────────────

DEFAULT_LOG_LEVEL: Final[str] = "INFO"  # # дефолтный уровень логов (можно переопределить через env)


#────────────────────────────────────────
# Settings: единый источник конфигурации
#────────────────────────────────────────

class Settings(BaseSettings):
    """Главный контейнер настроек приложения.

    ВАЖНО:
    - Это единственный источник правды по конфигу.
    - Никаких os.getenv() в роутерах/сервисах/репозиториях.
    - Настройки читаются из env + backend/.env.
    """

    #────────────────────────────────────────
    # Конфиг pydantic-settings (как читать .env и env)
    #────────────────────────────────────────

    model_config = SettingsConfigDict(
        # # ЖЁСТКО указываем путь к backend/.env, чтобы не зависеть от того,
        # # откуда ты запускаешь uvicorn (из корня проекта или из backend).
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",  # # кодировка файла .env
        case_sensitive=False,       # # APP_ENV и app_env — считаем одинаковыми (удобно)
        extra="ignore",             # # лишние ключи в .env не ломают запуск
    )

    #────────────────────────────────────────
    # Базовые параметры приложения
    #────────────────────────────────────────

    app_env: Literal["dev", "test", "prod"] = Field(
        default="dev",               # # дефолт: dev (удобно локально)
        alias="APP_ENV",             # # имя переменной окружения
        description="Среда запуска приложения: dev/test/prod",  # # для читаемости
    )

    log_level: str = Field(
        default="INFO",              # # дефолтный уровень логов (безопасный)
        alias="LOG_LEVEL",           # # переменная окружения
        description="Уровень логирования: DEBUG/INFO/WARNING/ERROR",  # # подсказка
    )

    #────────────────────────────────────────
    # База данных
    #────────────────────────────────────────

    database_url: str = Field(
        # # ВАЖНО: тут НЕТ default="" — значит поле ОБЯЗАТЕЛЬНОЕ.
        # # Если DATABASE_URL не задан, pydantic-settings кинет ошибку уже на старте.
        alias="DATABASE_URL",        # # переменная окружения
        description="DSN для БД (ОЖИДАЕМ: postgresql+asyncpg://...)",  # # ожидаемый формат
    )

    #────────────────────────────────────────
    # Удобные хелперы (свойства)
    #────────────────────────────────────────

    @property
    def is_prod(self) -> bool:
        """Проверка: это прод?

        Returns:
            bool: True если APP_ENV=prod, иначе False.
        """
        return self.app_env == "prod"  # # простая проверка среды

    @property
    def alembic_database_url(self) -> str:
        """DSN для Alembic (синхронный).

        Почему так:
        - Alembic часто гоняют синхронно.
        - Приложение использует asyncpg.
        - Поэтому для миграций меняем asyncpg -> psycopg.

        Returns:
            str: строка подключения для миграций.
        """
        # # Преобразуем asyncpg -> psycopg (psycopg3)
        # # Пример:
        # # postgresql+asyncpg://... -> postgresql+psycopg://...
        return self.database_url.replace(
            "postgresql+asyncpg://",  # # что заменяем
            "postgresql+psycopg://",  # # на что заменяем
        )
    """Главный контейнер настроек приложения.

    ВАЖНО:
    - Это единственный источник правды по конфигу.
    - Никаких os.getenv() в роутерах/сервисах/репозиториях.
    """

    #────────────────────────────────────────
    # Конфиг pydantic-settings (как читать .env и env)
    #────────────────────────────────────────

    model_config = SettingsConfigDict(
        env_file=".env",               # # файл окружения (в корне backend/ обычно)
        env_file_encoding="utf-8",      # # кодировка .env
        case_sensitive=False,           # # APP_ENV и app_env — одно и то же (удобно на разных ОС)
        extra="ignore",                # # если в .env есть лишние ключи — не падаем
    )

    #────────────────────────────────────────
    # Базовые параметры приложения
    #────────────────────────────────────────

    app_env: Literal["dev", "test", "prod"] = Field(
        default="dev",                 # # дефолт: dev
        alias="APP_ENV",               # # имя переменной окружения
        description="Среда запуска приложения: dev/test/prod",  # # чисто для читаемости/доков
    )

    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,     # # дефолтный уровень логов
        alias="LOG_LEVEL",             # # переменная окружения
        description="Уровень логирования: DEBUG/INFO/WARNING/ERROR",  # # подсказка
    )

    #────────────────────────────────────────
    # База данных
    #────────────────────────────────────────

    database_url: str = Field(
        default="",                    # # пусто по умолчанию, чтобы не “случайно подключиться” неизвестно куда
        alias="DATABASE_URL",          # # переменная окружения
        description="DSN для БД (ОЖИДАЕМ: postgresql+asyncpg://...)",  # # ожидаемый формат
    )

    #────────────────────────────────────────
    # Удобные хелперы (свойства)
    #────────────────────────────────────────

    @property
    def is_prod(self) -> bool:
        """Проверка: это прод?

        Returns:
            bool: True если APP_ENV=prod, иначе False.
        """
        return self.app_env == "prod"  # # простая проверка среды

    @property
    def alembic_database_url(self) -> str:
        """DSN для Alembic (синхронный).

        Почему так:
        - Alembic по умолчанию работает синхронно.
        - Мы в приложении используем asyncpg, но миграции часто проще гонять синхронно.

        Как делаем:
        - если DSN вида postgresql+asyncpg://..., превращаем в postgresql+psycopg://...
        - если DSN уже синхронный — возвращаем как есть

        Returns:
            str: строка подключения для миграций.
        """
        # # если пользователь вообще не задал DATABASE_URL — отдаём пустую строку (потом упадём с понятной ошибкой)
        if not self.database_url:
            return ""

        # # преобразуем asyncpg -> psycopg (psycopg3)
        return self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")


#────────────────────────────────────────
# Factory: единый экземпляр настроек
#────────────────────────────────────────

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Вернуть единый экземпляр Settings (кэшируем).

    Зачем кэш:
    - настройки читаются один раз
    - любые импорты get_settings() получают один и тот же объект

    Returns:
        Settings: объект настроек приложения.
    """
    settings = Settings()  # # создаём settings (pydantic-settings сам прочитает env/.env)
    # # минимальная валидация руками: убеждаемся, что DSN под async SQLAlchemy правильный
    if settings.database_url and not settings.database_url.startswith("postgresql+asyncpg://"):
        # # падаем сразу при старте — лучше, чем ловить странные ошибки при подключении к БД
        raise ValueError(
            "DATABASE_URL должен начинаться с 'postgresql+asyncpg://'. "
            "Пример: postgresql+asyncpg://user:pass@localhost:5432/bardak"
        )
    return settings  # # отдаём кэшируемый объект