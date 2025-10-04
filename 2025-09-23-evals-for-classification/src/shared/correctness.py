"""Flexible correctness evaluation for classification results.

This module provides different definitions of "correct" classification beyond exact matching,
including hierarchical relationships like parent/child categories and siblings.
"""

from enum import Enum
from typing import List

from src.data.models import Category


class CorrectnessDefinition(str, Enum):
    """Different definitions of correctness for classification evaluation."""

    EXACT = "exact"
    LENIENT_GENERAL = "lenient_general"  # exact OR one level more general
    LENIENT_SPECIFIC = "lenient_specific"  # exact OR one level more specific OR sibling


class CategoryHierarchyHelper:
    """Helper class for navigating category hierarchies."""

    def __init__(self, all_categories: List[Category]):
        """Initialize with all available categories for hierarchy navigation.

        Args:
            all_categories: Complete list of categories to build hierarchy from
        """
        self.categories_by_path = {cat.path: cat for cat in all_categories}
        self._build_hierarchy_maps()

    def _build_hierarchy_maps(self):
        """Build lookup maps for efficient hierarchy navigation."""
        self.children_map = {}  # parent_path -> [child_paths]
        self.parent_map = {}  # child_path -> parent_path

        for category in self.categories_by_path.values():
            parent_path = category.parent_path

            # Store parent relationship
            if parent_path != category.path:  # Not root
                self.parent_map[category.path] = parent_path

                # Store children relationship
                if parent_path not in self.children_map:
                    self.children_map[parent_path] = []
                self.children_map[parent_path].append(category.path)

    def get_parent_path(self, path: str) -> str | None:
        """Get parent category path.

        Args:
            path: Category path

        Returns:
            Parent path or None if root category
        """
        return self.parent_map.get(path)

    def get_child_paths(self, path: str) -> List[str]:
        """Get all direct child category paths.

        Args:
            path: Parent category path

        Returns:
            List of child category paths
        """
        return self.children_map.get(path, [])

    def get_sibling_paths(self, path: str) -> List[str]:
        """Get all sibling category paths (same parent, excluding self).

        Args:
            path: Category path

        Returns:
            List of sibling category paths
        """
        parent_path = self.get_parent_path(path)
        if parent_path is None:
            return []  # Root has no siblings

        siblings = self.get_child_paths(parent_path)
        return [sibling for sibling in siblings if sibling != path]

    def is_parent_of(self, potential_parent: str, child: str) -> bool:
        """Check if one category is the parent of another.

        Args:
            potential_parent: Path that might be parent
            child: Path that might be child

        Returns:
            True if potential_parent is direct parent of child
        """
        return self.get_parent_path(child) == potential_parent

    def is_child_of(self, potential_child: str, parent: str) -> bool:
        """Check if one category is a child of another.

        Args:
            potential_child: Path that might be child
            parent: Path that might be parent

        Returns:
            True if potential_child is direct child of parent
        """
        return self.is_parent_of(parent, potential_child)

    def is_sibling_of(self, path1: str, path2: str) -> bool:
        """Check if two categories are siblings (same parent).

        Args:
            path1: First category path
            path2: Second category path

        Returns:
            True if categories are siblings
        """
        parent1 = self.get_parent_path(path1)
        parent2 = self.get_parent_path(path2)
        return parent1 is not None and parent1 == parent2


class CorrectnessEvaluator:
    """Evaluates classification correctness using flexible definitions."""

    def __init__(self, all_categories: List[Category]):
        """Initialize evaluator with category hierarchy.

        Args:
            all_categories: Complete list of categories for hierarchy navigation
        """
        self.hierarchy = CategoryHierarchyHelper(all_categories)

    def is_correct(self, predicted_path: str, ground_truth_path: str, definition: CorrectnessDefinition) -> bool:
        """Evaluate if a prediction is correct under the given definition.

        Args:
            predicted_path: The predicted category path
            ground_truth_path: The ground truth category path
            definition: The correctness definition to use

        Returns:
            True if prediction is considered correct under the definition
        """
        if definition == CorrectnessDefinition.EXACT:
            return predicted_path == ground_truth_path

        elif definition == CorrectnessDefinition.LENIENT_GENERAL:
            # Exact match OR predicted is one level more general (parent)
            return predicted_path == ground_truth_path or self.hierarchy.is_parent_of(predicted_path, ground_truth_path)

        elif definition == CorrectnessDefinition.LENIENT_SPECIFIC:
            # Exact match OR predicted is one level more specific (child) OR sibling
            return (
                predicted_path == ground_truth_path
                or self.hierarchy.is_child_of(predicted_path, ground_truth_path)
                or self.hierarchy.is_sibling_of(predicted_path, ground_truth_path)
            )

        else:
            raise ValueError(f"Unknown correctness definition: {definition}")

    def get_correctness_explanation(
        self, predicted_path: str, ground_truth_path: str, definition: CorrectnessDefinition
    ) -> str:
        """Get human-readable explanation of why a prediction is correct/incorrect.

        Args:
            predicted_path: The predicted category path
            ground_truth_path: The ground truth category path
            definition: The correctness definition used

        Returns:
            Human-readable explanation string
        """
        is_correct = self.is_correct(predicted_path, ground_truth_path, definition)

        if predicted_path == ground_truth_path:
            return "✅ Exact match"

        if not is_correct:
            return f"❌ Incorrect under {definition.value} definition"

        # Determine the type of correct match
        if self.hierarchy.is_parent_of(predicted_path, ground_truth_path):
            return "✅ Correct (one level more general)"
        elif self.hierarchy.is_child_of(predicted_path, ground_truth_path):
            return "✅ Correct (one level more specific)"
        elif self.hierarchy.is_sibling_of(predicted_path, ground_truth_path):
            return "✅ Correct (sibling category)"
        else:
            return f"✅ Correct under {definition.value} definition"
