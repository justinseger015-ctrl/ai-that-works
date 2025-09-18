# 🦄 Large Scale Classification System

> A production-ready AI classification system that handles 1000+ categories using a various approaches combining embeddings and LLM-based selection.

[Video Tutorial](https://youtu.be/6B7MzraQMZk)

[![Large Scale Classification](https://img.youtube.com/vi/6B7MzraQMZk/0.jpg)](https://www.youtube.com/watch?v=6B7MzraQMZk)

## Overview

This system solves the challenge of classifying text into large category sets (1000+ categories) by using a two-stage approach:

1. **Narrowing Stage**: Uses vector embeddings to quickly narrow down from 1000+ categories to ~5-10 candidates
2. **Selection Stage**: Uses LLM reasoning to select the best final category from the narrowed candidates

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- UV package manager

### Installation

```bash
# Clone and navigate to the project
cd level-3-code/large_scale_classification

# Install runtime dependencies (for running the system)
uv sync

# OR install with development dependencies (for contributing/development)
uv sync --extra dev

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

> **Note**: Use `uv sync --extra dev` if you plan to contribute to the project or need development tools like linting (ruff), type checking (pyright), and testing (pytest). For just running the classification system, `uv sync` is sufficient.

### Generate BAML Client

```bash
# Convert BAML files to Python client code
uv run baml-cli generate
```

### Basic Usage

```bash
# Run the interactive classification system
uv run python src/main.py
```

This will prompt you to enter text for classification and return the most appropriate category.

## Architecture

### Core Components

The system is built with a modular architecture:

```
src/
├── main.py                    # Entry point
├── classification/            # Core classification logic
│   ├── pipeline.py           # Main orchestrator
│   ├── embeddings.py         # OpenAI embedding service
│   ├── narrowing.py          # Category narrowing strategies
│   ├── selection.py          # LLM-based final selection
│   └── vector_store.py       # ChromaDB vector store
├── data/                     # Data management
│   ├── category_loader.py    # Category loading and processing
│   └── models.py             # Pydantic data models
├── config/                   # Configuration
│   └── settings.py           # Application settings
└── shared/                   # Shared utilities
    ├── logger.py             # Structured logging
    ├── constants.py          # Application constants
    └── enums.py              # Enums and types
```

### Classification Pipeline

1. **Text Input**: User provides text to classify
2. **Category Loading**: System loads 1000+ categories from `data/categories.txt`
3. **Embedding Generation**: Creates embeddings for input text and categories
4. **Narrowing**: Reduces categories to top candidates using similarity search
5. **LLM Selection**: Uses BAML/LLM to choose the best category from candidates
6. **Result**: Returns selected category with metadata and timing

## Performance Features

### Vector Store Caching

The system includes an advanced ChromaDB-based vector store for performance:

- **Faster lookups**: Cached embeddings vs fresh API calls
- **Automatic caching**: New categories are automatically added to the store
- **Model validation**: Ensures compatibility between stored and current embeddings

#### Build Vector Store

```bash
# Build the vector store from categories
python scripts/build_vector_store.py

# Force rebuild (e.g., after changing embedding models)
python scripts/build_vector_store.py --force-rebuild
```

### Narrowing Strategies

The system supports multiple narrowing strategies:

- **Embedding**: Pure embedding similarity (fastest)
- **Hybrid**: Embedding + LLM reasoning (most accurate, default)
- **LLM**: Pure LLM-based narrowing (most flexible)

Configure in `src/config/settings.py`:

```python
narrowing_strategy = NarrowingStrategy.HYBRID  # EMBEDDING, HYBRID, or LLM
max_narrowed_categories = 5  # Number of candidates to pass to final selection
```

## Testing

The system includes comprehensive testing infrastructure:

### Run Tests

```bash
# Run all tests
cd tests
python run_tests.py

# Run specific test types
python run_tests.py --narrowing-accuracy
python run_tests.py --all
```

### Test Types

- **Narrowing Accuracy**: Tests how often the correct category is included in narrowed results
- **Selection Accuracy**: Tests final category selection accuracy
- **Integration Tests**: End-to-end pipeline testing
- **Unit Tests**: Individual component testing

### Test Results

Tests automatically save detailed JSON results with timestamps for performance tracking:

```bash
# Compare results across test runs
python tests/compare_results.py --narrowing file1.json file2.json
```

## Configuration

### Environment Variables

Create a `.env` file with only the required API key:

```bash
# Required - the only thing needed in .env
OPENAI_API_KEY=your_api_key_here
```

### Application Settings

All other configuration is done in `src/config/settings.py`. You can modify the default values directly in the file:

```python
class Settings(BaseSettings):
    """Application configuration settings."""

    # OpenAI Configuration
    openai_api_key: str  # Loaded automatically from .env. Don't put your key here
    embedding_model: str = "text-embedding-3-small"
    
    # Classification Strategy
    narrowing_strategy: NarrowingStrategy = NarrowingStrategy.HYBRID
    max_narrowed_categories: int = 5
    
    # Hybrid Strategy Specific Settings
    max_embedding_candidates: int = 10  # How many categories embedding stage returns
    max_final_categories: int = 3       # How many categories LLM stage returns
    
    # Data Configuration
    categories_file_path: pathlib.Path = CWD.parents[1] / C.DATA / C.CATEGORIES_TXT
```

### Available Narrowing Strategies

Configure `narrowing_strategy` in settings.py:

- `NarrowingStrategy.EMBEDDING`: Pure embedding similarity (fastest)
- `NarrowingStrategy.HYBRID`: Embedding + LLM reasoning (most accurate, default)
- `NarrowingStrategy.LLM`: Pure LLM-based narrowing (most flexible)

### Tuning Performance

Adjust these settings in `settings.py` to optimize for your use case:

- `max_narrowed_categories`: Number of candidates passed to final selection (default: 5)
- `max_embedding_candidates`: For hybrid strategy, how many categories the embedding stage returns (default: 10)
- `max_final_categories`: For hybrid strategy, how many categories the LLM stage returns (default: 3)
- `embedding_model`: OpenAI embedding model to use (default: "text-embedding-3-small")

### Category Data

Categories are loaded from `data/categories.txt`. The format supports hierarchical categories:

```
/Appliances/Refrigerators/French Door Refrigerators
/Appliances/Dishwashers/Built-in Dishwashers
/Appliances/Appliance Parts/Dishwasher Parts
```

## 🔧 Advanced Usage

### Programmatic Usage

```python
from src.classification.pipeline import ClassificationPipeline

# Initialize pipeline
pipeline = ClassificationPipeline()

# Classify text
result = pipeline.classify("Samsung 17.5-cu ft French door refrigerator")

print(f"Category: {result.category.name}")
print(f"Confidence: {result.confidence}")
print(f"Processing time: {result.processing_time_ms:.1f}ms")
print(f"Candidates: {[c.name for c in result.candidates]}")
```

### Custom Categories

To use your own category set:

1. Replace `data/categories.txt` with your categories
2. Rebuild the vector store: `python scripts/build_vector_store.py --force-rebuild`
3. Update test cases in `tests/data/test_cases.py` if needed

### BAML Integration

The system uses [BAML](https://docs.boundaryml.com/) for LLM interactions. BAML files are in `src/baml_src/`:

- `clients.baml`: LLM client configurations
- `pick_best_category.baml`: Category selection prompt
- `generators.baml`: Type definitions
- `resume.baml`: Additional functionality

## Development

### Adding New Features

The modular architecture makes it easy to extend:

1. **New Narrowing Strategy**: Inherit from `NarrowingStrategy` in `narrowing.py`
2. **Custom Embedding Models**: Modify `EmbeddingService` in `embeddings.py`
3. **Additional Metadata**: Extend `ClassificationResult` in `models.py`

### Code Quality

- **Type Safety**: Full Pydantic models and type hints
- **Logging**: Structured logging with performance metrics
- **Error Handling**: Comprehensive exception handling
- **Testing**: Unit, integration, and accuracy tests

---

Built with ❤️ using BAML, OpenAI, ChromaDB, and Python, but especially BAML.
