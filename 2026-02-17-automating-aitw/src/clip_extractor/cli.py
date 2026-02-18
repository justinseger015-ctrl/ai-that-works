#!/usr/bin/env python3
"""CLI to extract high-impact clips from episode transcripts."""

import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from project root .env
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from baml_client import b
from baml_client.types import HighImpactClip


async def extract_clips(
    transcript: str,
    episode_title: str,
    episode_description: str,
) -> list[HighImpactClip]:
    """Extract the three highest-impact clips from an episode transcript.

    Two-stage pipeline:
    1. ExtractEmailStructure - Extract key takeaways from the transcript
    2. ExtractHighImpactClips - Find the best clips that relate to those takeaways

    Args:
        transcript: Full episode transcript
        episode_title: Title of the episode
        episode_description: Episode description/summary

    Returns:
        List of 3 HighImpactClip objects with rationale, timestamps, transcript excerpt, and hook
    """
    # Stage 1: Extract key takeaways using the email structure function
    structure = await b.ExtractEmailStructure(
        transcript=transcript,
        episode_title=episode_title,
        episode_description=episode_description,
    )

    # Stage 2: Find the high-impact clips based on those takeaways
    clips = await b.ExtractHighImpactClips(
        transcript=transcript,
        episode_title=episode_title,
        key_takeaways=structure.quick_recap,
        one_thing_to_remember=structure.one_thing_to_remember,
    )

    return clips


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract high-impact clips from an episode transcript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python -m src.clip_extractor.extract_clip --transcript transcript.txt --title "My Episode" --description "About AI" --output ./output
""",
    )
    parser.add_argument(
        "--transcript",
        "-t",
        type=Path,
        required=True,
        help="Path to transcript file",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Episode title",
    )
    parser.add_argument(
        "--description",
        "-d",
        required=True,
        help="Episode description",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output directory for clips.json",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    transcript = args.transcript.read_text()

    results = await extract_clips(
        transcript=transcript,
        episode_title=args.title,
        episode_description=args.description,
    )

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    # Write clips.json to output directory
    output_file = args.output / "clips.json"
    clips_data = [
        {
            "rationale": clip.rationale,
            "start_timestamp": clip.start_timestamp,
            "end_timestamp": clip.end_timestamp,
            "speaker": clip.speaker,
            "transcript_excerpt": clip.transcript_excerpt,
            "hook": clip.hook,
        }
        for clip in results
    ]
    output_file.write_text(json.dumps(clips_data, indent=2))

    print(f"Clips extracted to {output_file}")
    for i, clip in enumerate(results, 1):
        print(f"\n--- Clip {i} ---")
        print(f"Hook: {clip.hook}")
        print(f"Timestamps: {clip.start_timestamp} - {clip.end_timestamp}")


if __name__ == "__main__":
    asyncio.run(main())
