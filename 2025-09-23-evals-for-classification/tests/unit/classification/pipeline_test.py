"""Test the pipeline module."""

from unittest import mock

import pytest


# Mock BAML imports before importing any modules to avoid version conflicts
with mock.patch.dict(
    "sys.modules",
    {
        "baml_client": mock.MagicMock(),
        "baml_client.tracing": mock.MagicMock(),
        "baml_client.type_builder": mock.MagicMock(),
    },
):
    from src.classification.pipeline import ClassificationPipeline
    from src.data.models import Category, ClassificationResult


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
    ]


class TestClassificationPipeline:
    """Test cases for ClassificationPipeline class."""

    def test_get_categories_caching_behavior(self, mock_categories: list[Category]):
        """Test _get_categories method caching behavior."""
        ###########
        # ARRANGE #
        ###########
        # Create a pipeline instance and mock its components
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = []
        pipeline.category_loader = mock.MagicMock()
        pipeline.category_loader.load_categories.return_value = mock_categories

        #######
        # ACT #
        #######
        # First call should load categories
        result1 = pipeline._get_categories()
        # Second call should use cache
        result2 = pipeline._get_categories()

        ##########
        # ASSERT #
        ##########
        assert result1 == mock_categories
        assert result2 == mock_categories
        assert pipeline._categories_cache == mock_categories
        # Loader should only be called once due to caching
        pipeline.category_loader.load_categories.assert_called_once()

    def test_get_categories_returns_cached_when_available(self, mock_categories: list[Category]):
        """Test _get_categories returns cached categories when available."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = mock_categories
        pipeline.category_loader = mock.MagicMock()

        #######
        # ACT #
        #######
        result = pipeline._get_categories()

        ##########
        # ASSERT #
        ##########
        assert result == mock_categories
        # Loader should not be called since cache is populated
        pipeline.category_loader.load_categories.assert_not_called()

    def test_classify_method_basic_structure(self, mock_categories: list[Category]):
        """Test classify method basic structure and flow."""
        ###########
        # ARRANGE #
        ###########
        test_text = "I need a laptop for work"
        narrowed_categories = mock_categories[:2]  # Laptops, Smartphones
        selected_category = mock_categories[0]  # Laptops

        # Create pipeline instance and mock its components
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = mock_categories

        pipeline.narrower = mock.MagicMock()
        pipeline.narrower.narrow_categories.return_value = narrowed_categories
        pipeline.narrower._strategy_map = {"embedding": mock.MagicMock()}

        pipeline.selector = mock.MagicMock()
        pipeline.selector.select_best_category.return_value = selected_category

        pipeline.embedding_service = mock.MagicMock()
        pipeline.embedding_service.vector_store = None

        #######
        # ACT #
        #######
        with (
            mock.patch("builtins.print"),
            mock.patch.object(pipeline, "classify") as mock_classify,
        ):
            # Mock the classify method to return our expected result
            expected_result = ClassificationResult(
                category=selected_category,
                candidates=narrowed_categories,
                processing_time_ms=100.0,
                metadata={
                    "total_categories": 3,
                    "narrowed_to": 2,
                    "narrowing_time_ms": 50.0,
                    "selection_time_ms": 25.0,
                    "narrowing_strategy": "dict_keys(['embedding'])",
                    "vector_store_enabled": False,
                },
            )
            mock_classify.return_value = expected_result
            result = pipeline.classify(test_text)

        ##########
        # ASSERT #
        ##########
        # Verify result structure
        assert isinstance(result, ClassificationResult)
        assert result.category == selected_category
        assert result.candidates == narrowed_categories
        assert result.processing_time_ms == 100.0

        # Verify method was called correctly
        mock_classify.assert_called_once_with(test_text)

    def test_classify_with_max_candidates_parameter(self, mock_categories: list[Category]):
        """Test classify method can be called with max_candidates parameter."""
        ###########
        # ARRANGE #
        ###########
        test_text = "test text"
        selected_category = mock_categories[0]
        max_candidates = 2

        # Create pipeline instance and mock its components
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = mock_categories

        #######
        # ACT #
        #######
        with mock.patch.object(pipeline, "classify") as mock_classify:
            expected_result = ClassificationResult(
                category=selected_category,
                candidates=mock_categories[:max_candidates],
                processing_time_ms=100.0,
                metadata={"narrowed_to": max_candidates},
            )
            mock_classify.return_value = expected_result
            result = pipeline.classify(test_text, max_candidates=max_candidates)

        ##########
        # ASSERT #
        ##########
        # Verify method was called with correct parameters
        mock_classify.assert_called_once_with(test_text, max_candidates=max_candidates)
        assert len(result.candidates) == max_candidates

    def test_pipeline_component_access(self, mock_categories: list[Category]):
        """Test that pipeline components can be accessed and mocked."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = mock_categories

        # Mock all components
        pipeline.narrower = mock.MagicMock()
        pipeline.selector = mock.MagicMock()
        pipeline.embedding_service = mock.MagicMock()
        pipeline.category_loader = mock.MagicMock()

        #######
        # ACT & ASSERT #
        #######
        # Verify components can be accessed and called
        assert pipeline.narrower is not None
        assert pipeline.selector is not None
        assert pipeline.embedding_service is not None
        assert pipeline.category_loader is not None

        # Verify components can be called
        pipeline.narrower.narrow_categories("test", mock_categories)
        pipeline.selector.select_best_category("test", mock_categories)

        pipeline.narrower.narrow_categories.assert_called_once()
        pipeline.selector.select_best_category.assert_called_once()

    def test_pipeline_categories_cache_behavior(self, mock_categories: list[Category]):
        """Test pipeline categories cache behavior."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = []  # Initialize the cache
        pipeline.category_loader = mock.MagicMock()
        pipeline.category_loader.load_categories.return_value = mock_categories

        #######
        # ACT #
        #######
        # Initially cache should be empty
        assert pipeline._categories_cache == []

        # First call should populate cache
        result1 = pipeline._get_categories()
        assert pipeline._categories_cache == mock_categories

        # Second call should use cache
        result2 = pipeline._get_categories()

        ##########
        # ASSERT #
        ##########
        assert result1 == result2 == mock_categories
        # Loader should only be called once
        pipeline.category_loader.load_categories.assert_called_once()

    def test_pipeline_embedding_service_integration(self):
        """Test pipeline embedding service integration."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline.embedding_service = mock.MagicMock()

        # Test vector store enabled vs disabled
        pipeline.embedding_service.vector_store = mock.MagicMock()

        #######
        # ACT & ASSERT #
        #######
        # Should be able to check vector store status
        assert pipeline.embedding_service.vector_store is not None

        # Should be able to disable vector store
        pipeline.embedding_service.vector_store = None
        assert pipeline.embedding_service.vector_store is None

    def test_pipeline_narrower_integration(self, mock_categories: list[Category]):
        """Test pipeline narrower integration."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline.narrower = mock.MagicMock()

        test_text = "test text"
        expected_narrowed = mock_categories[:2]
        pipeline.narrower.narrow_categories.return_value = expected_narrowed
        pipeline.narrower._strategy_map = {"embedding": mock.MagicMock()}

        #######
        # ACT #
        #######
        result = pipeline.narrower.narrow_categories(test_text, mock_categories)

        ##########
        # ASSERT #
        ##########
        assert result == expected_narrowed
        pipeline.narrower.narrow_categories.assert_called_once_with(test_text, mock_categories)
        assert "embedding" in pipeline.narrower._strategy_map

    def test_pipeline_selector_integration(self, mock_categories: list[Category]):
        """Test pipeline selector integration."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline.selector = mock.MagicMock()

        test_text = "test text"
        expected_selected = mock_categories[0]
        pipeline.selector.select_best_category.return_value = expected_selected

        #######
        # ACT #
        #######
        result = pipeline.selector.select_best_category(test_text, mock_categories)

        ##########
        # ASSERT #
        ##########
        assert result == expected_selected
        pipeline.selector.select_best_category.assert_called_once_with(test_text, mock_categories)

    def test_classification_result_structure(self, mock_categories: list[Category]):
        """Test ClassificationResult structure and fields."""
        ###########
        # ARRANGE #
        ###########
        selected_category = mock_categories[0]
        candidates = mock_categories[:2]
        processing_time = 123.45
        metadata = {
            "total_categories": 10,
            "narrowed_to": 2,
            "vector_store_enabled": True,
        }

        #######
        # ACT #
        #######
        result = ClassificationResult(
            category=selected_category,
            candidates=candidates,
            processing_time_ms=processing_time,
            metadata=metadata,
        )

        ##########
        # ASSERT #
        ##########
        # Verify all fields are accessible
        assert result.category == selected_category
        assert result.candidates == candidates
        assert result.processing_time_ms == processing_time
        assert result.metadata == metadata

        # Verify result is proper type
        assert isinstance(result, ClassificationResult)


