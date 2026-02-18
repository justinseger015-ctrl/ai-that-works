"""Configuration management for thumbnail creation."""

import os
from pathlib import Path


class ThumbnailConfig:
    """Manages configuration and paths for thumbnail generation."""
    
    def __init__(self, base_dir: Path | None = None):
        """
        Initialize configuration.
        
        Args:
            base_dir: Base directory for the module. Defaults to this file's directory.
        """
        self.base_dir = base_dir or Path(__file__).parent
        self.base_thumbnail_path = self.base_dir / "base_thumbnail.png"
        self.prompt_path = self.base_dir / "prompt.txt"
        self.output_dir = self.base_dir / "output"
        
    def get_google_api_key(self) -> str:
        """
        Get Google API key from environment.
        
        Returns:
            The Google API key
            
        Raises:
            ValueError: If GOOGLE_API_KEY is not set
        """
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        return api_key
    
    def get_output_path(self, episode_number: str) -> Path:
        """
        Get the default output path for a given episode number.
        
        Args:
            episode_number: The episode number
            
        Returns:
            Path to save the thumbnail
        """
        return self.output_dir / f"thumbnail_ep{episode_number}.png"

