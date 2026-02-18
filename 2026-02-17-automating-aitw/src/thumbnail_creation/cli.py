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
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Import BAML client (must be after sys.path modification)
from baml_client import b  # noqa: E402

# Import thumbnail creation (now a relative import since we're in the same module)
from .create_thumbnail import generate_icon_image  # noqa: E402

load_dotenv()


async def generate_subtitle(title: str, description: str, feedback: str | None = None) -> str:
    """Generate subtitle using BAML function."""
    try:
        if feedback is not None:
            result = await b.GenerateSubtitle(title=title, description=description, feedback=feedback)  # type: ignore[attr-defined]
        else:
            result = await b.GenerateSubtitle(title=title, description=description)  # type: ignore[attr-defined]
        return result.subtitle
    except Exception as e:
        print(f"Error generating subtitle: {e}")
        sys.exit(1)


async def classify_feedback(
    title: str,
    description: str,
    current_subtitle: str,
    feedback: str
) -> tuple[str, str | None, str | None]:
    """
    Classify user feedback to determine if it's about subtitle, image, or both.

    Returns:
        Tuple of (target, subtitle_feedback, image_feedback)
    """
    try:
        result = await b.ClassifyFeedback(  # type: ignore[attr-defined]
            title=title,
            description=description,
            current_subtitle=current_subtitle,
            feedback=feedback
        )
        return result.target, result.subtitle_feedback, result.image_feedback
    except Exception as e:
        print(f"Error classifying feedback: {e}")
        sys.exit(1)


def create_thumbnail_with_subtitle(
    title: str,
    subtitle: str,
    episode_number: str,
    output_path: Path | None = None,
    image_feedback: str | None = None
) -> Path:
    """Create thumbnail using the generated subtitle."""
    try:
        return generate_icon_image(
            title=title,
            subtitle=subtitle,
            episode_number=episode_number,
            output_path=output_path,
            image_feedback=image_feedback
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
  %(prog)s --title "Understanding Latency" --description "..." --episode-number "42" --feedback "The subtitle is too boring"
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

    parser.add_argument(
        "--feedback",
        type=str,
        help="Feedback to improve the subtitle or image"
    )

    parser.add_argument(
        "--current-subtitle",
        type=str,
        help="Current subtitle (required when providing feedback)"
    )

    args = parser.parse_args()

    # Handle feedback mode
    if args.feedback:
        if not args.current_subtitle:
            print("Error: --current-subtitle is required when providing feedback")
            sys.exit(1)

        print(f"\n🔍 Analyzing feedback: '{args.feedback}'")
        target, subtitle_feedback, image_feedback = await classify_feedback(
            title=args.title,
            description=args.description,
            current_subtitle=args.current_subtitle,
            feedback=args.feedback
        )

        print(f"📊 Feedback target: {target}")
        if subtitle_feedback:
            print(f"   Subtitle feedback: {subtitle_feedback}")
        if image_feedback:
            print(f"   Image feedback: {image_feedback}")

        # Regenerate subtitle if needed
        if target in ["subtitle", "both"]:
            print(f"\n🔄 Regenerating subtitle with feedback...")
            subtitle = await generate_subtitle(args.title, args.description, subtitle_feedback)
            print(f"✨ New subtitle: '{subtitle}'")
        else:
            subtitle = args.current_subtitle
            print(f"✓ Keeping current subtitle: '{subtitle}'")

        if args.subtitle_only:
            return

        # Regenerate image if needed
        if target in ["image", "both"]:
            print(f"\n🎨 Regenerating thumbnail with feedback...")
            output_path = create_thumbnail_with_subtitle(
                title=args.title,
                subtitle=subtitle,
                episode_number=args.episode_number,
                output_path=args.output_path,
                image_feedback=image_feedback
            )
        else:
            print(f"\n🎨 Regenerating thumbnail with new subtitle...")
            output_path = create_thumbnail_with_subtitle(
                title=args.title,
                subtitle=subtitle,
                episode_number=args.episode_number,
                output_path=args.output_path
            )

        print(f"✅ Thumbnail updated: {output_path}")
        return

    # Normal generation flow (no feedback)
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