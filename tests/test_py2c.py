"""Tests for Python to C converter."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cgen.core.py2c import PythonToCConverter, convert_python_to_c, UnsupportedFeatureError, TypeMappingError


class TestPythonToCConverter(unittest.TestCase):
    """Test Python to C converter functionality."""

    def setUp(self):
        self.converter = PythonToCConverter()

    def test_simple_function_conversion(self):
        """Test conversion of a simple function."""
        python_code = """
def add(x: int, y: int) -> int:
    return x + y
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("#include <stdio.h>", c_code)
        self.assertIn("#include <stdbool.h>", c_code)
        self.assertIn("int add(int x, int y)", c_code)
        self.assertIn("return x + y;", c_code)

    def test_function_with_variable_declaration(self):
        """Test function with local variable."""
        python_code = """
def multiply(x: int, y: int) -> int:
    result: int = x * y
    return result
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("int result;", c_code)
        self.assertIn("result = x * y;", c_code)
        self.assertIn("return result;", c_code)

    def test_type_mappings(self):
        """Test various type mappings."""
        python_code = """
def test_types(a: int, b: float, c: bool) -> None:
    pass
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("void test_types(int a, double b, bool c)", c_code)

    def test_string_type_mapping(self):
        """Test string type mapping."""
        python_code = """
def greet(name: str) -> str:
    greeting: str = "Hello"
    return greeting
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("char* greet(char* name)", c_code)
        self.assertIn("char* greeting;", c_code)
        self.assertIn('greeting = "Hello";', c_code)

    def test_multiple_operations(self):
        """Test function with multiple arithmetic operations."""
        python_code = """
def calculate(a: int, b: int, c: int) -> int:
    sum_val: int = a + b
    product: int = sum_val * c
    return product
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("sum_val = a + b;", c_code)
        self.assertIn("product = sum_val * c;", c_code)

    def test_function_call_conversion(self):
        """Test function call conversion."""
        python_code = """
def helper() -> int:
    return 42

def main() -> int:
    result: int = helper()
    return result
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("result = helper();", c_code)

    def test_missing_type_annotation_error(self):
        """Test error when type annotation is missing."""
        python_code = """
def bad_function(x):
    return x
"""
        with self.assertRaises(TypeMappingError):
            convert_python_to_c(python_code)

    def test_unsupported_type_error(self):
        """Test error for unsupported types."""
        python_code = """
def bad_function(x: dict) -> None:
    pass
"""
        with self.assertRaises(TypeMappingError):
            convert_python_to_c(python_code)

    def test_constants_conversion(self):
        """Test conversion of various constants."""
        python_code = """
def test_constants() -> None:
    x: int = 42
    y: float = 3.14
    z: bool = True
    w: bool = False
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("x = 42;", c_code)
        self.assertIn("y = 3.14;", c_code)
        self.assertIn("z = true;", c_code)
        self.assertIn("w = false;", c_code)

    def test_variable_assignment_without_declaration(self):
        """Test error when assigning to undeclared variable."""
        python_code = """
def bad_function() -> int:
    x = 5  # No type annotation
    return x
"""
        with self.assertRaises(TypeMappingError):
            convert_python_to_c(python_code)

    def test_void_function(self):
        """Test function with no return type."""
        python_code = """
def print_number(x: int) -> None:
    pass
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("void print_number(int x)", c_code)

    def test_function_with_no_return_annotation(self):
        """Test function without return type annotation defaults to void."""
        python_code = """
def no_return_type(x: int):
    pass
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("void no_return_type(int x)", c_code)

    def test_list_type_to_pointer(self):
        """Test list type conversion to pointer."""
        python_code = """
def process_array(arr: list[int], size: int) -> int:
    return size
"""
        c_code = convert_python_to_c(python_code)
        self.assertIn("int process_array(int* arr, int size)", c_code)

    def test_docstring_ignored(self):
        """Test that docstrings are ignored."""
        python_code = '''
def documented_function(x: int) -> int:
    """This is a docstring."""
    return x
'''
        c_code = convert_python_to_c(python_code)
        self.assertNotIn("This is a docstring", c_code)
        self.assertIn("return x;", c_code)


if __name__ == '__main__':
    unittest.main()