"""Tests for the Call Graph Analyzer."""

import ast
import unittest
from unittest.mock import Mock

from src.cgen.frontend.ast_analyzer import AnalysisResult
from src.cgen.intelligence.analyzers.call_graph import (
    CallContext,
    CallGraphAnalyzer,
    CallGraphReport,
    CallPath,
    CallSite,
    CallType,
    FunctionNode,
)
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel


class TestCallGraphAnalyzer(unittest.TestCase):
    """Test cases for the CallGraphAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CallGraphAnalyzer()

    def _create_analysis_context(self, source_code: str) -> AnalysisContext:
        """Create an analysis context from source code."""
        tree = ast.parse(source_code)
        mock_result = Mock(spec=AnalysisResult)
        return AnalysisContext(
            source_code=source_code,
            ast_node=tree,
            analysis_result=mock_result,
            analysis_level=AnalysisLevel.BASIC
        )

    def test_simple_function_call(self):
        """Test analysis of simple function calls."""
        source = """
def foo():
    pass

def bar():
    foo()
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        self.assertIn("foo", report.call_graph)
        self.assertIn("bar", report.call_graph)

        bar_node = report.call_graph["bar"]
        self.assertIn("foo", bar_node.callees)
        self.assertEqual(len(bar_node.call_sites), 1)

        foo_node = report.call_graph["foo"]
        self.assertIn("bar", foo_node.callers)
        self.assertTrue(foo_node.is_leaf)

    def test_recursive_function(self):
        """Test analysis of recursive functions."""
        source = """
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        factorial_node = report.call_graph["factorial"]
        self.assertTrue(factorial_node.is_recursive)
        self.assertIn("factorial", factorial_node.callees)

        # Should detect the recursive call
        recursive_calls = [cs for cs in factorial_node.call_sites if cs.call_type == CallType.RECURSIVE]
        self.assertEqual(len(recursive_calls), 1)

    def test_mutually_recursive_functions(self):
        """Test analysis of mutually recursive functions."""
        source = """
def is_even(n: int) -> bool:
    if n == 0:
        return True
    return is_odd(n - 1)

def is_odd(n: int) -> bool:
    if n == 0:
        return False
    return is_even(n - 1)
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)

        even_node = report.call_graph["is_even"]
        odd_node = report.call_graph["is_odd"]

        self.assertIn("is_odd", even_node.callees)
        self.assertIn("is_even", odd_node.callees)

        # Should detect cycles
        self.assertTrue(len(report.cycles) > 0)
        cycle_functions = set()
        for cycle in report.cycles:
            cycle_functions.update(cycle)
        self.assertIn("is_even", cycle_functions)
        self.assertIn("is_odd", cycle_functions)

    def test_call_context_detection(self):
        """Test detection of different call contexts."""
        source = """
def main():
    foo()  # Unconditional

    if True:
        bar()  # Conditional

    for i in range(10):
        baz()  # Loop

    try:
        qux()  # Exception handling
    except:
        pass

def foo(): pass
def bar(): pass
def baz(): pass
def qux(): pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        main_node = report.call_graph["main"]

        call_contexts = {cs.callee: cs.call_context for cs in main_node.call_sites}
        self.assertEqual(call_contexts["foo"], CallContext.UNCONDITIONAL)
        self.assertEqual(call_contexts["bar"], CallContext.CONDITIONAL)
        self.assertEqual(call_contexts["baz"], CallContext.LOOP)
        self.assertEqual(call_contexts["qux"], CallContext.EXCEPTION)

    def test_builtin_function_calls(self):
        """Test handling of builtin function calls."""
        source = """
def process_data(data):
    length = len(data)
    print("Processing", length, "items")
    result = sum(data)
    return result
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        process_node = report.call_graph["process_data"]

        builtin_calls = [cs for cs in process_node.call_sites if cs.is_builtin]
        builtin_names = {cs.callee for cs in builtin_calls}
        self.assertIn("len", builtin_names)
        self.assertIn("print", builtin_names)
        self.assertIn("sum", builtin_names)

        # Builtin calls should be in external_calls
        self.assertIn("len", process_node.external_calls)
        self.assertIn("print", process_node.external_calls)
        self.assertIn("sum", process_node.external_calls)

    def test_method_call_detection(self):
        """Test detection of method calls."""
        source = """
def process_string(text):
    upper_text = text.upper()
    words = text.split()
    return words

class MyClass:
    def method(self):
        return self.helper()

    def helper(self):
        return 42
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)

        # Check method calls in function
        process_node = report.call_graph["process_string"]
        method_calls = [cs for cs in process_node.call_sites if cs.is_method_call]
        self.assertTrue(len(method_calls) > 0)

        # Check method calls in class
        if "method" in report.call_graph:
            method_node = report.call_graph["method"]
            self_calls = [cs for cs in method_node.call_sites if cs.callee == "helper"]
            if self_calls:
                self.assertTrue(self_calls[0].is_method_call)

    def test_call_graph_metrics(self):
        """Test calculation of call graph metrics."""
        source = """
def main():
    foo()
    bar()

def foo():
    baz()

def bar():
    baz()

