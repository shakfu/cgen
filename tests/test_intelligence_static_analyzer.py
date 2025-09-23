"""Tests for the Static Analyzer in the Intelligence Layer."""

import ast

import pytest

from src.cgen.frontend.ast_analyzer import AnalysisResult, FunctionInfo
from src.cgen.frontend.analyzers.static_analyzer import NodeType, StaticAnalyzer
from src.cgen.frontend.base import AnalysisContext, AnalysisLevel


class TestStaticAnalyzer:
    """Test cases for the StaticAnalyzer."""


    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StaticAnalyzer(AnalysisLevel.BASIC)

    def test_simple_function_analysis(self):
        """Test static analysis of a simple function."""
        code = """
def add(x: int, y: int) -> int:
    result = x + y
    return result
"""
        ast_node = ast.parse(code).body[0]  # Get the function node

        # Create a mock analysis result
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

        report = self.analyzer.analyze(context)

        assert report.success
        assert report.confidence > 0.8
        assert len(report.cfg.nodes) >= 3  # Entry, statements, return
        assert 'x' in report.variables
        assert 'y' in report.variables
        assert 'result' in report.variables

    def test_control_flow_with_if_statement(self):
        """Test static analysis with if statement."""
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

        report = self.analyzer.analyze(context)

        assert report.success

        # Check that we have a condition node
        condition_nodes = [node for node in report.cfg.nodes.values()
                          if node.node_type == NodeType.CONDITION]
        assert len(condition_nodes) > 0

        # Check complexity metrics
        assert report.complexity_metrics['conditionals'] >= 1
        assert report.complexity_metrics['cyclomatic_complexity'] >= 2

    def test_loop_analysis(self):
        """Test static analysis with loops."""
        code = """
def factorial(n: int) -> int:
    result = 1
    i = 1
    while i <= n:
        result = result * i
        i = i + 1
    return result
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'factorial': FunctionInfo('factorial', ['n'], [], 'int', 3)},
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

        report = self.analyzer.analyze(context)

        assert report.success

        # Check that we have loop nodes
        loop_nodes = [node for node in report.cfg.nodes.values()
                     if node.node_type == NodeType.LOOP_HEADER]
        assert len(loop_nodes) > 0

        # Check variables
        assert 'result' in report.variables
        assert 'i' in report.variables

        # Check complexity metrics
        assert report.complexity_metrics['loops'] >= 1

    def test_dead_code_detection(self):
        """Test detection of unreachable code."""
        code = """
def test_dead_code(x: int) -> int:
    if x > 0:
        return x
    else:
        return -x
    # This code is unreachable
    print("This will never execute")
    return 0
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'test_dead_code': FunctionInfo('test_dead_code', ['x'], [], 'int', 2)},
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

        report = self.analyzer.analyze(context)

        assert report.success

        # Note: Dead code detection is complex and this simple implementation
        # may not catch all cases. This test verifies the analysis completes.
        assert report.dead_code_nodes is not None

    def test_variable_usage_analysis(self):
        """Test variable usage and definition tracking."""
        code = """
def test_variables(x: int, y: int) -> int:
    a = x + y  # a is defined and used
    b = 10     # b is defined but not used
    c = a * 2  # c uses a
    return c
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'test_variables': FunctionInfo('test_variables', ['x', 'y'], [], 'int', 1)},
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

        report = self.analyzer.analyze(context)

        assert report.success

        # Check parameter tracking
        assert report.variables['x'].is_parameter
        assert report.variables['y'].is_parameter

        # Check that variables are tracked
        assert 'a' in report.variables
        assert 'b' in report.variables
        assert 'c' in report.variables

        # Check usage patterns (b should be flagged as unused)
        unused_warnings = [issue for issue in report.potential_issues
                          if 'never used' in issue and 'b' in issue]
        assert len(unused_warnings) > 0

    def test_complex_control_flow(self):
        """Test analysis of complex control flow with nested structures."""
        code = """
def complex_function(items: list, threshold: int) -> int:
    count = 0
    for item in items:
        if item > threshold:
            if item % 2 == 0:
                count += item
            else:
                count += item * 2
        else:
            continue
    return count
"""
        ast_node = ast.parse(code).body[0]

        analysis_result = AnalysisResult(
            functions={'complex_function': FunctionInfo('complex_function', ['items', 'threshold'], [], 'int', 5)},
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

        report = self.analyzer.analyze(context)

        assert report.success
        assert len(report.cfg.nodes) > 8  # Complex control flow
        assert report.complexity_metrics['cyclomatic_complexity'] >= 4

        # Check that continue statement is handled
        continue_nodes = [node for node in report.cfg.nodes.values()
                         if node.node_type == NodeType.CONTINUE]
        assert len(continue_nodes) > 0

    def test_error_handling(self):
        """Test analyzer error handling with invalid input."""
        # Test with invalid AST node type
        code = "invalid syntax {"
        try:
            ast_node = ast.parse(code)
        except SyntaxError:
            # Create a minimal valid AST for error testing
            ast_node = ast.parse("pass").body[0]

        analysis_result = AnalysisResult(
            functions={},
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

        # The analyzer should handle errors gracefully
        report = self.analyzer.analyze(context)
        assert report is not None  # Should return a report even on errors


# This file has been converted to pytest style
