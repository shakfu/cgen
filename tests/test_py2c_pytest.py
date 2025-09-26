"""Pytest-style tests for Python to C converter."""

import pytest

from cgen.generator.py2c import TypeMappingError, convert_python_to_c


@pytest.mark.py2c
@pytest.mark.unit
class TestPythonToCConverter:
    """Test Python to C converter functionality using pytest."""

    def test_simple_function_conversion(self, py2c_converter, sample_python_code):
        """Test conversion of a simple function."""
        python_code = sample_python_code["simple_function"]
        c_sequence = py2c_converter.convert_code(python_code)

        # Check that we get a sequence with the function
        assert c_sequence is not None

        # Test the convenience function
        c_code = convert_python_to_c(python_code)
        assert "int add(int x, int y)" in c_code
        assert "return x + y;" in c_code

    def test_void_function(self, py2c_converter, sample_python_code):
        """Test function with no return type."""
        python_code = sample_python_code["void_function"]
        c_code = convert_python_to_c(python_code)

        assert "void print_hello(void)" in c_code

    def test_function_with_variable_declaration(self, py2c_converter, sample_python_code):
        """Test function with local variable."""
        python_code = sample_python_code["with_variables"]
        c_code = convert_python_to_c(python_code)

        assert "double calculate(int x, double y)" in c_code
        assert "double result;" in c_code
        assert "result = x * y;" in c_code

    def test_multiple_operations(self, py2c_converter, sample_python_code):
        """Test function with multiple arithmetic operations."""
        python_code = sample_python_code["multiple_operations"]
        c_code = convert_python_to_c(python_code)

        assert "int complex_calc(int a, int b, int c)" in c_code
        assert "return a + b * c - 10;" in c_code

    @pytest.mark.parametrize("python_type,c_type", [
        ("int", "int"),
        ("float", "double"),
        ("bool", "bool"),
        ("str", "char*"),
    ])
    def test_type_mappings(self, py2c_converter, python_type, c_type):
        """Test various type mappings."""
        python_code = f"def test_func(x: {python_type}) -> {python_type}:\n    return x"
        c_code = convert_python_to_c(python_code)

        expected_signature = f"{c_type} test_func({c_type} x)"
        assert expected_signature in c_code

    def test_string_type_mapping(self, py2c_converter):
        """Test string type mapping."""
        python_code = """
def greet(name: str) -> str:
    return name
"""
        c_code = convert_python_to_c(python_code)
        assert "char* greet(char* name)" in c_code

    def test_list_type_to_stc_container(self, py2c_converter):
        """Test list type conversion to STC container."""
        python_code = """
def process_array(data: list[int]) -> int:
    return 0
"""
        c_code = convert_python_to_c(python_code)
        assert "int process_array(vec_int32 data)" in c_code
        assert "declare_vec(vec_int32, int32_t);" in c_code
        assert '#include "stc/vec.h"' in c_code

    def test_function_call_conversion(self, py2c_converter):
        """Test function call conversion."""
        python_code = """
def main() -> int:
    result: int = add(5, 3)
    return result
"""
        c_code = convert_python_to_c(python_code)
        assert "result = add(5, 3);" in c_code

    def test_constants_conversion(self, py2c_converter):
        """Test conversion of various constants."""
        python_code = """
def test_constants() -> int:
    a: int = 42
    b: float = 3.14
    c: bool = True
    d: bool = False
    return a
"""
        c_code = convert_python_to_c(python_code)
        assert "a = 42;" in c_code
        assert "b = 3.14;" in c_code  # Note: will be double, but value should be there
        assert "c = true;" in c_code
        assert "d = false;" in c_code

    def test_function_with_no_return_annotation(self, py2c_converter):
        """Test function without return type annotation defaults to void."""
        python_code = """
def no_return():
    pass
"""
        c_code = convert_python_to_c(python_code)
        assert "void no_return(void)" in c_code

    def test_docstring_ignored(self, py2c_converter):
        """Test that docstrings are ignored."""
        python_code = '''
def documented_function(x: int) -> int:
    """This is a docstring."""
    return x * 2
'''
        c_code = convert_python_to_c(python_code)
        assert "This is a docstring" not in c_code
        assert "int documented_function(int x)" in c_code
        assert "return x * 2;" in c_code

    # Error handling tests
    def test_missing_type_annotation_error(self, py2c_converter):
        """Test error when type annotation is missing."""
        python_code = """
def bad_function(x):
    return x
"""
        with pytest.raises(TypeMappingError, match="Parameter 'x' must have type annotation"):
            convert_python_to_c(python_code)

    def test_unsupported_type_error(self, py2c_converter):
        """Test error for unsupported types."""
        python_code = """
def bad_function(x: dict) -> dict:
    return x
"""
        with pytest.raises(TypeMappingError, match="Unsupported type"):
            convert_python_to_c(python_code)

    def test_variable_assignment_without_declaration(self, py2c_converter):
        """Test that local variables can now be inferred (updated for new type system)."""
        python_code = """
def good_function() -> int:
    x = 5  # Local variables can now be inferred
    return x
"""
        # This should now succeed with the new type inference system
        c_code = convert_python_to_c(python_code)
        assert "int good_function(void)" in c_code
        assert "x = 5;" in c_code

    def test_parameter_without_annotation_error(self, py2c_converter):
        """Test error when parameter lacks type annotation (still required)."""
        python_code = """
def bad_function(x) -> int:  # Parameter 'x' missing annotation
    return x
"""
        with pytest.raises(TypeMappingError, match="Parameter 'x' must have type annotation"):
            convert_python_to_c(python_code)


@pytest.mark.py2c
@pytest.mark.integration
class TestFileOperations:
    """Test file-based operations."""

    def test_convert_python_file_to_c(self, temp_python_file, temp_c_file, sample_python_code):
        """Test file-to-file conversion."""
        from cgen.generator.py2c import convert_python_file_to_c

        # Create temporary files
        python_file = temp_python_file(sample_python_code["simple_function"])
        c_file = temp_c_file()

        # Convert
        convert_python_file_to_c(python_file, c_file)

        # Verify output file exists and contains expected content
        with open(c_file) as f:
            content = f.read()
            assert "int add(int x, int y)" in content


@pytest.mark.py2c
@pytest.mark.benchmark
class TestPerformance:
    """Performance tests for Python-to-C conversion."""

    def test_conversion_performance(self, py2c_converter, performance_timer, sample_python_code):
        """Test conversion performance for simple functions."""
        python_code = sample_python_code["simple_function"]

        with performance_timer() as timer:
            for _ in range(100):  # Convert 100 times
                convert_python_to_c(python_code)

        # Should complete 100 conversions in under 1 second
        assert timer.elapsed < 1.0, f"Conversion took {timer.elapsed:.3f}s for 100 iterations"

    @pytest.mark.slow
    def test_large_function_conversion(self, py2c_converter, performance_timer):
        """Test conversion of larger functions."""
        # Generate a larger function
        lines = ["def large_function(x: int) -> int:"]
        for i in range(100):
            lines.append(f"    temp_{i}: int = x + {i}")
        lines.append("    return temp_99")

        python_code = "\n".join(lines)

        with performance_timer() as timer:
            c_code = convert_python_to_c(python_code)

        # Should still be reasonably fast
        assert timer.elapsed < 0.1, f"Large function conversion took {timer.elapsed:.3f}s"
        assert "int large_function(int x)" in c_code
        assert "return temp_99;" in c_code
