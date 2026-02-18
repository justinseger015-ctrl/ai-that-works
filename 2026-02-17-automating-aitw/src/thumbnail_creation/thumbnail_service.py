"""Thumbnail generation service - orchestrates all components."""

import sys
from pathlib import Path

# Handle both direct script execution and module import
try:
    from .config import ThumbnailConfig
    from .image_loader import ImageLoader
    from .prompt_formatter import PromptFormatter
    from .gemini_client import GeminiImageGenerator
    from .image_processor import ImageProcessor
    from .file_manager import FileManager
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import ThumbnailConfig
    from image_loader import ImageLoader
    from prompt_formatter import PromptFormatter
    from gemini_client import GeminiImageGenerator
    from image_processor import ImageProcessor
    from file_manager import FileManager


class ThumbnailService:
    """
    Orchestrates thumbnail generation workflow.
    
    This is a facade that coordinates all the individual components
    to generate podcast thumbnails.
    """
    
    def __init__(self, config: ThumbnailConfig | None = None):
        """
        Initialize the thumbnail service with all required components.
        
        Args:
            config: Optional ThumbnailConfig. If not provided, uses defaults.
        """
        self.config = config or ThumbnailConfig()
        self.image_loader = ImageLoader()
        self.prompt_formatter = PromptFormatter(self.config.prompt_path)
        self.image_processor = ImageProcessor()
        self.file_manager = FileManager()
        
        # Initialize Gemini client with API key from config
        api_key = self.config.get_google_api_key()
        self.gemini_client = GeminiImageGenerator(api_key)
    
    def generate_thumbnail(
        self,
        title: str,
        subtitle: str,
        episode_number: str,
        output_path: Path | None = None,
        image_feedback: str | None = None,
    ) -> Path:
        """
        Generate a podcast thumbnail.

        This method orchestrates the entire workflow:
        1. Load base image as base64
        2. Format the prompt with episode details and feedback
        3. Send to Gemini API for image generation
        4. Process the returned image bytes
        5. Save to disk

        Args:
            title: The episode title
            subtitle: The episode subtitle
            episode_number: The episode number (e.g., "42")
            output_path: Optional custom output path. If not provided,
                        uses default path based on episode number.
            image_feedback: Optional feedback for image regeneration

        Returns:
            Path to the saved thumbnail

        Raises:
            ValueError: If GOOGLE_API_KEY is not set or if Gemini fails to generate an image
            FileNotFoundError: If base thumbnail or prompt template is missing
        """
        # Step 1: Load base image
        base_image_base64 = self.image_loader.load_as_base64(
            self.config.base_thumbnail_path
        )

        # Step 2: Format prompt with optional feedback
        prompt = self.prompt_formatter.format(
            title, subtitle, episode_number, feedback=image_feedback
        )

        # Step 3: Generate image via Gemini
        image_bytes = self.gemini_client.generate_image(prompt, base_image_base64)

        # Step 4: Process image bytes
        image = self.image_processor.process_image_bytes(image_bytes)

        # Step 5: Determine output path and save
        if output_path is None:
            output_path = self.config.get_output_path(episode_number)

        saved_path = self.file_manager.save_image(image, output_path)

        print(f"Saved thumbnail to: {saved_path}")

        return saved_path

