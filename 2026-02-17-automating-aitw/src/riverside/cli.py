#!/usr/bin/env python3
"""
CLI for creating 'ai that works' recording sessions on Riverside.
"""

import argparse
import sys
from datetime import date, datetime
from typing import List

from dotenv import load_dotenv

from src.riverside.riverside_agent import RiversideAgent, SessionDetails

load_dotenv()

DEFAULT_GUEST = "dexter@humanlayer.dev"


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD."
        )


def parse_guests(guests_str: str) -> List[str]:
    """Parse a comma-separated list of guest emails."""
    if not guests_str:
        return []
    return [email.strip() for email in guests_str.split(",") if email.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Create an 'AI That Works' recording session on Riverside",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --title "Understanding Latency" --episode-number 42 --description "This week we discuss latency..." --date 2026-02-17
  %(prog)s -t "Prompt Optimization" -n 43 -d "Deep dive into prompts" --date 2026-02-24 --guests "guest1@example.com,guest2@example.com"
        """,
    )

    parser.add_argument(
        "--title",
        "-t",
        required=True,
        help="Episode title (will be formatted as '<title>: 🦄 AI That Works #NN')",
    )

    parser.add_argument(
        "--episode-number",
        "-n",
        required=True,
        type=int,
        help="Episode number",
    )

    parser.add_argument(
        "--description",
        "-d",
        required=True,
        help="Episode description",
    )

    parser.add_argument(
        "--date",
        required=True,
        type=parse_date,
        help="Recording date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "--guests",
        "-g",
        type=parse_guests,
        default=[],
        help="Comma-separated list of guest email addresses",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )

    args = parser.parse_args()

    # Format the title: "<title>: 🦄 AI That Works #NN"
    formatted_title = f"{args.title}: 🦄 AI That Works #{args.episode_number}"

    # Ensure dexter@humanlayer.dev is always in the guest list
    guests = list(args.guests)
    if DEFAULT_GUEST not in guests:
        guests.append(DEFAULT_GUEST)

    # Create datetime for 10:00 AM PST
    session_datetime = datetime(
        args.date.year,
        args.date.month,
        args.date.day,
        10,  # 10 AM
        0,   # 0 minutes
    )

    session = SessionDetails(
        name=formatted_title,
        description=args.description,
        date=session_datetime,
        duration_minutes=60,  # 10-11 AM
        guests=guests,
    )

    try:
        print(f"Creating Riverside session:")
        print(f"  Title: {formatted_title}")
        print(f"  Episode: #{args.episode_number}")
        print(f"  Date: {args.date}")
        print(f"  Time: 10:00 AM - 11:00 AM PST")
        print(f"  Guests: {', '.join(guests)}")

        with RiversideAgent(headless=args.headless) as agent:
            session_url = agent.run(session)

        print(f"\n✅ Session created successfully!")
        print(f"Session URL: {session_url}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating session: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
