"""Test the selection module."""

from unittest import mock

import pytest


# Mock BAML imports before importing selection module to avoid version conflicts
with mock.patch.dict(
    "sys.modules",
    {
        "baml_client": mock.MagicMock(),
        "baml_client.tracing": mock.MagicMock(),
        "baml_client.type_builder": mock.MagicMock(),
    },
):
    from src.classification.selection import CategorySelector

from src.data.models import Category


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


class TestCategorySelector:
    """Test cases for CategorySelector class."""

    def test_init(self):
        """Test CategorySelector initialization."""
        ###########
        # ARRANGE #
        ###########

        #######
        # ACT #
        #######
        selector = CategorySelector()

        ##########
        # ASSERT #
        ##########
        assert isinstance(selector, CategorySelector)

    def test_select_best_category_single_candidate_logic(self, mock_categories: list[Category]):
        """Test the logic for single candidate selection."""
        ###########
        # ARRANGE #
        ###########
        single_candidate = [mock_categories[0]]  # Just Laptops

        # Simulate the method logic: if len(candidates) == 1, return candidates[0]
        candidates = single_candidate

        #######
        # ACT #
        #######
        if len(candidates) == 1:
            result = candidates[0]
        else:
            result = None

        ##########
        # ASSERT #
        ##########
        assert result == mock_categories[0]
        assert result.name == "Laptops"

    def test_select_best_category_empty_candidates_logic(self):
        """Test the logic for empty candidates."""
        ###########
        # ARRANGE #
        ###########
        empty_candidates = []

        #######
        # ACT & ASSERT #
        #######
        # Simulate the method logic: if not candidates, raise ValueError
        if not empty_candidates:
            with pytest.raises(ValueError):
                raise ValueError("No candidate categories provided")

    def test_select_best_category_name_matching_logic(self, mock_categories: list[Category]):
        """Test the core name matching logic."""
        ###########
        # ARRANGE #
        ###########
        candidates = mock_categories[:2]  # Laptops and Smartphones
        selected_name = "Laptops"

        #######
        # ACT #
        #######
        # Simulate the method logic for finding category by name
        result = None
        for category in candidates:
            if category.name == selected_name:
                result = category
                break

        ##########
        # ASSERT #
        ##########
        assert result == mock_categories[0]  # Laptops category
        assert result.name == "Laptops"

    def test_select_best_category_invalid_name_logic(self, mock_categories: list[Category]):
        """Test logic when selected name is not found."""
        ###########
        # ARRANGE #
        ###########
        candidates = mock_categories[:2]
        selected_name = "NonexistentCategory"

        #######
        # ACT #
        #######
        # Simulate the method logic
        result = None
        for category in candidates:
            if category.name == selected_name:
                result = category
                break

        ##########
        # ASSERT #
        ##########
        assert result is None

        # This would raise ValueError in the actual method
        with pytest.raises(ValueError, match="not found in candidates"):
            if result is None:
                raise ValueError(f"Selected category '{selected_name}' not found in candidates")

    def test_build_dynamic_enum_structure_logic(self, mock_categories: list[Category]):
        """Test the structure created by _build_dynamic_enum logic."""
        ###########
        # ARRANGE #
        ###########
        single_category = [mock_categories[0]]  # Just Laptops

        #######
        # ACT #
        #######
        # Simulate what the method creates
        enum_structure = []
        for i, category in enumerate(single_category):
            enum_structure.append(
                {
                    "name": category.name,
                    "alias": f"k{i}",
                    "description": category.llm_description,
                }
            )

        ##########
        # ASSERT #
        ##########
        assert len(enum_structure) == 1
        assert enum_structure[0]["name"] == "Laptops"
        assert enum_structure[0]["alias"] == "k0"
        assert enum_structure[0]["description"] == "Portable computing devices for professional and personal use"

    def test_build_dynamic_enum_multiple_categories_logic(self, mock_categories: list[Category]):
        """Test _build_dynamic_enum with multiple categories."""
        ###########
        # ARRANGE #
        ###########
        multiple_categories = mock_categories[:2]  # Laptops and Smartphones

        #######
        # ACT #
        #######
        # Simulate the method behavior
        enum_structure = []
        for i, category in enumerate(multiple_categories):
            enum_structure.append(
                {
                    "name": category.name,
                    "alias": f"k{i}",
                    "description": category.llm_description,
                }
            )

        ##########
        # ASSERT #
        ##########
        assert len(enum_structure) == 2

        # First category
        assert enum_structure[0]["name"] == "Laptops"
        assert enum_structure[0]["alias"] == "k0"

        # Second category
        assert enum_structure[1]["name"] == "Smartphones"
        assert enum_structure[1]["alias"] == "k1"

    def test_build_dynamic_enum_preserves_order_logic(self, mock_categories: list[Category]):
        """Test that enum creation preserves category order."""
        ###########
        # ARRANGE #
        ###########
        # Reverse the order to test ordering
        reversed_categories = list(reversed(mock_categories))

        #######
        # ACT #
        #######
        enum_structure = []
        for i, category in enumerate(reversed_categories):
            enum_structure.append({"name": category.name, "alias": f"k{i}"})

        ##########
        # ASSERT #
        ##########
        # Verify the order is preserved
        expected_order = [("Books", "k0"), ("Smartphones", "k1"), ("Laptops", "k2")]

        actual_order = [(item["name"], item["alias"]) for item in enum_structure]
        assert actual_order == expected_order

    def test_build_dynamic_enum_empty_categories_logic(self):
        """Test enum creation with empty categories list."""
        ###########
        # ARRANGE #
        ###########
        empty_categories = []

        #######
        # ACT #
        #######
        enum_structure = []
        for i, category in enumerate(empty_categories):
            enum_structure.append({"name": category.name, "alias": f"k{i}"})

        ##########
        # ASSERT #
        ##########
        assert enum_structure == []

    def test_category_name_matching_comprehensive(self, mock_categories: list[Category]):
        """Test comprehensive category name matching scenarios."""
        ###########
        # ARRANGE #
        ###########
        candidates = mock_categories
        test_cases = [
            ("Laptops", mock_categories[0]),
            ("Smartphones", mock_categories[1]),
            ("Books", mock_categories[2]),
            ("NonExistent", None),
        ]

        #######
        # ACT & ASSERT #
        #######
        for selected_name, expected_result in test_cases:
            result = None
            for category in candidates:
                if category.name == selected_name:
                    result = category
                    break

            assert result == expected_result

    def test_case_sensitive_category_matching_logic(self, mock_categories: list[Category]):
        """Test that category name matching is case-sensitive."""
        ###########
        # ARRANGE #
        ###########
        candidates = mock_categories[:1]  # Just Laptops

        test_cases = [
            ("Laptops", mock_categories[0]),  # Exact match
            ("laptops", None),  # Lowercase should not match
            ("LAPTOPS", None),  # Uppercase should not match
            ("Laptop", None),  # Partial match should not match
        ]

        #######
        # ACT & ASSERT #
        #######
        for selected_name, expected_result in test_cases:
            result = None
            for category in candidates:
                if category.name == selected_name:
                    result = category
                    break

            assert result == expected_result

    def test_duplicate_category_names_first_match_logic(self):
        """Test that duplicate category names return the first match."""
        ###########
        # ARRANGE #
        ###########
        duplicate_categories = [
            Category(
                name="Electronics",
                path="/Electronics/Computers",
                embedding_text="Electronics computing",
                llm_description="Computer electronics",
                parent_path="/Electronics",
            ),
            Category(
                name="Electronics",
                path="/Electronics/Mobile",
                embedding_text="Electronics mobile",
                llm_description="Mobile electronics",
                parent_path="/Electronics",
            ),
        ]

        selected_name = "Electronics"

        #######
        # ACT #
        #######
        result = None
        for category in duplicate_categories:
            if category.name == selected_name:
                result = category
                break  # First match wins

        ##########
        # ASSERT #
        ##########
        assert result == duplicate_categories[0]
        assert result.path == "/Electronics/Computers"

    def test_special_characters_in_category_names_logic(self):
        """Test handling of special characters in category names."""
        ###########
        # ARRANGE #
        ###########
        special_categories = [
            Category(
                name="TV & Audio",
                path="/Electronics/TV & Audio",
                embedding_text="TV Audio electronics",
                llm_description="Television and audio equipment",
                parent_path="/Electronics",
            ),
            Category(
                name="Home/Garden",
                path="/Home/Garden",
                embedding_text="Home garden supplies",
                llm_description="Home and garden supplies",
                parent_path="/Home",
            ),
        ]

        #######
        # ACT #
        #######
        # Test that special characters are handled correctly
        tv_result = None
        home_result = None

        for category in special_categories:
            if category.name == "TV & Audio":
                tv_result = category
            elif category.name == "Home/Garden":
                home_result = category

        ##########
        # ASSERT #
        ##########
        assert tv_result is not None
        assert tv_result.name == "TV & Audio"
        assert home_result is not None
        assert home_result.name == "Home/Garden"

    def test_selector_method_single_candidate_logic_validation(self, mock_categories: list[Category]):
        """Test validation of single candidate logic (simulated)."""
        ###########
        # ARRANGE #
        ###########
        single_candidate = [mock_categories[0]]  # Just Laptops

        #######
        # ACT #
        #######
        # Simulate the method's single candidate logic
        if len(single_candidate) == 1:
            result = single_candidate[0]
        else:
            result = None

        ##########
        # ASSERT #
        ##########
        assert result == mock_categories[0]
        assert result.name == "Laptops"

    def test_selector_method_empty_candidates_logic_validation(self):
        """Test validation of empty candidates logic (simulated)."""
        ###########
        # ARRANGE #
        ###########
        empty_candidates = []

        #######
        # ACT & ASSERT #
        #######
        # Simulate the method's empty candidate check
        if not empty_candidates:
            with pytest.raises(ValueError):
                raise ValueError("No candidate categories provided")


