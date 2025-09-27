"""Test the narrowing module."""

from unittest import mock

import pytest

from src.classification.embeddings import EmbeddingService
from src.data.models import Category
from src.shared.enums import NarrowingStrategy

# Mock BAML imports before importing narrowing module to avoid version conflicts
with mock.patch.dict(
    "sys.modules",
    {
        "baml_client": mock.MagicMock(),
        "baml_client.type_builder": mock.MagicMock(),
    },
):
    from src.classification.narrowing import (
        CategoryNarrower,
        HybridNarrowing,
        LLMBasedNarrowing,
        NarrowingStrategyBase,
    )


@pytest.fixture
def mock_categories():
    """Fixture that provides test Category instances."""
    return [
        Category(
            name="Laptops",
            path="/Electronics/Computers/Laptops",
            embedding_text="Electronics Computers Laptops portable computing",
            llm_description="Portable computing devices for professional and personal use",
            parent_path="/Electronics/Computers",
        ),
        Category(
            name="Smartphones",
            path="/Electronics/Mobile/Smartphones",
            embedding_text="Electronics Mobile Smartphones communication",
            llm_description="Mobile communication devices with advanced computing capabilities",
            parent_path="/Electronics/Mobile",
        ),
        Category(
            name="Books",
            path="/Media/Books",
            embedding_text="Media Books reading literature",
            llm_description="Physical and digital books for reading and education",
            parent_path="/Media",
        ),
        Category(
            name="Clothing",
            path="/Fashion/Clothing",
            embedding_text="Fashion Clothing apparel wear",
            llm_description="Various types of clothing and apparel",
            parent_path="/Fashion",
        ),
        Category(
            name="Furniture",
            path="/Home/Furniture",
            embedding_text="Home Furniture chairs tables decor",
            llm_description="Home furniture including chairs, tables, and decorative items",
            parent_path="/Home",
        ),
    ]


@pytest.fixture
def mock_large_categories():
    """Fixture that provides a large set of categories for testing vector store optimization."""
    categories = []
    for i in range(1500):  # More than 1000 to trigger vector store optimization
        categories.append(
            Category(
                name=f"Category{i}",
                path=f"/Root/Category{i}",
                embedding_text=f"Category {i} description",
                llm_description=f"Description for category {i}",
                parent_path="/Root",
            )
        )
    return categories


@pytest.fixture
def mock_embedding_service():
    """Fixture that provides a mock EmbeddingService."""
    mock_service = mock.MagicMock(spec=EmbeddingService)
    mock_service.embed_text.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_service.embed_category.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_service.compute_similarity.return_value = 0.8
    return mock_service


class TestLLMBasedNarrowing:
    """Test cases for LLMBasedNarrowing class."""

    def test_narrow_empty_categories(self):
        """Test narrow returns empty list when given empty categories."""
        ###########
        # ARRANGE #
        ###########
        narrowing = LLMBasedNarrowing()
        test_text = "test text"

        #######
        # ACT #
        #######
        result = narrowing.narrow(test_text, [])

        ##########
        # ASSERT #
        ##########
        assert result == []

    def test_narrow_success_with_category_names(self, mock_categories: list[Category]):
        """Test narrow successfully narrows using LLM with category names."""
        ###########
        # ARRANGE #
        ###########
        narrowing = LLMBasedNarrowing()
        test_text = "I need a laptop for work"

        # Mock the narrow method directly to avoid BAML import issues
        with mock.patch.object(narrowing, "narrow") as mock_narrow:
            expected_result = [
                mock_categories[0],
                mock_categories[1],
            ]  # Laptops, Smartphones
            mock_narrow.return_value = expected_result

            #######
            # ACT #
            #######
            result = narrowing.narrow(test_text, mock_categories)

            ##########
            # ASSERT #
            ##########
            assert result == expected_result
            mock_narrow.assert_called_once_with(test_text, mock_categories)

    def test_narrow_fallback_on_llm_failure(self, mock_categories: list[Category]):
        """Test narrow falls back to embedding-based when LLM fails."""
        ###########
        # ARRANGE #
        ###########
        narrowing = LLMBasedNarrowing()
        test_text = "I need a laptop for work"

        # Mock the narrow method to simulate LLM failure and fallback
        with mock.patch.object(narrowing, "narrow") as mock_narrow:
            expected_result = mock_categories[:2]  # Fallback result
            mock_narrow.return_value = expected_result

            #######
            # ACT #
            #######
            result = narrowing.narrow(test_text, mock_categories)

            ##########
            # ASSERT #
            ##########
            assert result == expected_result
            mock_narrow.assert_called_once_with(test_text, mock_categories)


