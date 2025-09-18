#!/usr/bin/env python3
"""Script to build a ChromaDB vector store from categories.txt.

This script reads the categories.txt file, generates embeddings for each category
using the configured OpenAI embedding model, and stores them in a ChromaDB vector
database for fast similarity search.

Usage:
    python scripts/build_vector_store.py [--force-rebuild]
"""

import argparse
import pathlib
import time

import chromadb
import openai
from chromadb.config import Settings as ChromaSettings

from src.config.settings import settings
from src.data.category_loader import CategoryLoader
from src.shared import constants as C

# Vector store configuration
COLLECTION_NAME = C.CATEGORIES
VECTOR_STORE_PATH = pathlib.Path(__file__).parents[1] / C.DATA / C.VECTOR_STORE


class VectorStoreBuilder:
    """Builds and manages the ChromaDB vector store for categories."""

    def __init__(self, force_rebuild: bool = False):
        """Initialize the VectorStoreBuilder.

        Args:
            force_rebuild: Whether to force rebuild the vector store. Defaults to False.
        """
        self.force_rebuild = force_rebuild
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_PATH),
            settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True),
        )
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)

    def build_vector_store(self) -> None:
        """Build the vector store from categories.txt."""
        print(f"Building vector store at: {VECTOR_STORE_PATH}")

        # Check if collection already exists
        existing_collections = [col.name for col in self.client.list_collections()]

        if COLLECTION_NAME in existing_collections:
            if not self.force_rebuild:
                print(f"Collection '{COLLECTION_NAME}' already exists. Use --force-rebuild to recreate.")
                return
            else:
                print(f"Deleting existing collection '{COLLECTION_NAME}'...")
                self.client.delete_collection(COLLECTION_NAME)

        # Create collection
        print(f"Creating collection '{COLLECTION_NAME}'...")
        collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "Product categories with OpenAI embeddings",
                "embedding_model": settings.embedding_model,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
            },
        )

        # Load categories
        print("Loading categories...")
        category_loader = CategoryLoader()
        categories = category_loader.load_categories()
        print(f"Loaded {len(categories)} categories")

        # Generate embeddings and add to collection in batches
        batch_size = 100  # Process in batches to avoid rate limits
        total_batches = (len(categories) + batch_size - 1) // batch_size

        for batch_idx in range(0, len(categories), batch_size):
            batch_end = min(batch_idx + batch_size, len(categories))
            batch_categories = categories[batch_idx:batch_end]

            print(
                f"Processing batch {batch_idx // batch_size + 1}/{total_batches} "
                f"({len(batch_categories)} categories)..."
            )

            # Generate embeddings for this batch
            embeddings = self._generate_embeddings([cat.embedding_text for cat in batch_categories])

            # Prepare data for ChromaDB
            ids = [f"cat_{i}" for i in range(batch_idx, batch_end)]
            documents = [cat.embedding_text for cat in batch_categories]
            metadatas = [
                {
                    "path": cat.path,
                    "name": cat.name,
                    "level": cat.level,
                    "llm_description": cat.llm_description,
                }
                for cat in batch_categories
            ]

            # Add to collection
            collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

            # Rate limiting - small delay between batches
            if batch_idx + batch_size < len(categories):
                time.sleep(0.5)

        print(f"✅ Successfully built vector store with {len(categories)} categories")
        print(f"📁 Vector store saved to: {VECTOR_STORE_PATH}")

    def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        try:
            response = self.openai_client.embeddings.create(model=settings.embedding_model, input=texts)
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            raise


def main():
    """Build the vector store from categories.txt."""
    parser = argparse.ArgumentParser(description="Build ChromaDB vector store from categories.txt")
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild even if vector store already exists",
    )

    args = parser.parse_args()

    builder = VectorStoreBuilder(force_rebuild=args.force_rebuild)
    builder.build_vector_store()


if __name__ == "__main__":
    main()
