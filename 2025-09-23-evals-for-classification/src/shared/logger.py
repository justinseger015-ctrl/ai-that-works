"""Logging configuration for the large scale classification project."""

import logging
import sys
from pathlib import Path


class ClassificationLogger:
    """Custom logger for the classification pipeline with appropriate verbosity levels."""

    def __init__(self, name: str = "classification", level: str = "INFO"):
        """Initialize the logger.

        Args:
            name: Logger name, typically the module name
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Prevent duplicate handlers if logger already configured
        if not self.logger.handlers:
            self._setup_handler()

    def _setup_handler(self):
        """Set up console handler with custom formatting."""
        handler = logging.StreamHandler(sys.stdout)

        # Custom formatter with colors and emojis for better readability
        formatter = ColoredFormatter(fmt="%(levelname_with_icon)s %(name)s: %(message)s", datefmt="%H:%M:%S")

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, message: str, **kwargs):
        """Log info message - for successful operations and progress updates."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message - for recoverable issues and fallbacks."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message - for serious issues that affect functionality."""
        self.logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message - for detailed troubleshooting (use sparingly)."""
        self.logger.debug(message, **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message - for completed operations."""
        # Use info level but with success formatting
        self.logger.info(f"✅ {message}", **kwargs)

    def processing(self, message: str, **kwargs):
        """Log processing message - for ongoing operations."""
        self.logger.info(f"⚙️  {message}", **kwargs)


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors and icons to log messages."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }

    # Icons for different log levels
    ICONS = {
        "DEBUG": "🔍",
        "INFO": "ℹ️ ",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    RESET = "\033[0m"  # Reset color

    def format(self, record):
        """Format the log record."""
        # Add colored level name with icon
        level_name = record.levelname
        color = self.COLORS.get(level_name, "")
        icon = self.ICONS.get(level_name, "")

        record.levelname_with_icon = f"{color}{icon} {level_name}{self.RESET}"

        return super().format(record)


def get_logger(name: str, level: str = "INFO") -> ClassificationLogger:
    """Get a logger instance for a module.

    Args:
        name: Logger name, typically __name__ of the calling module
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured ClassificationLogger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting classification pipeline")
        >>> logger.success("Classification completed successfully")
        >>> logger.warning("Using fallback embedding model")
        >>> logger.error("Failed to load vector store")
    """
    return ClassificationLogger(name, level)


# Convenience function for quick logging setup
def setup_logging(level: str = "INFO", log_file: Path | None = None):
    """Set up logging configuration for the entire project.

    Args:
        level: Global logging level
        log_file: Optional file to write logs to (in addition to console)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(fmt="%(levelname_with_icon)s %(name)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
