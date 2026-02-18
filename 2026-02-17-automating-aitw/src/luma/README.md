# luma

A module for creating and managing "ai that works" events on Luma via their public API.

## Usage

The module is invoked via its `cli` submodule:

```bash
python -m luma.cli \
  --name "My Event" \
  --description "Event description in **markdown**" \
  --date 2026-02-17 \
  --cover-image-path /path/to/cover.jpg \
  --luma-url-suffix my-event-slug
```

### Required Arguments

| Argument | Short | Description |
|---|---|---|
| `--name` | `-n` | Event name |
| `--description` | `-d` | Event description (markdown) |
| `--date` | | Event date in `YYYY-MM-DD` format (must be a Tuesday) |
| `--cover-image-path` | `-c` | Path to cover image file |
| `--luma-url-suffix` | `-s` | URL slug for the event |

### Environment Variables

| Variable | Description |
|---|---|
| `LUMA_API_KEY` | Luma API authentication key (required) |

## Flow

```
CLI (cli.py)
  └── parse & validate arguments
      └── LumaClient.create_ai_that_works_event()
            ├── 1. upload_cover_image(cover_image_path)
            │       ├── POST /images/create-upload-url → get S3 upload URL + CDN URL
            │       └── PUT image binary to S3 upload URL
            │           → returns CDN file_url
            │
            └── 2. create_event(name, description, date, cover_url, slug)
                    ├── _verify_tuesday(date)       → raises if not Tuesday
                    ├── _create_event_times(date)   → 10–11 AM PST, converted to UTC
                    ├── _format_slug(slug)           → lowercase, dashes
                    ├── _check_slug_available(slug)  → raises if taken
                    └── POST /event/create
                        → returns created Event
```

### Step-by-step

1. **CLI parses arguments** and validates that the cover image file exists on disk.

2. **`upload_cover_image()`** runs a two-step upload:
   - Requests a pre-signed S3 upload URL from Luma (`POST /images/create-upload-url`).
   - PUTs the image binary directly to S3.
   - Returns the CDN URL for use as the event cover.

3. **`create_event()`** validates and creates the event:
   - Confirms the date is a Tuesday (all "ai that works" events are Tuesdays).
   - Builds start/end times as 10–11 AM PST, converting to UTC for the API.
   - Formats the slug (lowercase, spaces/underscores → dashes) and checks it isn't already in use.
   - POSTs to `/event/create` with all event details.

## Module Structure

```
src/luma/
├── __init__.py       # Exports: LumaClient, Event, constants
├── cli.py            # CLI entry point (argparse)
├── constants.py      # API base URL, defaults (timezone, meeting URL, etc.)
├── luma_client.py    # LumaClient class with all API interactions
└── luma_event.py     # Example usage
```

## Key Defaults (constants.py)

| Constant | Value |
|---|---|
| `DEFAULT_TIMEZONE` | `America/Los_Angeles` |
| `DEFAULT_MEETING_URL` | Riverside.fm studio URL |
| `DEFAULT_DURATION_HOURS` | `1` |
| `CALENDAR_API_ID` | Luma calendar the event is created under |
| `AI_THAT_WORKS_PREFIX` | `🦄 ai that works` |

## Additional Client Methods

Beyond event creation, `LumaClient` exposes query helpers:

- `list_events()` — lists events (defaults to 2-month lookback)
- `get_next_ai_that_works_event()` — finds the next future event
- `get_most_recent_ai_that_works_event()` — finds the most recent past event
- `get_guests(event_api_id)` — returns the guest list for an event
- `get_most_recent_ai_that_works_event_guests()` — guests for the most recent event
