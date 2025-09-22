"""Performance benchmarking utilities for cgen tests."""

import gc
import statistics
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, List

import pytest

from cgen.core import CFactory, StyleOptions, Writer
from cgen.core.py2c import PythonToCConverter, convert_python_to_c


class BenchmarkResult:
    """Container for benchmark results."""

    def __init__(self, name: str, times: List[float], iterations: int):
        self.name = name
        self.times = times
        self.iterations = iterations
        self.mean = statistics.mean(times)
        self.median = statistics.median(times)
        self.stdev = statistics.stdev(times) if len(times) > 1 else 0.0
        self.min_time = min(times)
        self.max_time = max(times)

    def __str__(self):
        return f"{self.name}: {self.mean:.4f}s ± {self.stdev:.4f}s (n={self.iterations})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "mean": self.mean,
            "median": self.median,
            "stdev": self.stdev,
            "min": self.min_time,
            "max": self.max_time,
            "iterations": self.iterations,
            "times": self.times
        }


@contextmanager
def benchmark_timer():
    """Context manager for timing operations."""
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    return end_time - start_time


def benchmark_function(func: Callable, *args, iterations: int = 100, warmup: int = 10, **kwargs) -> BenchmarkResult:
    """Benchmark a function with multiple iterations.

    Args:
        func: Function to benchmark
        *args: Arguments to pass to function
        iterations: Number of benchmark iterations
        warmup: Number of warmup iterations (not counted)
        **kwargs: Keyword arguments to pass to function

    Returns:
        BenchmarkResult with timing statistics
    """
    # Warmup runs
    for _ in range(warmup):
        func(*args, **kwargs)

    # Clear garbage before benchmarking
    gc.collect()

    # Benchmark runs
    times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    return BenchmarkResult(func.__name__, times, iterations)


# Benchmark test fixtures and sample data
BENCHMARK_SAMPLES = {
    "tiny_function": """
def add(x: int, y: int) -> int:
    return x + y
""",

    "small_function": """
def calculate(a: int, b: float, c: bool) -> float:
    result: float = 0.0
    if c:
        result = a + b
    else:
        result = a - b
    return result
""",

    "medium_function": """
def matrix_multiply_2x2(a11: float, a12: float, a21: float, a22: float,
                       b11: float, b12: float, b21: float, b22: float) -> tuple[float, float, float, float]:
    c11: float = a11 * b11 + a12 * b21
    c12: float = a11 * b12 + a12 * b22
    c21: float = a21 * b11 + a22 * b21
    c22: float = a21 * b12 + a22 * b22
    return (c11, c12, c21, c22)
""",

    "large_function": None  # Will be generated dynamically
}


def generate_large_function(num_variables: int = 50) -> str:
    """Generate a large function for benchmarking."""
    lines = ["def large_calculation(x: int) -> int:"]

    # Generate many variable declarations and operations
    for i in range(num_variables):
        lines.append(f"    var_{i}: int = x + {i}")

    # Generate some calculations using the variables
    lines.append("    result: int = 0")
    for i in range(0, num_variables, 5):
        lines.append(f"    result = result + var_{i}")

    lines.append("    return result")
    return "\n".join(lines)


# Initialize large function sample
BENCHMARK_SAMPLES["large_function"] = generate_large_function()


@pytest.mark.benchmark
class TestPy2CPerformance:
    """Performance benchmarks for Python-to-C conversion."""

    def test_tiny_function_benchmark(self, benchmark):
        """Benchmark conversion of tiny functions."""
        result = benchmark_function(
            convert_python_to_c,
            BENCHMARK_SAMPLES["tiny_function"],
            iterations=1000
        )
        print(f"\nTiny function benchmark: {result}")
        assert result.mean < 0.01  # Should complete in under 10ms

    def test_small_function_benchmark(self, benchmark):
        """Benchmark conversion of small functions."""
        result = benchmark_function(
            convert_python_to_c,
            BENCHMARK_SAMPLES["small_function"],
            iterations=500
        )
        print(f"\nSmall function benchmark: {result}")
        assert result.mean < 0.02  # Should complete in under 20ms

    def test_medium_function_benchmark(self, benchmark):
        """Benchmark conversion of medium functions."""
        result = benchmark_function(
            convert_python_to_c,
            BENCHMARK_SAMPLES["medium_function"],
            iterations=200
        )
        print(f"\nMedium function benchmark: {result}")
        assert result.mean < 0.05  # Should complete in under 50ms

    @pytest.mark.slow
    def test_large_function_benchmark(self, benchmark):
        """Benchmark conversion of large functions."""
        result = benchmark_function(
            convert_python_to_c,
            BENCHMARK_SAMPLES["large_function"],
            iterations=50
        )
        print(f"\nLarge function benchmark: {result}")
        assert result.mean < 0.1  # Should complete in under 100ms

    def test_converter_initialization_benchmark(self, benchmark):
        """Benchmark converter initialization."""
        def create_converter():
            return PythonToCConverter()

        result = benchmark_function(create_converter, iterations=1000)
        print(f"\nConverter initialization benchmark: {result}")
        assert result.mean < 0.001  # Should be very fast


@pytest.mark.benchmark
class TestCorePerformance:
    """Performance benchmarks for core C generation."""

    def test_cfactory_creation_benchmark(self, benchmark):
        """Benchmark CFactory creation."""
        def create_factory():
            return CFactory()

        result = benchmark_function(create_factory, iterations=10000)
        print(f"\nCFactory creation benchmark: {result}")
        assert result.mean < 0.0001  # Should be extremely fast

    def test_writer_creation_benchmark(self, benchmark):
        """Benchmark Writer creation."""
        def create_writer():
            return Writer(StyleOptions())

        result = benchmark_function(create_writer, iterations=1000)
        print(f"\nWriter creation benchmark: {result}")
        assert result.mean < 0.001  # Should be very fast

    def test_simple_c_generation_benchmark(self, benchmark):
        """Benchmark simple C code generation."""
        def generate_simple_c():
            factory = CFactory()
            seq = factory.sequence()
            func = factory.function("test", "int")
            seq.append(factory.declaration(func))
            writer = Writer(StyleOptions())
            return writer.write_str(seq)

        result = benchmark_function(generate_simple_c, iterations=1000)
        print(f"\nSimple C generation benchmark: {result}")
        assert result.mean < 0.005  # Should complete in under 5ms


def run_all_benchmarks():
    """Run all benchmarks and display results."""
    print("🚀 Running CGen Performance Benchmarks")
    print("=" * 60)

    # Run py2c benchmarks
    print("\n📊 Python-to-C Conversion Benchmarks")
    print("-" * 40)

    for name, sample in BENCHMARK_SAMPLES.items():
        if sample:
            print(f"\nBenchmarking {name}...")
            result = benchmark_function(convert_python_to_c, sample, iterations=100)
            print(f"  {result}")

    # Run core benchmarks
    print("\n⚙️  Core Generation Benchmarks")
    print("-" * 40)

    # CFactory benchmark
    result = benchmark_function(CFactory, iterations=10000)
    print(f"  {result}")

    # Writer benchmark
    result = benchmark_function(lambda: Writer(StyleOptions()), iterations=1000)
    print(f"  Writer creation: {result}")

    print("\n🏁 Benchmark suite completed!")


if __name__ == "__main__":
    run_all_benchmarks()
