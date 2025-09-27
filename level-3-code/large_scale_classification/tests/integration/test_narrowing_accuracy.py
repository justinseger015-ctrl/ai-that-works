"""Test script to evaluate the accuracy of category narrowing strategies.

This script tests how often the correct category is included in the narrowed
results for each narrowing strategy (hybrid). It provides detailed
metrics and analysis to help optimize the narrowing process.
"""

import json
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from src.classification.embeddings import EmbeddingService
from src.classification.narrowing import (
    HybridNarrowing,
)
from src.config.settings import settings
from src.data.category_loader import CategoryLoader
from src.data.models import Category
from src.shared import constants as C
from tests.data.test_cases import TestCase, tests

src_path = Path(__file__).parents[2] / C.SRC
sys.path.insert(0, str(src_path))

CATEGORIES_DISPLAY_CUTOFF = 3


@dataclass
class NarrowingResult:
    """Result of a single narrowing test."""

    test_case: TestCase
    narrowed_categories: list[Category]
    correct_category_found: bool
    processing_time_ms: float
    narrowed_count: int
    # New fields for hybrid strategy
    stage1_categories: list[Category] = None  # Embedding stage results (e.g., 14 categories)
    stage1_processing_time_ms: float = None  # Time for embedding stage
    stage2_processing_time_ms: float = None  # Time for LLM stage
    is_hybrid_result: bool = False


@dataclass
class StrategyResults:
    """Aggregated results for a narrowing strategy."""

    strategy_name: str
    total_tests: int
    correct_found: int
    accuracy_percent: float
    avg_narrowed_count: float
    avg_processing_time_ms: float
    results: list[NarrowingResult]


