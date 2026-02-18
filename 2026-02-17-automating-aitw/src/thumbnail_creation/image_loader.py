"""Image loading functionality for thumbnail creation."""

import base64
from pathlib import Path


class ImageLoader:
    """Handles loading and encoding of images."""
    
    def load_as_base64(self, image_path: Path) -> str:
        """
        Load an image file and encode it as base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64-encoded string of the image
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            return base64.b64encode(image_bytes).decode("utf-8")

