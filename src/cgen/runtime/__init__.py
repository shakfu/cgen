"""
CGen Runtime Library

This module provides C runtime support for generated Python-to-C code.
It complements STC (Smart Template Containers) rather than replacing it,
focusing on Python-specific semantics and operations.

Components:
- error_handling: Error handling and reporting system with Python-like exceptions
- file_ops: File I/O wrapper functions with Python semantics
- stc_bridge: Bridge between Python semantics and STC containers
- python_ops: Python-specific operations (bool, range, slice, etc.)
- memory_ops: Memory management utilities complementing STC allocators

Design Philosophy:
- Leverage STC for high-performance container operations
- Provide Python-specific semantics where STC doesn't naturally fit
- Focus on error handling and bounds checking for safety
- Enable seamless Python-to-C translation with familiar behavior
"""

__version__ = "1.0.0"
__all__ = [
    "get_runtime_headers",
    "get_runtime_sources",
    "get_include_path",
    "RuntimeConfig"
]

import os
from pathlib import Path
from typing import List, Dict, Any

class RuntimeConfig:
    """Configuration for CGen runtime library integration."""

    def __init__(self):
        self.runtime_dir = Path(__file__).parent

        # Core components (always included)
        self.include_error_handling = True
        self.include_python_ops = True

        # Optional components
        self.include_file_ops = True
        self.include_stc_bridge = True
        self.include_memory_ops = True

        # STC integration settings
        self.stc_enabled = True
        self.stc_include_path = None

        # Legacy components (for fallback when STC not available)
        self.include_string_ops = False  # Use STC cstr instead

    def get_headers(self) -> List[str]:
        """Get list of runtime header files to include."""
        headers = []

        # Core headers (always included)
        if self.include_error_handling:
            headers.append("cgen_error_handling.h")
        if self.include_python_ops:
            headers.append("cgen_python_ops.h")

        # Optional headers
        if self.include_file_ops:
            headers.append("cgen_file_ops.h")
        if self.include_stc_bridge and self.stc_enabled:
            headers.append("cgen_stc_bridge.h")
        if self.include_memory_ops:
            headers.append("cgen_memory_ops.h")

        # Legacy fallback
        if self.include_string_ops and not self.stc_enabled:
            headers.append("cgen_string_ops.h")

        return headers

    def get_sources(self) -> List[str]:
        """Get list of runtime source files to compile."""
        sources = []

        # Core sources
        if self.include_error_handling:
            sources.append(str(self.runtime_dir / "cgen_error_handling.c"))
        if self.include_python_ops:
            sources.append(str(self.runtime_dir / "cgen_python_ops.c"))

        # Optional sources
        if self.include_file_ops:
            sources.append(str(self.runtime_dir / "cgen_file_ops.c"))
        if self.include_stc_bridge and self.stc_enabled:
            sources.append(str(self.runtime_dir / "cgen_stc_bridge.c"))
        if self.include_memory_ops:
            sources.append(str(self.runtime_dir / "cgen_memory_ops.c"))

        # Legacy fallback
        if self.include_string_ops and not self.stc_enabled:
            sources.append(str(self.runtime_dir / "cgen_string_ops.c"))

        return sources

    def get_compile_flags(self) -> List[str]:
        """Get compiler flags needed for runtime library."""
        flags = []

        if self.stc_enabled:
            flags.append("-DSTC_ENABLED")
            if self.stc_include_path:
                flags.append(f"-I{self.stc_include_path}")

        return flags

def get_runtime_headers() -> List[str]:
    """Get list of all runtime header files."""
    config = RuntimeConfig()
    return config.get_headers()

def get_runtime_sources() -> List[str]:
    """Get list of all runtime source files."""
    config = RuntimeConfig()
    return config.get_sources()

def get_include_path() -> str:
    """Get the include path for runtime headers."""
    return str(Path(__file__).parent)