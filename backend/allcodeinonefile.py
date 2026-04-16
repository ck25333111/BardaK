# ────────────────────────────────────────────────────────────────
# Путь: tools/export_backend_project_snapshot.py
# Описание: Скрипт рекурсивно обходит директорию проекта, собирает
#           содержимое текстовых файлов с кодом и сохраняет всё
#           в один итоговый файл для анализа архитектуры проекта.
# ────────────────────────────────────────────────────────────────

from __future__ import annotations

# Импорт стандартного парсера аргументов командной строки
import argparse

# Импорт fnmatch для фильтрации файлов по маскам
import fnmatch

# Импорт pathlib для удобной и безопасной работы с путями
from pathlib import Path

# Импорт typing для аннотаций типов контейнеров
from typing import Iterable


# ────────────────────────────────────────────────────────────────
# Набор директорий, которые обычно не нужны при экспорте проекта
# ────────────────────────────────────────────────────────────────
DEFAULT_IGNORED_DIRS: set[str] = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".eggs",
    ".next",
    ".nuxt",
    "coverage",
    ".coverage",
    ".cache",
}


# ────────────────────────────────────────────────────────────────
# Набор расширений файлов, которые по умолчанию считаем полезными
# для анализа архитектуры и логики проекта
# ────────────────────────────────────────────────────────────────
DEFAULT_ALLOWED_EXTENSIONS: set[str] = {
    ".py",
    ".pyi",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".env",
    ".sql",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".xml",
    ".sh",
    ".bat",
    ".ps1",
    ".dockerfile",
}


# ────────────────────────────────────────────────────────────────
# Маски имён файлов, которые обычно тоже не нужны в выгрузке
# ────────────────────────────────────────────────────────────────
DEFAULT_IGNORED_FILE_PATTERNS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.exe",
    "*.bin",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.pdf",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.7z",
    "*.rar",
    "*.mp3",
    "*.mp4",
    "*.avi",
    "*.mov",
    "*.mkv",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.log",
    "*.lock",
)


# ────────────────────────────────────────────────────────────────
# Функция проверки, является ли файл скрытым
# ────────────────────────────────────────────────────────────────
def is_hidden_path(path: Path) -> bool:
    """
    Проверяет, содержит ли путь скрытые элементы.

    Args:
        path: Путь к файлу или директории.

    Returns:
        True, если путь содержит скрытую часть, иначе False.
    """

    # Проходим по всем частям пути
    for part in path.parts:
        # Если имя части начинается с точки и это не "." или "..",
        # считаем путь скрытым
        if part.startswith(".") and part not in {".", ".."}:
            return True

    # Если скрытых частей не найдено, возвращаем False
    return False


# ────────────────────────────────────────────────────────────────
# Функция проверки, нужно ли исключить файл по маскам
# ────────────────────────────────────────────────────────────────
def matches_any_pattern(file_name: str, patterns: Iterable[str]) -> bool:
    """
    Проверяет, подходит ли имя файла хотя бы под одну маску.

    Args:
        file_name: Имя файла.
        patterns: Набор масок fnmatch.

    Returns:
        True, если найдено совпадение, иначе False.
    """

    # Последовательно проверяем все переданные маски
    for pattern in patterns:
        # Если файл совпал с текущей маской — сразу завершаем
        if fnmatch.fnmatch(file_name, pattern):
            return True

    # Если ни одна маска не подошла — совпадений нет
    return False


# ────────────────────────────────────────────────────────────────
# Функция определения, является ли файл допустимым для экспорта
# ────────────────────────────────────────────────────────────────
def should_include_file(
    file_path: Path,
    root_dir: Path,
    allowed_extensions: set[str],
    ignored_dirs: set[str],
    ignored_file_patterns: Iterable[str],
    include_hidden: bool,
) -> bool:
    """
    Определяет, нужно ли включать файл в итоговую выгрузку.

    Args:
        file_path: Путь к проверяемому файлу.
        root_dir: Корневая директория обхода.
        allowed_extensions: Разрешённые расширения файлов.
        ignored_dirs: Исключённые директории.
        ignored_file_patterns: Маски исключаемых файлов.
        include_hidden: Включать ли скрытые файлы и папки.

    Returns:
        True, если файл нужно добавить в экспорт, иначе False.
    """

    # Если объект не является обычным файлом, исключаем его
    if not file_path.is_file():
        return False

    # Получаем относительный путь файла относительно корня проекта
    relative_path: Path = file_path.relative_to(root_dir)

    # Если скрытые пути запрещены и путь скрытый — исключаем
    if not include_hidden and is_hidden_path(relative_path):
        return False

    # Если в пути встречается исключённая директория — исключаем
    if any(part in ignored_dirs for part in relative_path.parts[:-1]):
        return False

    # Если имя файла попадает под исключающие маски — исключаем
    if matches_any_pattern(file_path.name, ignored_file_patterns):
        return False

    # Специальная обработка для Dockerfile и подобных файлов без suffix
    normalized_name: str = file_path.name.lower()

    # Если файл называется dockerfile — включаем его явно
    if normalized_name == "dockerfile":
        return True

    # Получаем расширение файла в нижнем регистре
    suffix: str = file_path.suffix.lower()

    # Если у файла есть расширение и оно разрешено — включаем
    if suffix in allowed_extensions:
        return True

    # Если расширения нет, но имя файла само по себе включено в список
    # допустимых "расширений" наподобие ".env" — проверяем отдельно
    if normalized_name in {ext.lstrip(".") for ext in allowed_extensions if ext.startswith(".")}:
        return True

    # Если ни одно условие не сработало — файл не включаем
    return False


