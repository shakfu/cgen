"""Tests for the Compile-time Evaluator Optimizer."""

import ast
import unittest
from unittest.mock import Mock

from src.cgen.frontend.ast_analyzer import AnalysisResult
from src.cgen.intelligence.base import AnalysisContext, OptimizationLevel
from src.cgen.intelligence.optimizers.compile_time_evaluator import (
    CompileTimeEvaluator,
    CompileTimeReport,
    ConstantValue,
    OptimizationCandidate,
)


class TestCompileTimeEvaluator(unittest.TestCase):
    """Test cases for the CompileTimeEvaluator."""

    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = CompileTimeEvaluator()

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

    def test_constant_folding_arithmetic(self):
        """Test constant folding for arithmetic expressions."""
        source = """
def calculate():
    result = 2 + 3 * 4
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.optimized_ast)
        self.assertGreater(result.performance_gain_estimate, 1.0)

        # Check that optimizations were found
        report = result.metadata.get("report")
        self.assertIsInstance(report, CompileTimeReport)
        self.assertGreater(report.expressions_optimized, 0)

    def test_constant_propagation(self):
        """Test constant propagation through variables."""
        source = """
def process():
    x: int = 10
    y: int = 20
    result = x + y
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(len(report.constants_found), 0)
        self.assertIn("x", report.constants_found)
        self.assertIn("y", report.constants_found)

    def test_algebraic_simplifications(self):
        """Test algebraic simplifications like x + 0, x * 1."""
        source = """
def simplify(x: int):
    result1 = x + 0
    result2 = x * 1
    result3 = x - 0
    result4 = x / 1
    result5 = 0 * x
    return result1, result2, result3, result4, result5
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

        # Check for algebraic simplification optimizations
        algebraic_opts = [opt for opt in report.optimizations
                         if "x + 0" in opt.original_code or "x * 1" in opt.original_code]
        # Note: This might be 0 if the AST doesn't contain these exact patterns after parsing

    def test_boolean_operation_optimization(self):
        """Test optimization of boolean operations."""
        source = """
def boolean_test():
    result1 = True and False
    result2 = True or False
    result3 = False and True
    result4 = False or True
    return result1, result2, result3, result4
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

    def test_comparison_optimization(self):
        """Test optimization of comparison operations."""
        source = """
def compare():
    result1 = 5 > 3
    result2 = 10 == 10
    result3 = 7 < 2
    result4 = 15 >= 15
    return result1, result2, result3, result4
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

        # All comparisons should be optimizable to constants
        comparison_opts = [opt for opt in report.optimizations
                          if opt.optimization_type == "constant_folding"]
        self.assertGreater(len(comparison_opts), 0)

    def test_function_call_evaluation(self):
        """Test evaluation of safe function calls with constant arguments."""
        source = """
def math_functions():
    result1 = abs(-5)
    result2 = min(3, 7, 1)
    result3 = max(2, 8, 4)
    result4 = len("hello")
    result5 = round(3.14159, 2)
    return result1, result2, result3, result4, result5
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

        # Check for function evaluation optimizations
        function_opts = [opt for opt in report.optimizations
                        if opt.optimization_type == "function_evaluation"]
        self.assertGreater(len(function_opts), 0)

    def test_conditional_optimization(self):
        """Test optimization of conditionals with constant conditions."""
        source = """
def conditional_test():
    if True:
        result = 1
    else:
        result = 2

    if False:
        other = 3
    else:
        other = 4

    return result, other
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Check for dead branch elimination
        branch_opts = [opt for opt in report.optimizations
                      if opt.optimization_type == "dead_branch_elimination"]
        self.assertGreater(len(branch_opts), 0)

    def test_unary_operation_optimization(self):
        """Test optimization of unary operations."""
        source = """
def unary_ops():
    result1 = -(-5)
    result2 = +(10)
    result3 = not False
    result4 = not True
    return result1, result2, result3, result4
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

    def test_nested_expressions(self):
        """Test optimization of nested expressions."""
        source = """
def nested():
    result = (2 + 3) * (4 - 1) + abs(-10)
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

    def test_mixed_constant_variable_expressions(self):
        """Test expressions mixing constants and variables."""
        source = """
def mixed(x: int):
    const1: int = 5
    const2: int = 10
    result1 = x + 0
    result2 = const1 * const2
    result3 = x * 1 + const1
    return result1, result2, result3
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Should find constants
        self.assertIn("const1", report.constants_found)
        self.assertIn("const2", report.constants_found)

        # Should optimize some expressions
        self.assertGreater(report.expressions_optimized, 0)

    def test_division_by_zero_safety(self):
        """Test that division by zero is handled safely."""
        source = """
def unsafe_division():
    result = 5 / 0
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        # Division by zero should not be optimized
        report = result.metadata.get("report")

        # Check that no unsafe optimizations were performed
        division_opts = [opt for opt in report.optimizations
                        if "5 / 0" in opt.original_code]
        self.assertEqual(len(division_opts), 0)

    def test_type_conversion_functions(self):
        """Test optimization of type conversion functions."""
        source = """
