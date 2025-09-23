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

## [0.1.x]

### Added

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
