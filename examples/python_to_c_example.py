#!/usr/bin/env python3
"""Example usage of Python to C converter.

This script demonstrates how to use the cfile Python-to-C converter
to convert type-annotated Python functions to C code.
"""

import sys
import os

# Add the src directory to the path for this example
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cfile import convert_python_to_c, convert_python_file_to_c

# Example 1: Simple arithmetic function
print("=== Example 1: Simple arithmetic function ===")
python_code1 = """
def add_numbers(x: int, y: int) -> int:
    \"\"\"Add two integers and return the result.\"\"\"
    result: int = x + y
    return result
"""

print("Python code:")
print(python_code1)
print("\nConverted C code:")
print(convert_python_to_c(python_code1))

# Example 2: More complex function with multiple variables
print("\n=== Example 2: Function with multiple operations ===")
python_code2 = """
def calculate_area_and_perimeter(length: int, width: int) -> int:
    area: int = length * width
    perimeter: int = 2 * (length + width)
    total: int = area + perimeter
    return total
"""

print("Python code:")
print(python_code2)
print("\nConverted C code:")
print(convert_python_to_c(python_code2))

# Example 3: Function with different data types
print("\n=== Example 3: Function with different data types ===")
python_code3 = """
def process_values(count: int, rate: float, active: bool) -> float:
    base_value: float = count * rate
    if active:
        return base_value * 2.0
    else:
        return base_value
"""

print("Python code:")
print(python_code3)
print("\nConverted C code (note: if statements not yet supported):")
try:
    print(convert_python_to_c(python_code3))
except Exception as e:
    print(f"Error: {e}")

# Example 4: Working with arrays (list types)
print("\n=== Example 4: Working with arrays ===")
python_code4 = """
def sum_array(numbers: list[int], size: int) -> int:
    total: int = 0
    # Note: for loops not yet supported, but this shows the function signature
    return total
"""

print("Python code:")
print(python_code4)
print("\nConverted C code:")
print(convert_python_to_c(python_code4))

# Example 5: Multiple functions in one module
print("\n=== Example 5: Multiple functions ===")
python_code5 = """
def helper_function(x: int) -> int:
    return x * 2

def main_function(a: int, b: int) -> int:
    doubled_a: int = helper_function(a)
    result: int = doubled_a + b
    return result
"""

print("Python code:")
print(python_code5)
print("\nConverted C code:")
print(convert_python_to_c(python_code5))

# Example 6: File conversion
print("\n=== Example 6: File conversion ===")

# Create a sample Python file
sample_file_content = """
def factorial(n: int) -> int:
    \"\"\"Calculate factorial using recursion.\"\"\"
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    \"\"\"Calculate nth Fibonacci number.\"\"\"
    if n <= 1:
        return n

    a: int = 0
    b: int = 1
    i: int = 2

    while i <= n:
        temp: int = a + b
        a = b
        b = temp
        i = i + 1

    return b
"""

input_file = "sample_input.py"
output_file = "sample_output.c"

with open(input_file, 'w') as f:
    f.write(sample_file_content)

print(f"Created sample input file: {input_file}")
print(f"Converting to C and saving as: {output_file}")

try:
    convert_python_file_to_c(input_file, output_file)
    print("Conversion successful!")

    print("\nGenerated C code:")
    with open(output_file, 'r') as f:
        print(f.read())

except Exception as e:
    print(f"Error during conversion: {e}")

# Cleanup
try:
    os.remove(input_file)
    os.remove(output_file)
    print("Cleaned up temporary files.")
except:
    pass

print("\n=== Summary ===")
print("The Python-to-C converter supports:")
print("✓ Type-annotated function definitions")
print("✓ Basic data types: int, float, bool, str")
print("✓ List types converted to pointers")
print("✓ Variable declarations with type annotations")
print("✓ Basic arithmetic operations (+, -, *, /, %)")
print("✓ Function calls")
print("✓ Return statements")
print("✓ Docstring filtering")
print("✓ Pass statements")
print()
print("Limitations (not yet implemented):")
print("✗ Control structures (if, while, for loops)")
print("✗ Complex expressions")
print("✗ Python-specific features")
print("✗ Standard library functions")
print("✗ Dynamic typing")
print("✗ Classes and objects")