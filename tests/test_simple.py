#!/usr/bin/env python3
"""Simple test file for CGen CLI."""

def add_numbers(x: int, y: int) -> int:
    """Add two integers."""
    return x + y

def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    result: int = a * b
    return result