"""Luma API client for fetching calendar events."""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from urllib.parse import quote
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Number of months to look back for events
LOOKBACK_MONTHS = 2


@dataclass
class Event:
    """Represents a Luma calendar event."""

    api_id: str
    name: str
    description: str
    start_at: datetime
    end_at: datetime
    url: str
    meeting_url: Optional[str]
    cover_url: Optional[str]
    timezone: str
    visibility: str

    @property
    def clean_description(self) -> str:
        """
        Get the description with everything after 'Pre-reading' removed.

        Returns:
            Cleaned description string
        """
        if "🦄 ai that works" in self.description:
            self.description = self.description.split("🦄 ai that works")[1].strip()
        if "Pre-reading" in self.description:
            return self.description.split("Pre-reading")[0].strip()
        return self.description

    @classmethod
    def from_api_response(cls, entry: dict) -> "Event":
        """
        Create an Event from the API response entry.

        Args:
            entry: API response entry containing event data

        Returns:
            Event object
        """
        event_data = entry["event"]
        return cls(
            api_id=event_data["api_id"],
            name=event_data["name"],
            description=event_data["description"],
            start_at=datetime.fromisoformat(event_data["start_at"].replace("Z", "+00:00")),
            end_at=datetime.fromisoformat(event_data["end_at"].replace("Z", "+00:00")),
            url=event_data["url"],
            meeting_url=event_data.get("meeting_url"),
            cover_url=event_data.get("cover_url"),
            timezone=event_data["timezone"],
            visibility=event_data["visibility"],
        )


class LumaClient:
    """Client for interacting with the Luma Calendar API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Luma client.

        Args:
            api_key: Luma API key. If not provided, reads from LUMA_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("LUMA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Luma API key is required. Set LUMA_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = "https://public-api.luma.com/v1"

    def _get_lookback_date(self, months: int = LOOKBACK_MONTHS) -> datetime:
        """
        Calculate the date to look back from today.

        Args:
            months: Number of months to look back (default: LOOKBACK_MONTHS)

        Returns:
            Datetime object representing the lookback date
        """
        today = datetime.now(timezone.utc)
        # Approximate months as 30 days each for simplicity
        lookback_date = today - timedelta(days=months * 30)
        return lookback_date

    def list_events(self, after: Optional[datetime] = None) -> List[Event]:
        """
        List calendar events after a specific date.

        Args:
            after: Start date for event search. If not provided, uses LOOKBACK_MONTHS from today.

        Returns:
            List of Event objects
        """
        if after is None:
            after = self._get_lookback_date()

        # Format datetime to ISO 8601 and URL encode
        after_str = after.isoformat()
        after_encoded = quote(after_str, safe="")

        url = f"{self.base_url}/calendar/list-events?after={after_encoded}"
        headers = {"accept": "application/json", "x-luma-api-key": self.api_key}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        events = [Event.from_api_response(entry) for entry in data.get("entries", [])]

        return events

    def get_next_ai_that_works_event(self) -> Optional[Event]:
        """
        Get the next upcoming 'ai that works' event.

        Returns:
            The next upcoming Event with "🦄 ai that works" in the name, or None if not found
        """
        events = self.list_events()
        now = datetime.now(timezone.utc)

        # Filter for "🦄 ai that works" events that haven't started yet
        ai_works_events = [
            event
            for event in events
            if "🦄 ai that works" in event.name and event.start_at > now
        ]

        if not ai_works_events:
            return None

        # Sort by start_at ascending (soonest first)
        ai_works_events.sort(key=lambda e: e.start_at)

        return ai_works_events[0]
