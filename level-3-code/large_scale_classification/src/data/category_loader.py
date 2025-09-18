"""Loads and manages category data from files."""

from pathlib import Path

from src.config.settings import settings
from src.data.models import Category
from src.shared.logger import get_logger


class CategoryLoader:
    """Loads and manages category data from files."""

    def __init__(self) -> None:
        """Initialize the category loader."""
        self._categories: list[Category] = []
        self._loaded = False
        self.logger = get_logger(__name__)

    def load_categories(self) -> list[Category]:
        """Load categories from configured source.

        Returns:
            The categories.
        """
        if self._loaded:
            return self._categories
        file_path = Path(settings.categories_file_path)
        self._categories = self._parse_category_file(file_path)
        self._loaded = True
        return self._categories

    def _parse_category_file(self, file_path: Path) -> list[Category]:
        """Parse category.txt into Category objects.

        Args:
            file_path: The path to the category file.

        Returns:
            The categories.
        """
        categories = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    category = self._parse_category_line(line)
                    categories.append(category)
                except Exception as e:
                    self.logger.warning(f"Failed to parse line {line_num}: {line} - {e}")
        return categories

    def _parse_category_line(self, line: str) -> Category:
        """Parse a single category line.

        Args:
            line: The line to parse.

        Returns:
            The category.
        """
        parts = line.strip("/").split("/")
        name = parts[-1]  # Last part is the name
        level = len(parts) - 1
        parent_path = "/".join(parts[:-1]) if level > 0 else None
        if parent_path:
            parent_path = "/" + parent_path
        embedding_text = " ".join(parts).lower().replace("_", " ")
        llm_description = f"Items in the {name} category under {' > '.join(parts[:-1]) if parts[:-1] else 'root'}"
        return Category(
            name=name,
            path=line,
            embedding_text=embedding_text,
            llm_description=llm_description,
        )
