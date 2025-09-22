"""CGen Builder Module - Build System Generation and Direct Compilation.

This module provides build system generation and direct compilation capabilities
for CGen-generated C code, with integrated STC (Smart Template Containers) support.
"""

from .makefilegen import Builder, MakefileGenerator, CGenMakefileGenerator

__all__ = [
    "Builder",
    "MakefileGenerator",
    "CGenMakefileGenerator",
]