"""Test the embeddings module."""
from unittest import mock

import numpy as np
import pytest

from src.classification.embeddings import EmbeddingService
from src.data.models import Category



@pytest.fixture
def mock_category():
    """Fixture that provides a test Category instance."""
    return Category(
        name="Test Category",
        path="/Electronics/Computers/Laptops",
        embedding_text="Electronics Computers Laptops high-performance portable computing",
        llm_description="High-performance portable computing devices for professional and personal use",
        parent_path="/Electronics/Computers",
    )


@pytest.fixture
def mock_openai_response():
    """Fixture that provides a mock OpenAI embedding response."""
    mock_response = mock.MagicMock()
    mock_response.data = [mock.MagicMock()]
    mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    return mock_response


@pytest.fixture
def mock_settings():
    """Fixture that provides mock settings."""
    mock_settings = mock.MagicMock()
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.embedding_model = "text-embedding-3-small"
    return mock_settings


@pytest.fixture
def embedding_service_no_vector_store():
    """Fixture that provides an EmbeddingService without vector store."""
    with (
        mock.patch("src.classification.embeddings.openai.OpenAI"),
        mock.patch("src.classification.embeddings.settings") as mock_settings,
        mock.patch("src.classification.embeddings.get_logger"),
    ):
        mock_settings.openai_api_key = "test-api-key"
        return EmbeddingService(use_vector_store=False)


@pytest.fixture
def embedding_service_with_vector_store():
    """Fixture that provides an EmbeddingService with vector store."""
    with (
        mock.patch("src.classification.embeddings.openai.OpenAI"),
        mock.patch("src.classification.embeddings.settings") as mock_settings,
        mock.patch("src.classification.embeddings.CategoryVectorStore") as mock_vector_store,
        mock.patch("src.classification.embeddings.get_logger"),
    ):
        mock_settings.openai_api_key = "test-api-key"
        mock_vector_store.return_value = mock.MagicMock()
        return EmbeddingService(use_vector_store=True)


@mock.patch("src.classification.embeddings.openai.OpenAI")
@mock.patch("src.classification.embeddings.settings")
@mock.patch("src.classification.embeddings.CategoryVectorStore")
@mock.patch("src.classification.embeddings.get_logger")
def test_init_with_vector_store_success(
    mock_get_logger: mock.MagicMock,
    mock_vector_store_class: mock.MagicMock,
    mock_settings: mock.MagicMock,
    mock_openai: mock.MagicMock,
):
    """Test EmbeddingService initialization with successful vector store creation."""
    ###########
    # ARRANGE #
    ###########
    mock_settings.openai_api_key = "test-api-key"
    mock_openai_client = mock.MagicMock()
    mock_openai.return_value = mock_openai_client
    mock_vector_store = mock.MagicMock()
    mock_vector_store_class.return_value = mock_vector_store
    mock_logger = mock.MagicMock()
    mock_get_logger.return_value = mock_logger

    #######
    # ACT #
    #######
    service = EmbeddingService(use_vector_store=True)

    ##########
    # ASSERT #
    ##########
    mock_openai.assert_called_once_with(api_key="test-api-key")
    assert service.client == mock_openai_client
    assert service._cache == {}
    assert service.vector_store == mock_vector_store
    mock_vector_store_class.assert_called_once_with(auto_create=True)
    # Verify logger.success was called
    mock_logger.success.assert_called_once_with("EmbeddingService using vector store for caching")


@mock.patch("src.classification.embeddings.openai.OpenAI")
@mock.patch("src.classification.embeddings.settings")
@mock.patch("src.classification.embeddings.CategoryVectorStore")
@mock.patch("src.classification.embeddings.get_logger")
def test_init_with_vector_store_failure(
    mock_get_logger: mock.MagicMock,
    mock_vector_store_class: mock.MagicMock,
    mock_settings: mock.MagicMock,
    mock_openai: mock.MagicMock,
):
    """Test EmbeddingService initialization with vector store creation failure."""
    ###########
    # ARRANGE #
    ###########
    mock_settings.openai_api_key = "test-api-key"
    mock_openai_client = mock.MagicMock()
    mock_openai.return_value = mock_openai_client
    mock_vector_store_class.side_effect = Exception("Vector store initialization failed")
    mock_logger = mock.MagicMock()
    mock_get_logger.return_value = mock_logger

    #######
    # ACT #
    #######
    service = EmbeddingService(use_vector_store=True)

    ##########
    # ASSERT #
    ##########
    mock_openai.assert_called_once_with(api_key="test-api-key")
    assert service.client == mock_openai_client
    assert service._cache == {}
    assert service.vector_store is None
    mock_vector_store_class.assert_called_once_with(auto_create=True)
    mock_logger.warning.assert_called_once_with(
        "EmbeddingService failed to load vector store: Vector store initialization failed"
    )


