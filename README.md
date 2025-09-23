# CGen - Complete Python-to-C Translation Pipeline

**CGen** provides a comprehensive pipeline for converting Python modules into optimized C code and executables. The system follows a clear **7-phase pipeline architecture** that transforms Python source code through validation, analysis, optimization, mapping, generation, and optional compilation.

## Pipeline Architecture

CGen implements a streamlined pipeline approach that provides clear flow from Python source to executable:

```
┌─────────────────────┐
│  Python Module      │
│  Input              │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  1. Validation      │  Static-python style validation & translatability assessment
│     Phase           │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  2. Analysis        │  AST parsing & semantic element breakdown
│     Phase           │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  3. Python          │  Python-level optimizations (constant folding, loop analysis)
│     Optimization    │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  4. Mapping         │  Python semantics → C semantics mapping
│     Phase           │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  5. C Optimization  │  C-level optimizations (vectorization, memory layout)
│     Phase           │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  6. Generation      │  Optimized C code generation
│     Phase           │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  7. Build Phase     │  Direct compilation OR Makefile generation
│     (Optional)      │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Executable Output  │
│  (or Makefile)      │
└─────────────────────┘
```

### Core Components

- **Frontend Layer**: Unified analysis combining static Python parsing with intelligent optimization
- **Generator Layer**: C code generation with [STC (Smart Template Containers)](https://github.com/stclib/STC) integration
- **Builder Layer**: Makefile generation and direct compilation capabilities
- **Pipeline Orchestrator**: Coordinates all phases and provides clear API

## Key Features

### 🚀 Complete Pipeline
- **Python-to-Executable**: Single command from Python source to running executable
- **7-Phase Architecture**: Clear validation → analysis → optimization → generation → build flow
- **Flexible Build Options**: Direct compilation or Makefile generation

### 🔧 Advanced Optimization
- **Multi-Level Optimization**: Python-level and C-level optimization phases
- **Static Analysis**: Bounds checking, symbolic execution, call graph analysis
- **Intelligence Layer**: Function specialization, vectorization detection, compile-time evaluation
- **Formal Verification**: Memory safety and algorithm correctness verification

### 🏗️ Production Ready
- **STC Integration**: Python containers (list/dict/set) → STC containers (vec/hmap/hset) with automatic memory management
- **Comprehensive Testing**: 619+ tests covering all phases with 100% pass rate
- **Clear Error Reporting**: Phase-by-phase error tracking and debugging
- **Professional Output**: Optimized, readable C code with configurable styling

### 📚 Easy to Use
- **Simple API**: `convert_python_to_c("file.py")` for basic usage
- **Advanced Control**: Full pipeline configuration for power users
- **Clear Documentation**: Phase-by-phase architecture explanations
- **Multiple Interfaces**: Python API, CLI commands, and direct integration

## Vision

CGen breaks through traditional compiler limitations by using Python's full ecosystem at code-generation-time to analyze, optimize, and generate C code that can exceed hand-written performance while maintaining readability and correctness.

## Quick Start

```bash
# Install CGen
pip install -e .

# Run tests
make test

# Convert Python to C (basic usage)
python -c "
from cgen import convert_python_to_c
result = convert_python_to_c('my_module.py')
print(f'Generated: {result.output_files[\"c_source\"]}')
"

# Convert with Makefile generation
python -c "
from cgen import convert_and_build
result = convert_and_build('my_module.py', build_mode='makefile')
print(f'C file: {result.output_files[\"c_source\"]}')
print(f'Makefile: {result.output_files[\"makefile\"]}')
"

# Advanced pipeline usage
python -c "
from cgen.pipeline import CGenPipeline, PipelineConfig, OptimizationLevel
config = PipelineConfig(optimization_level=OptimizationLevel.AGGRESSIVE)
pipeline = CGenPipeline(config)
result = pipeline.convert('my_module.py', build='direct')
print(f'Executable: {result.executable_path}')
"
```

## Usage Examples

### Simple Python-to-C Conversion
```python
from cgen import convert_python_to_c

# Convert a Python file to C
result = convert_python_to_c("my_algorithm.py")
if result.success:
    print(f"C code generated: {result.output_files['c_source']}")
else:
    print(f"Conversion failed: {result.errors}")
```

### Complete Pipeline with Build
```python
from cgen import convert_and_build

# Convert and generate Makefile
result = convert_and_build(
    "my_module.py",
    build_mode="makefile"
)

if result.success:
    # Generated files ready to build
    print(f"C source: {result.output_files['c_source']}")
    print(f"Makefile: {result.output_files['makefile']}")

    # Build with: make -f generated_makefile
```

### Advanced Configuration
```python
from cgen.pipeline import CGenPipeline, PipelineConfig, OptimizationLevel, BuildMode

# Create custom configuration
config = PipelineConfig(
    optimization_level=OptimizationLevel.AGGRESSIVE,
    build_mode=BuildMode.DIRECT,
    compiler="clang",
    compiler_flags=["-O3", "-march=native"],
    include_dirs=["/opt/include"],
    libraries=["math"]
)

# Run pipeline
pipeline = CGenPipeline(config)
result = pipeline.convert("high_performance_module.py")

if result.success:
    print(f"Executable ready: {result.executable_path}")
    print(f"Optimizations applied: {len(result.phase_results)}")
```

## Pipeline Phases Explained

### Phase 1: Validation
- **Static-Python Style Check**: Ensures code follows static-python conventions
- **Translatability Assessment**: Verifies code can be converted to C
- **Constraint Checking**: Validates memory safety and type constraints
- **Subset Validation**: Confirms compatibility with supported Python features

### Phase 2: Analysis
- **AST Parsing**: Breaks down Python code into semantic elements
- **Type Inference**: Determines types for unannotated variables
- **Control Flow Analysis**: Maps execution paths and dependencies
- **Complexity Assessment**: Evaluates computational complexity

### Phase 3: Python Optimization
- **Constant Folding**: Pre-computes constant expressions
- **Loop Analysis**: Identifies optimization opportunities in loops
- **Function Specialization**: Creates optimized versions for specific use cases
- **Dead Code Elimination**: Removes unreachable code paths

### Phase 4: Mapping
- **Semantic Translation**: Maps Python constructs to C equivalents
- **Container Mapping**: Translates Python containers to STC containers
- **Memory Layout Planning**: Optimizes data structure arrangements
- **API Bridging**: Handles Python-to-C interface requirements

### Phase 5: C Optimization
- **Vectorization**: Applies SIMD optimizations where possible
- **Memory Access Optimization**: Improves cache locality and alignment
- **Register Allocation Hints**: Guides compiler register usage
- **Architecture-Specific Tuning**: Optimizes for target architecture

### Phase 6: Generation
- **C Code Generation**: Produces clean, readable C source code
- **Style Application**: Applies consistent formatting and conventions
- **Comment Generation**: Adds helpful documentation to generated code
- **Header Management**: Includes necessary headers and declarations

### Phase 7: Build (Optional)
- **Makefile Generation**: Creates comprehensive build system
- **Direct Compilation**: Compiles to executable immediately
- **Dependency Management**: Handles libraries and include paths
- **Optimization Flags**: Applies appropriate compiler optimizations

## Performance Goals

- **10-100x** performance improvement over CPython for computational code
- **2-10x** performance improvement over hand-written C through superior optimization
- **Sub-second** compilation times for typical functions
- **100%** test coverage with formal verification

## Credits

- cgen uses quite a bit of code from Conny Gustafsson'w [cfile](https://github.com/cogu/cfile) project in `cgen.generator`, to the extent that the respective license of `cfile` is included in that sub-package. Indeed cgen started off as a fork of `cfile`. Most likely cgen would not have existed if it wasn't for `cfile`. If the same sub-package evolves further it should be contributed back the `cfile` project.
