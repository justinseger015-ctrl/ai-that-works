"""Main entry point for the classification pipeline."""

import dotenv

from src.classification.pipeline import ClassificationPipeline
from src.shared.logger import get_logger

dotenv.load_dotenv()

logger = get_logger(__name__)
logger.info("Initializing classification pipeline")

pipeline = ClassificationPipeline()

TEXT_SAMPLE_LENGTH = 50

if __name__ == "__main__":
    text = input("Enter a text: ")
    logger.processing(
        f"Classifying text: '{text[:TEXT_SAMPLE_LENGTH]}{'...' if len(text) > TEXT_SAMPLE_LENGTH else ''}'"
    )

    result = pipeline.classify(text)

    logger.success(f"Classification completed in {result.processing_time_ms:.2f}ms")
    print(f"Selected: {result.category.name}")
    print(f"Processing time: {result.processing_time_ms:.2f}ms")
    print(f"Candidates: {[cat.name for cat in result.candidates]}")
    print(f"Metadata: {result.metadata}")
