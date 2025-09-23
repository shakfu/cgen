#!/usr/bin/env python3
"""CGen CLI Entry Point.

This allows running cgen as a module with:
    python -m cgen <command> [args]

Commands:
    convert   - Convert Python to C code
    build     - Convert and generate Makefile
    compile   - Convert and compile executable
    clean     - Clean build directory
"""

import sys
from .cli.simple_cli import main

if __name__ == "__main__":
    sys.exit(main())