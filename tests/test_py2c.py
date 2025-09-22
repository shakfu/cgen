"""Tests for Python to C converter."""


# Add the src directory to the path
import pytest

from cgen.core.py2c import PythonToCConverter, TypeMappingError, convert_python_to_c


class TestPythonToCConverter:
    """Test Python to C converter functionality."""

    def setup_method(self):
        self.converter = PythonToCConverter()

    def test_simple_function_conversion(self):
        """Test conversion of a simple function."""
        python_code = """
def add(x: int, y: int) -> int:
    return x + y
"""
        c_code = convert_python_to_c(python_code)
        assert "#include <stdio.h>" in c_code
        assert "#include <stdbool.h>" in c_code
        assert "int add(int x, int y)" in c_code
        assert "return x + y;" in c_code

    def test_function_with_variable_declaration(self):
        """Test function with local variable."""
        python_code = """
def multiply(x: int, y: int) -> int:
    result: int = x * y
    return result
"""
        c_code = convert_python_to_c(python_code)
        assert "int result;" in c_code
        assert "result = x * y;" in c_code
        assert "return result;" in c_code

    def test_type_mappings(self):
        """Test various type mappings."""
        python_code = """
def test_types(a: int, b: float, c: bool) -> None:
    pass
"""
        c_code = convert_python_to_c(python_code)
        assert "void test_types(int a, double b, bool c)" in c_code

    def test_string_type_mapping(self):
        """Test string type mapping."""
        python_code = """
def greet(name: str) -> str:
    greeting: str = "Hello"
    return greeting
"""
        c_code = convert_python_to_c(python_code)
        assert "char* greet(char* name)" in c_code
        assert "char* greeting;" in c_code
        assert 'greeting = "Hello";' in c_code

    def test_multiple_operations(self):
        """Test function with multiple arithmetic operations."""
        python_code = """
def calculate(a: int, b: int, c: int) -> int:
    sum_val: int = a + b
    product: int = sum_val * c
    return product
"""
        c_code = convert_python_to_c(python_code)
        assert "sum_val = a + b;" in c_code
        assert "product = sum_val * c;" in c_code

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
        assert "result = helper();" in c_code

    def test_missing_type_annotation_error(self):
        """Test error when type annotation is missing."""
        python_code = """
def bad_function(x):
    return x
"""
        with pytest.raises(TypeMappingError):
            convert_python_to_c(python_code)

    def test_unsupported_type_error(self):
        """Test error for unsupported types."""
        python_code = """
def bad_function(x: dict) -> None:
    pass
"""
        with pytest.raises(TypeMappingError):
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
        assert "x = 42;" in c_code
        assert "y = 3.14;" in c_code
        assert "z = true;" in c_code
        assert "w = false;" in c_code

    def test_variable_assignment_without_declaration(self):
        """Test error when assigning to undeclared variable."""
        python_code = """
def bad_function() -> int:
    x = 5  # No type annotation
    return x
"""
        with pytest.raises(TypeMappingError):
            convert_python_to_c(python_code)

    def test_void_function(self):
        """Test function with no return type."""
        python_code = """
def print_number(x: int) -> None:
    pass
"""
        c_code = convert_python_to_c(python_code)
        assert "void print_number(int x)" in c_code

    def test_function_with_no_return_annotation(self):
        """Test function without return type annotation defaults to void."""
        python_code = """
def no_return_type(x: int):
    pass
"""
        c_code = convert_python_to_c(python_code)
        assert "void no_return_type(int x)" in c_code

    def test_list_type_to_pointer(self):
        """Test list type conversion to pointer."""
        python_code = """
def process_array(arr: list[int], size: int) -> int:
    return size
"""
        c_code = convert_python_to_c(python_code)
        assert "int process_array(int* arr, int size)" in c_code

    def test_docstring_ignored(self):
        """Test that docstrings are ignored."""
        python_code = '''
def documented_function(x: int) -> int:
    """This is a docstring."""
    return x
'''
        c_code = convert_python_to_c(python_code)
        assert "This is a docstring" not in c_code
        assert "return x;" in c_code


# This file has been converted to pytest style
