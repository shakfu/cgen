# CGen - Three-Layer Code Generation Platform

**CGen** is a Python-to-C code generation system that implements a three-layer architecture designed to leverage computational resources at code-generation-time to produce optimized and readable C code.

## Core Architecture

CGen implements a three-layer approach that breaks through traditional compiler limitations:

### 1. Layer 1 - Frontend (Static Python Analysis)

- Comprehensive AST parsing and validation
- Type inference and constraint checking
- Python subset validation (4-tier feature hierarchy)
- Static IR generation for C code compatibility

### 2. Layer 2 - Intelligence Layer

- 8 core analyzers and optimizers (static analysis, symbolic execution, bounds checking, etc.)
- Formal verification with Z3 theorem prover integration
- Advanced optimizations (function specialization, vectorization, loop analysis)
- Performance analysis and algorithm correctness verification

### 3. Layer 3 - C Code Generation

- Enhanced cfile library for C language element generation
- Intelligent code writer with optimization-aware output
- [STC (Smart Template Containers)](https://github.com/stclib/STC) integration for high-performance container operations
- Configurable code styling and formatting

## Key Features

- Python-to-C Translation: Complete AST translation with working C code generation

- STC Integration: Python containers (list/dict/set) → STC containers (vec/hmap/hset) with automatic memory management

- Comprehensive Testing: 430+ tests covering all layers with 100% pass rate

- CLI Interface: 8 comprehensive commands for analysis, verification, optimization, and code generation

## Vision

CGen breaks through traditional compiler limitations by using Python's full ecosystem at code-generation-time to analyze, optimize, and generate C code that can exceed hand-written performance while maintaining readability and correctness.

## Quick Start

```bash
# Install CGen
pip install -e .

# Run tests
make test

# Try the CLI
python -m cgen.cli.main --help
```

## Performance Goals

- **10-100x** performance improvement over CPython for computational code
- **2-10x** performance improvement over hand-written C through superior optimization
- **Sub-second** compilation times for typical functions
- **100%** test coverage with formal verification

## Credits

- cgen uses quite a bit of code from Conny Gustafsson'w [cfile]() project in `cgen.generator`, to the extent that the respective license of `cfile` is included in that sub-package. Indeed cgen started off as a fork of `cfile`. Most likely cgen would not have existed if it wasn't for `cfile`. If the same sub-package evolves further it should be contributed back the `cfile` project.