class NarrowingAccuracyTester:
    """Test harness for evaluating narrowing strategy accuracy."""

    def __init__(self):
        """Initialize the tester with required components."""
        self.category_loader = CategoryLoader()
        self.embedding_service = EmbeddingService()
        self.categories = self.category_loader.load_categories()

        # Create category lookup for validation
        self.category_lookup = {cat.path: cat for cat in self.categories}

        print(f"Loaded {len(self.categories)} categories for testing")
        print(f"Running tests with max_narrowed_categories = {settings.max_narrowed_categories}")
        print("-" * 60)

    def test_strategy(self, strategy_name: str, narrower) -> StrategyResults:
        """Test a specific narrowing strategy against all test cases.

        Args:
            strategy_name: Name of the strategy being tested
            narrower: The narrowing strategy instance

        Returns:
            Aggregated results for the strategy
        """
        results = []

        print(f"\nTesting {strategy_name} Strategy")
        print("=" * 50)

        for i, test_case in enumerate(tests, 1):
            start_time = time.time()

            # Check if this is a hybrid strategy to capture intermediate results
            is_hybrid = strategy_name == "Hybrid" and hasattr(narrower, '_narrow_with_embedding')
            stage1_categories = None
            stage1_time_ms = None
            stage2_time_ms = None

            if is_hybrid:
                # Capture Stage 1: Embedding narrowing
                stage1_start = time.time()
                stage1_categories = narrower._narrow_with_embedding(test_case["text"], self.categories)
                stage1_time_ms = (time.time() - stage1_start) * 1000

                # Capture Stage 2: LLM refinement
                stage2_start = time.time()
                narrowed_categories = narrower._narrow_with_llm_stage(test_case["text"], stage1_categories)
                stage2_time_ms = (time.time() - stage2_start) * 1000
                
                processing_time_ms = stage1_time_ms + stage2_time_ms
            else:
                # Regular narrowing for non-hybrid strategies
                narrowed_categories = narrower.narrow(test_case["text"], self.categories)
                processing_time_ms = (time.time() - start_time) * 1000

            # Check if correct category is in narrowed results
            expected_category_path = test_case["category"]
            correct_category_found = any(cat.path == expected_category_path for cat in narrowed_categories)

            result = NarrowingResult(
                test_case=test_case,
                narrowed_categories=narrowed_categories,
                correct_category_found=correct_category_found,
                processing_time_ms=processing_time_ms,
                narrowed_count=len(narrowed_categories),
                stage1_categories=stage1_categories,
                stage1_processing_time_ms=stage1_time_ms,
                stage2_processing_time_ms=stage2_time_ms,
                is_hybrid_result=is_hybrid,
            )
            results.append(result)

            # Print progress
            status = "✅" if correct_category_found else "❌"
            print(f"{i:2d}. {status} {test_case['text'][:CATEGORIES_DISPLAY_CUTOFF]}...")
            print(f"    Expected: {expected_category_path}")
            
            if is_hybrid and stage1_categories:
                print(f"    Stage 1 (Embedding): {len(stage1_categories)} categories ({stage1_time_ms:.1f}ms)")
                print(f"    Stage 2 (LLM): {len(narrowed_categories)} categories ({stage2_time_ms:.1f}ms)")
                print(f"    Total: {processing_time_ms:.1f}ms")
            else:
                print(f"    Narrowed to {len(narrowed_categories)} categories ({processing_time_ms:.1f}ms)")
            
            if not correct_category_found:
                print("    ⚠️  Correct category NOT found in narrowed results!")
                print(
                    f"    Got: {[cat.path for cat in narrowed_categories[:CATEGORIES_DISPLAY_CUTOFF]]}"
                    f"{'...' if len(narrowed_categories) > CATEGORIES_DISPLAY_CUTOFF else ''}"
                )
            print()

        # Calculate aggregate metrics
        correct_found = sum(1 for r in results if r.correct_category_found)
        accuracy_percent = (correct_found / len(results)) * 100
        avg_narrowed_count = sum(r.narrowed_count for r in results) / len(results)
        avg_processing_time_ms = sum(r.processing_time_ms for r in results) / len(results)

        return StrategyResults(
            strategy_name=strategy_name,
            total_tests=len(results),
            correct_found=correct_found,
            accuracy_percent=accuracy_percent,
            avg_narrowed_count=avg_narrowed_count,
            avg_processing_time_ms=avg_processing_time_ms,
            results=results,
        )

    def analyze_failures(self, strategy_results: StrategyResults) -> None:
        """Analyze and report on failed test cases.

        Args:
            strategy_results: Results to analyze
        """
        failures = [r for r in strategy_results.results if not r.correct_category_found]

        if not failures:
            print("No failures to analyze!")
            return

        print(f"\nFailure Analysis for {strategy_results.strategy_name}")
        print("=" * 50)

        # Group failures by category level
        level_failures = defaultdict(list)
        for failure in failures:
            expected_path = failure.test_case["category"]
            level = expected_path.count("/") - 1
            level_failures[level].append(failure)

        print(f"Failed {len(failures)} out of {strategy_results.total_tests} tests:")

        for level in sorted(level_failures.keys()):
            count = len(level_failures[level])
            print(f"  Level {level}: {count} failures")

            for failure in level_failures[level][:3]:  # Show first 3 examples
                print(f"    - {failure.test_case['category']}")
                print(f"      Text: {failure.test_case['text'][:50]}...")
                narrowed_paths = [cat.path for cat in failure.narrowed_categories]
                print(f"      Got: {narrowed_paths}")
                print()

    def compare_strategies(self, results_list: list[StrategyResults]) -> None:
        """Compare results across different strategies.

        Args:
            results_list: List of strategy results to compare
        """
        print("\nStrategy Comparison")
        print("=" * 60)

        # Print comparison table
        print(f"{'Strategy':<15} {'Accuracy':<10} {'Avg Categories':<15} {'Avg Time (ms)':<15}")
        print("-" * 60)

        for results in results_list:
            print(
                f"{results.strategy_name:<15} "
                f"{results.accuracy_percent:>7.1f}%   "
                f"{results.avg_narrowed_count:>11.1f}     "
                f"{results.avg_processing_time_ms:>11.1f}"
            )

        # Find best performing strategy
        best_accuracy = max(results_list, key=lambda x: x.accuracy_percent)
        fastest = min(results_list, key=lambda x: x.avg_processing_time_ms)

        print(f"\nBest Accuracy: {best_accuracy.strategy_name} ({best_accuracy.accuracy_percent:.1f}%)")
        print(f"⚡ Fastest: {fastest.strategy_name} ({fastest.avg_processing_time_ms:.1f}ms avg)")

    def run_all_tests(self) -> dict[str, StrategyResults]:
        """Run tests for all available narrowing strategies.

        Each strategy gets a fresh embedding service to ensure fair performance
        comparison without caching effects between tests.

        Returns:
            Dictionary mapping strategy names to their results
        """
        # Define strategy constructors (not instances) to create fresh services
        strategy_constructors = {
            "Hybrid": lambda: HybridNarrowing(EmbeddingService()),
        }

        results = {}

        for strategy_name, constructor in strategy_constructors.items():
            print(f"\nCreating fresh embedding service for {strategy_name} strategy...")
            # Create fresh strategy instance with new embedding service
            narrower = constructor()
            results[strategy_name] = self.test_strategy(strategy_name, narrower)
            self.analyze_failures(results[strategy_name])

        # Compare all strategies
        self.compare_strategies(list(results.values()))

        return results

    def save_results_to_json(self, results: dict[str, StrategyResults]) -> Path:
        """Save test results to a JSON file with timestamp.

        Args:
            results: Dictionary mapping strategy names to their results

        Returns:
            Path to the saved JSON file
        """
        # Create results directory if it doesn't exist
        results_dir = Path(__file__).parents[1] / C.RESULTS / C.NARROWING
        results_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"narrowing_accuracy_{timestamp}.json"
        filepath = results_dir / filename

        # Prepare data for JSON serialization
        json_data = {
            "test_info": {
                "test_type": "narrowing_accuracy",
                "timestamp": datetime.now().isoformat(),
                "total_categories": len(self.categories),
                "max_narrowed_categories": settings.max_narrowed_categories,
                "total_test_cases": len(tests),
            },
            "strategies": {},
        }

        for strategy_name, strategy_results in results.items():
            # Convert dataclass to dict and handle Category objects
            strategy_dict = asdict(strategy_results)

            # Convert individual results to serializable format
            serializable_results = []
            for result in strategy_results.results:
                result_dict = {
                    "test_case": result.test_case,
                    "narrowed_categories": [
                        {"path": cat.path, "name": cat.name, "description": cat.llm_description}
                        for cat in result.narrowed_categories
                    ],
                    "correct_category_found": result.correct_category_found,
                    "processing_time_ms": result.processing_time_ms,
                    "narrowed_count": result.narrowed_count,
                    "is_hybrid_result": result.is_hybrid_result,
                }
                
                # Add hybrid-specific fields if available
                if result.is_hybrid_result and result.stage1_categories:
                    result_dict.update({
                        "stage1_categories": [
                            {"path": cat.path, "name": cat.name, "description": cat.llm_description}
                            for cat in result.stage1_categories
                        ],
                        "stage1_processing_time_ms": result.stage1_processing_time_ms,
                        "stage2_processing_time_ms": result.stage2_processing_time_ms,
                        "stage1_count": len(result.stage1_categories),
                    })
                serializable_results.append(result_dict)

            strategy_dict["results"] = serializable_results
            json_data["strategies"][strategy_name] = strategy_dict

        # Save to JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return filepath


def main():
    """Execute the test."""
    print("Category Narrowing Accuracy Test")
    print("=" * 60)
    print("This test evaluates how often the correct category is included")
    print("in the narrowed results for different narrowing strategies.")
    print()

    tester = NarrowingAccuracyTester()
    results = tester.run_all_tests()

    # Save results to JSON file
    json_filepath = tester.save_results_to_json(results)

    print("\nTesting Complete!")
    print("=" * 60)

    # Print final summary
    for strategy_name, strategy_results in results.items():
        print(
            f"{strategy_name}: {strategy_results.correct_found}/{strategy_results.total_tests} "
            f"({strategy_results.accuracy_percent:.1f}%) correct categories found in narrowed results"
        )

    print(f"\nResults saved to: {json_filepath}")
    print("   Use this file for detailed analysis and comparison with other test runs.")


if __name__ == "__main__":
    main()
