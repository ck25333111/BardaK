# ────────────────────────────────────────────────────────────────
# Путь: backend/tests/test_category_smoke.py
# Описание: Ручной smoke-test полного CRUD сценария Category API.
#           Проверяет:
#           - создание категории
#           - запрет создания дубля по имени
#           - получение списка категорий
#           - получение категории по id
#           - обновление категории
#           - запрет обновления имени на уже занятое
#           - удаление категории
#           - проверку 404 после удаления
# ────────────────────────────────────────────────────────────────

"""Smoke-test сценарий для Category API проекта BardaK.

Назначение:
    Этот файл нужен как ручной быстрый регрессионный тест.
    Он проверяет, что backend, API-слой, service-слой, repository-слой
    и PostgreSQL работают вместе на полном CRUD-сценарии Category.

Что проверяется:
    - API умеет создавать категорию.
    - API запрещает создать категорию с повторяющимся именем.
    - API возвращает список категорий.
    - API возвращает конкретную категорию по id.
    - API умеет обновлять категорию.
    - API запрещает обновить категорию на имя, которое уже занято.
    - API умеет удалить категорию.
    - API возвращает 404 для удалённой категории.

Перед запуском:
    1. Должен быть запущен PostgreSQL.
    2. Должны быть применены миграции Alembic.
    3. Должен быть запущен backend:
        uvicorn app.main:app --reload --port 8000

Запуск из папки backend:
    python .\\tests\\test_category_smoke.py
"""

from __future__ import annotations

# Импорт datetime нужен для создания уникальных имён тестовых категорий.
from datetime import datetime

# Импорт Any нужен для типизации произвольных JSON-ответов.
from typing import Any

# Импорт requests нужен для ручных HTTP-запросов к FastAPI backend.
import requests


# Базовый URL API для Category endpoints.
BASE_URL: str = "http://127.0.0.1:8000/api/v1/categories"

# Таймаут каждого HTTP-запроса в секундах.
TIMEOUT_SECONDS: int = 5


def print_step(title: str) -> None:
    """Вывести красивый заголовок текущего шага smoke-test.

    Args:
        title: Название текущего этапа проверки.

    Returns:
        None. Функция только печатает текст в консоль.
    """

    # Печатаем пустую строку и заголовок шага для читаемости вывода.
    print(f"\n=== {title} ===")


def print_payload(payload: Any) -> None:
    """Вывести полезную нагрузку ответа API.

    Args:
        payload: Любой объект, который надо показать в консоли.

    Returns:
        None. Функция только печатает данные.
    """

    # Печатаем тело ответа или любой другой объект диагностики.
    print(payload)


def assert_status(
    response: requests.Response,
    expected_status_code: int,
) -> None:
    """Проверить, что HTTP-ответ имеет ожидаемый статус.

    Args:
        response: HTTP-ответ библиотеки requests.
        expected_status_code: Ожидаемый HTTP status code.

    Raises:
        AssertionError: Если фактический HTTP-код отличается от ожидаемого.

    Returns:
        None. Если статус корректный, функция ничего не возвращает.
    """

    # Проверяем, совпадает ли фактический HTTP-код с ожидаемым.
    if response.status_code != expected_status_code:
        # Если код не совпал, падаем с подробной ошибкой.
        raise AssertionError(
            f"Ожидался HTTP {expected_status_code}, "
            f"получен HTTP {response.status_code}. "
            f"Ответ: {response.text}"
        )


