#!/usr/bin/env python3
"""
CGen package main entry point.

This allows running cgen as a module with:
    python -m cgen <command> [args]
"""

import sys
from .cli.main import main

if __name__ == "__main__":
    sys.exit(main())