"""
Thumbnail creation module for AI That Works podcast episodes.

This module provides a simple interface for generating podcast thumbnails
using Google Gemini for image editing.
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Handle both direct script execution and module import
try:
    from .thumbnail_service import ThumbnailService
except ImportError:
    # When run as a script, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    from thumbnail_service import ThumbnailService

load_dotenv()


def generate_icon_image(
    title: str,
    subtitle: str,
    episode_number: str,
    output_path: Path | None = None,
) -> Path:
    """
    Generate a podcast thumbnail by sending the base image and prompt to Gemini.
    
    Args:
        title: The episode title
        subtitle: The episode subtitle
        episode_number: The episode number (e.g., "42")
        output_path: Optional custom output path. Defaults to output directory.
    
    Returns:
        Path to the generated thumbnail
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set or if Gemini fails to generate an image
        FileNotFoundError: If base thumbnail or prompt template is missing
    """
    service = ThumbnailService()
    return service.generate_thumbnail(title, subtitle, episode_number, output_path)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Generate podcast thumbnail for AI That Works episodes"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Episode title"
    )
    parser.add_argument(
        "--subtitle",
        required=True,
        help="Episode subtitle"
    )
    parser.add_argument(
        "--episode_number",
        required=True,
        help="Episode number (e.g., '42')"
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Optional custom output path for the thumbnail"
    )
    
    args = parser.parse_args()
    
    output_path = generate_icon_image(
        title=args.title,
        subtitle=args.subtitle,
        episode_number=args.episode_number,
        output_path=args.output_path
    )
    print(f"Created thumbnail: {output_path}")
