# ────────────────────────────────────────────────────────────────
# Путь: backend/tests/test_location_smoke.py
# Описание: Ручной smoke-test полного CRUD сценария Location API.
#           Проверяет:
#           - создание корневой локации
#           - создание дочерней локации
#           - получение списка локаций
#           - получение локации по id
#           - обновление дочерней локации
#           - запрет удаления родителя с дочерними локациями
#           - удаление дочерней локации
#           - удаление корневой локации
#           - проверку 404 после удаления
# ────────────────────────────────────────────────────────────────

"""Smoke-test сценарий для Location API проекта BardaK.

Назначение:
    Этот файл нужен как ручной быстрый регрессионный тест.
    Он проверяет, что backend, API-слой, service-слой, repository-слой
    и PostgreSQL работают вместе на полном CRUD-сценарии Location.

Что проверяется:
    - API умеет создавать корневую локацию.
    - API умеет создавать дочернюю локацию.
    - API возвращает список локаций.
    - API возвращает конкретную локацию по id.
    - API умеет обновлять локацию.
    - API запрещает удалить родителя, если у него есть дети.
    - API умеет удалить дочернюю локацию.
    - API умеет удалить корневую локацию после удаления детей.
    - API возвращает 404 для удалённой локации.

Перед запуском:
    1. Должен быть запущен PostgreSQL.
    2. Должны быть применены миграции Alembic.
    3. Должен быть запущен backend:
        uvicorn app.main:app --reload --port 8000

Запуск из папки backend:
    python .\\tests\\test_location_smoke.py
"""

from __future__ import annotations

# Импорт datetime нужен для создания уникальных имён тестовых локаций.
from datetime import datetime

# Импорт Any нужен для типизации произвольных JSON-ответов.
from typing import Any

# Импорт requests нужен для ручных HTTP-запросов к FastAPI backend.
import requests


