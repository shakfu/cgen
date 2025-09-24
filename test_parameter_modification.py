#!/usr/bin/env python3
"""Test parameter modification functionality."""

def modify_param(n: int) -> int:
    """Test: Should be able to modify parameters"""
    n = n + 1  # This should work in C
    return n

def main() -> int:
    result: int = modify_param(5)
    return result