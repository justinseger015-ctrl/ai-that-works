#!/usr/bin/env python3
"""CLI to generate email drafts from episode content."""

import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from project root .env
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from src.email_generator import generate_email


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an email draft from episode content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python -m src.email_generator.generate_email --transcript transcript.txt --title "My Episode" --description "About AI" --output ./output
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
        help="Output directory for email.json",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    transcript = args.transcript.read_text()

    result = await generate_email(
        transcript=transcript,
        episode_title=args.title,
        episode_description=args.description,
    )

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    # Write email.json to output directory
    output_file = args.output / "email.json"
    output_file.write_text(json.dumps({
        "subject": result.subject,
        "body": result.body,
        "call_to_action": result.call_to_action,
    }, indent=2))

    print(f"Email draft written to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
