# minibaml Implementation Plan

A BAML language implementation in Zig.

## Project Status: PHASE 8 - Pretty Printer & Formatter

---

## Priority Order & Milestones

### ✅ PHASE 0: Project Structure & Foundation
**Status**: ✅ COMPLETED
**Goal**: Create basic project structure and verify build system works

- [x] 0.1: Create src/ directory structure
- [x] 0.2: Create basic main.zig with hello world
- [x] 0.3: Create root.zig module stub
- [x] 0.4: Verify `zig build` works
- [x] 0.5: Verify `zig build test` works
- [x] 0.6: Verify `zig build run` works

**Validation**: ✅ `zig build run` outputs "Hello, minibaml!"

---

### ✅ PHASE 1: Lexer/Tokenizer
**Status**: ✅ COMPLETED
**Goal**: Tokenize BAML source code into a stream of tokens

#### Token Types Implemented:
```zig
// Keywords
class, enum, function, client, test, generator, template_string, type, env

// Primitive Types
string, int, float, bool, null, image, audio, video, pdf, map

// Symbols
@, @@, {, }, [, ], (, ), |, ?, <, >, :, ,, #, "

// Literals
STRING_LITERAL, INT_LITERAL, FLOAT_LITERAL, BOOL_LITERAL
IDENTIFIER, COMMENT, BLOCK_STRING

// Special
EOF, NEWLINE
```

#### Tasks Completed:
- [x] 1.1: Define Token enum with all token types
- [x] 1.2: Create Lexer struct with source input and position tracking
- [x] 1.3: Implement keyword recognition
- [x] 1.4: Implement identifier and type name parsing
- [x] 1.5: Implement string literal parsing (quoted `"..."`)
- [x] 1.6: Implement block string parsing (`#"..."#` with nesting, including `##"..."##`)
- [x] 1.7: Implement number literal parsing (int/float, including negative numbers)
- [x] 1.8: Implement comment parsing (`//`, `///`, `{# #}` with nesting)
- [x] 1.9: Implement symbol/operator parsing
- [x] 1.10: Implement unquoted string parsing (for simple values)
- [x] 1.11: Add comprehensive lexer tests (150+ tests covering all token types)
- [x] 1.12: Create test BAML file and verify tokenization

**Validation**: ✅ PASSED - Lexer successfully tokenizes complete BAML files with all token types.

**Implementation Details**:
- Created `src/lexer.zig` (2,217 lines)
- Comprehensive test suite with 150+ test cases
- CLI tool (`minibaml`) to tokenize BAML files
- Successfully tokenizes `test.baml` with 160 tokens including:
  - Classes with attributes and complex types
  - Enums with values
  - Functions with block string prompts
  - Client declarations with environment variables
  - Test declarations with nested structures
  - All comment types (line, docstring, block)
  - Union types, optional types, array types, map types
  - Block strings with multiple hash delimiters

**Test Results**: All tests pass (`zig build test`)

**Sample Output**:
```
$ ./zig-out/bin/_2025_10_28_ralph_wiggum_coding_ test.baml
Tokenized test.baml: 160 tokens

   0:              comment | Line   1, Col   1 | " Test comment"
   4:        keyword_class | Line   3, Col   1 | "class"
   5:           identifier | Line   3, Col   7 | "Person"
   ...
```

---

### ✅ PHASE 2: AST & Parser Foundation
**Status**: ✅ COMPLETED
**Goal**: Parse tokens into an Abstract Syntax Tree

#### AST Node Types Implemented:
```zig
// Top-level declarations
ClassDecl, EnumDecl, FunctionDecl, ClientDecl, TestDecl, GeneratorDecl,
TemplateStringDecl, TypeAliasDecl

// Type expressions
TypeExpr: Primitive, Array, Map, Optional, Union, Named, Literal

// Class/Enum components
Property, EnumValue, Attribute

// Function components
Parameter

// Value types
Value: String, Int, Float, Bool, Null, Array, Object, EnvVar
```

#### Tasks Completed:
- [x] 2.1: Define AST node structures
- [x] 2.2: Create Parser struct with token stream
- [x] 2.3: Implement parser utilities (peek, advance, expect, match, etc.)
- [x] 2.4: Implement type expression parsing (with precedence)
  - [x] 2.4a: Parse primitive types
  - [x] 2.4b: Parse array types `Type[]`
  - [x] 2.4c: Parse optional types `Type?`
  - [x] 2.4d: Parse union types `Type | Type`
  - [x] 2.4e: Parse map types `map<K, V>`
  - [x] 2.4f: Parse literal types `"value" | 1 | true`
