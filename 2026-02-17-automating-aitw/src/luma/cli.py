#!/usr/bin/env python3
"""
CLI for creating 'ai that works' events on Luma.
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from src.luma.luma_client import LumaClient


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Create an 'ai that works' event on Luma",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --name "Understanding Latency" --description "This week we discuss latency..." --date 2026-02-03 --cover-image-path /path/to/image.png --luma-url-suffix understanding-latency
  %(prog)s -n "Prompt Optimization" -d "Deep dive into prompts" --date 2026-02-10 -c thumbnail.png -s prompt-optimization
        """,
    )

    parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="Event name/title",
    )

    parser.add_argument(
        "--description",
        "-d",
        required=True,
        help="Event description in markdown format",
    )

    parser.add_argument(
        "--date",
        required=True,
        type=parse_date,
        help="Event date in YYYY-MM-DD format (must be a Tuesday)",
    )

    parser.add_argument(
        "--cover-image-path",
        "-c",
        required=True,
        type=Path,
        help="Path to the cover image file",
    )

    parser.add_argument(
        "--luma-url-suffix",
        "-s",
        required=True,
        help="URL suffix for the event page (e.g., 'my-event' -> luma.com/my-event)",
    )

    args = parser.parse_args()

    # Validate cover image exists
    if not args.cover_image_path.exists():
        print(f"Error: Cover image not found: {args.cover_image_path}")
        sys.exit(1)

    try:
        print(f"Creating event: {args.name}")
        print(f"  Date: {args.date}")
        print(f"  Slug: {args.luma_url_suffix}")
        print(f"  Cover image: {args.cover_image_path}")

        client = LumaClient()
        result = client.create_ai_that_works_event(
            name=args.name,
            description_md=args.description,
            event_date=args.date,
            cover_image_path=str(args.cover_image_path),
            luma_url_suffix=args.luma_url_suffix,
        )

        print(f"\n✅ Event created successfully!")
        print(f"\nAPI Response:")
        print(result)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating event: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

