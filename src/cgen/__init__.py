"""CGen - Complete Python-to-C Translation Pipeline.

CGen provides a comprehensive pipeline for converting Python modules into optimized
C code and executables. The system follows a clear 7-phase pipeline architecture:

PIPELINE ARCHITECTURE:
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

USAGE:
    # Simple conversion
    from cgen import convert_python_to_c
    result = convert_python_to_c("my_module.py")

    # Full pipeline with build
    from cgen import convert_and_build
    result = convert_and_build("my_module.py", build_mode="makefile")

    # Advanced pipeline control
    from cgen.pipeline import CGenPipeline, PipelineConfig
    config = PipelineConfig(optimization_level=OptimizationLevel.AGGRESSIVE)
    pipeline = CGenPipeline(config)
    result = pipeline.convert("my_module.py", build="direct")

FEATURES:
- Complete pipeline from Python source to executable
- Static-python subset validation
- Multi-phase optimization (Python-level and C-level)
- Intelligent code generation with formal verification
- Flexible build system (direct compilation or Makefile generation)
- Clear error reporting and debugging at each phase
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

# Complete Pipeline System
from .pipeline import (
    CGenPipeline,
    PipelineConfig,
    PipelineResult,
    BuildMode,
    PipelinePhase,
    convert_python_to_c,
    convert_and_build,
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
        # Complete Pipeline System
        "CGenPipeline",
        "PipelineConfig",
        "PipelineResult",
        "BuildMode",
        "PipelinePhase",
        "convert_python_to_c",
        "convert_and_build",
    # Package info
    "__version__",
]
