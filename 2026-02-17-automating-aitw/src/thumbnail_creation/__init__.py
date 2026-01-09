"""Thumbnail creation module for AI That Works podcast."""

import sys
from pathlib import Path

# Handle both direct script execution and module import
try:
    from .create_thumbnail import generate_icon_image
    from .thumbnail_service import ThumbnailService
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from create_thumbnail import generate_icon_image
    from thumbnail_service import ThumbnailService

__all__ = ["generate_icon_image", "ThumbnailService"]



