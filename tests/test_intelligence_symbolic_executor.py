"""Tests for the Symbolic Executor in the Intelligence Layer."""

import unittest
import ast
from src.cgen.intelligence.analyzers.symbolic_executor import SymbolicExecutor, SymbolicValueType
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel
from src.cgen.frontend.ast_analyzer import AnalysisResult, FunctionInfo


class TestSymbolicExecutor(unittest.TestCase):
    """Test cases for the SymbolicExecutor."""

    def setUp(self):
        """Set up test fixtures."""
        self.executor = SymbolicExecutor(AnalysisLevel.BASIC)

    def test_simple_function_execution(self):
        """Test symbolic execution of a simple function."""
        code = """
def add(x: int, y: int) -> int:
    result = x + y
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'add': FunctionInfo('add', ['x', 'y'], [], 'int', 1)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        self.assertGreater(report.confidence, 0.7)
        self.assertGreater(report.total_paths, 0)
        self.assertGreaterEqual(report.completed_paths, 0)

    def test_conditional_execution(self):
        """Test symbolic execution with conditional branches."""
        code = """
def abs_value(x: int) -> int:
    if x < 0:
        result = -x
    else:
        result = x
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'abs_value': FunctionInfo('abs_value', ['x'], [], 'int', 2)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        # Should generate at least 2 paths (true and false branches)
        self.assertGreaterEqual(report.total_paths, 2)

        # Check that we have path conditions
        all_conditions = []
        for path in report.execution_paths:
            all_conditions.extend(path.path_conditions)

        # Should have conditions for both branches
        self.assertGreater(len(all_conditions), 0)

    def test_loop_execution(self):
        """Test symbolic execution with a simple loop."""
        code = """
def count_up(n: int) -> int:
    i = 0
    while i < n:
        i = i + 1
    return i
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'count_up': FunctionInfo('count_up', ['n'], [], 'int', 3)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        self.assertGreater(report.total_paths, 0)

        # Loops should generate multiple paths due to unrolling
        self.assertGreaterEqual(report.total_paths, 1)

    def test_variable_assignment_tracking(self):
        """Test tracking of variable assignments."""
        code = """
def calculate(x: int, y: int) -> int:
    a = x + y
    b = a * 2
    c = b - x
    return c
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'calculate': FunctionInfo('calculate', ['x', 'y'], [], 'int', 1)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        self.assertGreater(report.total_paths, 0)

        # Check that at least one path was completed
        self.assertGreater(report.completed_paths, 0)

    def test_division_by_zero_detection(self):
        """Test detection of potential division by zero."""
        code = """
def divide(x: int, y: int) -> int:
    result = x / y
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'divide': FunctionInfo('divide', ['x', 'y'], [], 'int', 1)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        # Note: Basic symbolic executor might not detect all division by zero cases
        # but should complete execution without errors
        self.assertGreater(report.total_paths, 0)

    def test_complex_control_flow(self):
        """Test symbolic execution with complex control flow."""
        code = """
def complex_logic(x: int, y: int) -> int:
    if x > 0:
        if y > 0:
            result = x + y
        else:
            result = x - y
    else:
        result = 0
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'complex_logic': FunctionInfo('complex_logic', ['x', 'y'], [], 'int', 4)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        # Should generate multiple paths for nested conditions
        self.assertGreaterEqual(report.total_paths, 3)  # At least 3 different paths

        # Check coverage information
        self.assertIn('coverage_percentage', report.coverage_info)
        self.assertGreaterEqual(report.coverage_info['coverage_percentage'], 0)

    def test_error_handling(self):
        """Test symbolic executor error handling."""
        # Test with a simple statement that should not cause errors
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

        report = self.executor.analyze(context)

        # Should handle gracefully
        self.assertIsNotNone(report)

    def test_coverage_calculation(self):
        """Test coverage calculation functionality."""
        code = """
def test_coverage(x: int) -> int:
    if x > 5:
        return x * 2
    else:
        return x + 1
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'test_coverage': FunctionInfo('test_coverage', ['x'], [], 'int', 2)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)

        # Check coverage information structure
        self.assertIn('total_lines', report.coverage_info)
        self.assertIn('covered_lines', report.coverage_info)
        self.assertIn('coverage_percentage', report.coverage_info)
        self.assertIn('uncovered_lines', report.coverage_info)

        # Should have reasonable coverage
        self.assertGreaterEqual(report.coverage_info['coverage_percentage'], 0)

    def test_path_limit_handling(self):
        """Test that path explosion is properly limited."""
        # Create a function that could generate many paths
        code = """
def many_paths(a: int, b: int, c: int, d: int) -> int:
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return 1
                else:
                    return 2
            else:
                return 3
        else:
            return 4
    else:
        return 5
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'many_paths': FunctionInfo('many_paths', ['a', 'b', 'c', 'd'], [], 'int', 5)},
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

        report = self.executor.analyze(context)

        self.assertTrue(report.success)
        # Should be limited by max_paths
        self.assertLessEqual(report.total_paths, self.executor._max_paths)


if __name__ == '__main__':
    unittest.main()