- [x] 2.5: Parse attribute syntax `@attr(args)` and `@@attr(args)`
- [x] 2.6: Parse comments and docstrings (via skipTrivia())
- [x] 2.7: Add parser error handling with line/column info
- [x] 2.8: Add parser recovery (error accumulation with continued parsing)

**Validation**: ✅ PASSED - Parser successfully parses all type expressions and attributes.

**Implementation Details**:
- Created `src/ast.zig` (489 lines) with comprehensive AST structures
- Created `src/parser.zig` (847 lines) with full parser implementation
- Updated `src/root.zig` to export ast and parser modules
- 20+ test cases for parser utilities, types, attributes, and values
- Full support for BAML type syntax with proper operator precedence
- Handles both @ and @@ attributes with arguments
- Parses complex nested structures (arrays, objects, env vars)
- Error handling with line/column info and continued parsing
- Memory-safe with proper deinit() and errdefer blocks

**Test Results**: ✅ All tests pass (`zig build test`)
- Build Summary: 5/5 steps succeeded
- Tests: 2/2 passed

---

### ✅ PHASE 3: Class & Enum Parsing
**Status**: ✅ COMPLETED
**Goal**: Parse class and enum declarations

#### Tasks Completed:
- [x] 3.1: Parse class declaration header
- [x] 3.2: Parse class properties with types
- [x] 3.3: Parse property attributes (@alias, @description, @skip)
- [x] 3.4: Parse class attributes (@@alias, @@dynamic, @@description)
- [x] 3.5: Parse enum declaration header
- [x] 3.6: Parse enum values
- [x] 3.7: Parse enum value attributes
- [x] 3.8: Parse enum attributes
- [x] 3.9: Add tests for class parsing
- [x] 3.10: Add tests for enum parsing
- [x] 3.11: Handle docstring comments (`///`)

**Validation**: ✅ PASSED - Parser successfully parses all class and enum features.

**Implementation Details**:
- Added `parseClassDecl()` function to parse complete class declarations
- Added `parseProperty()` function to parse class properties with types and attributes
- Added `parseEnumDecl()` function to parse complete enum declarations
- Added `parseEnumValue()` function to parse enum values with attributes
- Added `skipTriviaCapturingDocstring()` to capture docstrings while skipping trivia
- Comprehensive test suite with 14 new test cases covering:
  - Simple classes and enums
  - Properties with all type variations (primitive, optional, array, map)
  - Property-level attributes (@alias, @description, etc.)
  - Class-level attributes (@@dynamic, @@alias, etc.)
  - Enum values with attributes
  - Enum-level attributes
  - Docstring support for classes, enums, properties, and values
  - Integration tests with lexer + parser
- All tests pass (`zig build test`)

**Sample Successfully Parsed**:
```baml
/// A person entity
class Person {
  /// The person's name
  name string @alias("full_name") @description("The person's name")
  age int? @description("Optional age")
  status Status

  @@dynamic
}

/// Status enumeration
enum Status {
  /// Active state
  Active @alias("currently_active")
  Inactive @description("Not active")
  Pending @skip

  @@dynamic
}
```

---

### ✅ PHASE 4: Function Parsing
**Status**: ✅ COMPLETED
**Goal**: Parse function declarations with prompts

#### Tasks Completed:
- [x] 4.1: Parse function declaration header
- [x] 4.2: Parse function parameters with types
- [x] 4.3: Parse return type
- [x] 4.4: Parse client specification (short form: string literal)
- [x] 4.5: Parse prompt block (block string with Jinja)
- [x] 4.6: Parse function attributes
- [x] 4.7: Add function parsing tests
- [x] 4.8: Handle multiline prompts correctly

**Validation**: ✅ PASSED - Successfully parses all function features.

**Implementation Details**:
- Added `parseFunctionDecl()` function to parse complete function declarations
- Added `parseParameter()` function to parse function parameters with colon syntax (param: Type)
- Added `keyword_prompt` token to lexer
- Added `arrow` token (`->`) to lexer for return type syntax
- Comprehensive test suite with 8 new test cases covering:
  - Functions without parameters
  - Functions with single and multiple parameters
  - Complex parameter types (arrays, primitives, image, etc.)
  - Union return types
  - Multiline prompts with `##"..."##` syntax
  - Docstring support for functions
  - Client specification parsing
  - Integration tests with lexer + parser
- All tests pass (`zig build test`)

