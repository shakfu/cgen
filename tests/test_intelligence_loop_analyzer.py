"""Tests for the Loop Analyzer Optimizer."""

import ast
import unittest
from unittest.mock import Mock

from src.cgen.frontend.ast_analyzer import AnalysisResult
from src.cgen.intelligence.base import AnalysisContext, OptimizationLevel
from src.cgen.intelligence.optimizers.loop_analyzer import (
    LoopAnalyzer,
    LoopAnalysisReport,
    LoopInfo,
    LoopOptimization,
    LoopPattern,
    LoopType,
    OptimizationType,
)


class TestLoopAnalyzer(unittest.TestCase):
    """Test cases for the LoopAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = LoopAnalyzer()

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

    def test_simple_range_loop_analysis(self):
        """Test analysis of simple range loops."""
        source = """
def process_data():
    for i in range(10):
        result = i * 2
    return result
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertIsInstance(report, LoopAnalysisReport)
        self.assertEqual(report.total_loops, 1)

        loop = report.loops_found[0]
        self.assertEqual(loop.loop_type, LoopType.FOR_RANGE)
        self.assertTrue(loop.bounds.is_constant)
        self.assertEqual(loop.bounds.total_iterations, 10)
        self.assertEqual(loop.bounds.start, 0)
        self.assertEqual(loop.bounds.end, 10)

    def test_range_loop_with_start_end_step(self):
        """Test analysis of range loops with start, end, and step."""
        source = """
def process_range():
    for i in range(5, 15, 2):
        value = i + 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertEqual(loop.loop_type, LoopType.FOR_RANGE)
        self.assertTrue(loop.bounds.is_constant)
        self.assertEqual(loop.bounds.start, 5)
        self.assertEqual(loop.bounds.end, 15)
        self.assertEqual(loop.bounds.step, 2)
        self.assertEqual(loop.bounds.total_iterations, 5)  # (15-5)/2 = 5

    def test_while_loop_analysis(self):
        """Test analysis of while loops."""
        source = """
def while_loop_test():
    i = 0
    while i < 10:
        result = i * 2
        i += 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertEqual(report.total_loops, 1)

        loop = report.loops_found[0]
        self.assertEqual(loop.loop_type, LoopType.WHILE_COUNTER)

    def test_accumulator_pattern_detection(self):
        """Test detection of accumulator patterns."""
        source = """
def accumulator_sum():
    total = 0
    for i in range(100):
        total = total + i
    return total
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertEqual(loop.pattern, LoopPattern.ACCUMULATOR)
        # Check that 'total' is identified as an accumulator
        self.assertIn("total", loop.variables)
        self.assertTrue(loop.variables["total"].is_accumulator)

    def test_nested_loop_analysis(self):
        """Test analysis of nested loops."""
        source = """
def nested_loops():
    for i in range(5):
        for j in range(3):
            result = i * j
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertEqual(report.total_loops, 2)  # Outer + inner loop
        self.assertEqual(report.nested_loops, 1)  # Only inner loop is nested

        # Find outer loop (nesting_level 0)
        outer_loop = next(loop for loop in report.loops_found if loop.nesting_level == 0)
        self.assertEqual(len(outer_loop.inner_loops), 1)
        self.assertEqual(outer_loop.nesting_level, 0)

        # Find inner loop (nesting_level 1)
        inner_loop = next(loop for loop in report.loops_found if loop.nesting_level == 1)
        self.assertEqual(inner_loop.nesting_level, 1)
        self.assertEqual(inner_loop.pattern, LoopPattern.NESTED_ITERATION)

    def test_loop_with_break_continue(self):
        """Test analysis of loops with break and continue statements."""
        source = """
def control_flow_loop():
    for i in range(20):
        if i == 5:
            continue
        if i == 15:
            break
        result = i * 2
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertTrue(loop.has_break)
        self.assertTrue(loop.has_continue)
        self.assertTrue(loop.has_early_exit)

    def test_enumerate_loop_analysis(self):
        """Test analysis of enumerate loops."""
        source = """
def enumerate_test():
    items = [1, 2, 3, 4, 5]
    for i, value in enumerate(items):
        result = i + value
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertEqual(loop.loop_type, LoopType.FOR_ENUMERATE)

    def test_vectorizable_loop_detection(self):
        """Test detection of vectorizable loops."""
        source = """
def vectorizable_loop():
    for i in range(1000):
        result = i * 2 + 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertTrue(loop.is_vectorizable)
        self.assertEqual(report.vectorizable_loops, 1)

    def test_non_vectorizable_loop_with_early_exit(self):
        """Test that loops with early exit are not vectorizable."""
        source = """
