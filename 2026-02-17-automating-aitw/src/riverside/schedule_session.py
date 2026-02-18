#!/usr/bin/env python3
"""Script to schedule a Riverside session."""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

from src.riverside import schedule_riverside_session

# Load environment variables from the project root .env
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


def main():
    """Schedule the test session on Riverside."""
    # Session details as specified
    session_date = datetime(2026, 2, 17, 10, 0)  # Feb 17, 2026 at 10:00 AM PST
    guests = ["dexter@humanlayer.dev"]

    print("=" * 50)
    print("Riverside Session Scheduler")
    print("=" * 50)
    print(f"Session Name: test session")
    print(f"Description: foo bar")
    print(f"Date/Time: {session_date.strftime('%B %d, %Y at %I:%M %p')} PST")
    print(f"Duration: 60 minutes (10:00 AM - 11:00 AM)")
    print(f"Guests: {', '.join(guests)}")
    print("=" * 50)
    print()

    # Screenshot directory for debugging
    screenshot_dir = Path(__file__).parent.parent.parent / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)

    try:
        session_url = schedule_riverside_session(
            name="test session",
            description="foo bar",
            date=session_date,
            duration_minutes=60,
            guests=guests,
            headless=False,  # Set to True for headless operation
            screenshot_dir=str(screenshot_dir)
        )
        print()
        print("=" * 50)
        print("SUCCESS!")
        print(f"Session URL: {session_url}")
        print("=" * 50)
    except Exception as e:
        print(f"Error scheduling session: {e}")
        raise


if __name__ == "__main__":
    main()
