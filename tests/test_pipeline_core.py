#!/usr/bin/env python3
"""
Test suite for CGen pipeline core functionality.

This module tests the Python-to-C conversion pipeline with increasing
levels of complexity to validate the core functionality.
"""

import os
import tempfile
import pytest
from pathlib import Path
from src.cgen.pipeline import CGenPipeline, PipelineConfig


class TestPipelineCore:
    """Test the core functionality of the CGen pipeline."""

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

    def test_basic_function(self):
        """Test basic function conversion."""
        code = '''def add(a: int, b: int) -> int:
    return a + b'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert result.c_code is not None
        assert "int add(int a, int b)" in result.c_code
        assert "return a + b;" in result.c_code

    def test_variables_and_expressions(self):
        """Test variable declarations and expressions."""
        code = '''def calculate(x: int, y: int) -> int:
    result: int = x * 2
    temp: int = y + 5
    return result + temp'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "int result;" in result.c_code
        assert "int temp;" in result.c_code
        assert "result = x * 2;" in result.c_code

    def test_conditionals(self):
        """Test if-else statements."""
        code = '''def max_value(a: int, b: int) -> int:
    if a > b:
        return a
    else:
        return b'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "if (a > b)" in result.c_code
        assert "else" in result.c_code

    def test_proper_scoping(self):
        """Test proper variable scoping."""
        code = '''def classify_number(n: int) -> int:
    result: int = 0
    if n > 0:
        result = 1
    elif n < 0:
        result = -1
    return result'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "int result;" in result.c_code
        assert "result = 0;" in result.c_code

    def test_while_loops(self):
        """Test while loop conversion."""
        code = '''def sum_range(n: int) -> int:
    total: int = 0
    i: int = 0
    while i < n:
        total = total + i
        i = i + 1
    return total'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "while (i < n)" in result.c_code
        assert "total = total + i;" in result.c_code

    def test_for_loops(self):
        """Test for loop conversion."""
        code = '''def factorial(n: int) -> int:
    result: int = 1
    for i in range(1, n + 1):
        result = result * i
    return result'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "for (int i = 1; i < n + 1; i++)" in result.c_code

    def test_boolean_functions(self):
        """Test boolean return types."""
        code = '''def is_positive(n: int) -> bool:
    if n > 0:
        return True
    else:
        return False'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "bool is_positive(int n)" in result.c_code
        assert "return true;" in result.c_code
        assert "return false;" in result.c_code

    def test_multiple_functions(self):
        """Test multiple function definitions."""
        code = '''def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b

def compute(x: int, y: int) -> int:
    sum_val: int = add(x, y)
    prod_val: int = multiply(x, y)
    return sum_val + prod_val'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        assert result.success
        assert "int add(int a, int b)" in result.c_code
        assert "int multiply(int a, int b)" in result.c_code
        assert "int compute(int x, int y)" in result.c_code

    def test_constraint_checking(self):
        """Test that constraint checker catches issues."""
        code = '''def divide(a: int, b: int) -> int:
    return a / b'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        # Should succeed but have warnings about division
        assert result.success
        assert len(result.warnings) > 0
        assert any("division" in warning.lower() for warning in result.warnings)

    def test_parameter_modification_allowed(self):
        """Test that parameter modification is now allowed."""
        code = '''def modify_function(n: int) -> int:
    n = n + 1  # This should now work
    return n'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        # Should succeed because parameter modification is now supported
        assert result.success
        assert "n = n + 1;" in result.c_code

    def test_missing_type_annotations(self):
        """Test handling of missing type annotations."""
        code = '''def no_types(a, b):
    return a + b'''

        test_file = self.create_test_file(code)
        result = self.pipeline.convert(test_file)

        # Should fail due to missing type annotations
        assert not result.success


class TestPipelineConfiguration:
    """Test pipeline configuration options."""

    def test_different_optimization_levels(self):
        """Test different optimization levels."""
        from src.cgen.frontend import OptimizationLevel

        code = '''def simple_add(a: int, b: int) -> int:
    return a + b'''

        temp_file = Path(tempfile.mktemp(suffix=".py"))
        temp_file.write_text(code)

        try:
            # Test different optimization levels
            for opt_level in [OptimizationLevel.NONE, OptimizationLevel.BASIC,
                            OptimizationLevel.MODERATE, OptimizationLevel.AGGRESSIVE]:
                config = PipelineConfig(optimization_level=opt_level)
                pipeline = CGenPipeline(config)
                result = pipeline.convert(temp_file)

                assert result.success, f"Failed with optimization level {opt_level}"

        finally:
            temp_file.unlink(missing_ok=True)

    def test_pipeline_phases(self):
        """Test that all pipeline phases are executed."""
        from src.cgen.pipeline import PipelinePhase

        code = '''def test_func(x: int) -> int:
    return x * 2'''

        temp_file = Path(tempfile.mktemp(suffix=".py"))
        temp_file.write_text(code)

        try:
            pipeline = CGenPipeline()
            result = pipeline.convert(temp_file)

            assert result.success

            # Check that key phases were executed
            assert PipelinePhase.VALIDATION in result.phase_results
            assert PipelinePhase.ANALYSIS in result.phase_results
            assert PipelinePhase.GENERATION in result.phase_results

        finally:
            temp_file.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])