def non_vectorizable():
    for i in range(100):
        if i == 50:
            break
        result = i * 2
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        # Loop with break should not be vectorizable
        self.assertFalse(loop.is_vectorizable)

    def test_parallelizable_loop_detection(self):
        """Test detection of parallelizable loops."""
        source = """
def parallelizable_loop():
    for i in range(100):
        result = i * i + 2
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertTrue(loop.is_parallelizable)

    def test_non_parallelizable_accumulator(self):
        """Test that accumulator loops are not parallelizable."""
        source = """
def non_parallelizable():
    total = 0
    for i in range(100):
        total = total + i
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertFalse(loop.is_parallelizable)

    def test_loop_unrolling_optimization(self):
        """Test loop unrolling optimization for small loops."""
        source = """
def small_loop():
    for i in range(4):
        result = i * 2
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Should suggest loop unrolling
        unroll_opts = [opt for opt in report.optimizations
                      if opt.optimization_type == OptimizationType.LOOP_UNROLLING]
        self.assertGreater(len(unroll_opts), 0)

        unroll_opt = unroll_opts[0]
        self.assertGreater(unroll_opt.estimated_speedup, 1.0)
        self.assertGreater(unroll_opt.confidence, 0.0)

    def test_c_style_conversion_optimization(self):
        """Test C-style loop conversion optimization."""
        source = """
def c_style_candidate():
    for i in range(0, 10, 1):
        value = i + 5
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Should suggest C-style conversion
        c_style_opts = [opt for opt in report.optimizations
                       if opt.optimization_type == OptimizationType.C_STYLE_CONVERSION]
        self.assertGreater(len(c_style_opts), 0)

        c_style_opt = c_style_opts[0]
        self.assertIsNotNone(c_style_opt.transformed_code)
        self.assertIn("for (int", c_style_opt.transformed_code)

    def test_vectorization_prep_optimization(self):
        """Test vectorization preparation optimization."""
        source = """
def vectorization_candidate():
    for i in range(1000):
        result = i * 3 + 7
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Should suggest vectorization preparation
        vec_opts = [opt for opt in report.optimizations
                   if opt.optimization_type == OptimizationType.VECTORIZATION_PREP]
        self.assertGreater(len(vec_opts), 0)

    def test_complex_loop_pattern(self):
        """Test detection of complex loop patterns."""
        source = """
def complex_loop():
    for i in range(50):
        if i % 2 == 0:
            func1(i)
        else:
            func2(i)

        for j in range(i):
            func3(j)

        if i > 25:
            break

        result = complex_calculation(i)
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Find the outer loop (nesting_level 0)
        outer_loop = next(loop for loop in report.loops_found if loop.nesting_level == 0)

        self.assertEqual(outer_loop.pattern, LoopPattern.COMPLEX)
        self.assertGreater(outer_loop.body_complexity, 5)
        self.assertEqual(report.complex_loops, 1)

    def test_loop_complexity_estimation(self):
        """Test loop complexity estimation."""
        source = """
def complexity_test():
    # O(1) - small constant
    for i in range(5):
        pass

    # O(n) - larger range
    for i in range(1000):
        pass

    # O(n²) - nested loops
    for i in range(10):
        for j in range(10):
            pass
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        self.assertEqual(len(report.loops_found), 4)  # All loops (2 outer + 2 inner)

        # Check complexity estimations
        complexities = [loop.estimated_complexity for loop in report.loops_found]
        self.assertIn("O(1)", complexities)  # Small loop
        self.assertIn("O(n²)", complexities)  # Nested loop

    def test_variable_usage_analysis(self):
        """Test analysis of variable usage in loops."""
        source = """
def variable_usage():
    total = 0
    multiplier = 2
    for i in range(10):
        total = total + i * multiplier
        temp = i + 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        # Check variable classifications
        self.assertIn("i", loop.variables)
        self.assertTrue(loop.variables["i"].is_iterator)

        self.assertIn("total", loop.variables)
        self.assertTrue(loop.variables["total"].is_accumulator)

        self.assertIn("temp", loop.variables)
        self.assertTrue(loop.variables["temp"].is_modified)

    def test_performance_gain_estimation(self):
        """Test performance gain estimation."""
        source = """
def performance_test():
    for i in range(4):  # Small loop - unrollable
        result = i * 2
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        self.assertGreater(result.performance_gain_estimate, 1.0)
        self.assertLessEqual(result.performance_gain_estimate, 5.0)  # Capped maximum

    def test_safety_analysis(self):
        """Test safety analysis of loop optimizations."""
        source = """
