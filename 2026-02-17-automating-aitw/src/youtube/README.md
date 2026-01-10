# YouTube API Module

This module provides a simple interface to fetch recent videos from YouTube channels using the YouTube Data API v3.

## Setup

1. **Get a YouTube Data API Key**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the "YouTube Data API v3"
   - Create credentials (API Key)
   - Copy the API key

2. **Configure the API Key**:
   Add your API key to the `.env` file in the project root:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

## Usage

### Basic Example

```python
from src.youtube import YouTubeClient

# Initialize the client (reads YOUTUBE_API_KEY from environment)
client = YouTubeClient()

# Fetch the 3 most recent videos from a channel
videos = client.get_recent_videos_from_handle("@boundaryml", max_results=3)

# Display the videos
for video in videos:
    print(f"{video.title}")
    print(f"URL: {video.url}")
    print(f"Published: {video.published_at}")
    print()
```

### Running the Example Script

```bash
cd src/youtube
python example.py
```

## API Reference

### YouTubeClient

#### `__init__(api_key: Optional[str] = None)`
Initialize the YouTube client. If `api_key` is not provided, reads from `YOUTUBE_API_KEY` environment variable.

#### `get_recent_videos_from_handle(handle: str, max_results: int = 3) -> List[Video]`
Fetch recent videos from a channel using its handle (e.g., "@boundaryml").

**Parameters:**
- `handle`: Channel handle with or without @ prefix
- `max_results`: Number of videos to fetch (default: 3)

**Returns:** List of `Video` objects sorted by publish date (newest first)

#### `get_recent_videos(channel_id: str, max_results: int = 3) -> List[Video]`
Fetch recent videos from a channel using its ID.

**Parameters:**
- `channel_id`: YouTube channel ID
- `max_results`: Number of videos to fetch (default: 3)

**Returns:** List of `Video` objects sorted by publish date (newest first)

### Video

A dataclass representing a YouTube video with the following properties:

- `title`: Video title
- `video_id`: YouTube video ID
- `published_at`: Publication datetime
- `description`: Video description
- `thumbnail_url`: URL to video thumbnail
- `url`: Full YouTube URL (property)

## Notes

- The API uses Python's built-in `urllib` for HTTP requests (no external dependencies required)
- API quota: The YouTube Data API has daily quota limits. Each request consumes quota units.
- Error handling: The module will raise `ValueError` if the channel is not found or if the API key is missing.
