# CHANGELOG

All notable project-wide changes will be documented in this file. Note that each subproject has its own CHANGELOG.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and [Commons Changelog](https://common-changelog.org). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Types of Changes

- Added: for new features.
- Changed: for changes in existing functionality.
- Deprecated: for soon-to-be removed features.
- Removed: for now removed features.
- Fixed: for any bug fixes.
- Security: in case of vulnerabilities.

---

## [0.3.0] - 2024-09-23

### Added

#### Complete Container Operations Implementation

- **Dictionary Element Access**: Full implementation of `dict[key]` access and `dict[key] = value` assignment
- **Dictionary Operations**: Native STC hmap operations with `dict_insert()` and `dict_at()` mapping
- **Set Operations Suite**: Complete set functionality including `set.add()`, `set.remove()`, `set.discard()`
- **Set Membership Testing**: Support for `element in set` and `element not in set` with STC `contains()` operations
- **List Element Access**: Implementation of `list[index]` access and `list[index] = value` assignment
- **Cross-Container Operations**: Complex operations between different container types in single functions
- **Comprehensive Container System**: All three container types (list, dict, set) fully operational with real-world usage patterns

#### Advanced Expression Processing

- **Subscript Operations**: Complete `ast.Subscript` handling for all container types
- **Membership Operators**: Support for `ast.In` and `ast.NotIn` comparison operations
- **Container Constructor Handling**: Special processing for `set()` empty constructor calls
- **Complex Expression Chains**: Support for nested container operations like `dict[key] = list[index] * 2`

#### Implementation Details

- **Enhanced STC Operation Mapper**: Extended with `map_set_operation()` method for comprehensive set operations
- **Assignment Target Expansion**: Updated `_convert_assignment()` to handle `ast.Subscript` targets for container element assignment
- **Membership Test Processing**: New `_convert_membership_test()` method for `in`/`not in` operations with proper negation handling
- **Container Method Call Resolution**: Extended method call handling to support set operations alongside existing list operations
- **Built-in Function Enhancement**: Enhanced `len()` function support to work with all container types

#### Generated C Code Examples

**Dictionary Operations:**
```python
scores: dict[str, int] = {}
scores["Alice"] = 95
alice_score: int = scores["Alice"]
```
Generated C:
```c
hmap_cstr_int32 scores = {0};
scores_insert(&scores, "Alice", 95);
int alice_score = *scores_at(&scores, "Alice");
```

**Set Operations:**
```python
unique_nums: set[int] = set()
unique_nums.add(42)
has_42: bool = 42 in unique_nums
```
Generated C:
```c
hset_int32 unique_nums = {0};
unique_nums_insert(&unique_nums, 42);
bool has_42 = unique_nums_contains(&unique_nums, 42);
```

**List Element Access:**
```python
numbers: list[int] = [10, 20, 30]
first: int = numbers[0]
numbers[1] = 25
```
Generated C:
```c
vec_int32 numbers = {0};
numbers_push(&numbers, 10); numbers_push(&numbers, 20); numbers_push(&numbers, 30);
int first = *numbers_at(&numbers, 0);
*numbers_at(&numbers, 1) = 25;
```

## [0.2.0]

### Added

#### Complete STC (Smart Template Containers) Integration

- **Full Container Support**: Comprehensive Python-to-STC container mapping with automatic header generation
- **Type System**: `list[int]` → `vec_int32`, `dict[str, int]` → `hmap_cstr_int32`, `set[str]` → `hset_cstr`
- **Container Operations**: Native STC operations for append, length, iteration with proper C code generation
- **Memory Management**: Automatic STC container initialization and cleanup with `{0}` initialization
- **Multi-Container Discovery**: Two-pass analysis for automatic STC include and declaration generation

#### Expression System Overhaul

- **Binary Expression Support**: New `BinaryExpression` class for proper arithmetic and logical operations
- **Unary Expression Support**: New `UnaryExpression` class for negation, logical not, and bitwise operations
- **Function Call Integration**: Fixed function calls in expressions to generate proper C code instead of Python object representations
- **Complex Expression Handling**: Nested expressions, boolean operations, and comparison chains

#### Code Generation Improvements

- **Element-Based Architecture**: Replaced string interpolation with proper C element objects
- **Raw Code Support**: New `RawCode` element for direct C code insertion
- **STC Writers**: Dedicated writers for STC container elements and operations
- **Container Method Calls**: Support for `list.append()`, `len(list)` with automatic STC operation mapping

#### Parser and Analysis Enhancements

- **Container Type Analysis**: `analyze_container_type()` function for detecting Python container annotations
- **Variable Tracking**: Container variable registry for proper operation mapping
- **Type Annotation Processing**: Enhanced type extraction with full container type support
- **Method Call Resolution**: Attribute-based method calls for container operations

### Fixed

- **Function Call Object Representation**: Resolved issue where function calls showed `<object at 0x...>` in expressions
- **For-Loop Range Expressions**: Fixed complex expressions in for-loop ranges (e.g., `range(1, n + 1)`)
- **Expression Type Consistency**: All expression methods now return proper `core.Element` objects
- **Import Dependencies**: Corrected module imports for STC integration and writer classes

### Changed

- **Expression Architecture**: Migrated from string-based to element-based expression handling
- **Container Type Mapping**: Updated from simple pointer conversion to full STC container integration
- **Test Expectations**: Updated tests to reflect STC containers instead of C pointers
- **Module Processing**: Enhanced two-pass module processing for container discovery and generation

#### Previously Added (0.1.1)

#### Runtime Library Support

- **CGen Runtime Library**: Comprehensive C runtime support for generated Python-to-C code
- **STC Integration Design**: Runtime complements STC containers rather than replacing them
- **Error Handling System**: Python-like exception handling with detailed error context and stack traces
- **Python Operations Library**: Essential Python operations (bool, range, slice, enumerate, zip) implemented in C
- **STC Bridge Functions**: Seamless bridge between Python semantics and STC container operations
- **File I/O Operations**: Python-compatible file operations (open, read, write, exists) with error handling
- **Memory Management**: Safe memory operations with bounds checking and automatic cleanup
- **Python Semantic Layer**: Maintains Python behavior while leveraging C performance

#### Runtime Library Components

- **`cgen_error_handling`**: Python exception system with IndexError, KeyError, ValueError support
- **`cgen_python_ops`**: Core Python functions (bool, abs, min, max, sum, range, slice operations)
- **`cgen_stc_bridge`**: Python semantics on STC containers (split, join, bounds checking, iteration)
- **`cgen_file_ops`**: File I/O with Python `open()`, context manager, and path operations
- **`cgen_memory_ops`**: Memory pools, scope allocators, reference counting, and safety utilities

#### Translation Quality Improvements

- **STC Template Fixes**: Resolved multiple `#define T` macro redefinitions in STC generation
- **Python Construct Support**: Enhanced support for dictionary literals, attribute access, method calls
- **Expression Translation**: Improved handling of `sys.argv`, `os.path.exists`, string methods
- **Error Messages**: Better error reporting for unsupported constructs with specific guidance

## [0.1.0]

### Added

#### Testing Infrastructure

- **Framework Modernization**: Complete migration from unittest to pytest (500+ tests)
- **Zero Test Failures**: 100% test pass rate with comprehensive coverage
- **Enhanced Capabilities**: Pytest fixtures, parametrized tests, better error reporting
- **CI/CD Ready**: Makefile integration with pytest workflow
- **Multi-layer Coverage**: Frontend, Intelligence, Generator, and Integration testing

#### Advanced C11 Features

- **Function Pointers**: Type-safe function pointer declarations with parameter lists
- **Variadic Functions**: Variable argument function declarations with storage classes
- **Static Assertions**: Compile-time assertion statements with condition validation
- **Generic Selections**: C11 type-generic programming with type associations
- **Function Pointer Variables**: Function pointer declarations with qualifiers

#### STC Integration

- **Container Type Mappings**: Python list → STC vec with full operation support
- **Memory Safety**: Automatic cleanup and exception-safe wrapper generation
- **Type Safety**: Type-safe container operations with compile-time validation
- **Performance Optimization**: High-performance container operations exceeding STL

#### Generator Layer

- **Python-to-C AST Translator**: Complete expression and statement translation
- **STC Container Integration**: Python list/dict/set → STC vec/hmap/hset translation
- **Memory Management**: Automatic cleanup and exception-safe wrappers
- **Type System Integration**: Python type annotations to C type mapping
- **Build System**: Complete integration with makefilegen for C compilation

#### Intelligence Layer

- **Static Code Analyzer**: Control flow analysis and symbolic execution
- **Memory Bounds Checker**: Memory safety analysis and bounds checking
- **Call Graph Analyzer**: Inter-function analysis and optimization
- **Compile-time Evaluator**: 8 transformation types with performance analysis
- **Loop Analyzer**: Loop unrolling and optimization with performance metrics
- **Function Specializer**: 8 specialization strategies for performance optimization
- **Vectorization Detector**: SIMD optimization with architecture-specific features
- **Formal Verification**: Z3 theorem prover integration with memory safety proofs
- **Performance Analyzer**: Algorithm correctness verification and complexity detection

#### Frontend Layer

- **AST Analysis Framework**: Comprehensive Python code analysis with complexity calculation
- **Type Inference Engine**: Multi-method type inference with confidence scoring
- **Constraint Checker**: 22+ rules for memory safety, type safety, and C compatibility
- **Subset Validator**: 4-tier feature hierarchy with 20+ validation rules
- **Static IR System**: Intermediate representation with C code generation capabilities

### Architecture

- **Three-Layer Architecture**: Frontend analysis, Intelligence layer, and C code generation

### Changed

- **Package Structure**: Migrated from cfile to comprehensive cgen package
- **Testing Framework**: Upgraded from unittest to pytest for enhanced capabilities
- **CLI Interface**: Enhanced from basic commands to 8 comprehensive intelligence commands
- **Code Generation**: Upgraded from manual C patterns to intelligent STC-based generation

### Fixed

- **STC Template Issues**: Multiple #define T macro redefinitions in template generation
- **Python Construct Support**: Dictionary literals, attribute access, complex for loops
- **Translation Quality**: Enhanced method call handling and string operations
- **Memory Management**: Proper container lifecycle and cleanup generation
