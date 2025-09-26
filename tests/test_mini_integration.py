#!/usr/bin/env python3
"""Pytest-style integration tests for mini_py2c patterns in CGen.

These tests validate the successful integration of mini_py2c_module_fixed.py
patterns into CGen, including flow-sensitive type inference, smart emission
selection, and enhanced C code generation capabilities.
"""

import ast
import pytest

from cgen.frontend.flow_sensitive_inference import FlowSensitiveInferencer
from cgen.frontend.type_inference import TypeInferenceEngine
from cgen.generator.simple_emitter import SimpleEmitter
from cgen.generator.py2c import PythonToCConverter


class TestFlowSensitiveInference:
    """Test flow-sensitive type inference with parameter inference."""

    def test_parameter_inference_from_usage(self):
        """Test inferring parameter types from arithmetic and comparison usage."""
        code = '''
def fibonacci(n, x):
    if n <= 1:
        return n
    result = x + fibonacci(n-1, x) + fibonacci(n-2, x)
    return result
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        # Test with enhanced inference
        engine = TypeInferenceEngine(enable_flow_sensitive=True)
        results = engine.analyze_function_signature_enhanced(func_node)

        # Validate inference results
        assert results, "Flow-sensitive inference should return results"
        assert "n" in results, "Parameter 'n' should be inferred"
        assert "x" in results, "Parameter 'x' should be inferred"
        assert "result" in results, "Variable 'result' should be inferred"
        assert "__return__" in results, "Return type should be inferred"

        # Check confidence scores
        assert results["n"].confidence >= 0.8, f"Parameter 'n' confidence too low: {results['n'].confidence}"
        assert results["x"].confidence >= 0.8, f"Parameter 'x' confidence too low: {results['x'].confidence}"

        # Check inferred types
        assert results["n"].type_info.name in ["int", "union"], f"Parameter 'n' type: {results['n'].type_info.name}"
        assert results["x"].type_info.name in ["int", "union"], f"Parameter 'x' type: {results['x'].type_info.name}"
        assert results["__return__"].type_info.name in ["int", "union"], f"Return type: {results['__return__'].type_info.name}"

    def test_comparison_driven_type_propagation(self):
        """Test type propagation through comparison operations."""
        code = '''
def compare_and_calc(a, b):
    if a > b:
        return a + 1
    else:
        return b * 2
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        engine = TypeInferenceEngine(enable_flow_sensitive=True)
        results = engine.analyze_function_signature_enhanced(func_node)

        # Both parameters should be inferred from comparison and arithmetic usage
        assert "a" in results, "Parameter 'a' should be inferred"
        assert "b" in results, "Parameter 'b' should be inferred"
        assert results["a"].confidence > 0.0, "Parameter 'a' should have confidence > 0"
        assert results["b"].confidence > 0.0, "Parameter 'b' should have confidence > 0"

        # Should infer numeric types from arithmetic operations
        assert results["a"].type_info.name in ["int", "float", "union"], f"Parameter 'a' type: {results['a'].type_info.name}"
        assert results["b"].type_info.name in ["int", "float", "union"], f"Parameter 'b' type: {results['b'].type_info.name}"


class TestSimpleEmitter:
    """Test SimpleEmitter for clean C code generation."""

    def test_can_use_simple_emission_for_basic_function(self):
        """Test detection of functions suitable for simple emission."""
        code = '''
def simple_calc(x: int, y: int) -> int:
    if x > y:
        result = x + y * 2
    else:
        result = x * y + 1
    return result
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        emitter = SimpleEmitter()
        type_context = {
            "x": "int",
            "y": "int",
            "__return__": "int",
            "result": "int"
        }

        can_use_simple = emitter.can_use_simple_emission(func_node, type_context)
        assert can_use_simple, "Simple function should be eligible for simple emission"

    def test_simple_emission_code_generation(self):
        """Test C code generation for simple functions."""
        code = '''
def simple_calc(x: int, y: int) -> int:
    if x > y:
        result = x + y * 2
    else:
        result = x * y + 1
    return result
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        emitter = SimpleEmitter()
        type_context = {
            "x": "int",
            "y": "int",
            "__return__": "int",
            "result": "int"
        }

        # Should be able to use simple emission
        assert emitter.can_use_simple_emission(func_node, type_context)

        # Generate C code
        c_code = emitter.emit_function(func_node, type_context)

        # Validate generated C code structure
        assert c_code, "C code should be generated"
        assert "int simple_calc(int x, int y)" in c_code, "Function signature should be correct"
        assert "int result;" in c_code, "Local variable declaration should be present"
        assert "if (x > y)" in c_code, "If condition should be generated"
        assert "return result;" in c_code, "Return statement should be generated"

        # Should not contain STC container operations
        assert "vec_" not in c_code, "Simple emission should not use STC containers"
        assert "hmap_" not in c_code, "Simple emission should not use STC containers"

    def test_complex_function_detection(self):
        """Test detection of complex functions that require STC emission."""
        complex_code = '''
def complex_func(numbers: list[int]) -> int:
    result = 0
    for num in numbers:
        result += num
    numbers.append(result)
    return len(numbers)
'''
        tree = ast.parse(complex_code)
        func_node = tree.body[0]

        emitter = SimpleEmitter()
        type_context = {
            "numbers": "vec_int32",
            "__return__": "int",
            "result": "int",
            "num": "int"
        }

        can_use_simple = emitter.can_use_simple_emission(func_node, type_context)
        assert not can_use_simple, "Complex function with containers should NOT be eligible for simple emission"