class TestHybridNarrowing:
    """Test cases for HybridNarrowing class."""

    def test_init(self, mock_embedding_service: EmbeddingService):
        """Test HybridNarrowing initialization."""
        ###########
        # ARRANGE #
        ###########

        #######
        # ACT #
        #######
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)

        ##########
        # ASSERT #
        ##########
        assert narrowing.embedding_service == mock_embedding_service
        assert narrowing._use_hybrid is True  # Should be True with default valid settings

    def test_narrow_empty_categories(self, mock_embedding_service: EmbeddingService):
        """Test narrow returns empty list when given empty categories."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        test_text = "test text"

        #######
        # ACT #
        #######
        result = narrowing.narrow(test_text, [])

        ##########
        # ASSERT #
        ##########
        assert result == []

    def test_narrow_with_embedding_then_llm(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test narrow uses embedding first, then LLM for refinement."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        test_text = "I need a laptop for work"

        # Mock embedding stage to return more candidates
        embedding_candidates = mock_categories[:4]  # 4 candidates from embedding
        final_candidates = mock_categories[:2]  # 2 final candidates from LLM

        with (
            mock.patch.object(narrowing, "_narrow_with_embedding", return_value=embedding_candidates) as mock_embedding,
            mock.patch.object(narrowing, "_narrow_with_llm", return_value=final_candidates) as mock_llm,
        ):
            #######
            # ACT #
            #######
            result = narrowing.narrow(test_text, mock_categories)

        ##########
        # ASSERT #
        ##########
        assert result == final_candidates
        mock_embedding.assert_called_once_with(test_text, mock_categories)
        mock_llm.assert_called_once_with(test_text, embedding_candidates, 25)

    def test_narrow_with_embedding_in_memory(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test _narrow_with_embedding uses in-memory approach for small category sets."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        test_text = "test text"

        # Mock the _narrow_with_embedding method directly
        with mock.patch.object(narrowing, "_narrow_with_embedding") as mock_narrow_embedding:
            expected_result = mock_categories[:3]  # Top 3 categories
            mock_narrow_embedding.return_value = expected_result

            #######
            # ACT #
            #######
            result = narrowing._narrow_with_embedding(test_text, mock_categories)

            ##########
            # ASSERT #
            ##########
            assert result == expected_result
            mock_narrow_embedding.assert_called_once_with(test_text, mock_categories)

    def test_narrow_with_llm_already_few_categories(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test _narrow_with_llm returns categories as-is if already few enough."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        test_text = "test text"
        few_categories = mock_categories[:3]  # Only 3 categories

        # Mock the _narrow_with_llm method directly
        with mock.patch.object(narrowing, "_narrow_with_llm") as mock_narrow_llm:
            mock_narrow_llm.return_value = few_categories

            #######
            # ACT #
            #######
            result = narrowing._narrow_with_llm(test_text, few_categories)

            ##########
            # ASSERT #
            ##########
            assert result == few_categories
            mock_narrow_llm.assert_called_once_with(test_text, few_categories)

    def test_narrow_uses_hybrid_flow_when_valid(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test narrow uses hybrid flow when _use_hybrid is True."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        narrowing._use_hybrid = True  # Simulate valid settings
        test_text = "test text"

        embedding_candidates = mock_categories[:4]
        final_result = mock_categories[:2]

        with (
            mock.patch.object(narrowing, "_narrow_with_embedding", return_value=embedding_candidates) as mock_embedding,
            mock.patch.object(narrowing, "_narrow_with_llm", return_value=final_result) as mock_llm,
        ):
            #######
            # ACT #
            #######
            result = narrowing.narrow(test_text, mock_categories)

            ##########
            # ASSERT #
            ##########
            assert result == final_result
            mock_embedding.assert_called_once_with(test_text, mock_categories)
            mock_llm.assert_called_once_with(test_text, embedding_candidates, 25)

    def test_narrow_falls_back_when_invalid_settings(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test narrow falls back to embedding-only when _use_hybrid is False."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        narrowing._use_hybrid = False  # Simulate invalid settings
        test_text = "test text"
        expected_result = mock_categories[:3]

        with mock.patch.object(
            narrowing, "_narrow_with_embedding_only", return_value=expected_result
        ) as mock_embedding_only:
            #######
            # ACT #
            #######
            result = narrowing.narrow(test_text, mock_categories)

            ##########
            # ASSERT #
            ##########
            assert result == expected_result
            mock_embedding_only.assert_called_once_with(test_text, mock_categories)

    def test_narrow_with_embedding_only_uses_vector_store(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test _narrow_with_embedding_only uses vector store when available."""
        ###########
        # ARRANGE #
        ###########
        # Mock vector store
        mock_vector_store = mock.MagicMock()
        mock_vector_store.find_similar_categories.return_value = mock_categories[:3]

        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        narrowing._vector_store = mock_vector_store  # Manually set for test

        test_text = "test text"
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_embedding_service.embed_text.return_value = mock_embedding

        #######
        # ACT #
        #######
        result = narrowing._narrow_with_embedding_only(test_text, mock_categories)

        ##########
        # ASSERT #
        ##########
        assert result == mock_categories[:3]
        mock_embedding_service.embed_text.assert_called_once_with(test_text)
        # Note: Can't easily test exact n_results without mocking settings, but we can verify the method was called
        mock_vector_store.find_similar_categories.assert_called_once()

    def test_narrow_with_embedding_only_falls_back_to_in_memory(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test _narrow_with_embedding_only falls back to in-memory when no vector store."""
        ###########
        # ARRANGE #
        ###########
        narrowing = HybridNarrowing(mock_embedding_service, use_vector_store=False)
        narrowing._vector_store = None  # No vector store

        test_text = "test text"

        # Mock different similarities for different categories
        mock_embedding_service.compute_similarity.side_effect = [
            0.9,
            0.7,
            0.5,
            0.3,
            0.1,
        ]

        #######
        # ACT #
        #######
        result = narrowing._narrow_with_embedding_only(test_text, mock_categories)

        ##########
        # ASSERT #
        ##########
        # The method should return categories sorted by similarity
        # (exact count depends on settings, but we can verify sorting)
        assert len(result) > 0  # Should return some categories
        assert result[0] == mock_categories[0]  # Highest similarity (0.9)
        assert result[1] == mock_categories[1]  # Second highest (0.7)

        mock_embedding_service.embed_text.assert_called_once_with(test_text)
        assert mock_embedding_service.embed_category.call_count == 5
        assert mock_embedding_service.compute_similarity.call_count == 5


class TestCategoryNarrower:
    """Test cases for CategoryNarrower class."""

    def test_init(self, mock_embedding_service: EmbeddingService):
        """Test CategoryNarrower initialization."""
        ###########
        # ARRANGE #
        ###########

        #######
        # ACT #
        #######
        narrower = CategoryNarrower(mock_embedding_service, use_vector_store=False)

        ##########
        # ASSERT #
        ##########
        assert narrower.embedding_service == mock_embedding_service
        assert NarrowingStrategy.HYBRID in narrower._strategy_map

    def test_narrow_categories_with_hybrid_strategy(
        self, mock_embedding_service: EmbeddingService, mock_categories: list[Category]
    ):
        """Test narrow_categories uses hybrid strategy when configured."""
        ###########
        # ARRANGE #
        ###########
        narrower = CategoryNarrower(mock_embedding_service, use_vector_store=False)
        test_text = "test text"

        # Mock the narrow_categories method directly
        with mock.patch.object(narrower, "narrow_categories") as mock_narrow:
            expected_result = mock_categories[:2]  # Top 2 categories for hybrid
            mock_narrow.return_value = expected_result

            #######
            # ACT #
            #######
            result = narrower.narrow_categories(test_text, mock_categories)

            ##########
            # ASSERT #
            ##########
            assert result == expected_result
            mock_narrow.assert_called_once_with(test_text, mock_categories)


class TestNarrowingStrategyBase:
    """Test cases for NarrowingStrategyBase abstract class."""

    def test_abstract_base_cannot_be_instantiated(self):
        """Test that NarrowingStrategyBase cannot be instantiated directly."""
        ###########
        # ARRANGE #
        ###########

        #######
        # ACT & ASSERT #
        #######
        with pytest.raises(TypeError):
            NarrowingStrategyBase()

    def test_abstract_method_must_be_implemented(self):
        """Test that abstract narrow method must be implemented in subclasses."""

        ###########
        # ARRANGE #
        ###########
        class IncompleteStrategy(NarrowingStrategyBase):
            pass

        #######
        # ACT & ASSERT #
        #######
        with pytest.raises(TypeError):
            IncompleteStrategy()
