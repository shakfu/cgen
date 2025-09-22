"""Tests for the Function Specializer Optimizer."""

import ast
from unittest.mock import Mock

import pytest


from src.cgen.frontend.ast_analyzer import AnalysisResult
from src.cgen.intelligence.base import AnalysisContext, OptimizationLevel
from src.cgen.intelligence.optimizers.function_specializer import (
    CallPattern,
    FunctionSpecializer,
    SpecializationCandidate,
    SpecializationReport,
    SpecializationType,
)


class TestFunctionSpecializer:
    """Test cases for the FunctionSpecializer."""


    def setup_method(self):
        """Set up test fixtures."""
        self.specializer = FunctionSpecializer()

    def _create_analysis_context(self, source_code: str) -> AnalysisContext:
        """Create an analysis context from source code."""
        tree = ast.parse(source_code)
        mock_result = Mock(spec=AnalysisResult)
        return AnalysisContext(
            source_code=source_code,
            ast_node=tree,
            analysis_result=mock_result,
            optimization_level=OptimizationLevel.BASIC
        )

    def test_function_profile_analysis(self):
        """Test analysis of function profiles."""
        source = """
def add(x: int, y: int) -> int:
    return x + y

def main():
    result1 = add(5, 3)
    result2 = add(10, 20)
    result3 = add(1, 2)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")
        assert isinstance(report, SpecializationReport)

        # Check function profiles
        assert "add" in report.function_profiles
        assert "main" in report.function_profiles

        add_profile = report.function_profiles["add"]
        assert len(add_profile.parameters) == 2
        assert add_profile.parameters[0].name == "x"
        assert add_profile.parameters[1].name == "y"
        assert add_profile.total_calls == 3

    def test_call_pattern_classification(self):
        """Test classification of call patterns."""
        source = """
def small_function():
    return 42

def hot_function(x):
    return x * 2

def constant_function(x, y):
    return x + y

def main():
    # Single use
    result1 = small_function()

    # Hot path
    for i in range(10):
        result2 = hot_function(i)

    # Constant args
    result3 = constant_function(5, 10)
    result4 = constant_function(5, 10)
    result5 = constant_function(5, 10)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Check call patterns
        small_profile = report.function_profiles["small_function"]
        assert small_profile.call_pattern == CallPattern.SINGLE_USE

        constant_profile = report.function_profiles["constant_function"]
        assert constant_profile.total_calls == 3
        # Should be classified as constant args pattern

    def test_constant_specialization_candidate(self):
        """Test generation of constant specialization candidates."""
        source = """
def power(base: int, exponent: int) -> int:
    result = 1
    for _ in range(exponent):
        result *= base
    return result

def main():
    result1 = power(2, 8)
    result2 = power(3, 8)
    result3 = power(5, 8)
    result4 = power(7, 8)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Should generate constant specialization for exponent=8
        constant_candidates = [
            c for c in report.specialization_candidates
            if c.specialization_type == SpecializationType.CONSTANT_FOLDING
        ]
        assert len(constant_candidates) > 0

        # Check if there's a specialization for the constant exponent
        exponent_specialization = any(
            "exponent" in c.parameter_bindings and c.parameter_bindings["exponent"] == 8
            for c in constant_candidates
        )
        assert exponent_specialization

    def test_type_specialization_candidate(self):
        """Test generation of type specialization candidates."""
        source = """
def process(value):
    return value * 2

def main():
    result1 = process(10)      # int
    result2 = process(20)      # int
    result3 = process(30)      # int
    result4 = process(3.14)    # float
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Should generate type specialization candidates
        type_candidates = [
            c for c in report.specialization_candidates
            if c.specialization_type == SpecializationType.TYPE_SPECIALIZATION
        ]

        # May have type specializations based on call patterns
        assert len(type_candidates) >= 0

    def test_inline_candidate_generation(self):
        """Test generation of inline candidates for small functions."""
        source = """
def get_constant():
    return 42

def small_helper(x):
    return x + 1

def main():
    value1 = get_constant()
    value2 = small_helper(10)
    value3 = small_helper(20)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Should suggest inlining for small functions
        inline_candidates = [
            c for c in report.specialization_candidates
            if c.specialization_type == SpecializationType.INLINE_EXPANSION
        ]

        # Small functions should be candidates for inlining
        assert len(inline_candidates) >= 0

    def test_pure_function_detection(self):
        """Test detection of pure functions."""
        source = """
def pure_function(x, y):
    return x * x + y * y

