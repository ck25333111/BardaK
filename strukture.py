# ────────────────────────────────────────────────────────────────
# strukture.py
# Печать дерева проекта из указанной директории.
# Поддерживает исключения по точным именам и по маскам (glob/fnmatch).
# ────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TreeConfig:
    """Конфигурация печати дерева проекта."""
    exclude_names: frozenset[str]
    exclude_patterns: tuple[str, ...]
    max_depth: int | None = None  # None = без ограничений


DEFAULT_CONFIG = TreeConfig(
    exclude_names=frozenset(
        {
            ".git",
            ".idea",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".vscode",
            ".venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            "logs",
            ".DS_Store",
        }
    ),
    # Маски исключений (вот тут твои *.json и т.п. должны быть именно так)
    exclude_patterns=(
        "*.pyc",
        "*.pyo",
        "*.log",
        "*.tmp",
        "*.json",   # если НЕ хочешь видеть json вообще
        "*.lock",
        "*.map",
    ),
    max_depth=None,
)


class ProjectTreePrinter:
    """Печатает дерево файлов/папок с исключениями."""

    def __init__(self, config: TreeConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    def print_tree(self, start_path: Path | str | None = None) -> None:
        """Печатает дерево, начиная с start_path (по умолчанию текущая директория)."""
        root = Path(start_path).resolve() if start_path else Path.cwd().resolve()
        print(f"{root.as_posix()}/")
        self._print_recursive(root, prefix="", depth=0)

    def _print_recursive(self, path: Path, prefix: str, depth: int) -> None:
        if self._config.max_depth is not None and depth >= self._config.max_depth:
            return

        children = self._list_children(path)
        for idx, child in enumerate(children):
            is_last = idx == len(children) - 1
            connector = "└── " if is_last else "├── "
            print(prefix + connector + child.name + ("/" if child.is_dir() else ""))

            if child.is_dir():
                extension = "    " if is_last else "│   "
                self._print_recursive(child, prefix + extension, depth + 1)

    def _list_children(self, path: Path) -> list[Path]:
        """Возвращает отсортированный список детей, применяя исключения."""
        try:
            items = list(path.iterdir())
        except PermissionError:
            return []

        filtered: list[Path] = [p for p in items if not self._is_excluded(p)]
        filtered.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        return filtered

    def _is_excluded(self, p: Path) -> bool:
        name = p.name

        # точные совпадения
        if name in self._config.exclude_names:
            return True

        # маски
        for pattern in self._config.exclude_patterns:
            if fnmatch(name, pattern):
                return True

        return False


if __name__ == "__main__":
    print("📂 Структура проекта:\n")

    printer = ProjectTreePrinter(
        # Если хочешь ограничить глубину, например 6 уровней:
        # TreeConfig(DEFAULT_CONFIG.exclude_names, DEFAULT_CONFIG.exclude_patterns, max_depth=6)
        DEFAULT_CONFIG
    )

    # Печатаем дерево из текущей папки.
    # Если хочешь из конкретной: printer.print_tree("C:/Projects/BardaK")
    printer.print_tree()