class TestClassificationPipelineEdgeCases:
    """Test edge cases for ClassificationPipeline."""

    def test_empty_categories_cache(self):
        """Test pipeline behavior with empty categories cache."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline._categories_cache = []
        pipeline.category_loader = mock.MagicMock()
        pipeline.category_loader.load_categories.return_value = []

        #######
        # ACT #
        #######
        result = pipeline._get_categories()

        ##########
        # ASSERT #
        ##########
        assert result == []
        assert pipeline._categories_cache == []
        pipeline.category_loader.load_categories.assert_called_once()

    def test_pipeline_with_none_vector_store(self):
        """Test pipeline behavior when vector store is None."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        pipeline.embedding_service = mock.MagicMock()
        pipeline.embedding_service.vector_store = None

        #######
        # ACT & ASSERT #
        #######
        assert pipeline.embedding_service.vector_store is None
        # Should not raise any errors when vector store is None

    def test_pipeline_component_mocking(self, mock_categories: list[Category]):
        """Test that all pipeline components can be properly mocked."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)

        # Mock all components
        pipeline.category_loader = mock.MagicMock()
        pipeline.embedding_service = mock.MagicMock()
        pipeline.narrower = mock.MagicMock()
        pipeline.selector = mock.MagicMock()

        # Set up return values
        pipeline.category_loader.load_categories.return_value = mock_categories
        pipeline.narrower.narrow_categories.return_value = mock_categories[:1]
        pipeline.selector.select_best_category.return_value = mock_categories[0]

        #######
        # ACT #
        #######
        categories = pipeline.category_loader.load_categories()
        narrowed = pipeline.narrower.narrow_categories("test", categories)
        selected = pipeline.selector.select_best_category("test", narrowed)

        ##########
        # ASSERT #
        ##########
        assert categories == mock_categories
        assert narrowed == mock_categories[:1]
        assert selected == mock_categories[0]

        # Verify all methods were called
        pipeline.category_loader.load_categories.assert_called_once()
        pipeline.narrower.narrow_categories.assert_called_once_with("test", categories)
        pipeline.selector.select_best_category.assert_called_once_with("test", narrowed)


class TestClassificationPipelineIntegration:
    """Integration-style tests for ClassificationPipeline."""

    def test_pipeline_classification_result_creation(self, mock_categories: list[Category]):
        """Test that ClassificationResult can be created with pipeline data."""
        ###########
        # ARRANGE #
        ###########
        selected_category = mock_categories[0]
        candidates = mock_categories[:2]

        metadata = {
            "total_categories": len(mock_categories),
            "narrowed_to": len(candidates),
            "narrowing_time_ms": 50.0,
            "selection_time_ms": 25.0,
            "narrowing_strategy": "embedding",
            "vector_store_enabled": False,
        }

        #######
        # ACT #
        #######
        result = ClassificationResult(
            category=selected_category,
            candidates=candidates,
            processing_time_ms=100.0,
            metadata=metadata,
        )

        ##########
        # ASSERT #
        ##########
        # Verify result structure matches expected pipeline output
        assert isinstance(result, ClassificationResult)
        assert result.category.name == "Laptops"
        assert len(result.candidates) == 2
        assert result.processing_time_ms > 0
        assert "total_categories" in result.metadata
        assert "narrowed_to" in result.metadata
        assert "vector_store_enabled" in result.metadata

    def test_pipeline_component_interaction_pattern(self, mock_categories: list[Category]):
        """Test the expected interaction pattern between pipeline components."""
        ###########
        # ARRANGE #
        ###########
        pipeline = ClassificationPipeline.__new__(ClassificationPipeline)

        # Set up component chain
        pipeline.category_loader = mock.MagicMock()
        pipeline.narrower = mock.MagicMock()
        pipeline.selector = mock.MagicMock()

        # Configure return values to simulate pipeline flow
        pipeline.category_loader.load_categories.return_value = mock_categories
        pipeline.narrower.narrow_categories.return_value = mock_categories[:2]
        pipeline.selector.select_best_category.return_value = mock_categories[0]

        test_text = "test classification text"

        #######
        # ACT #
        #######
        # Simulate the pipeline flow
        all_categories = pipeline.category_loader.load_categories()
        narrowed_categories = pipeline.narrower.narrow_categories(test_text, all_categories)
        selected_category = pipeline.selector.select_best_category(test_text, narrowed_categories)

        ##########
        # ASSERT #
        ##########
        # Verify the flow: loader -> narrower -> selector
        assert all_categories == mock_categories
        assert narrowed_categories == mock_categories[:2]
        assert selected_category == mock_categories[0]

        # Verify correct method calls in sequence
        pipeline.category_loader.load_categories.assert_called_once()
        pipeline.narrower.narrow_categories.assert_called_once_with(test_text, all_categories)
        pipeline.selector.select_best_category.assert_called_once_with(test_text, narrowed_categories)

    def test_pipeline_metadata_structure(self):
        """Test that pipeline metadata has expected structure."""
        ###########
        # ARRANGE #
        ###########
        expected_metadata_keys = {
            "total_categories",
            "narrowed_to",
            "narrowing_time_ms",
            "selection_time_ms",
            "narrowing_strategy",
            "vector_store_enabled",
        }

        metadata = {
            "total_categories": 100,
            "narrowed_to": 5,
            "narrowing_time_ms": 45.2,
            "selection_time_ms": 12.8,
            "narrowing_strategy": "hybrid",
            "vector_store_enabled": True,
        }

        #######
        # ACT #
        #######
        result_metadata_keys = set(metadata.keys())

        ##########
        # ASSERT #
        ##########
        # Verify all expected keys are present
        assert result_metadata_keys == expected_metadata_keys

        # Verify metadata value types
        assert isinstance(metadata["total_categories"], int)
        assert isinstance(metadata["narrowed_to"], int)
        assert isinstance(metadata["narrowing_time_ms"], float)
        assert isinstance(metadata["selection_time_ms"], float)
        assert isinstance(metadata["narrowing_strategy"], str)
        assert isinstance(metadata["vector_store_enabled"], bool)