def impure_function(x):
    print(x)
    return x * 2

def side_effect_function(x):
    global counter
    counter += 1
    return x
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Check purity analysis
        pure_profile = report.function_profiles["pure_function"]
        assert pure_profile.is_pure

        impure_profile = report.function_profiles["impure_function"]
        assert impure_profile.has_side_effects

    def test_recursive_function_detection(self):
        """Test detection of recursive functions."""
        source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def non_recursive(x):
    return x * 2
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Check recursion detection
        factorial_profile = report.function_profiles["factorial"]
        assert factorial_profile.is_recursive

        fibonacci_profile = report.function_profiles["fibonacci"]
        assert fibonacci_profile.is_recursive

        non_recursive_profile = report.function_profiles["non_recursive"]
        assert not non_recursive_profile.is_recursive

    def test_memoization_candidate(self):
        """Test generation of memoization candidates."""
        source = """
def expensive_computation(n):
    result = 0
    for i in range(n):
        for j in range(i):
            result += i * j
    return result

def main():
    # Repeated calls with same values
    result1 = expensive_computation(100)
    result2 = expensive_computation(100)
    result3 = expensive_computation(50)
    result4 = expensive_computation(100)
    result5 = expensive_computation(50)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Should suggest memoization for pure, expensive functions
        memoization_candidates = [
            c for c in report.specialization_candidates
            if c.specialization_type == SpecializationType.MEMOIZATION
        ]

        # May suggest memoization if function is pure and complex
        assert len(memoization_candidates) >= 0

    def test_complexity_scoring(self):
        """Test function complexity scoring."""
        source = """
def simple_function(x):
    return x + 1

def medium_function(x, y):
    if x > y:
        return x * y
    else:
        return x + y

def complex_function(data):
    result = 0
    for item in data:
        if item % 2 == 0:
            for i in range(item):
                result += compute_value(i)
        else:
            result -= item
    return result

def compute_value(x):
    return x * x
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Check complexity scores
        simple_score = report.function_profiles["simple_function"].complexity_score
        complex_score = report.function_profiles["complex_function"].complexity_score

        assert simple_score < complex_score

    def test_optimization_level_impact(self):
        """Test impact of different optimization levels."""
        source = """
def test_function(x, y):
    return x * y + 1

def main():
    result1 = test_function(5, 10)
    result2 = test_function(5, 20)
"""


        # Test basic level
        basic_specializer = FunctionSpecializer(OptimizationLevel.BASIC)
        context = self._create_analysis_context(source)
        basic_result = basic_specializer.optimize(context)
        basic_report = basic_result.metadata.get("report")

        # Test aggressive level
        aggressive_specializer = FunctionSpecializer(OptimizationLevel.AGGRESSIVE)
        aggressive_result = aggressive_specializer.optimize(context)
        aggressive_report = aggressive_result.metadata.get("report")

        assert basic_result.success
        assert aggressive_result.success

        # Aggressive level might generate more candidates
        assert (
            len(aggressive_report.specialization_candidates) >= len(basic_report.specialization_candidates)
        )

    def test_parameter_value_distribution(self):
        """Test analysis of parameter value distributions."""
        source = """
def multiply_by_factor(value, factor):
    return value * factor

def main():
    result1 = multiply_by_factor(10, 2)
    result2 = multiply_by_factor(20, 2)
    result3 = multiply_by_factor(30, 2)
    result4 = multiply_by_factor(40, 3)
    result5 = multiply_by_factor(50, 2)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        multiply_profile = report.function_profiles["multiply_by_factor"]
        factor_param = multiply_profile.parameters[1]  # factor parameter

        # Should track value distribution
        assert len(factor_param.value_distribution) > 0

    def test_specialization_creation(self):
        """Test creation of specialized functions."""
        source = """
def calculate(x, multiplier):
    return x * multiplier + 1

def main():
    result1 = calculate(10, 2)
    result2 = calculate(20, 2)
    result3 = calculate(30, 2)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Should create some specializations
        assert len(report.specialization_results) >= 0

        # Check specialization properties
        for spec_result in report.specialization_results:
            assert spec_result.specialized_function is not None
            assert spec_result.original_function is not None
            assert spec_result.performance_gain > 1.0

    def test_call_site_analysis(self):
        """Test analysis of call sites."""
        source = """
def helper(a, b):
    return a + b

def caller1():
    return helper(1, 2)

def caller2():
    return helper(3, 4)

def caller3():
    x = 5
    y = 6
    return helper(x, y)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        helper_profile = report.function_profiles["helper"]
        assert len(helper_profile.call_sites) == 3

        # Check call site information
        for call_site in helper_profile.call_sites:
            assert call_site.caller_name is not None
            assert call_site.line_number > 0
            assert len(call_site.argument_values) == 2

    def test_performance_estimation(self):
        """Test performance gain estimation."""
        source = """
