"""ChromaDB vector store utilities for category similarity search."""

import pathlib
import time
from typing import Any

import chromadb
import openai
from chromadb.config import Settings as ChromaSettings

from src.config.settings import settings
from src.data.models import Category
from src.shared import constants as C
from src.shared.logger import get_logger

VECTOR_STORE_PATH = pathlib.Path(__file__).parents[2] / C.DATA / C.VECTOR_STORE
COLLECTION_NAME = C.CATEGORIES


class CategoryVectorStore:
    """Interface to the ChromaDB vector store for category similarity search."""

    def __init__(self, auto_create: bool = False) -> None:
        """Initialize the CategoryVectorStore.

        Args:
            auto_create: Whether to create the vector store if it doesn't exist.
        """
        self.client = None
        self.collection = None
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self._category_cache = {}  # Cache path -> id mapping
        self.logger = get_logger(__name__)
        self._load_vector_store(auto_create)

    @staticmethod
    def is_available() -> bool:
        """Check if the vector store is available."""
        try:
            store = CategoryVectorStore()
            return store.collection is not None
        except (FileNotFoundError, ValueError):
            return False

    def _load_vector_store(self, auto_create: bool = False) -> None:
        """Load the ChromaDB vector store.

        Args:
            auto_create: Whether to create the vector store if it doesn't exist.
        """
        if not VECTOR_STORE_PATH.exists():
            if auto_create:
                VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(
                    f"Vector store not found at {VECTOR_STORE_PATH}. "
                    "Please run 'python scripts/build_vector_store.py' first."
                )
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_PATH),
            settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True),
        )
        try:
            self.collection = self.client.get_collection(COLLECTION_NAME)
            self._validate_embedding_model()
            self._build_category_cache()
        except ValueError:
            if auto_create:
                self._create_collection()
            else:
                raise ValueError(
                    f"Collection '{COLLECTION_NAME}' not found in vector store. "
                    "Please run 'python scripts/build_vector_store.py' first."
                )

    def _validate_embedding_model(self) -> None:
        """Validate that the vector store uses the same embedding model as the current configuration."""
        if self.collection is None:
            return
        metadata = self.collection.metadata
        stored_model = metadata.get(C.EMBEDDING_MODEL)
        current_model = settings.embedding_model
        if stored_model and stored_model != current_model:
            raise ValueError(
                f"Vector store was created with embedding model '{stored_model}' "
                f"but current configuration uses '{current_model}'. "
                f"Please rebuild the vector store with 'python scripts/build_vector_store.py --force-rebuild'"
            )

    def _create_collection(self) -> None:
        """Create a new collection with current settings."""
        if self.client is None:
            raise RuntimeError("Vector store not loaded")
        self.logger.info(f"Creating new collection '{COLLECTION_NAME}'...")
        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                C.DESCRIPTION: "Product categories with OpenAI embeddings",
                C.EMBEDDING_MODEL: settings.embedding_model,
                C.CREATED_AT: time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    def _build_category_cache(self) -> None:
        """Build cache of existing categories for fast lookup."""
        if self.collection is None:
            return
        results = self.collection.get()
        for doc_id, metadata in zip(results[C.IDS], results[C.METADATA]):
            if metadata and C.PATH in metadata:
                self._category_cache[metadata[C.PATH]] = doc_id

    def find_similar_categories(
        self,
        query_embedding: list[float],
        n_results: int = 10,
    ) -> list[Category]:
        """Find the most similar categories to a query embedding.

        Args:
            query_embedding: The embedding to search for similar categories.
            n_results: Maximum number of results to return.

        Returns:
            List of Category objects sorted by similarity (most similar first).
        """
        if self.collection is None:
            raise RuntimeError("Vector store not loaded")
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        categories = []
        documents = results[C.DOCUMENTS][0]
        metadatas = results[C.METADATA][0]
        for doc, metadata in zip(documents, metadatas):
            category = Category(
                path=metadata[C.PATH],
                name=metadata[C.NAME],
                embedding_text=doc,
                llm_description=metadata[C.LLM_DESCRIPTION],
            )
            categories.append(category)

        return categories

    def get_cached_embedding(self, category_path: str) -> list[float] | None:
        """Get cached embedding for a category if it exists.

        Args:
            category_path: The category path to look up.

        Returns:
            The cached embedding if found, None otherwise.
        """
        if self.collection is None or category_path not in self._category_cache:
            return None
        doc_id = self._category_cache[category_path]
        result = self.collection.get(ids=[doc_id], include=[C.EMBEDDINGS])
        if result[C.EMBEDDINGS] is not None and len(result[C.EMBEDDINGS]) > 0:
            return result[C.EMBEDDINGS][0]
        return None

    def add_category(self, category: Category, embedding: list[float]) -> str:
        """Add a new category to the vector store.

        Args:
            category: The category to add.
            embedding: The category's embedding.

        Returns:
            The ID assigned to the category.
        """
        if self.collection is None:
            raise RuntimeError("Vector store not loaded")
        doc_id = f"cat_{int(time.time() * 1000)}_{hash(category.path) % 10000}"
        self.collection.add(
            embeddings=[embedding],
            documents=[category.embedding_text],
            metadatas=[
                {
                    C.PATH: category.path,
                    C.NAME: category.name,
                    C.LLM_DESCRIPTION: category.llm_description,
                    C.CREATED_AT: time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ],
            ids=[doc_id],
        )
        self._category_cache[category.path] = doc_id

        return doc_id

    def has_category(self, category_path: str) -> bool:
        """Check if a category exists in the vector store.

        Args:
            category_path: The category path to check.

        Returns:
            True if the category exists, False otherwise.
        """
        return category_path in self._category_cache

    def get_collection_info(self) -> dict[str, Any]:
        """Get information about the vector store collection."""
        if self.collection is None:
            raise RuntimeError("Vector store not loaded")
        count = self.collection.count()
        metadata = self.collection.metadata
        return {
            C.NAME: COLLECTION_NAME,
            C.COUNT: count,
            C.METADATA: metadata,
            C.PATH: str(VECTOR_STORE_PATH),
        }
