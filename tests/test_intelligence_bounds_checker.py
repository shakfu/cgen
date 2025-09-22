"""Tests for the Bounds Checker in the Intelligence Layer."""

import ast

import pytest

from src.cgen.frontend.ast_analyzer import AnalysisResult, FunctionInfo
from src.cgen.intelligence.analyzers.bounds_checker import BoundsChecker, BoundsViolationType
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel


class TestBoundsChecker:
    """Test cases for the BoundsChecker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = BoundsChecker(AnalysisLevel.BASIC)

    def test_simple_array_access_safe(self):
        """Test safe array access."""
        code = """
def access_array(arr: list) -> int:
    result = arr[0]
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'access_array': FunctionInfo('access_array', ['arr'], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success
        assert report.confidence > 0.8
        assert len(report.memory_regions) >= 1  # At least the parameter

    def test_negative_index_detection(self):
        """Test detection of negative array indices."""
        code = """
def bad_access(arr: list) -> int:
    result = arr[-5]  # This should be flagged
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'bad_access': FunctionInfo('bad_access', ['arr'], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should detect negative index
        negative_index_violations = [v for v in report.violations
                                   if v.violation_type == BoundsViolationType.NEGATIVE_INDEX]
        assert len(negative_index_violations) > 0

    def test_list_bounds_checking(self):
        """Test bounds checking for list literals."""
        code = """
def test_list_bounds() -> int:
    arr = [1, 2, 3, 4, 5]
    safe_access = arr[2]    # Safe
    unsafe_access = arr[10] # Out of bounds
    return safe_access + unsafe_access
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'test_list_bounds': FunctionInfo('test_list_bounds', [], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should detect out-of-bounds access
        oob_violations = [v for v in report.violations
                         if v.violation_type == BoundsViolationType.ARRAY_INDEX_OUT_OF_BOUNDS]
        assert len(oob_violations) > 0

        # Should have memory region for the list
        assert 'arr' in report.memory_regions
        assert report.memory_regions['arr'].size == 5

    def test_variable_index_warning(self):
        """Test warning for variable indices."""
        code = """
def variable_index(arr: list, idx: int) -> int:
    return arr[idx]  # Should warn about unchecked variable index
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'variable_index': FunctionInfo('variable_index', ['arr', 'idx'], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should have warnings about variable index
        assert len(report.warnings) > 0

        # Should have memory regions for parameters
        assert 'arr' in report.memory_regions
        assert 'idx' in report.memory_regions

    def test_uninitialized_variable_detection(self):
        """Test detection of uninitialized variable access."""
        code = """
def uninitialized_access() -> int:
    result = undefined_var  # Should be flagged
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'uninitialized_access': FunctionInfo('uninitialized_access', [], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should detect uninitialized access
        uninit_violations = [v for v in report.violations
                           if v.violation_type == BoundsViolationType.UNINITIALIZED_ACCESS]
        assert len(uninit_violations) > 0

    def test_loop_variable_tracking(self):
        """Test tracking of variables in loops."""
        code = """
def loop_access(arr: list) -> int:
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'loop_access': FunctionInfo('loop_access', ['arr'], [], 'int', 2)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should track loop variables
        assert 'i' in report.memory_regions
        assert 'total' in report.memory_regions

    def test_assignment_tracking(self):
        """Test tracking of variable assignments."""
        code = """
def assignment_test() -> int:
    a = 5
    b = [1, 2, 3]
    c = a + b[1]
    return c
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'assignment_test': FunctionInfo('assignment_test', [], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should track all assigned variables
        assert 'a' in report.memory_regions
        assert 'b' in report.memory_regions
        assert 'c' in report.memory_regions

        # Variable 'b' should have correct size
        assert report.memory_regions['b'].size == 3

    def test_function_call_analysis(self):
        """Test analysis of function calls for potential memory issues."""
        code = """
def function_calls() -> None:
    # This would be dangerous in C
    ptr = malloc(100)
    data = some_function(ptr)
    free(ptr)
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'function_calls': FunctionInfo('function_calls', [], [], 'None', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should have warnings about memory allocation/deallocation
        memory_warnings = [v for v in report.violations
                          if v.violation_type in [BoundsViolationType.MEMORY_LEAK, BoundsViolationType.DOUBLE_FREE]]
        assert len(memory_warnings) > 0

    def test_complex_expression_handling(self):
        """Test handling of complex expressions."""
        code = """
def complex_expressions(matrix: list) -> int:
    # Complex index expression
    result = matrix[i + j * width]  # Should warn about complex index
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'complex_expressions': FunctionInfo('complex_expressions', ['matrix'], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should have warnings about complex indices
        assert len(report.warnings) > 0

    def test_memory_usage_estimation(self):
        """Test memory usage estimation."""
        code = """
def memory_usage() -> None:
    small_array = [1, 2, 3]          # 3 elements
    large_array = [0] * 1000         # 1000 elements (if we could detect this)
    single_var = 42
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'memory_usage': FunctionInfo('memory_usage', [], [], 'None', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should estimate some memory usage
        assert report.memory_usage_estimate >= 0

        # Should track the arrays
        assert 'small_array' in report.memory_regions

    def test_error_handling(self):
        """Test bounds checker error handling."""
        # Test with a simple valid function
        code = """
def simple() -> None:
    pass
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'simple': FunctionInfo('simple', [], [], 'None', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        # Should handle gracefully
        assert report.success
        assert report is not None

    def test_statistics_calculation(self):
        """Test calculation of safety statistics."""
        code = """
def mixed_access() -> int:
    arr = [1, 2, 3, 4, 5]
    safe1 = arr[0]      # Safe
    safe2 = arr[2]      # Safe
    unsafe = arr[10]    # Unsafe
    unknown = arr[idx]  # Unknown safety
    return safe1 + safe2 + unsafe + unknown
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'mixed_access': FunctionInfo('mixed_access', [], [], 'int', 1)},
            global_variables={},
            imports=[],
            errors=[],
            warnings=[]
        )

        context = AnalysisContext(
            source_code=code,
            ast_node=ast_node,
            analysis_result=analysis_result
        )

        report = self.checker.analyze(context)

        assert report.success

        # Should have some violations
        assert len(report.violations) > 0

        # Should have calculated statistics
        total_accesses = report.safe_accesses + report.unsafe_accesses + report.unknown_accesses
        assert total_accesses >= 0


# This file has been converted to pytest style