# ────────────────────────────────────────────────────────────────
# Функция безопасного чтения текстового файла
# ────────────────────────────────────────────────────────────────
def read_text_file(file_path: Path) -> str | None:
    """
    Безопасно читает текстовый файл, используя несколько кодировок.

    Args:
        file_path: Путь к файлу.

    Returns:
        Текст файла, если чтение удалось, иначе None.
    """

    # Набор кодировок, которые чаще всего встречаются в проектах
    encodings_to_try: tuple[str, ...] = ("utf-8", "utf-8-sig", "cp1251", "latin-1")

    # Пробуем читать файл по очереди разными кодировками
    for encoding in encodings_to_try:
        try:
            # Пытаемся прочитать содержимое файла
            return file_path.read_text(encoding=encoding)

        except UnicodeDecodeError:
            # Если кодировка не подошла — продолжаем пробовать дальше
            continue

        except OSError:
            # Если произошла файловая ошибка — прекращаем попытки
            return None

    # Если ни одна кодировка не подошла — считаем файл неподходящим
    return None


# ────────────────────────────────────────────────────────────────
# Функция построения списка файлов для экспорта
# ────────────────────────────────────────────────────────────────
def collect_files(
    root_dir: Path,
    allowed_extensions: set[str],
    ignored_dirs: set[str],
    ignored_file_patterns: Iterable[str],
    include_hidden: bool,
) -> list[Path]:
    """
    Собирает список файлов, подходящих для включения в экспорт.

    Args:
        root_dir: Корневая директория проекта.
        allowed_extensions: Разрешённые расширения.
        ignored_dirs: Исключённые директории.
        ignored_file_patterns: Исключённые маски файлов.
        include_hidden: Включать ли скрытые пути.

    Returns:
        Отсортированный список путей к файлам.
    """

    # Подготавливаем список, в который будем складывать найденные файлы
    collected_files: list[Path] = []

    # Рекурсивно обходим все объекты в директории
    for path in root_dir.rglob("*"):
        # Проверяем, подходит ли текущий файл под условия экспорта
        if should_include_file(
            file_path=path,
            root_dir=root_dir,
            allowed_extensions=allowed_extensions,
            ignored_dirs=ignored_dirs,
            ignored_file_patterns=ignored_file_patterns,
            include_hidden=include_hidden,
        ):
            # Если файл подходит — добавляем его в список
            collected_files.append(path)

    # Сортируем файлы по относительному пути для стабильного результата
    collected_files.sort(key=lambda item: str(item.relative_to(root_dir)).lower())

    # Возвращаем готовый список
    return collected_files


# ────────────────────────────────────────────────────────────────
# Функция сборки общего текстового дампа проекта
# ────────────────────────────────────────────────────────────────
def build_snapshot_text(root_dir: Path, files: list[Path]) -> str:
    """
    Собирает итоговый текстовый снимок проекта.

    Args:
        root_dir: Корневая директория проекта.
        files: Список файлов для включения.

    Returns:
        Готовый текст экспорта.
    """

    # Создаём список строк, из которых потом соберём финальный текст
    lines: list[str] = []

    # Добавляем общий заголовок файла
    lines.append("=" * 120)
    lines.append("PROJECT SNAPSHOT")
    lines.append(f"ROOT: {root_dir.resolve()}")
    lines.append(f"FILES COUNT: {len(files)}")
    lines.append("=" * 120)
    lines.append("")

    # Последовательно добавляем содержимое каждого файла
    for index, file_path in enumerate(files, start=1):
        # Вычисляем относительный путь файла
        relative_path: Path = file_path.relative_to(root_dir)

        # Пытаемся прочитать содержимое файла
        content: str | None = read_text_file(file_path)

        # Если файл не удалось прочитать как текст — отмечаем это и идём дальше
        if content is None:
            lines.append("-" * 120)
            lines.append(f"[{index}] FILE: {relative_path}")
            lines.append("STATUS: SKIPPED (unable to read as text)")
            lines.append("-" * 120)
            lines.append("")
            continue

        # Добавляем разделитель перед файлом
        lines.append("-" * 120)

        # Добавляем номер и путь файла
        lines.append(f"[{index}] FILE: {relative_path}")

        # Добавляем размер файла в байтах
        lines.append(f"SIZE: {file_path.stat().st_size} bytes")

        # Добавляем ещё один разделитель
        lines.append("-" * 120)

        # Добавляем содержимое файла как есть
        lines.append(content)

        # Если файл не заканчивается переводом строки, добавляем пустую строку
        if not content.endswith("\n"):
            lines.append("")

        # Добавляем пустую строку после каждого файла
        lines.append("")

    # Склеиваем все строки в один итоговый текст
    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────