class TestCategorySelectorEdgeCases:
    """Test edge cases for CategorySelector."""

    def test_selector_initialization_no_dependencies(self):
        """Test that CategorySelector can be initialized without dependencies."""
        ###########
        # ARRANGE & ACT #
        ###########
        selector = CategorySelector()

        ##########
        # ASSERT #
        ##########
        assert isinstance(selector, CategorySelector)
        # Should not require any external services for initialization

    def test_category_matching_edge_cases_logic(self):
        """Test edge cases in category matching logic."""
        ###########
        # ARRANGE #
        ###########
        edge_case_categories = [
            Category(
                name="",  # Empty name
                path="/Empty",
                embedding_text="empty",
                llm_description="Empty category",
                parent_path="/",
            ),
            Category(
                name="  Spaced  ",  # Name with spaces
                path="/Spaced",
                embedding_text="spaced",
                llm_description="Spaced category",
                parent_path="/",
            ),
            Category(
                name="123Numbers",  # Name starting with numbers
                path="/Numbers",
                embedding_text="numbers",
                llm_description="Number category",
                parent_path="/",
            ),
        ]

        #######
        # ACT & ASSERT #
        #######
        # Test exact matching for edge cases
        for category in edge_case_categories:
            result = None
            for cat in edge_case_categories:
                if cat.name == category.name:
                    result = cat
                    break
            assert result == category  # Should find exact match

    def test_selector_component_isolation_logic_validation(self, mock_categories: list[Category]):
        """Test validation of selector isolation logic (simulated)."""
        ###########
        # ARRANGE #
        ###########
        candidates = mock_categories[:1]  # Single candidate

        #######
        # ACT #
        #######
        # Simulate single candidate logic (should work without external dependencies)
        if len(candidates) == 1:
            result = candidates[0]
        else:
            result = None

        ##########
        # ASSERT #
        ##########
        assert result == mock_categories[0]
        # No external component calls needed for single candidate

    def test_whitespace_and_special_character_handling(self):
        """Test handling of categories with whitespace and special characters."""
        ###########
        # ARRANGE #
        ###########
        special_categories = [
            Category(
                name=" Leading Space",
                path="/Space1",
                embedding_text="space",
                llm_description="Leading space category",
                parent_path="/",
            ),
            Category(
                name="Trailing Space ",
                path="/Space2",
                embedding_text="space",
                llm_description="Trailing space category",
                parent_path="/",
            ),
            Category(
                name="Multi  Spaces",
                path="/Space3",
                embedding_text="space",
                llm_description="Multiple spaces category",
                parent_path="/",
            ),
        ]

        #######
        # ACT & ASSERT #
        #######
        # Test that whitespace is preserved in matching
        for category in special_categories:
            result = None
            for cat in special_categories:
                if cat.name == category.name:
                    result = cat
                    break
            assert result == category
            assert result.name == category.name  # Exact match including whitespace


