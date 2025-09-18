"""Shared enums for the classification system."""

from enum import Enum


class NarrowingStrategy(str, Enum):
    """Strategy for narrowing down categories before final classification."""

    EMBEDDING = "embedding"
    HYBRID = "hybrid"
