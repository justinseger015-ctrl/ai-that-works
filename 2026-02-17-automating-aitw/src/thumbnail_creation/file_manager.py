"""File management for thumbnail creation."""

from pathlib import Path
from PIL import Image


class FileManager:
    """Handles file persistence operations for thumbnails."""
    
    def save_image(self, image: Image.Image, output_path: Path) -> Path:
        """
        Save a PIL Image to disk.
        
        Creates parent directories if they don't exist.
        
        Args:
            image: PIL Image to save
            output_path: Path where the image should be saved
            
        Returns:
            Path to the saved image
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the image
        image.save(output_path, "PNG")
        
        return output_path