# Функция парсинга аргументов командной строки
# ────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    """
    Разбирает аргументы командной строки.

    Returns:
        Пространство имён argparse с параметрами запуска.
    """

    # Создаём парсер аргументов
    parser = argparse.ArgumentParser(
        description=(
            "Рекурсивно собирает код и текстовые файлы проекта "
            "в один итоговый файл для передачи на анализ."
        )
    )

    # Добавляем обязательный аргумент — корневая папка проекта
    parser.add_argument(
        "root",
        type=str,
        help="Путь к корневой директории проекта.",
    )

    # Добавляем необязательный аргумент — путь к выходному файлу
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="backend_backend_project_snapshot.txt",
        help="Путь к итоговому txt-файлу.",
    )

    # Добавляем аргумент для пользовательского списка расширений
    parser.add_argument(
        "--ext",
        nargs="*",
        default=None,
        help=(
            "Список расширений для включения, например: "
            "--ext .py .json .md .ts"
        ),
    )

    # Добавляем аргумент для дополнительных исключаемых директорий
    parser.add_argument(
        "--ignore-dir",
        nargs="*",
        default=None,
        help="Дополнительные имена директорий для исключения.",
    )

    # Добавляем аргумент для дополнительных масок исключаемых файлов
    parser.add_argument(
        "--ignore-file",
        nargs="*",
        default=None,
        help="Дополнительные маски файлов для исключения.",
    )

    # Добавляем флаг включения скрытых файлов и папок
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Включать скрытые файлы и директории.",
    )

    # Возвращаем распарсенные аргументы
    return parser.parse_args()


# ────────────────────────────────────────────────────────────────
# Главная функция выполнения скрипта
# ────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Точка входа в программу.

    Выполняет:
    - чтение аргументов
    - сбор списка файлов
    - генерацию общего snapshot-файла
    - сохранение результата на диск
    """

    # Получаем аргументы командной строки
    args: argparse.Namespace = parse_args()

    # Преобразуем путь корневой директории в объект Path
    root_dir: Path = Path(args.root).expanduser().resolve()

    # Проверяем, что корневая директория существует
    if not root_dir.exists():
        raise FileNotFoundError(f"Директория не найдена: {root_dir}")

    # Проверяем, что путь указывает именно на директорию
    if not root_dir.is_dir():
        raise NotADirectoryError(f"Указанный путь не является директорией: {root_dir}")

    # Формируем набор разрешённых расширений
    allowed_extensions: set[str] = (
        {ext.lower() for ext in args.ext}
        if args.ext
        else set(DEFAULT_ALLOWED_EXTENSIONS)
    )

    # Формируем набор исключённых директорий
    ignored_dirs: set[str] = set(DEFAULT_IGNORED_DIRS)
    if args.ignore_dir:
        ignored_dirs.update(args.ignore_dir)

    # Формируем итоговый набор масок исключаемых файлов
    ignored_file_patterns: list[str] = list(DEFAULT_IGNORED_FILE_PATTERNS)
    if args.ignore_file:
        ignored_file_patterns.extend(args.ignore_file)

    # Собираем список подходящих файлов
    files: list[Path] = collect_files(
        root_dir=root_dir,
        allowed_extensions=allowed_extensions,
        ignored_dirs=ignored_dirs,
        ignored_file_patterns=ignored_file_patterns,
        include_hidden=args.include_hidden,
    )

    # Собираем итоговый текст snapshot-файла
    snapshot_text: str = build_snapshot_text(root_dir=root_dir, files=files)

    # Определяем путь выходного файла
    output_path: Path = Path(args.output).expanduser().resolve()

    # Сохраняем итоговый текст в выходной файл
    output_path.write_text(snapshot_text, encoding="utf-8")

    # Выводим краткий отчёт о завершении работы
    print(f"Корневая директория: {root_dir}")
    print(f"Собрано файлов: {len(files)}")
    print(f"Итоговый файл: {output_path}")


# ────────────────────────────────────────────────────────────────
# Стандартная точка входа при запуске скрипта напрямую
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Запускаем главную функцию программы
    main()