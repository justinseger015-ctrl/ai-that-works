"""Image processing utilities for thumbnail creation."""

from io import BytesIO
from PIL import Image


class ImageProcessor:
    """Handles image data processing and conversion."""
    
    def bytes_to_image(self, image_bytes: bytes) -> Image.Image:
        """
        Convert raw image bytes to a PIL Image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            PIL Image object
        """
        return Image.open(BytesIO(image_bytes))
    
    def convert_to_rgb(self, image: Image.Image) -> Image.Image:
        """
        Convert an image to RGB format if needed.
        
        Handles RGBA images by creating a black background and pasting
        the image with alpha channel as a mask.
        
        Args:
            image: PIL Image to convert
            
        Returns:
            PIL Image in RGB format
        """
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (0, 0, 0))
            background.paste(image, mask=image.split()[3])
            return background
        
        return image
    
    def process_image_bytes(self, image_bytes: bytes) -> Image.Image:
        """
        Process raw image bytes into a ready-to-save PIL Image.
        
        Combines bytes_to_image and convert_to_rgb operations.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            PIL Image in RGB format, ready to save
        """
        image = self.bytes_to_image(image_bytes)
        return self.convert_to_rgb(image)