# Базовый URL API для Location endpoints.
BASE_URL: str = "http://127.0.0.1:8000/api/v1/locations"

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
    """Запустить полный smoke-test сценарий Location API.

    Сценарий:
        1. Создать корневую локацию.
        2. Создать дочернюю локацию.
        3. Получить список локаций.
        4. Получить дочернюю локацию по id.
        5. Обновить дочернюю локацию.
        6. Проверить, что родителя нельзя удалить, пока есть ребёнок.
        7. Удалить дочернюю локацию.
        8. Удалить корневую локацию.
        9. Проверить, что удалённая корневая локация возвращает 404.

    Returns:
        None. Результат отображается в консоли.
    """

    # Создаём уникальный суффикс для имён.
    suffix: str = build_unique_suffix()

    # Формируем уникальное имя корневой локации.
    root_name: str = f"Smoke Кладовка {suffix}"

    # Формируем уникальное имя дочерней локации.
    child_name: str = f"Smoke Шкаф {suffix}"

    # Формируем имя дочерней локации после обновления.
    updated_child_name: str = f"{child_name} Updated"

    # =========================================================
    # ШАГ 1. Создание корневой локации.
    # =========================================================
    print_step("CREATE ROOT LOCATION")

    # Отправляем POST-запрос на создание корневой локации.
    response = requests.post(
        BASE_URL,
        json={
            "name": root_name,
            "location_type": "room",
            "description": "Корневая локация, созданная smoke-test.",
        },
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 201 Created.
    assert_status(response, 201)

    # Преобразуем JSON-ответ в словарь.
    root: dict[str, Any] = response.json()

    # Достаём id созданной корневой локации.
    root_id: int = root["id"]

    # Печатаем созданную корневую локацию.
    print_payload(root)

    # =========================================================
    # ШАГ 2. Создание дочерней локации.
    # =========================================================
    print_step("CREATE CHILD LOCATION")

    # Отправляем POST-запрос на создание дочерней локации.
    response = requests.post(
        BASE_URL,
        json={
            "name": child_name,
            "location_type": "wardrobe",
            "parent_id": root_id,
            "description": "Дочерняя локация, созданная smoke-test.",
        },
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 201 Created.
    assert_status(response, 201)

    # Преобразуем JSON-ответ в словарь.
    child: dict[str, Any] = response.json()

    # Достаём id созданной дочерней локации.
    child_id: int = child["id"]

    # Печатаем созданную дочернюю локацию.
    print_payload(child)

    # =========================================================
    # ШАГ 3. Получение списка локаций.
    # =========================================================
    print_step("LIST LOCATIONS")

    # Отправляем GET-запрос списка локаций.
    response = requests.get(
        BASE_URL,
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 200 OK.
    assert_status(response, 200)

    # Печатаем список локаций.
    print_payload(response.json())

    # =========================================================
    # ШАГ 4. Получение дочерней локации по id.
    # =========================================================
    print_step("GET CHILD LOCATION")

    # Отправляем GET-запрос конкретной дочерней локации.
    response = requests.get(
        f"{BASE_URL}/{child_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 200 OK.
    assert_status(response, 200)

    # Печатаем найденную дочернюю локацию.
    print_payload(response.json())

    # =========================================================
    # ШАГ 5. Обновление дочерней локации.
    # =========================================================
    print_step("PATCH CHILD LOCATION")

    # Отправляем PATCH-запрос на обновление дочерней локации.
    response = requests.patch(
        f"{BASE_URL}/{child_id}",
        json={
            "name": updated_child_name,
            "description": "Дочерняя локация обновлена smoke-test.",
        },
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 200 OK.
    assert_status(response, 200)

    # Преобразуем JSON-ответ в словарь.
    updated_child: dict[str, Any] = response.json()

    # Проверяем, что имя реально обновилось.
    if updated_child["name"] != updated_child_name:
        # Если имя не обновилось, падаем с понятной ошибкой.
        raise AssertionError(
            f"Имя дочерней локации не обновилось. Ответ: {updated_child}"
        )

    # Печатаем обновлённую дочернюю локацию.
    print_payload(updated_child)

    # =========================================================
    # ШАГ 6. Проверка запрета удаления родителя с детьми.
    # =========================================================
    print_step("DELETE ROOT WITH CHILD (EXPECT 409)")

    # Пытаемся удалить корневую локацию, пока у неё есть ребёнок.
    response = requests.delete(
        f"{BASE_URL}/{root_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 409 Conflict.
    assert_status(response, 409)

    # Печатаем ответ с ошибкой.
    print_payload(response.json())

    # =========================================================
    # ШАГ 7. Удаление дочерней локации.
    # =========================================================
    print_step("DELETE CHILD LOCATION")

    # Отправляем DELETE-запрос на удаление дочерней локации.
    response = requests.delete(
        f"{BASE_URL}/{child_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 204 No Content.
    assert_status(response, 204)

    # Печатаем статус удаления.
    print(f"STATUS CODE: {response.status_code}")

    # =========================================================
    # ШАГ 8. Удаление корневой локации.
    # =========================================================
    print_step("DELETE ROOT LOCATION")

    # Отправляем DELETE-запрос на удаление корневой локации.
    response = requests.delete(
        f"{BASE_URL}/{root_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 204 No Content.
    assert_status(response, 204)

    # Печатаем статус удаления.
    print(f"STATUS CODE: {response.status_code}")

    # =========================================================
    # ШАГ 9. Проверка 404 после удаления.
    # =========================================================
    print_step("GET DELETED ROOT LOCATION (EXPECT 404)")

    # Пробуем получить удалённую корневую локацию.
    response = requests.get(
        f"{BASE_URL}/{root_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Проверяем, что API вернул 404 Not Found.
    assert_status(response, 404)

    # Печатаем ответ с ошибкой.
    print_payload(response.json())

    # =========================================================
    # Финал.
    # =========================================================
    print_step("DONE")

    # Печатаем сообщение об успешном завершении теста.
    print("Location smoke-test completed successfully.")


# Проверяем, что файл запущен напрямую, а не импортирован.
if __name__ == "__main__":
    # Запускаем основной smoke-test сценарий.
    main()