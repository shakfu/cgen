"""CGen - Intelligent Python-to-C Code Generation with Simplified Two-Layer Architecture.

CGen implements a streamlined two-layer architecture:
1. Layer 1 (Frontend): Unified analysis layer combining static Python parsing with intelligent optimization
2. Layer 2 (Generator): C code generation and output

This package provides:
- High-performance Python-to-C conversion
- Intelligent optimization during code generation
- Static analysis with bounds checking and symbolic execution
- Loop optimization and vectorization detection
- Function specialization and compile-time evaluation
- Formal verification capabilities
- Comprehensive C code generation capabilities
- Build system generation and direct compilation
"""

# C code generation capabilities (Layer 2)
from .generator import (
    Alignment,
    BreakBeforeBraces,
    CFactory,
    PythonToCConverter,
    StyleOptions,
    Writer,
    convert_python_file_to_c,
    convert_python_to_c,
)

# Build system generation and compilation
from .builder import (
    Builder,
    MakefileGenerator,
    CGenMakefileGenerator,
)

# Version information
__version__ = "0.4.0"

__all__ = [
    # Core API
    "CFactory",
    "Writer",
    "StyleOptions",
    "BreakBeforeBraces",
    "Alignment",
    # Python-to-C conversion
    "PythonToCConverter",
    "convert_python_to_c",
    "convert_python_file_to_c",
    # Build system and compilation
    "Builder",
    "MakefileGenerator",
    "CGenMakefileGenerator",
    # Package info
    "__version__",
]
