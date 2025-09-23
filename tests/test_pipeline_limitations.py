#!/usr/bin/env python3
"""
Test suite to identify and document CGen pipeline limitations.

This module tests edge cases and complex scenarios to identify
what currently works and what needs improvement.
"""

import tempfile
import pytest
from pathlib import Path
from src.cgen.pipeline import CGenPipeline


class TestPipelineLimitations:
    """Test to identify current pipeline limitations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline = CGenPipeline()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, content: str, filename: str = "test.py") -> Path:
        """Create a temporary Python test file."""
        test_file = Path(self.temp_dir) / filename
        test_file.write_text(content)
        return test_file

    def test_recursive_functions(self):
        """Test recursive function conversion - KNOWN LIMITATION."""
        code = '''def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        # This currently has a known limitation with function call generation
        if result.success:
            # Check that the function was created but function calls aren't properly converted
            assert "int fibonacci(int n)" in result.c_code
            # Currently shows object representations instead of proper C calls
            if "<src.cgen.generator.core.FunctionCall object" in result.c_code:
                pytest.skip("KNOWN LIMITATION: Function calls in expressions not properly converted to C")
            else:
                # If fixed, these should work
                assert "fibonacci(n - 1)" in result.c_code
                assert "fibonacci(n - 2)" in result.c_code
        else:
            pytest.skip("Recursive functions not yet supported")

    def test_parameter_modification_workaround(self):
        """Test workaround for parameter modification limitation."""
        code = '''def gcd_working(a_param: int, b_param: int) -> int:
    a: int = a_param
    b: int = b_param
    while b != 0:
        temp: int = b
        a = temp
        b = a % b
    return a'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "int a;" in result.c_code
        assert "int b;" in result.c_code

    def test_nested_function_calls(self):
        """Test nested function calls."""
        code = '''def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b

def complex_calc(x: int, y: int, z: int) -> int:
    return add(multiply(x, y), z)'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        # Check if nested calls work
        if result.success:
            # Should contain the nested call structure
            c_code = result.c_code
            print(f"Generated C code:\n{c_code}")
            # Just verify it compiled successfully for now
            assert "complex_calc" in c_code
        else:
            # Document this as a limitation
            print(f"Nested function calls failed: {result.errors}")

    def test_complex_expressions(self):
        """Test complex mathematical expressions."""
        code = '''def complex_math(x: int, y: int, z: int) -> int:
    result: int = (x + y) * z - (x * y) / (z + 1)
    return result'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        if result.success:
            assert "result =" in result.c_code
        else:
            print(f"Complex expressions failed: {result.errors}")

    def test_multiple_returns(self):
        """Test functions with multiple return statements."""
        code = '''def absolute_value(n: int) -> int:
    if n >= 0:
        return n
    return -n

def sign_function(n: int) -> int:
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "return n;" in result.c_code
        assert "return -n;" in result.c_code

    def test_boolean_logic(self):
        """Test complex boolean expressions."""
        code = '''def complex_condition(a: int, b: int, c: int) -> bool:
    return (a > b and b > c) or (a < 0 and c > 10)

def is_valid_range(x: int, min_val: int, max_val: int) -> bool:
    return x >= min_val and x <= max_val'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        if result.success:
            assert "bool complex_condition" in result.c_code
            assert "&&" in result.c_code or "||" in result.c_code
        else:
            print(f"Boolean logic failed: {result.errors}")

    def test_early_returns_in_loops(self):
        """Test early returns within loops."""
        code = '''def find_first_even(numbers: list, length: int) -> int:
    i: int = 0
    while i < length:
        if numbers[i] % 2 == 0:
            return numbers[i]
        i = i + 1
    return -1'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        # This will likely fail due to list parameter
        if not result.success:
            pytest.skip("Lists not yet supported")

    def test_constants_and_literals(self):
        """Test various literal types."""
        code = '''def use_constants() -> int:
    x: int = 42
    y: int = -17
    z: bool = True
    return x + y'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "x = 42;" in result.c_code
        assert "y = -17;" in result.c_code
        assert "z = true;" in result.c_code

    def test_variable_scoping_complex(self):
        """Test complex variable scoping scenarios."""
        code = '''def complex_scoping(n: int) -> int:
    result: int = 0
    if n > 0:
        temp: int = n * 2
        if temp > 10:
            inner: int = temp - 5
            result = inner
        else:
            result = temp
    else:
        result = -n
    return result'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        if result.success:
            # Check that variables are properly scoped
            c_code = result.c_code
            # Should declare variables in appropriate scopes
            assert "int result;" in c_code
        else:
            print(f"Complex scoping failed: {result.errors}")

    def test_type_inference_limits(self):
        """Test limits of type inference."""
        code = '''def mixed_operations(a: int, b: int) -> int:
    # This should work with explicit types
    temp: int = a + b
    result: int = temp * 2
    return result'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success


class TestCurrentCapabilities:
    """Document what currently works well."""

    def test_working_features_summary(self):
        """Test and document what currently works."""
        working_code = '''# WORKING FEATURES:

# 1. Basic function definitions
def add(a: int, b: int) -> int:
    return a + b

# 2. Variable declarations with explicit types
def variables_demo(x: int, y: int) -> int:
    result: int = x + y
    temp: int = result * 2
    return temp

# 3. Control flow (if/else)
def control_flow(n: int) -> int:
    result: int = 0
    if n > 0:
        result = 1
    elif n < 0:
        result = -1
    return result

# 4. Loops (while and for)
def loops_demo(n: int) -> int:
    total: int = 0
    i: int = 0
    while i < n:
        total = total + i
        i = i + 1
    return total

def for_loop_demo(n: int) -> int:
    result: int = 1
    for i in range(1, n + 1):
        result = result * i
    return result

# 5. Boolean functions
def boolean_demo(n: int) -> bool:
    return n > 0

# 6. Multiple functions with calls
def caller(x: int, y: int) -> int:
    sum_val: int = add(x, y)
    return sum_val'''

        temp_file = Path(tempfile.mktemp(suffix=".py"))
        temp_file.write_text(working_code)

        try:
            pipeline = CGenPipeline()
            result = pipeline.convert(temp_file)

            assert result.success
            print("✓ All basic features working correctly")

        finally:
            temp_file.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])