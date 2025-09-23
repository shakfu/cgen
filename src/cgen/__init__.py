"""CGen - Intelligent Python-to-C Code Generation with Three-Layer Architecture.

CGen implements a revolutionary three-layer architecture:
1. Layer 1 (Frontend): Static Python analysis and parsing
2. Layer 2 (Intelligence): Code-generation-time optimization and transformation
3. Layer 3 (Core): C code generation and output

This package provides:
- High-performance Python-to-C conversion
- Intelligent optimization during code generation
- Extensible architecture for domain-specific optimizations
- Comprehensive C code generation capabilities
- Build system generation and direct compilation
"""

# C code generation capabilities (Layer 3)
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
