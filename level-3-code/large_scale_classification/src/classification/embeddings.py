"""OpenAI embedding service with caching and error handling."""

import numpy as np
import openai

from src.classification.vector_store import CategoryVectorStore
from src.config.settings import settings
from src.data.models import Category
from src.shared.logger import get_logger


class EmbeddingService:
    """Handles OpenAI embedding operations with caching."""

    def __init__(self, use_vector_store: bool = True) -> None:
        """Initialize the EmbeddingService.

        Args:
            use_vector_store: Whether to use the vector store for caching. Defaults to True.
        """
        self.logger = get_logger(__name__)
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self._cache: dict[str, list[float]] = {}
        self.vector_store: CategoryVectorStore | None = None
        if use_vector_store:
            try:
                self.vector_store = CategoryVectorStore(auto_create=True)
                self.logger.success("EmbeddingService using vector store for caching")
            except Exception as e:
                self.logger.warning(f"EmbeddingService failed to load vector store: {e}")
                self.vector_store = None

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text.

        Args:
            text: The text to embed.

        Returns:
            The embedding of the text.
        """
        if text in self._cache:
            return self._cache[text]
        response = self.client.embeddings.create(
            model=settings.embedding_model,
            input=text,
        )
        embedding = response.data[0].embedding
        self._cache[text] = embedding
        return embedding

    def embed_category(self, category: Category) -> list[float]:
        """Embed a category with vector store.

        If the category is already in the vector store, return the cached embedding.
        If the category is not in the vector store, generate a new embedding and add
            it to the vector store.

        Args:
            category: The category to embed.

        Returns:
            The embedding of the category.
        """
        if self.vector_store and self.vector_store.has_category(category.path):
            embedding = self.vector_store.get_cached_embedding(category.path)
            if embedding is not None:
                return embedding
        if category.embedding_text in self._cache:
            embedding = self._cache[category.embedding_text]
        else:
            embedding = self.embed_text(category.embedding_text)
        if self.vector_store and not self.vector_store.has_category(category.path):
            try:
                self.vector_store.add_category(category, embedding)
                self.logger.info(f"Added category to vector store: {category.path}")
            except Exception as e:
                self.logger.warning(f"Failed to add category to vector store: {e}")

        return embedding

    def compute_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Compute cosine similarity between embeddings.

        Args:
            embedding1: The first embedding.
            embedding2: The second embedding.

        Returns:
            The cosine similarity between the two embeddings.
        """
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