def baz():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        metrics = report.metrics

        self.assertEqual(metrics.total_functions, 4)
        self.assertEqual(metrics.leaf_functions, 1)  # baz
        self.assertEqual(metrics.root_functions, 1)  # main

        # Check fan-out/fan-in calculations
        self.assertGreater(metrics.average_fan_out, 0)
        self.assertGreater(metrics.average_fan_in, 0)

    def test_optimization_opportunities(self):
        """Test identification of optimization opportunities."""
        source = """
def main():
    helper()
    helper()
    helper()

def another_caller():
    helper()

def helper():
    pass

def big_function():
    func1()
    func2()
    func3()
    func4()
    func5()

def func1(): pass
def func2(): pass
def func3(): pass
def func4(): pass
def func5(): pass
def func6(): pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        opportunities = report.optimization_opportunities

        # Should suggest inlining helper (called by multiple functions)
        inline_suggestions = [opp for opp in opportunities if "Inline candidate" in opp and "helper" in opp]
        self.assertTrue(len(inline_suggestions) > 0)

        # Should suggest refactoring big_function (high fan-out)
        fanout_suggestions = [opp for opp in opportunities if "High fan-out" in opp and "big_function" in opp]
        self.assertTrue(len(fanout_suggestions) > 0)

    def test_call_path_analysis(self):
        """Test analysis of call paths."""
        source = """
def main():
    level1()

def level1():
    level2()

def level2():
    level3()

def level3():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        self.assertTrue(len(report.call_paths) > 0)

        # Find the longest path
        longest_path = max(report.call_paths, key=lambda p: p.total_depth)
        self.assertEqual(longest_path.total_depth, 4)
        self.assertEqual(longest_path.functions, ["main", "level1", "level2", "level3"])

    def test_cycle_detection(self):
        """Test detection of call cycles."""
        source = """
def a():
    b()

def b():
    c()

def c():
    a()

def independent():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        self.assertTrue(len(report.cycles) > 0)

        # Should find the a->b->c->a cycle
        cycle_found = False
        for cycle in report.cycles:
            if "a" in cycle and "b" in cycle and "c" in cycle:
                cycle_found = True
                break
        self.assertTrue(cycle_found)

    def test_critical_path_identification(self):
        """Test identification of critical paths."""
        source = """
def main():
    simple_path()
    complex_path()

def simple_path():
    pass

def complex_path():
    step1()
    step2()
    step3()

def step1():
    substep1()

def step2():
    substep2()
    substep3()

def step3():
    pass

def substep1(): pass
def substep2(): pass
def substep3(): pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        self.assertTrue(len(report.critical_paths) > 0)

        # Critical paths should be sorted by complexity
        first_critical = report.critical_paths[0]
        self.assertGreater(first_critical.estimated_complexity, 0)

    def test_unreachable_function_warning(self):
        """Test warning about unreachable functions."""
        source = """
def main():
    called_function()

def called_function():
    pass

def unreachable_function():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)

        # Should warn about unreachable function
        unreachable_warnings = [w for w in report.warnings if "unreachable" in w.lower()]
        self.assertTrue(len(unreachable_warnings) > 0)

    def test_empty_program(self):
        """Test analysis of empty program."""
        source = ""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        self.assertEqual(len(report.call_graph), 0)
        self.assertEqual(len(report.call_sites), 0)
        self.assertEqual(report.metrics.total_functions, 0)

    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        source = """
def broken_function(
    # Missing closing parenthesis
"""
        try:
            context = self._create_analysis_context(source)
            report = self.analyzer.analyze(context)

            # If we get here, the parser didn't raise an exception
            # The analyzer should handle this gracefully
            self.assertIsInstance(report, CallGraphReport)
        except SyntaxError:
            # This is expected for malformed code
            pass

    def test_confidence_calculation(self):
        """Test confidence calculation in analysis."""
        source = """
def certain_call():
    known_function()

def uncertain_call():
    obj.method_call()
    dynamic_function()

def known_function():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        self.assertGreater(report.confidence, 0.0)
        self.assertLessEqual(report.confidence, 1.0)

        # Check individual call site confidences
        for call_site in report.call_sites:
            self.assertGreater(call_site.confidence, 0.0)
            self.assertLessEqual(call_site.confidence, 1.0)

    def test_node_properties(self):
        """Test proper setting of node properties."""
        source = """
def root_function():
    intermediate()

def intermediate():
    leaf1()
    leaf2()

def leaf1():
    pass

def leaf2():
    pass

def isolated():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)

        # Check root function
        root_node = report.call_graph["root_function"]
        self.assertTrue(root_node.is_root)
        self.assertFalse(root_node.is_leaf)

        # Check leaf functions
        leaf1_node = report.call_graph["leaf1"]
        leaf2_node = report.call_graph["leaf2"]
        self.assertTrue(leaf1_node.is_leaf)
        self.assertTrue(leaf2_node.is_leaf)
        self.assertFalse(leaf1_node.is_root)
        self.assertFalse(leaf2_node.is_root)

        # Check intermediate function
        intermediate_node = report.call_graph["intermediate"]
        self.assertFalse(intermediate_node.is_root)
        self.assertFalse(intermediate_node.is_leaf)

    def test_call_site_line_numbers(self):
        """Test that call sites record correct line numbers."""
        source = """def main():
    foo()  # Line 2

    bar()  # Line 4

def foo():
    pass

def bar():
    pass
"""
        context = self._create_analysis_context(source)
        report = self.analyzer.analyze(context)

        self.assertTrue(report.success)
        main_node = report.call_graph["main"]

        # Check line numbers are recorded
        for call_site in main_node.call_sites:
            self.assertGreater(call_site.line_number, 0)

        # Sort by line number to check specific calls
        sorted_calls = sorted(main_node.call_sites, key=lambda cs: cs.line_number)
        self.assertEqual(sorted_calls[0].callee, "foo")
        self.assertEqual(sorted_calls[1].callee, "bar")


if __name__ == "__main__":
    unittest.main()