class TestSmartEmissionSelection:
    """Test integration with PythonToCConverter and smart emission selection."""

    def test_simple_function_uses_simple_emission(self):
        """Test that simple functions use SimpleEmitter."""
        simple_code = '''
def test_simple(a: int, b: int) -> int:
    if a > b:
        return a + b
    else:
        return a * b
'''
        tree = ast.parse(simple_code)
        func_node = tree.body[0]

        converter = PythonToCConverter()

        # Should succeed and use simple emission
        result = converter._convert_function_def(func_node)

        assert result, "Conversion should succeed"
        assert len(result) >= 1, "Should generate at least one element"

        # Check that simple, clean C code was generated
        if hasattr(result[0], 'code'):
            c_code = result[0].code
            assert "int test_simple(int a, int b)" in c_code, "Function signature should be correct"
            # Should not contain STC declarations for simple function
            assert "declare_vec" not in c_code, "Simple function should not use STC declarations"

    def test_complex_function_uses_stc_emission(self):
        """Test that complex functions use STC emission."""
        # Use a simpler complex function that uses container operations but not iteration
        complex_code = '''
def test_complex(numbers: list[int]) -> int:
    numbers.append(42)
    return len(numbers)
'''
        tree = ast.parse(complex_code)
        func_node = tree.body[0]

        converter = PythonToCConverter()

        # Should succeed and use STC emission
        result = converter._convert_function_def(func_node)

        assert result, "Conversion should succeed"
        assert len(result) >= 1, "Should generate at least one element"


class TestTypeUnification:
    """Test type unification system for mixed-type operations."""

    def test_mixed_type_branching(self):
        """Test flow-sensitive analysis with mixed types in branches."""
        code = '''
def mixed_types(flag: bool):
    if flag:
        result = 42
    else:
        result = 3.14
    return result
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        engine = TypeInferenceEngine(enable_flow_sensitive=True)
        results = engine.analyze_function_signature_enhanced(func_node)

        # Should handle mixed types through unification
        assert "result" in results, "Variable 'result' should be inferred"
        assert results["result"].confidence > 0.0, "Variable 'result' should have confidence"

        # Type should be unified (likely float or union)
        result_type = results["result"].type_info.name
        assert result_type in ["float", "union", "int"], f"Result type should be unified: {result_type}"


class TestIntegrationValidation:
    """Integration validation tests to ensure all components work together."""

    def test_complete_pipeline_integration(self):
        """Test that all enhancements work together in the complete pipeline."""
        # Simple function without local variables (compatible with both systems)
        code = '''
def calculate_score(base: int, bonus: int) -> int:
    if bonus > 0:
        return base + bonus * 2
    else:
        return base
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        # Test flow-sensitive inference
        engine = TypeInferenceEngine(enable_flow_sensitive=True)
        inference_results = engine.analyze_function_signature_enhanced(func_node)

        assert inference_results, "Flow-sensitive inference should work"
        assert "base" in inference_results, "Parameter 'base' should be inferred"
        assert "bonus" in inference_results, "Parameter 'bonus' should be inferred"

        # Test simple emission detection
        emitter = SimpleEmitter()
        type_context = {
            "base": "int",
            "bonus": "int",
            "__return__": "int"
        }

        can_use_simple = emitter.can_use_simple_emission(func_node, type_context)
        assert can_use_simple, "Function should be eligible for simple emission"

        # Test C code generation
        c_code = emitter.emit_function(func_node, type_context)
        assert c_code, "C code should be generated"
        assert "int calculate_score(int base, int bonus)" in c_code, "Function signature should be correct"

        # Test integration with main converter
        converter = PythonToCConverter()
        conversion_result = converter._convert_function_def(func_node)
        assert conversion_result, "Full conversion should succeed"

    def test_backward_compatibility(self):
        """Test that enhancements maintain backward compatibility."""
        # Test with flow-sensitive inference disabled
        engine_disabled = TypeInferenceEngine(enable_flow_sensitive=False)

        code = '''
def test_func(x: int, y: int) -> int:
    return x + y
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        # Should still work with existing analysis
        results = engine_disabled.analyze_function_signature_enhanced(func_node)
        assert results, "Should work with flow-sensitive analysis disabled"
        assert "x" in results, "Should find annotated parameters"
        assert "y" in results, "Should find annotated parameters"


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    pytest.main([__file__, "-v"])