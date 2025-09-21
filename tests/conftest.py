"""Pytest configuration and fixtures for cgen tests."""

import sys
import os
from pathlib import Path
import pytest

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import common modules for test fixtures
import cgen.core as cgen_core
from cgen.core.py2c import PythonToCConverter
from cgen.core.style import StyleOptions


@pytest.fixture
def cgen_factory():
    """Provide a CFactory instance for tests."""
    return cgen_core.CFactory()


@pytest.fixture
def cgen_writer():
    """Provide a Writer instance with default style for tests."""
    return cgen_core.Writer(StyleOptions())


@pytest.fixture
def py2c_converter():
    """Provide a PythonToCConverter instance for tests."""
    return PythonToCConverter()


@pytest.fixture
def allman_style():
    """Provide Allman brace style configuration."""
    style = StyleOptions()
    style.break_before_braces = cgen_core.BreakBeforeBraces.ALLMAN
    return style


@pytest.fixture
def kr_style():
    """Provide K&R brace style configuration."""
    style = StyleOptions()
    style.break_before_braces = cgen_core.BreakBeforeBraces.ATTACH
    return style


@pytest.fixture
def sample_python_code():
    """Provide sample Python code for testing."""
    return {
        'simple_function': '''
def add(x: int, y: int) -> int:
    return x + y
''',
        'void_function': '''
def print_hello():
    pass
''',
        'with_variables': '''
def calculate(x: int, y: float) -> float:
    result: float = x * y
    return result
''',
        'multiple_operations': '''
def complex_calc(a: int, b: int, c: int) -> int:
    return a + b * c - 10
'''
    }


@pytest.fixture
def expected_c_code():
    """Provide expected C code outputs for testing."""
    return {
        'simple_function': '''#include <stdio.h>
#include <stdbool.h>

int add(int x, int y)
{
    return x + y;
}
''',
        'void_function': '''#include <stdio.h>
#include <stdbool.h>

void print_hello()
{
}
'''
    }


# Test markers for categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "py2c: marks tests for Python-to-C conversion"
    )
    config.addinivalue_line(
        "markers", "core: marks tests for core C generation functionality"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "intelligence: marks tests for intelligence layer"
    )
    config.addinivalue_line(
        "markers", "frontend: marks tests for frontend layer"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks tests that include benchmarking"
    )


# Performance testing utilities
class PerformanceTimer:
    """Simple performance timer for benchmarking tests."""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        import time
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        import time
        self.end_time = time.perf_counter()

    @property
    def elapsed(self):
        """Return elapsed time in seconds."""
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time


@pytest.fixture
def performance_timer():
    """Provide a performance timer for benchmarking tests."""
    return PerformanceTimer


# Test data utilities
@pytest.fixture
def temp_python_file(tmp_path):
    """Create a temporary Python file for testing file operations."""
    def _create_file(content, filename="test.py"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return str(file_path)
    return _create_file


@pytest.fixture
def temp_c_file(tmp_path):
    """Create a temporary C file path for testing file operations."""
    def _create_path(filename="test.c"):
        return str(tmp_path / filename)
    return _create_path