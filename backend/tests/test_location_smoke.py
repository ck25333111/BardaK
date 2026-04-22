# ────────────────────────────────────────────────────────────────
# Путь: backend/tests/test_location_smoke.py
# Описание: Ручной smoke-test полного CRUD сценария Location API.
#           Проверяет:
#           - создание корневой локации
#           - создание дочерней локации
#           - получение списка
#           - обновление записи
#           - запрет удаления родителя с детьми
#           - удаление ребёнка
#           - удаление родителя
# ────────────────────────────────────────────────────────────────

"""Smoke-test сценарий для Location API проекта BardaK.

Назначение:
- быстро проверить вертикальный срез системы после изменений
- убедиться, что backend + БД работают вместе
- использовать как ручной регрессионный тест

Запуск:
    python .\tests\test_location_smoke.py
"""

from __future__ import annotations

# Импорт HTTP-клиента для запросов к FastAPI backend
import requests

# Импорт типов для читаемости
from typing import Any


# Базовый URL endpoints локаций
BASE_URL: str = "http://127.0.0.1:8000/api/v1/locations"

# Таймаут каждого HTTP-запроса в секундах
TIMEOUT_SECONDS: int = 5


def print_step(title: str) -> None:
    """Вывести красивый заголовок шага теста.

    Args:
        title: Название текущего этапа проверки.
    """

    # Пустая строка + заголовок блока
    print(f"\n=== {title} ===")


def print_payload(payload: Any) -> None:
    """Вывести полезную нагрузку ответа.

    Args:
        payload: Любой JSON-объект ответа.
    """

    # Печать содержимого ответа
    print(payload)


def main() -> None:
    """Запустить полный smoke-test сценарий Location API."""

    # =========================================================
    # ШАГ 1. Создание корневой локации
    # =========================================================
    print_step("CREATE ROOT")

    # POST запрос на создание корневой сущности
    response = requests.post(
        BASE_URL,
        json={
            "name": "Кладовка",
            "location_type": "room",
        },
        timeout=TIMEOUT_SECONDS,
    )

    # Если ошибка HTTP — аварийно завершить тест
    response.raise_for_status()

    # Получаем JSON ответа
    root: dict[str, Any] = response.json()

    # Сохраняем id созданной записи
    root_id: int = root["id"]

    # Выводим ответ
    print_payload(root)

    # =========================================================
    # ШАГ 2. Создание дочерней локации
    # =========================================================
    print_step("CREATE CHILD")

    # POST запрос на создание дочерней записи
    response = requests.post(
        BASE_URL,
        json={
            "name": "Шкаф",
            "location_type": "wardrobe",
            "parent_id": root_id,
        },
        timeout=TIMEOUT_SECONDS,
    )

    # Проверка успешного ответа
    response.raise_for_status()

    # Получаем JSON
    child: dict[str, Any] = response.json()

    # Сохраняем id дочерней записи
    child_id: int = child["id"]

    # Выводим ответ
    print_payload(child)

    # =========================================================
    # ШАГ 3. Получение списка всех локаций
    # =========================================================
    print_step("LIST")

    # GET запрос списка
    response = requests.get(
        BASE_URL,
        timeout=TIMEOUT_SECONDS,
    )

    # Проверка ответа
    response.raise_for_status()

    # Вывод списка
    print_payload(response.json())

    # =========================================================
    # ШАГ 4. Обновление дочерней записи
    # =========================================================
    print_step("PATCH CHILD")

    # PATCH запрос изменения имени
    response = requests.patch(
        f"{BASE_URL}/{child_id}",
        json={
            "name": "Большой шкаф",
        },
        timeout=TIMEOUT_SECONDS,
    )

    # Проверка ответа
    response.raise_for_status()

    # Вывод обновлённой записи
    print_payload(response.json())

    # =========================================================
    # ШАГ 5. Проверка запрета удаления родителя с детьми
    # =========================================================
    print_step("DELETE ROOT WITH CHILD (EXPECT ERROR)")

    # Пытаемся удалить родителя пока есть ребёнок
    response = requests.delete(
        f"{BASE_URL}/{root_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Выводим код ответа
    print(f"STATUS CODE: {response.status_code}")

    # Выводим тело ответа
    print_payload(response.text)

    # =========================================================
    # ШАГ 6. Удаление дочерней записи
    # =========================================================
    # print_step("DELETE CHILD")

    # Удаляем ребёнка
    response = requests.delete(
        f"{BASE_URL}/{child_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Ожидаем успешное удаление
    print(f"STATUS CODE: {response.status_code}")

    # =========================================================
    # ШАГ 7. Удаление родительской записи
    # =========================================================
    # print_step("DELETE ROOT")

    # Теперь родителя можно удалить
    response = requests.delete(
        f"{BASE_URL}/{root_id}",
        timeout=TIMEOUT_SECONDS,
    )

    # Код успешного удаления
    print(f"STATUS CODE: {response.status_code}")

    # =========================================================
    # Финал
    # =========================================================
    print_step("DONE")

    # Сообщение о завершении
    print("Smoke-test completed successfully.")


# Точка входа при прямом запуске файла
if __name__ == "__main__":
    # Запускаем сценарий
    main()