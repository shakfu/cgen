#!/usr/bin/env python3
"""CGen CLI Entry Point.

This allows running cgen as a module with:
    python -m cgen <command> [args]

Commands:
    convert   - Convert Python to C code
    build     - Convert and build (compile directly or generate Makefile with -m)
    clean     - Clean build directory
"""

import sys

from .cli.main import main

if __name__ == "__main__":
    sys.exit(main())