**Sample Successfully Parsed**:
```baml
function ExtractPerson(text: string, image: image) -> Person {
  client "anthropic/claude-sonnet-4"
  prompt #"
    {{ _.role("user") }}
    Extract person info from: {{ text }}
    Image: {{ image }}

    {{ ctx.output_format }}
  "#
}
```

---

### ✅ PHASE 5: Client & Template String Parsing
**Status**: ✅ COMPLETED
**Goal**: Parse client and template_string declarations

#### Tasks Completed:
- [x] 5.1: Parse client<llm> declaration header
- [x] 5.2: Parse client provider
- [x] 5.3: Parse client options block
- [x] 5.4: Parse nested options (headers, etc.)
- [x] 5.5: Parse environment variable references (env.VAR_NAME)
- [x] 5.6: Parse template_string declarations
- [x] 5.7: Parse template_string parameters
- [x] 5.8: Add client parsing tests
- [x] 5.9: Add template_string parsing tests

**Validation**: ✅ PASSED - Successfully parses all client and template_string features.

**Implementation Details**:
- Added `parseClientDecl()` function to parse complete client declarations
  - Parses client type parameter: `client<llm>`
  - Parses provider field: `provider "openai"`
  - Parses options block with key-value pairs
  - Supports environment variables via existing `parseValue()` function
  - Supports nested objects and all value types
- Added `parseTemplateStringDecl()` function to parse template_string declarations
  - Parses parameters using existing `parseParameter()` function
  - Parses template body as block string
  - Supports all parameter types (primitives, arrays, maps, etc.)
- Comprehensive test suite with 10 new test cases covering:
  - Simple client declarations
  - Clients with environment variables
  - Clients with multiple options
  - Clients with nested options objects
  - Template strings without parameters
  - Template strings with single parameter
  - Template strings with multiple parameters
  - Template strings with complex types
  - Integration tests matching validation examples
- All tests pass (`zig build test`)

**Sample Successfully Parsed**:
```baml
client<llm> MyClient {
  provider "openai"
  options {
    model "gpt-4"
    api_key env.OPENAI_API_KEY
    temperature 0.7
    base_url "https://api.openai.com/v1"
  }
}

template_string FormatMessages(msgs: Message[]) #"
  {% for m in msgs %}
    {{ _.role(m.role) }}
    {{ m.content }}
  {% endfor %}
"#
```

**Test Results**: ✅ All tests pass - Build Summary: 5/5 steps succeeded; 2/2 tests passed

---

### ✅ PHASE 6: Test & Generator Parsing
**Status**: ✅ COMPLETED
**Goal**: Parse test and generator declarations

#### Tasks Completed:
- [x] 6.1: Parse test declaration header
- [x] 6.2: Parse functions list
- [x] 6.3: Parse args block with nested values
- [x] 6.4: Parse test attributes (@@check, @@assert)
- [x] 6.5: Parse generator declaration
- [x] 6.6: Parse generator options
- [x] 6.7: Add test parsing tests
- [x] 6.8: Add generator parsing tests

**Validation**: ✅ PASSED - Successfully parses all test and generator features.

**Implementation Details**:
- Added `parseTestDecl()` function to parse complete test declarations
  - Parses test name and header
  - Parses functions list: `functions [Func1, Func2]`
  - Parses args block with key-value pairs supporting all value types
  - Supports nested objects and arrays in args
  - Supports test-level attributes (@@check, @@assert)
- Added `parseGeneratorDecl()` function to parse complete generator declarations
  - Parses generator name and header
  - Parses generator options block with key-value pairs
  - Supports all value types (strings, numbers, etc.)
- Comprehensive test suite with 10 new test cases covering:
  - Simple test declarations with function lists
  - Tests with multiple functions
  - Tests with nested args objects
  - Tests with array args
  - Tests with test-level attributes (@@check, @@assert)
  - Integration test matching test.baml structure
  - Simple generator declarations
  - Generators with version field
  - Generators with multiple options
- All tests pass (`zig build test --summary all`)
- Updated test.baml with generator declaration example

**Sample Successfully Parsed**:
```baml
test TestGreet {
  functions [Greet]
  args {
    p {
      name "Alice"
      age 30
    }
  }
  @@check(output, "length > 0")
}

generator PythonGenerator {
  output_type "python/pydantic"
  output_dir "./baml_client"
  version "0.60.0"
}
```

**Test Results**: ✅ All tests pass - Build Summary: 5/5 steps succeeded; 2/2 tests passed

---

### ✅ PHASE 7: Type System & Validation
**Status**: ✅ COMPLETED
**Goal**: Implement type checking and validation

