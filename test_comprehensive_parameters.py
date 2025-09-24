#!/usr/bin/env python3
"""Comprehensive test for parameter modification functionality."""

def gcd_with_param_modification(a: int, b: int) -> int:
    """Test: Euclidean GCD algorithm with parameter modification"""
    while b != 0:
        temp: int = b
        b = a % b
        a = temp
    return a

def factorial_with_param_modification(n: int) -> int:
    """Test: Factorial using parameter modification"""
    result: int = 1
    while n > 1:
        result = result * n
        n = n - 1  # Modify parameter
    return result

def string_param_modification(text: str, prefix: str) -> str:
    """Test: String parameter modification"""
    text = prefix + text  # Modify string parameter
    return text

def multiple_param_modification(x: int, y: int, z: int) -> int:
    """Test: Multiple parameter modifications"""
    x = x * 2      # Modify first parameter
    y = y + 10     # Modify second parameter
    z = z - 5      # Modify third parameter
    return x + y + z

def main() -> int:
    """Main test function"""
    # Test GCD
    gcd_result: int = gcd_with_param_modification(48, 18)

    # Test factorial
    fact_result: int = factorial_with_param_modification(5)

    # Test multiple param modification
    multi_result: int = multiple_param_modification(5, 15, 20)

    return gcd_result + fact_result + multi_result