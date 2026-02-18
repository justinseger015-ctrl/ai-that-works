"""Example usage of the YouTube API client."""

import re
from src.youtube.youtube_client import YouTubeClient
from dotenv import load_dotenv
load_dotenv()


def main()->dict[str, str]:
    """Get the unicorn video with the highest episode number from the YouTube channel."""
    client = YouTubeClient()
    videos = client.get_recent_videos_from_handle("@boundaryml", max_results=10)
    
    # Pattern to match: 🦄 #[number]
    pattern = r'🦄 #(\d+)'
    
    # Track the video with the highest episode number
    max_episode_video = None
    max_episode_number = -1
    
    for video in videos:
        match = re.search(pattern, video.title)
        if match:
            episode_number = int(match.group(1))
            if episode_number > max_episode_number:
                max_episode_number = episode_number
                max_episode_video = video
    
    # Return the video with the highest episode number, or empty dict if none found
    if max_episode_video:
        return {max_episode_video.title: max_episode_video.url}
    return {}

if __name__ == "__main__":
    videos = main()
    for title, url in videos.items():
        print(f"{title}: {url}")