@mock.patch("src.classification.embeddings.settings")
@mock.patch("src.classification.embeddings.openai.OpenAI")
def test_init_without_vector_store(mock_openai: mock.MagicMock, mock_settings: mock.MagicMock):
    """Test EmbeddingService initialization without vector store."""
    ###########
    # ARRANGE #
    ###########
    mock_settings.openai_api_key = "test-api-key"
    mock_openai_client = mock.MagicMock()
    mock_openai.return_value = mock_openai_client

    #######
    # ACT #
    #######
    service = EmbeddingService(use_vector_store=False)

    ##########
    # ASSERT #
    ##########
    mock_openai.assert_called_once_with(api_key="test-api-key")
    assert service.client == mock_openai_client
    assert service._cache == {}
    assert service.vector_store is None


def test_embed_text_cache_hit(embedding_service_no_vector_store: EmbeddingService):
    """Test embed_text returns cached embedding when available."""
    ###########
    # ARRANGE #
    ###########
    test_text = "test text"
    cached_embedding = [0.1, 0.2, 0.3]
    embedding_service_no_vector_store._cache[test_text] = cached_embedding

    ###########
    #   ACT   #
    ###########
    result = embedding_service_no_vector_store.embed_text(test_text)

    ##########
    # ASSERT #
    ##########
    assert result == cached_embedding
    # Ensure OpenAI client wasn't called
    embedding_service_no_vector_store.client.embeddings.create.assert_not_called()


@mock.patch("src.classification.embeddings.settings")
def test_embed_text_cache_miss(
    mock_settings: mock.MagicMock,
    embedding_service_no_vector_store: EmbeddingService,
    mock_openai_response: mock.MagicMock,
):
    """Test embed_text generates new embedding when not cached."""
    ###########
    # ARRANGE #
    ###########
    test_text = "test text"
    mock_settings.embedding_model = "text-embedding-3-small"
    embedding_service_no_vector_store.client.embeddings.create.return_value = mock_openai_response
    expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.embed_text(test_text)

    ##########
    # ASSERT #
    ##########
    assert result == expected_embedding
    embedding_service_no_vector_store.client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small", input=test_text
    )
    # Verify embedding was cached
    assert embedding_service_no_vector_store._cache[test_text] == expected_embedding


def test_embed_category_vector_store_cache_hit(
    embedding_service_with_vector_store: EmbeddingService, mock_category: Category
):
    """Test embed_category returns vector store cached embedding when available."""
    ###########
    # ARRANGE #
    ###########
    cached_embedding = [0.7, 0.8, 0.9]
    embedding_service_with_vector_store.vector_store.has_category.return_value = True
    embedding_service_with_vector_store.vector_store.get_cached_embedding.return_value = cached_embedding

    #######
    # ACT #
    #######
    result = embedding_service_with_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == cached_embedding
    embedding_service_with_vector_store.vector_store.has_category.assert_called_once_with(mock_category.path)
    embedding_service_with_vector_store.vector_store.get_cached_embedding.assert_called_once_with(mock_category.path)


def test_embed_category_memory_cache_hit(
    embedding_service_with_vector_store: EmbeddingService, mock_category: Category
):
    """Test embed_category returns memory cached embedding when vector store cache misses."""
    ###########
    # ARRANGE #
    ###########
    cached_embedding = [0.4, 0.5, 0.6]
    embedding_service_with_vector_store.vector_store.has_category.return_value = False
    embedding_service_with_vector_store._cache[mock_category.embedding_text] = cached_embedding
    embedding_service_with_vector_store.vector_store.add_category = mock.MagicMock()

    #######
    # ACT #
    #######
    result = embedding_service_with_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == cached_embedding
    # has_category should be called twice - once for cache check, once before adding
    assert embedding_service_with_vector_store.vector_store.has_category.call_count == 2
    # get_cached_embedding should not be called since has_category returned False
    embedding_service_with_vector_store.vector_store.get_cached_embedding.assert_not_called()
    embedding_service_with_vector_store.vector_store.add_category.assert_called_once_with(
        mock_category, cached_embedding
    )
    # Verify logger.info was called
    embedding_service_with_vector_store.logger.info.assert_called_once_with(
        f"Added category to vector store: {mock_category.path}"
    )


