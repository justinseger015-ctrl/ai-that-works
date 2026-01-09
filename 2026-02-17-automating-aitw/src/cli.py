#!/usr/bin/env python3
"""
CLI for generating podcast episode thumbnails with AI-generated subtitles.

This script combines BAML subtitle generation with thumbnail creation
for AI That Works podcast episodes.
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import baml_client from the correct location
# This must happen before importing baml_client to ensure we import from the
# local project directory, not from other projects in the Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import BAML client (must be after sys.path modification)
from baml_client import b  # noqa: E402

# Import thumbnail creation
from src.thumbnail_creation.create_thumbnail import generate_icon_image  # noqa: E402

load_dotenv()


async def generate_subtitle(title: str, description: str) -> str:
    """Generate subtitle using BAML function."""
    try:
        result = await b.GenerateSubtitle(title=title, description=description)  # type: ignore[attr-defined]
        return result.subtitle
    except Exception as e:
        print(f"Error generating subtitle: {e}")
        sys.exit(1)


def create_thumbnail_with_subtitle(
    title: str,
    subtitle: str,
    episode_number: str,
    output_path: Path | None = None
) -> Path:
    """Create thumbnail using the generated subtitle."""
    try:
        return generate_icon_image(
            title=title,
            subtitle=subtitle,
            episode_number=episode_number,
            output_path=output_path
        )
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate podcast thumbnail with AI-generated subtitle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --title "Understanding Latency" --description "This episode is all about latency..." --episode-number "42"
  %(prog)s --title "Prompt Optimization" --description "No one wants to write prompts..." --episode-number "43" --output output/thumbnail.png
        """
    )

    parser.add_argument(
        "--title",
        required=True,
        help="Episode title"
    )

    parser.add_argument(
        "--description",
        required=True,
        help="Episode description for subtitle generation"
    )

    parser.add_argument(
        "--episode-number",
        required=True,
        help="Episode number (e.g., '42')"
    )

    parser.add_argument(
        "--output-path",
        type=Path,
        help="Optional custom output path for the thumbnail"
    )

    parser.add_argument(
        "--subtitle-only",
        action="store_true",
        help="Only generate subtitle, don't create thumbnail"
    )

    args = parser.parse_args()

    print(f"Generating subtitle for episode: {args.title}")
    subtitle = await generate_subtitle(args.title, args.description)
    print(f"Generated subtitle: '{subtitle}'")

    if args.subtitle_only:
        return

    print(f"Creating thumbnail for episode {args.episode_number}...")
    output_path = create_thumbnail_with_subtitle(
        title=args.title,
        subtitle=subtitle,
        episode_number=args.episode_number,
        output_path=args.output_path
    )

    print(f"✅ Thumbnail created: {output_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())