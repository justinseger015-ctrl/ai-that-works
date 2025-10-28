# Building MiniBaml from Source

This guide covers building the MiniBaml compiler from source and running it against the test suite.

## Prerequisites

- **Zig 0.15.1** or compatible version
  - Download from [ziglang.org/download](https://ziglang.org/download/)
  - Verify: `zig version`

## Building

### 1. Clone or navigate to the repository

```bash
cd /path/to/2025-10-28-ralph-wiggum-coding-agent-power-tools
```

### 2. Build the project

```bash
zig build
```

This compiles the minibaml executable and places it in `zig-out/bin/`.

### 3. Build with optimizations (optional)

```bash
# Release-safe (recommended for production)
zig build -Doptimize=ReleaseSafe

# Release-fast (maximum performance)
zig build -Doptimize=ReleaseFast

# Release-small (minimum binary size)
zig build -Doptimize=ReleaseSmall
```

### 4. Run tests

```bash
zig build test
```

## Generating Code

### Generate Python Code

After building, generate Python code from your BAML files:

```bash
# Generate Python (default) and save to file
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ generate test_baml_src > baml_client.py

# Or using zig build run
zig build run -- generate test_baml_src > baml_client.py
```

Generate TypeScript instead:

```bash
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ generate test_baml_src --typescript > baml_client.ts
# or use the shorthand
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ gen test_baml_src -ts > baml_client.ts
```

Generate only the Python TypeBuilder module:

```bash
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ gen test_baml_src --typebuilder > type_builder.py
```

### Test the Generated Code

Verify that the generated Python code works:

```bash
# Generate the code
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ generate test_baml_src > baml_client.py

# Quick test: Check imports and available types
python3 -c "
import baml_client
print('✓ Generated code imports successfully')
print('Available types:', [name for name in dir(baml_client) if not name.startswith('_') and name[0].isupper()])
"
```

For a more thorough test, create a test script that validates the generated Pydantic models:

```python
# test_generated.py
import baml_client
from pydantic import ValidationError

# Test that generated types exist
print("Testing generated types...")
assert hasattr(baml_client, 'Person'), "Person class not found"
assert hasattr(baml_client, 'Address'), "Address class not found"
assert hasattr(baml_client, 'Status'), "Status enum not found"
assert hasattr(baml_client, 'Priority'), "Priority enum not found"
print("✓ All expected types found")

# Test enum values
print("\nTesting Status enum values:")
print(f"  - {baml_client.Status.Active.value}")
print(f"  - {baml_client.Status.Inactive.value}")
print(f"  - {baml_client.Status.Pending.value}")

print("\nTesting Priority enum values:")
print(f"  - {baml_client.Priority.Low.value}")
print(f"  - {baml_client.Priority.Medium.value}")
print(f"  - {baml_client.Priority.High.value}")
print(f"  - {baml_client.Priority.Urgent.value}")

# Test instantiating classes
print("\nTesting class instantiation...")
address = baml_client.Address(
    street="123 Main St",
    city="San Francisco",
    country="USA"
)
print(f"✓ Created Address: {address.city}, {address.country}")

person = baml_client.Person(
    name="John Doe",
    age=30,
    email="john@example.com",
    address=address
)
print(f"✓ Created Person: {person.name}, age {person.age}")

# Test Pydantic validation
print("\nTesting Pydantic validation...")
try:
    bad_person = baml_client.Person(
        name="Jane",
        age="invalid",  # Should be int
        email="jane@example.com"
    )
    print("✗ Validation should have failed")
except ValidationError as e:
    print(f"✓ Validation correctly rejected invalid data")

print("\n✓ All tests passed!")
```

Run the test:

```bash
python3 test_generated.py
```

Expected output:
```
Testing generated types...
✓ All expected types found

Testing Status enum values:
  - active
  - inactive

Testing Priority enum values:
  - high
  - medium
  - low

Testing class instantiation...
✓ Created Address: San Francisco, CA
✓ Created Person: John Doe, age 30

Testing Pydantic validation...
✓ Validation correctly rejected invalid data

✓ All tests passed!
```

## Running Against test_baml_src

The `test_baml_src/` directory contains sample BAML files that demonstrate the language features:

```
test_baml_src/
├── clients.baml          # Client configurations (OpenAI, Anthropic)
├── functions.baml        # Function definitions
└── models/
    ├── person.baml       # Person and Address class models
    └── status.baml       # Status and Priority enums
```

### Available Commands

#### Parse the test directory

Shows the Abstract Syntax Tree for all BAML files:

```bash
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ parse test_baml_src
```

#### Validate the test directory

Checks all BAML files for errors:

```bash
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ check test_baml_src
```

#### Tokenize individual files

View lexical tokens:

```bash
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ test_baml_src/clients.baml
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ test_baml_src/functions.baml
```

#### Format files

Pretty-print formatted BAML:

```bash
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ fmt test_baml_src/clients.baml
```

### Complete Verification Workflow

Validate everything works end-to-end:

```bash
# Build
zig build

# Validate BAML files
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ check test_baml_src

# Generate Python code
./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ generate test_baml_src > baml_client.py

# Test generated code
python3 -c "import baml_client; print('✓ Success: Generated code works!')"
```

## Development Tips

### Watch mode

For development, you can use a simple watch loop:

```bash
./loop.sh
```

This will rebuild on file changes (if the script is configured for watching).

### Clean build

```bash
rm -rf zig-out .zig-cache
zig build
```

### Verbose build

```bash
zig build --verbose
```

## Troubleshooting

### "Cannot open file" errors

Ensure you're running from the project root directory where `test_baml_src/` exists.

### Zig version mismatch

This project is built with Zig 0.15.1. Version mismatches may cause build errors. Check your version:

```bash
zig version
```

### Build cache issues

Clear the cache and rebuild:

```bash
rm -rf .zig-cache zig-out
zig build
```

## Project Structure

- `src/` - Zig source code
  - `main.zig` - CLI entry point
  - `codegen.zig` - Code generation (Python/TypeScript)
  - `lexer.zig` - Tokenization
  - `parser.zig` - AST construction
  - `ast.zig` - AST definitions
  - `validator.zig` - Semantic validation
  - `formatter.zig` - Pretty printer
- `test_baml_src/` - Test BAML files
- `build.zig` - Build configuration
- `zig-out/` - Build output (after building)

## What is BAML?

BAML (Boundary Markup Language) is a domain-specific language for defining LLM interactions. It supports:

- **Client configurations** - OpenAI, Anthropic, etc.
- **Data models** - Classes with fields, enums
- **Functions** - LLM prompts with typed inputs/outputs
- **Template strings** - Jinja-style templating

See the files in `test_baml_src/` for examples.