@mock.patch("src.classification.embeddings.EmbeddingService.embed_text")
def test_embed_category_generate_new_embedding(
    mock_embed_text: mock.MagicMock,
    embedding_service_with_vector_store: EmbeddingService,
    mock_category: Category,
):
    """Test embed_category generates new embedding when not in any cache."""
    ###########
    # ARRANGE #
    ###########
    new_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    embedding_service_with_vector_store.vector_store.has_category.return_value = False
    embedding_service_with_vector_store.vector_store.get_cached_embedding.return_value = None
    mock_embed_text.return_value = new_embedding
    embedding_service_with_vector_store.vector_store.add_category = mock.MagicMock()

    #######
    # ACT #
    #######
    result = embedding_service_with_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == new_embedding
    mock_embed_text.assert_called_once_with(mock_category.embedding_text)
    embedding_service_with_vector_store.vector_store.add_category.assert_called_once_with(mock_category, new_embedding)
    # Verify logger.info was called
    embedding_service_with_vector_store.logger.info.assert_called_once_with(
        f"Added category to vector store: {mock_category.path}"
    )


def test_embed_category_vector_store_add_failure(
    embedding_service_with_vector_store: EmbeddingService, mock_category: Category
):
    """Test embed_category handles vector store add failure gracefully."""
    ###########
    # ARRANGE #
    ###########
    cached_embedding = [0.4, 0.5, 0.6]
    embedding_service_with_vector_store.vector_store.has_category.return_value = False
    embedding_service_with_vector_store._cache[mock_category.embedding_text] = cached_embedding
    embedding_service_with_vector_store.vector_store.add_category.side_effect = Exception("Add failed")

    #######
    # ACT #
    #######
    result = embedding_service_with_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == cached_embedding
    embedding_service_with_vector_store.vector_store.add_category.assert_called_once_with(
        mock_category, cached_embedding
    )
    # Verify logger.warning was called
    embedding_service_with_vector_store.logger.warning.assert_called_once_with(
        "Failed to add category to vector store: Add failed"
    )


def test_embed_category_no_vector_store(embedding_service_no_vector_store: EmbeddingService, mock_category: Category):
    """Test embed_category works correctly without vector store."""
    ###########
    # ARRANGE #
    ###########
    cached_embedding = [0.4, 0.5, 0.6]
    embedding_service_no_vector_store._cache[mock_category.embedding_text] = cached_embedding

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == cached_embedding


@mock.patch("src.classification.embeddings.EmbeddingService.embed_text")
def test_embed_category_no_vector_store_generate_new(
    mock_embed_text: mock.MagicMock,
    embedding_service_no_vector_store: EmbeddingService,
    mock_category: Category,
):
    """Test embed_category generates new embedding without vector store."""
    ###########
    # ARRANGE #
    ###########
    new_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_embed_text.return_value = new_embedding

    ###########
    #   ACT   #
    ###########
    result = embedding_service_no_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == new_embedding
    mock_embed_text.assert_called_once_with(mock_category.embedding_text)


def test_embed_category_vector_store_has_category_already(
    embedding_service_with_vector_store: EmbeddingService, mock_category: Category
):
    """Test embed_category doesn't add to vector store if category already exists."""
    ###########
    # ARRANGE #
    ###########
    cached_embedding = [0.4, 0.5, 0.6]
    # First call returns False (not in vector store), second call returns True (already added)
    embedding_service_with_vector_store.vector_store.has_category.side_effect = [
        False,
        True,
    ]
    embedding_service_with_vector_store._cache[mock_category.embedding_text] = cached_embedding

    #######
    # ACT #
    #######
    result = embedding_service_with_vector_store.embed_category(mock_category)

    ##########
    # ASSERT #
    ##########
    assert result == cached_embedding
    # has_category should be called twice - once for cache check, once before adding
    assert embedding_service_with_vector_store.vector_store.has_category.call_count == 2
    embedding_service_with_vector_store.vector_store.add_category.assert_not_called()