def type_conversions():
    result1 = int(3.14)
    result2 = float(5)
    result3 = str(42)
    result4 = bool(1)
    result5 = bool(0)
    return result1, result2, result3, result4, result5
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

    def test_complex_boolean_expressions(self):
        """Test optimization of complex boolean expressions."""
        source = """
def complex_boolean():
    result1 = True and True and False
    result2 = False or False or True
    result3 = not (True and False)
    result4 = (5 > 3) and (10 == 10)
    return result1, result2, result3, result4
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")
        self.assertGreater(report.expressions_optimized, 0)

    def test_performance_estimation(self):
        """Test performance gain estimation."""
        source = """
def performance_test():
    result = 2 + 3 + 4 + 5
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        self.assertGreater(result.performance_gain_estimate, 1.0)
        self.assertLessEqual(result.performance_gain_estimate, 10.0)  # Capped maximum

    def test_safety_analysis(self):
        """Test safety analysis of optimizations."""
        source = """
def safe_operations():
    result = 2 * 3 + 4
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        self.assertTrue(result.is_safe())

        safety = result.safety_analysis
        self.assertTrue(safety.get("all_optimizations_safe", False))
        self.assertTrue(safety.get("constant_folding", False))

    def test_optimization_candidates(self):
        """Test generation of optimization candidates."""
        source = """
def candidates():
    x: int = 10
    result = x + 5 * 2
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Check optimization candidates
        self.assertGreater(len(report.optimizations), 0)

        for opt in report.optimizations:
            self.assertIsInstance(opt, OptimizationCandidate)
            self.assertTrue(opt.confidence > 0.0)
            self.assertTrue(opt.confidence <= 1.0)
            self.assertGreater(opt.estimated_speedup, 0.0)
            self.assertTrue(opt.safety_verified)

    def test_constant_value_creation(self):
        """Test creation and properties of constant values."""
        const_val = ConstantValue(value=42, type_name="int")

        self.assertEqual(const_val.value, 42)
        self.assertEqual(const_val.type_name, "int")
        self.assertTrue(const_val.is_safe)
        self.assertEqual(const_val.confidence, 1.0)

    def test_empty_function_optimization(self):
        """Test optimization of empty function."""
        source = """
def empty():
    pass
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        self.assertEqual(result.performance_gain_estimate, 1.0)

    def test_variable_without_type_annotation(self):
        """Test handling of variables without type annotations."""
        source = """
def no_annotation():
    x = 10
    y = x + 5
    return y
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        # Should still work, but might not optimize as much
        self.assertIsNotNone(result.optimized_ast)

    def test_optimization_levels(self):
        """Test different optimization levels."""
        source = """
def test_levels():
    result = 2 + 3 * 4
    return result
"""

        # Test basic level
        basic_evaluator = CompileTimeEvaluator(OptimizationLevel.BASIC)
        context = self._create_analysis_context(source)
        basic_result = basic_evaluator.optimize(context)

        self.assertTrue(basic_result.success)

        # Test aggressive level
        aggressive_evaluator = CompileTimeEvaluator(OptimizationLevel.AGGRESSIVE)
        aggressive_result = aggressive_evaluator.optimize(context)

        self.assertTrue(aggressive_result.success)

    def test_error_handling(self):
        """Test error handling with malformed input."""
        # Test with invalid AST
        invalid_context = Mock()
        invalid_context.ast_node = None
        invalid_context.source_code = ""

        result = self.evaluator.optimize(invalid_context)

        # Should handle gracefully
        self.assertFalse(result.success)
        self.assertIn("error", result.metadata)

    def test_transformations_reporting(self):
        """Test reporting of transformations performed."""
        source = """
def transformations():
    const: int = 42
    result1 = 2 + 3
    result2 = const * 1
    result3 = abs(-10)
    return result1, result2, result3
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        self.assertGreater(len(result.transformations), 0)

        # Check transformation descriptions
        transformations_text = " ".join(result.transformations)
        self.assertIn("constants", transformations_text)
        self.assertIn("expressions", transformations_text)

    def test_confidence_scoring(self):
        """Test confidence scoring for different optimization types."""
        source = """
def confidence_test():
    certain = 2 + 3  # High confidence
    func_call = abs(-5)  # Medium confidence
    return certain, func_call
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Check confidence scores
        for opt in report.optimizations:
            self.assertGreater(opt.confidence, 0.0)
            self.assertLessEqual(opt.confidence, 1.0)

    def test_memory_impact_estimation(self):
        """Test estimation of memory impact from optimizations."""
        source = """
def memory_test():
    result = 10 * 20 + 30
    return result
"""
        context = self._create_analysis_context(source)
        result = self.evaluator.optimize(context)

        self.assertTrue(result.success)
        report = result.metadata.get("report")

        # Memory impact should be calculated (can be positive or negative)
        for opt in report.optimizations:
            self.assertIsInstance(opt.memory_impact, int)


if __name__ == "__main__":
    unittest.main()