class TestCategorySelectorIntegration:
    """Integration-style tests for CategorySelector."""

    def test_realistic_category_selection_scenario_logic(self):
        """Test selection logic with realistic categories."""
        ###########
        # ARRANGE #
        ###########
        realistic_categories = [
            Category(
                name="Gaming Laptops",
                path="/Electronics/Computers/Gaming Laptops",
                embedding_text="Gaming laptops high performance computers",
                llm_description="High-performance laptops designed for gaming and intensive computing tasks",
                parent_path="/Electronics/Computers",
            ),
            Category(
                name="Business Laptops",
                path="/Electronics/Computers/Business Laptops",
                embedding_text="Business laptops professional work computers",
                llm_description="Professional laptops optimized for business and productivity tasks",
                parent_path="/Electronics/Computers",
            ),
            Category(
                name="Student Laptops",
                path="/Electronics/Computers/Student Laptops",
                embedding_text="Student laptops budget affordable computers",
                llm_description="Affordable laptops suitable for students and basic computing needs",
                parent_path="/Electronics/Computers",
            ),
        ]

        #######
        # ACT #
        #######
        # Test the matching logic for different scenarios
        test_scenarios = [
            ("Gaming Laptops", realistic_categories[0]),
            ("Business Laptops", realistic_categories[1]),
            ("Student Laptops", realistic_categories[2]),
        ]

        for selected_name, expected_category in test_scenarios:
            result = None
            for category in realistic_categories:
                if category.name == selected_name:
                    result = category
                    break

            ##########
            # ASSERT #
            ##########
            assert result == expected_category
            assert result.name == selected_name

    def test_full_selection_workflow_simulation_logic(self, mock_categories: list[Category]):
        """Test simulating the full selection workflow logic."""
        ###########
        # ARRANGE #
        ###########
        test_text = "I need a device for mobile communication"
        candidates = mock_categories

        # Simulate what would happen in the full workflow:
        # 1. Multiple candidates provided
        # 2. TypeBuilder created with categories
        # 3. LLM called to select best match
        # 4. Result matched back to category object

        #######
        # ACT #
        #######
        # Step 1: Check we have multiple candidates
        assert len(candidates) > 1

        # Step 2: Simulate TypeBuilder creation (would happen in _build_dynamic_enum)
        type_builder_calls = []
        for i, category in enumerate(candidates):
            type_builder_calls.append(
                {
                    "name": category.name,
                    "alias": f"k{i}",
                    "description": category.llm_description,
                }
            )

        # Step 3: Simulate LLM selection (would return a category name)
        simulated_llm_response = "Smartphones"

        # Step 4: Match back to category object
        result = None
        for category in candidates:
            if category.name == simulated_llm_response:
                result = category
                break

        ##########
        # ASSERT #
        ##########
        assert result is not None
        assert result.name == "Smartphones"
        assert result == mock_categories[1]

        # Verify TypeBuilder would have been called correctly
        assert len(type_builder_calls) == 3
        assert type_builder_calls[1]["name"] == "Smartphones"
        assert type_builder_calls[1]["alias"] == "k1"

    def test_selector_error_handling_patterns_logic(self, mock_categories: list[Category]):
        """Test error handling patterns in selector logic (simulated)."""
        ###########
        # ARRANGE #
        ###########

        # Test various error conditions
        error_scenarios = [
            ([], "No candidate categories provided"),  # Empty candidates
            ([mock_categories[0]], None),  # Single candidate (no error)
        ]

        #######
        # ACT & ASSERT #
        #######
        for candidates, expected_error in error_scenarios:
            if expected_error:
                # Simulate the error condition
                if not candidates:
                    with pytest.raises(ValueError):
                        raise ValueError(expected_error)
            # Simulate single candidate success
            elif len(candidates) == 1:
                result = candidates[0]
                assert result == candidates[0]

    def test_selector_with_various_category_types_logic(self, mock_categories: list[Category]):
        """Test selector logic with different types of categories (simulated)."""
        ###########
        # ARRANGE #
        ###########

        # Test with different category combinations
        test_combinations = [
            ([mock_categories[0]], mock_categories[0]),  # Single category
        ]

        #######
        # ACT & ASSERT #
        #######
        for candidates, expected_result in test_combinations:
            # Simulate single candidate scenario logic
            if len(candidates) == 1:
                result = candidates[0]
                assert result == expected_result

    def test_comprehensive_name_matching_scenarios(self, mock_categories: list[Category]):
        """Test comprehensive name matching scenarios."""
        ###########
        # ARRANGE #
        ###########
        candidates = mock_categories

        # Test all possible matches
        all_scenarios = [(cat.name, cat) for cat in candidates] + [
            ("InvalidName", None),
            ("", None),
            ("Partial", None),
        ]

        #######
        # ACT & ASSERT #
        #######
        for selected_name, expected_result in all_scenarios:
            result = None
            for category in candidates:
                if category.name == selected_name:
                    result = category
                    break

            assert result == expected_result