def safe_loop():
    for i in range(10):
        result = i + 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        self.assertTrue(result.is_safe())

        safety = result.safety_analysis
        self.assertTrue(safety.get("all_optimizations_safe", False))

    def test_empty_function_no_loops(self):
        """Test analysis of function with no loops."""
        source = """
def no_loops():
    x = 5
    y = x + 10
    return y
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertEqual(report.total_loops, 0)
        self.assertEqual(len(report.optimizations), 0)
        self.assertEqual(result.performance_gain_estimate, 1.0)

    def test_while_condition_loop(self):
        """Test analysis of while loops with complex conditions."""
        source = """
def complex_while():
    x = 0
    y = 100
    while x < y and x > -10:
        x += 1
        y -= 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertEqual(loop.loop_type, LoopType.WHILE_CONDITION)

    def test_transformation_pattern_detection(self):
        """Test detection of transformation patterns."""
        source = """
def transformation_loop():
    for i in range(10):
        var1 = i * 2
        var2 = i + 5
        var3 = var1 + var2
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        self.assertEqual(loop.pattern, LoopPattern.TRANSFORMATION)

    def test_optimization_levels(self):
        """Test different optimization levels."""
        source = """
def test_levels():
    for i in range(8):
        result = i * 2
"""

        # Test basic level
        basic_analyzer = LoopAnalyzer(OptimizationLevel.BASIC)
        context = self._create_analysis_context(source)
        basic_result = basic_analyzer.optimize(context)

        self.assertTrue(basic_result.success)

        # Test aggressive level
        aggressive_analyzer = LoopAnalyzer(OptimizationLevel.AGGRESSIVE)
        aggressive_result = aggressive_analyzer.optimize(context)

        self.assertTrue(aggressive_result.success)

    def test_loop_with_function_calls(self):
        """Test analysis of loops with function calls."""
        source = """
def loop_with_calls():
    for i in range(20):
        result = process_item(i)
        log_result(result)
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        loop = report.loops_found[0]

        # Should detect side effects from function calls
        self.assertGreater(len(loop.side_effects), 0)

    def test_error_handling(self):
        """Test error handling with malformed input."""
        # Test with invalid AST
        invalid_context = Mock()
        invalid_context.ast_node = None
        invalid_context.source_code = ""

        result = self.analyzer.optimize(invalid_context)

        # Should handle gracefully
        self.assertFalse(result.success)
        self.assertIn("error", result.metadata)

    def test_transformations_reporting(self):
        """Test reporting of transformations performed."""
        source = """
def transformation_report():
    for i in range(5):  # Small unrollable loop
        result = i * 2

    for j in range(1000):  # Vectorizable loop
        value = j + 1
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        self.assertGreater(len(result.transformations), 0)

        # Check transformation descriptions
        transformations_text = " ".join(result.transformations)
        self.assertIn("loops", transformations_text)

    def test_optimization_candidate_properties(self):
        """Test properties of optimization candidates."""
        source = """
def optimization_properties():
    for i in range(6):
        result = i * 3
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        for opt in report.optimizations:
            self.assertIsInstance(opt, LoopOptimization)
            self.assertGreater(opt.confidence, 0.0)
            self.assertLessEqual(opt.confidence, 1.0)
            self.assertGreater(opt.estimated_speedup, 0.0)
            self.assertGreater(opt.applicability_score, 0.0)
            self.assertLessEqual(opt.applicability_score, 1.0)

    def test_multiple_optimization_types(self):
        """Test that multiple optimization types can be suggested."""
        source = """
def multiple_optimizations():
    for i in range(6):  # Small enough for unrolling, good for C-style
        result = i * 2 + 1  # Simple enough for vectorization prep
"""
        context = self._create_analysis_context(source)
        result = self.analyzer.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Should have multiple optimization types
        opt_types = {opt.optimization_type for opt in report.optimizations}
        self.assertGreater(len(opt_types), 1)


if __name__ == "__main__":
    unittest.main()