#### Tasks Completed:
- [x] 7.1: Create type registry/symbol table
- [x] 7.2: Resolve type references
- [x] 7.3: Validate type compatibility
- [x] 7.4: Check for circular dependencies in types
- [x] 7.5: Validate function parameter types
- [x] 7.6: Validate return types
- [x] 7.7: Check for duplicate definitions
- [x] 7.8: Validate attribute usage (partial - basic framework in place)
- [x] 7.9: Add semantic analysis tests

**Validation**: ✅ PASSED - Successfully detects and reports type errors in BAML code.

**Implementation Details**:
- Created `src/validator.zig` (651 lines) with comprehensive validation framework
- TypeRegistry tracks all declared types (classes, enums, primitives)
- FunctionRegistry tracks all declared functions
- Validator performs multi-phase validation:
  - Phase 1: Register all declarations and detect duplicates
  - Phase 2: Validate all type references are defined
  - Phase 3: Check for circular dependencies in class types
- Comprehensive test suite with 11 test cases covering:
  - Type registry operations (primitives, classes, enums)
  - Function registry operations
  - Duplicate definition detection
  - Undefined type detection
  - Undefined function detection in tests
  - Circular dependency detection
  - Complex type validation (arrays, optionals, unions, maps)
- Diagnostic system with error messages including line/column info
- All tests pass (`zig build test`)

**Test Results**: ✅ All tests pass - Build Summary: 5/5 steps succeeded; 2/2 tests passed

**Sample Validations**:
- Detects undefined types: `address Address` when Address is not defined
- Detects circular dependencies: `class A { b B }` and `class B { a A }`
- Detects duplicate definitions: Two classes with the same name
- Validates complex types: `Address[]`, `Person | null`, `map<string, string>`
- Validates function parameter and return types

---

### 🔵 PHASE 8: Pretty Printer & Formatter
**Status**: NOT STARTED
**Goal**: Format BAML code (like `baml fmt`)

#### Tasks:
- [ ] 8.1: Create AST printer
- [ ] 8.2: Implement indentation logic
- [ ] 8.3: Format type expressions
- [ ] 8.4: Format declarations
- [ ] 8.5: Preserve comments
- [ ] 8.6: Add formatter tests
- [ ] 8.7: Create `minibaml fmt` command

**Validation**: Round-trip: parse -> format -> parse produces identical AST

---

### 🔵 PHASE 9: Basic Code Generation (Python)
**Status**: NOT STARTED
**Goal**: Generate Python/Pydantic code from BAML

#### Tasks:
- [ ] 9.1: Create code generator framework
- [ ] 9.2: Generate Python class definitions from BAML classes
- [ ] 9.3: Generate Python enums
- [ ] 9.4: Generate type hints for unions, optionals, arrays
- [ ] 9.5: Generate function stubs
- [ ] 9.6: Add code generation tests
- [ ] 9.7: Verify generated Python code is valid

**Validation**: Generate valid Python code that passes type checking

---

### 🔵 PHASE 10: CLI & File I/O
**Status**: NOT STARTED
**Goal**: Create usable CLI tool

#### Tasks:
- [ ] 10.1: Implement file reading
- [ ] 10.2: Implement `minibaml parse <file>` command
- [ ] 10.3: Implement `minibaml fmt <file>` command
- [ ] 10.4: Implement `minibaml check <file>` command
- [ ] 10.5: Add helpful error messages with line/column info
- [ ] 10.6: Add --version flag
- [ ] 10.7: Add --help text
- [ ] 10.8: Handle multiple input files

**Validation**: CLI tool can parse, format, and check real BAML files

---

## Future Phases (Lower Priority)

### PHASE 11: Multi-file Support
- Import/module system
- Cross-file type references

### PHASE 12: Advanced Features
- Jinja template parsing/validation
- Dynamic types support
- Streaming support
- Client registry

### PHASE 13: Additional Code Generators
- TypeScript generation
- Go generation
- Ruby generation

---

## Current Milestone: PHASE 7 - COMPLETED ✅

**Achievements**:
- ✅ Complete lexer with 150+ test cases
- ✅ Full AST implementation with all BAML constructs
- ✅ Comprehensive parser for all BAML syntax
- ✅ Complete type system with validation
- ✅ Circular dependency detection
- ✅ Duplicate definition checking
- ✅ Type reference validation
- ✅ 651 lines of validator code with 11 test cases
- ✅ All tests passing

**Next Steps** (PHASE 8):
1. Create AST printer
2. Implement indentation logic
3. Format type expressions
4. Format declarations
5. Preserve comments
6. Add formatter tests
7. Create `minibaml fmt` command