def build_unique_suffix() -> str:
    """Собрать уникальный суффикс для тестовых данных.

    Returns:
        Строка с timestamp, чтобы тестовые имена не конфликтовали
        с прошлыми запусками smoke-test.
    """

    # Формируем timestamp до секунд.
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def main() -> None:
    """Запустить полный smoke-test сценарий Category API.

    Сценарий:
        1. Создать основную категорию.
        2. Проверить запрет дубля по имени.
        3. Создать вторую категорию для проверки конфликта обновления.
        4. Получить список категорий.
        5. Получить основную категорию по id.
        6. Обновить основную категорию.
        7. Проверить запрет обновления на уже занятое имя.
        8. Удалить основную категорию.
        9. Проверить 404 после удаления.
        10. Удалить вторую категорию, созданную для теста конфликта.

    Returns:
        None. Результат отображается в консоли.
    """

    # Создаём уникальный суффикс для имён.
    suffix: str = build_unique_suffix()

    # Формируем уникальное имя основной категории.
    category_name: str = f"Smoke Category {suffix}"

    # Формируем уникальное имя после обновления основной категории.
    updated_category_name: str = f"{category_name} Updated"

    # Формируем имя второй категории для проверки конфликта имени.
    second_category_name: str = f"Smoke Category Conflict {suffix}"

    # Переменная для id основной категории.
    category_id: int | None = None

    # Переменная для id второй категории.
    second_category_id: int | None = None

    try:
        # =====================================================
        # ШАГ 1. Создание основной категории.
        # =====================================================
        print_step("CREATE CATEGORY")

        # Отправляем POST-запрос на создание категории.
        response = requests.post(
            BASE_URL,
            json={
                "name": category_name,
                "description": "Категория создана smoke-test сценарием.",
            },
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 201 Created.
        assert_status(response, 201)

        # Преобразуем JSON-ответ в словарь.
        category: dict[str, Any] = response.json()

        # Сохраняем id созданной категории.
        category_id = category["id"]

        # Печатаем созданную категорию.
        print_payload(category)

        # =====================================================
        # ШАГ 2. Проверка запрета дубля по имени.
        # =====================================================
        print_step("CREATE DUPLICATE CATEGORY (EXPECT 409)")

        # Отправляем POST-запрос с тем же именем категории.
        response = requests.post(
            BASE_URL,
            json={
                "name": category_name,
                "description": "Дубль категории, который должен быть запрещён.",
            },
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 409 Conflict.
        assert_status(response, 409)

        # Печатаем ответ с ошибкой.
        print_payload(response.json())

        # =====================================================
        # ШАГ 3. Создание второй категории для проверки конфликта.
        # =====================================================
        print_step("CREATE SECOND CATEGORY FOR NAME CONFLICT TEST")

        # Отправляем POST-запрос на создание второй категории.
        response = requests.post(
            BASE_URL,
            json={
                "name": second_category_name,
                "description": "Вторая категория для проверки конфликта имени.",
            },
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 201 Created.
        assert_status(response, 201)

        # Преобразуем JSON-ответ в словарь.
        second_category: dict[str, Any] = response.json()

        # Сохраняем id второй категории.
        second_category_id = second_category["id"]

        # Печатаем вторую категорию.
        print_payload(second_category)

        # =====================================================
        # ШАГ 4. Получение списка категорий.
        # =====================================================
        print_step("LIST CATEGORIES")

        # Отправляем GET-запрос списка категорий.
        response = requests.get(
            BASE_URL,
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 200 OK.
        assert_status(response, 200)

        # Печатаем список категорий.
        print_payload(response.json())

        # =====================================================
        # ШАГ 5. Получение основной категории по id.
        # =====================================================
        print_step("GET CATEGORY")

        # Отправляем GET-запрос основной категории.
        response = requests.get(
            f"{BASE_URL}/{category_id}",
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 200 OK.
        assert_status(response, 200)

        # Печатаем найденную категорию.
        print_payload(response.json())

        # =====================================================
        # ШАГ 6. Обновление основной категории.
        # =====================================================
        print_step("PATCH CATEGORY")

        # Отправляем PATCH-запрос на обновление основной категории.
        response = requests.patch(
            f"{BASE_URL}/{category_id}",
            json={
                "name": updated_category_name,
                "description": "Категория обновлена smoke-test сценарием.",
            },
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 200 OK.
        assert_status(response, 200)

        # Преобразуем JSON-ответ в словарь.
        updated_category: dict[str, Any] = response.json()

        # Проверяем, что имя реально обновилось.
        if updated_category["name"] != updated_category_name:
            # Если имя не обновилось, падаем с понятной ошибкой.
            raise AssertionError(
                f"Имя категории не обновилось. Ответ: {updated_category}"
            )

        # Печатаем обновлённую категорию.
        print_payload(updated_category)

        # =====================================================
        # ШАГ 7. Проверка запрета обновления на занятое имя.
        # =====================================================
        print_step("PATCH CATEGORY NAME TO EXISTING NAME (EXPECT 409)")

        # Пытаемся переименовать основную категорию в имя второй категории.
        response = requests.patch(
            f"{BASE_URL}/{category_id}",
            json={
                "name": second_category_name,
            },
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 409 Conflict.
        assert_status(response, 409)

        # Печатаем ответ с ошибкой.
        print_payload(response.json())

        # =====================================================
        # ШАГ 8. Удаление основной категории.
        # =====================================================
        print_step("DELETE CATEGORY")

        # Отправляем DELETE-запрос на удаление основной категории.
        response = requests.delete(
            f"{BASE_URL}/{category_id}",
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 204 No Content.
        assert_status(response, 204)

        # Печатаем статус удаления.
        print(f"STATUS CODE: {response.status_code}")

        # =====================================================
        # ШАГ 9. Проверка 404 после удаления.
        # =====================================================
        print_step("GET DELETED CATEGORY (EXPECT 404)")

        # Пробуем получить удалённую категорию.
        response = requests.get(
            f"{BASE_URL}/{category_id}",
            timeout=TIMEOUT_SECONDS,
        )

        # Проверяем, что API вернул 404 Not Found.
        assert_status(response, 404)

        # Печатаем ответ с ошибкой.
        print_payload(response.json())

        # =====================================================
        # Финал.
        # =====================================================
        print_step("DONE")

        # Печатаем сообщение об успешном завершении теста.
        print("Category smoke-test completed successfully.")

    finally:
        # =====================================================
        # CLEANUP. Удаление второй категории, если она осталась.
        # =====================================================

        # Проверяем, была ли создана вторая категория.
        if second_category_id is not None:
            # Отправляем DELETE-запрос для очистки второй категории.
            cleanup_response = requests.delete(
                f"{BASE_URL}/{second_category_id}",
                timeout=TIMEOUT_SECONDS,
            )

            # Если вторая категория уже удалена или не найдена, это не ошибка.
            if cleanup_response.status_code not in {204, 404}:
                # Если пришёл неожиданный статус, показываем предупреждение.
                print(
                    "WARNING: не удалось удалить вторую тестовую категорию. "
                    f"STATUS={cleanup_response.status_code}, "
                    f"BODY={cleanup_response.text}"
                )


# Проверяем, что файл запущен напрямую, а не импортирован.
if __name__ == "__main__":
    # Запускаем основной smoke-test сценарий.
    main()