@mock.patch("src.classification.embeddings.np.linalg.norm")
@mock.patch("src.classification.embeddings.np.dot")
def test_compute_similarity(
    mock_dot: mock.MagicMock,
    mock_norm: mock.MagicMock,
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test compute_similarity calculates cosine similarity correctly."""
    ###########
    # ARRANGE #
    ###########
    embedding1 = [1.0, 0.0, 0.0]
    embedding2 = [0.0, 1.0, 0.0]
    mock_dot.return_value = 0.0
    mock_norm.side_effect = [1.0, 1.0]  # Norms of the two embeddings

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.compute_similarity(embedding1, embedding2)

    ##########
    # ASSERT #
    ##########
    assert result == 0.0
    mock_dot.assert_called_once_with(embedding1, embedding2)
    assert mock_norm.call_count == 2
    mock_norm.assert_any_call(embedding1)
    mock_norm.assert_any_call(embedding2)


def test_compute_similarity_identical_embeddings(
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test compute_similarity returns 1.0 for identical embeddings."""
    ###########
    # ARRANGE #
    ###########
    embedding = [1.0, 2.0, 3.0]

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.compute_similarity(embedding, embedding)

    ##########
    # ASSERT #
    ##########
    # Should be very close to 1.0 (allowing for floating point precision)
    assert abs(result - 1.0) < 1e-10


def test_compute_similarity_orthogonal_embeddings(
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test compute_similarity returns 0.0 for orthogonal embeddings."""
    ###########
    # ARRANGE #
    ###########
    embedding1 = [1.0, 0.0, 0.0]
    embedding2 = [0.0, 1.0, 0.0]

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.compute_similarity(embedding1, embedding2)

    ##########
    # ASSERT #
    ##########
    # Should be very close to 0.0 (allowing for floating point precision)
    assert abs(result) < 1e-10


def test_compute_similarity_opposite_embeddings(
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test compute_similarity returns -1.0 for opposite embeddings."""
    ###########
    # ARRANGE #
    ###########
    embedding1 = [1.0, 0.0, 0.0]
    embedding2 = [-1.0, 0.0, 0.0]

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.compute_similarity(embedding1, embedding2)

    ##########
    # ASSERT #
    ##########
    # Should be very close to -1.0 (allowing for floating point precision)
    assert abs(result - (-1.0)) < 1e-10


def test_compute_similarity_real_embeddings(
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test compute_similarity with realistic embedding vectors."""
    ###########
    # ARRANGE #
    ###########
    # Two similar but not identical embeddings
    embedding1 = [0.1, 0.2, 0.3, 0.4, 0.5]
    embedding2 = [0.15, 0.25, 0.35, 0.45, 0.55]

    #######
    # ACT #
    #######
    result = embedding_service_no_vector_store.compute_similarity(embedding1, embedding2)

    ##########
    # ASSERT #
    ##########
    # Should be a positive value close to 1 (similar embeddings)
    assert 0.9 < result < 1.0


@mock.patch("src.classification.embeddings.np.linalg.norm")
@mock.patch("src.classification.embeddings.np.dot")
def test_compute_similarity_zero_norm_handling(
    mock_dot: mock.MagicMock,
    mock_norm: mock.MagicMock,
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test compute_similarity handles zero norm embeddings (edge case)."""
    ###########
    # ARRANGE #
    ###########
    embedding1 = [0.0, 0.0, 0.0]
    embedding2 = [1.0, 0.0, 0.0]
    mock_dot.return_value = 0.0
    mock_norm.side_effect = [0.0, 1.0]  # First embedding has zero norm

    #######
    # ACT #
    #######
    # This should raise a ZeroDivisionError or return inf/nan
    try:
        result = embedding_service_no_vector_store.compute_similarity(embedding1, embedding2)
        # If no exception, check if result is inf or nan
        assert np.isinf(result) or np.isnan(result)
    except ZeroDivisionError:
        # This is also acceptable behavior
        pass

    ##########
    # ASSERT #
    ##########
    mock_dot.assert_called_once_with(embedding1, embedding2)
    assert mock_norm.call_count == 2


def test_cache_persistence_across_calls(
    embedding_service_no_vector_store: EmbeddingService,
):
    """Test that cache persists across multiple calls."""
    ###########
    # ARRANGE #
    ###########
    test_text = "persistent cache test"
    mock_response = mock.MagicMock()
    mock_response.data = [mock.MagicMock()]
    mock_response.data[0].embedding = [0.1, 0.2, 0.3]
    embedding_service_no_vector_store.client.embeddings.create.return_value = mock_response

    #######
    # ACT #
    #######
    # First call should hit API
    result1 = embedding_service_no_vector_store.embed_text(test_text)
    # Second call should hit cache
    result2 = embedding_service_no_vector_store.embed_text(test_text)

    ##########
    # ASSERT #
    ##########
    assert result1 == result2
    assert result1 == [0.1, 0.2, 0.3]
    # OpenAI client should only be called once
    embedding_service_no_vector_store.client.embeddings.create.assert_called_once()
    # Verify cache contains the embedding
    assert test_text in embedding_service_no_vector_store._cache
    assert embedding_service_no_vector_store._cache[test_text] == [0.1, 0.2, 0.3]