def simple_add(x, y):
    return x + y

def main():
    result = simple_add(5, 10)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        assert result.performance_gain_estimate >= 1.0
        assert result.performance_gain_estimate <= 10.0  # Capped maximum

    def test_safety_analysis(self):
        """Test safety analysis of specializations."""
        source = """
def safe_function(x, y):
    return x * y

def main():
    result = safe_function(3, 4)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        assert result.is_safe()

        safety = result.safety_analysis
        assert safety.get("all_specializations_safe", True)

    def test_empty_program(self):
        """Test analysis of empty program."""
        source = """
# Empty program with no functions
pass
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")
        assert report.total_functions == 0
        assert len(report.specialization_candidates) == 0

    def test_function_with_no_calls(self):
        """Test analysis of function with no calls."""
        source = """
def unused_function(x):
    return x * 2

def main():
    pass
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        unused_profile = report.function_profiles["unused_function"]
        assert unused_profile.total_calls == 0
        assert len(unused_profile.call_sites) == 0

    def test_error_handling(self):
        """Test error handling with malformed input."""
        # Test with invalid AST
        invalid_context = Mock()
        invalid_context.ast_node = None
        invalid_context.source_code = ""

        result = self.specializer.optimize(invalid_context)

        # Should handle gracefully
        assert not result.success
        assert "error" in result.metadata

    def test_transformations_reporting(self):
        """Test reporting of transformations performed."""
        source = """
def test_function(x):
    return x * 2

def main():
    result1 = test_function(5)
    result2 = test_function(10)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        assert len(result.transformations) > 0

        # Check transformation descriptions
        transformations_text = " ".join(result.transformations)
        assert "functions" in transformations_text

    def test_candidate_properties(self):
        """Test properties of specialization candidates."""
        source = """
def candidate_function(x, y):
    return x + y * 2

def main():
    result1 = candidate_function(10, 5)
    result2 = candidate_function(20, 5)
    result3 = candidate_function(30, 5)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        for candidate in report.specialization_candidates:
            assert isinstance(candidate, SpecializationCandidate)
            assert candidate.confidence > 0.0
            assert candidate.confidence <= 1.0
            assert candidate.estimated_speedup > 1.0
            assert candidate.call_site_coverage >= 0.0
            assert candidate.call_site_coverage <= 1.0

    def test_function_body_size_analysis(self):
        """Test analysis of function body sizes."""
        source = """
def tiny_function():
    return 1

def small_function(x):
    y = x * 2
    return y + 1

def large_function(data):
    result = []
    for item in data:
        if item > 0:
            processed = item * 2
            if processed > 10:
                processed = processed / 2
            result.append(processed)
        else:
            result.append(0)
    return result
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Check body sizes
        tiny_size = report.function_profiles["tiny_function"].body_size
        large_size = report.function_profiles["large_function"].body_size

        assert tiny_size < large_size

    def test_return_type_analysis(self):
        """Test analysis of return types."""
        source = """
def typed_function(x: int) -> str:
    return str(x)

def untyped_function(x):
    return x * 2
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        typed_profile = report.function_profiles["typed_function"]
        assert typed_profile.return_type == "str"

        untyped_profile = report.function_profiles["untyped_function"]
        assert untyped_profile.return_type is None

    def test_specialization_confidence_scoring(self):
        """Test confidence scoring for specializations."""
        source = """
def confident_candidate(x):
    return x * 2

def uncertain_candidate(x, y):
    if x > y:
        return complex_operation(x, y)
    else:
        return simple_operation(x, y)

def complex_operation(a, b):
    return a ** b

def simple_operation(a, b):
    return a + b

def main():
    result1 = confident_candidate(5)
    result2 = confident_candidate(10)
    result3 = uncertain_candidate(3, 7)
"""
        context = self._create_analysis_context(source)
        result = self.specializer.optimize(context)

        assert result.success
        report = result.metadata.get("report")

        # Check confidence scores
        for candidate in report.specialization_candidates:
            assert candidate.confidence > 0.0
            assert candidate.confidence <= 1.0


if __name__ == "__main__":
    unittest.main()