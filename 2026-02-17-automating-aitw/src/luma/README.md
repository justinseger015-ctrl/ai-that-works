# Luma API Module

This module provides a simple interface to fetch calendar events from the Luma API and find the next upcoming "🦄 ai that works" event.

## Setup

The Luma API key is already configured in the `.env` file:
```
LUMA_API_KEY=secret-1QJSEs7EeXYTKRCvD5jWYzegh
```

## Usage

### Basic Example

```python
from src.luma import LumaClient

# Initialize the client (reads LUMA_API_KEY from environment)
client = LumaClient()

# Get the next upcoming "🦄 ai that works" event
event = client.get_next_ai_that_works_event()

if event:
    print(f"URL: {event.url}")
    print(f"Description: {event.clean_description}")
```

### List All Events

```python
from src.luma import LumaClient
from datetime import datetime, timedelta, timezone

client = LumaClient()

# List events from the last 2 months (default)
events = client.list_events()

# Or specify a custom date
custom_date = datetime.now(timezone.utc) - timedelta(days=60)
events = client.list_events(after=custom_date)

for event in events:
    print(f"{event.name}: {event.url}")
```

### Running the Example Script

```bash
cd src/luma
python example.py
```

## API Reference

### LumaClient

#### `__init__(api_key: Optional[str] = None)`
Initialize the Luma client. If `api_key` is not provided, reads from `LUMA_API_KEY` environment variable.

#### `list_events(after: Optional[datetime] = None) -> List[Event]`
List calendar events after a specific date.

**Parameters:**
- `after`: Start date for event search. If not provided, looks back 2 months from today (configurable via `LOOKBACK_MONTHS` constant)

**Returns:** List of `Event` objects

#### `get_most_recent_ai_that_works_event() -> Optional[Event]`
Get the most recent "🦄 ai that works" event that has already occurred (start_at < today).

**Returns:** The most recent past Event with "🦄 ai that works" in the name, or None if not found

### Event

A dataclass representing a Luma calendar event with the following properties:

- `api_id`: Event API ID
- `name`: Event name/title
- `description`: Event description
- `start_at`: Event start datetime
- `end_at`: Event end datetime
- `url`: Luma event page URL
- `meeting_url`: Meeting/streaming URL (optional)
- `cover_url`: Event cover image URL (optional)
- `timezone`: Event timezone
- `visibility`: Event visibility (public/private)

## Configuration

You can adjust the lookback period by modifying the `LOOKBACK_MONTHS` constant in `luma_client.py`:

```python
# Number of months to look back for events (default: 2)
LOOKBACK_MONTHS = 2
```

## Notes

- The module uses the `requests` library for HTTP requests (already in project dependencies)
- Dates are automatically converted to ISO 8601 format and URL-encoded for API calls
- The module uses `python-dotenv` to load environment variables from `.env`
- All datetime objects use UTC timezone for consistency
