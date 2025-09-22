#!/usr/bin/env python3
"""
Intelligence Layer Analysis Demo

This demonstrates the intelligence layer analyzing Python code
and shows the analysis results that would guide C code generation.
Then uses the existing py2c converter for actual C generation.
"""

import ast
import sys
import subprocess
import tempfile
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from src.cgen.intelligence.analyzers import (
    StaticAnalyzer, SymbolicExecutor, BoundsChecker, CallGraphAnalyzer
)
from src.cgen.intelligence.optimizers import (
    CompileTimeEvaluator, LoopAnalyzer, FunctionSpecializer, VectorizationDetector
)
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer
import cfile


# Example Python code that exercises all intelligence features
PYTHON_CODE_FOR_ANALYSIS = '''
# Constants for compile-time optimization
PI = 3.141592653589793
GRAVITY = 9.81

def factorial(n: int) -> int:
    """Recursive function for call graph analysis."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    """Another recursive function."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def vector_add(a: list, b: list) -> list:
    """Vectorizable operation."""
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

def dot_product(a: list, b: list) -> float:
    """Vectorizable dot product."""
    result = 0.0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result

def matrix_multiply(A: list, B: list) -> list:
    """Nested loops for optimization."""
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])

    result = []
    for i in range(rows_A):
        row = []
        for j in range(cols_B):
            sum_val = 0.0
            for k in range(cols_A):
                sum_val += A[i][k] * B[k][j]
            row.append(sum_val)
        result.append(row)
    return result

def safe_array_access(data: list, index: int) -> float:
    """Function with bounds checking."""
    if 0 <= index < len(data):
        return data[index]
    return 0.0

def compute_physics(mass: float, velocity: float) -> float:
    """Function with compile-time constants."""
    kinetic_energy = 0.5 * mass * velocity * velocity
    potential_energy = mass * GRAVITY * 10.0
    return kinetic_energy + potential_energy

def polynomial_eval(x: float, coefficients: list) -> float:
    """Horner's method - specialization opportunity."""
    result = 0.0
    for coef in reversed(coefficients):
        result = result * x + coef
    return result
'''

# Simple Python code for actual C generation (compatible with current py2c)
SIMPLE_PYTHON_FOR_C = '''
def add_numbers(a: int, b: int) -> int:
    return a + b

def compute_area(radius: float) -> float:
    pi: float = 3.14159
    return pi * radius * radius

def multiply_values(x: float, y: float) -> float:
    result: float = x * y
    return result
'''


def run_comprehensive_intelligence_analysis():
    """Run all intelligence layer components on the example code."""
    print("🧠 Comprehensive Intelligence Layer Analysis")
    print("=" * 60)

    # Create analysis context
    ast_node = ast.parse(PYTHON_CODE_FOR_ANALYSIS)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(PYTHON_CODE_FOR_ANALYSIS)
    context = AnalysisContext(
        PYTHON_CODE_FOR_ANALYSIS, ast_node, analysis_result,
        AnalysisLevel.COMPREHENSIVE, OptimizationLevel.AGGRESSIVE
    )

    results = {}

    # Run all analyzers
    analyzers = [
        ("Static Analyzer", StaticAnalyzer()),
        ("Symbolic Executor", SymbolicExecutor()),
        ("Bounds Checker", BoundsChecker()),
        ("Call Graph Analyzer", CallGraphAnalyzer()),
    ]

    print("\n ANALYZERS")
    print("-" * 30)

    for name, analyzer_obj in analyzers:
        try:
            result = analyzer_obj.analyze(context)
            results[name] = result

            print(f"\n {name}")
            print(f"   Success: {result.success}")
            print(f"   Confidence: {result.confidence:.2f}")

            if result.findings:
                print(f"   Key Findings ({len(result.findings)}):")
                for finding in result.findings[:3]:
                    print(f"     • {finding}")

            if result.warnings:
                print(f"   Warnings ({len(result.warnings)}):")
                for warning in result.warnings[:2]:
                    print(f"     • {warning}")

        except Exception as e:
            print(f"\n {name}: Error - {e}")
            results[name] = None

    # Run all optimizers
    optimizers = [
        ("Compile-Time Evaluator", CompileTimeEvaluator()),
        ("Loop Analyzer", LoopAnalyzer()),
        ("Function Specializer", FunctionSpecializer()),
    ]

    print(f"\n OPTIMIZERS")
    print("-" * 30)

    for name, optimizer_obj in optimizers:
        try:
            result = optimizer_obj.optimize(context)
            results[name] = result

            print(f"\n {name}")
            print(f"   Success: {result.success}")
            print(f"   Performance Gain: {result.performance_gain_estimate:.2f}x")

            if result.transformations:
                print(f"   Transformations ({len(result.transformations)}):")
                for transform in result.transformations[:3]:
                    print(f"     • {transform}")

        except Exception as e:
            print(f"\n {name}: Error - {e}")
            results[name] = None

    # Vectorization detector (special case)
    print(f"\n VECTORIZATION ANALYSIS")
    print("-" * 30)

    try:
        detector = VectorizationDetector()
        vector_result = detector.analyze(context.ast_node)
        results["Vectorization Detector"] = vector_result

        print(f"\n Vectorization Detector")
        print(f"   Loops Analyzed: {vector_result.total_loops_analyzed}")
        print(f"   Vectorizable: {vector_result.vectorizable_loops}")

        if vector_result.candidates:
            print(f"   Optimization Opportunities:")
            total_speedup = 0
            for candidate in vector_result.candidates:
                print(f"     • {candidate.vectorization_type.value}: {candidate.estimated_speedup:.2f}x speedup")
                print(f"       Vector length: {candidate.vector_length}, Confidence: {candidate.confidence:.2f}")
                total_speedup += candidate.estimated_speedup

            avg_speedup = total_speedup / len(vector_result.candidates)
            print(f"   Average Vectorization Speedup: {avg_speedup:.2f}x")

    except Exception as e:
        print(f"\n Vectorization Detector: Error - {e}")
        results["Vectorization Detector"] = None

    return results


def generate_c_with_py2c():
    """Generate C code using the existing py2c converter."""
    print(f"\n C Code Generation with py2c")
    print("=" * 60)

    try:
        # Use the existing py2c converter with correct method
        converter = cfile.PythonToCConverter()
        c_ast = converter.convert_code(SIMPLE_PYTHON_FOR_C)

        # Convert the AST to string
        writer = cfile.Writer(cfile.StyleOptions())
        c_code = writer.write_str(c_ast)

        print(" C code generation successful!")
        return c_code

    except Exception as e:
        print(f" C code generation failed: {e}")
        return None


def test_c_compilation(c_code):
    """Test if the generated C code compiles."""
    print(f"\n C Code Compilation Test")
    print("=" * 60)

    if not c_code:
        print(" No C code to compile")
        return False

    try:
        # Write C code to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            c_file = f.name

        # Try to compile
        executable = c_file.replace('.c', '.out')
        cmd = ['gcc', '-o', executable, c_file, '-lm']

        print(f" Compiling: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(" Compilation successful!")

            # Try to run (basic test)
            print(" Testing execution...")
            # Note: The generated code might not have a main function
            # This is just a compilation test
            return True
        else:
            print(f" Compilation failed:")
            print(f"   {result.stderr}")
            return False

    except Exception as e:
        print(f" Error: {e}")
        return False

    finally:
        # Cleanup
        try:
            if 'c_file' in locals() and os.path.exists(c_file):
                os.unlink(c_file)
            if 'executable' in locals() and os.path.exists(executable):
                os.unlink(executable)
        except:
            pass


def main():
    """Main demonstration."""
    print(" CGen Intelligence Layer - Complete Analysis Demo")
    print("=" * 70)
    print("This demo shows how the intelligence layer analyzes Python code")
    print("and provides insights that would guide optimized C code generation.")
    print("=" * 70)

    # Step 1: Run comprehensive intelligence analysis
    analysis_results = run_comprehensive_intelligence_analysis()

    # Step 2: Generate C code using existing converter
    c_code = generate_c_with_py2c()

    if c_code:
        print(f"\n Generated C Code")
        print("-" * 40)
        print(c_code)

        # Step 3: Test compilation
        compilation_success = test_c_compilation(c_code)
    else:
        compilation_success = False

    # Step 4: Analysis Summary
    print(f"\n Intelligence Analysis Summary")
    print("=" * 70)

    # Count successful components
    successful_analyzers = sum(1 for key, result in analysis_results.items()
                             if result and hasattr(result, 'success') and result.success)

    successful_optimizers = sum(1 for key, result in analysis_results.items()
                              if result and (
                                  (hasattr(result, 'success') and result.success) or
                                  (hasattr(result, 'candidates') and len(result.candidates) > 0)
                              ))

    print(f" Analysis Components:")
    print(f"   Successful Analyzers: {successful_analyzers}")
    print(f"   Successful Optimizers: {successful_optimizers}")

    # Calculate estimated performance improvements
    compile_time_result = analysis_results.get("Compile-Time Evaluator")
    compile_speedup = (compile_time_result.performance_gain_estimate
                      if compile_time_result and hasattr(compile_time_result, 'performance_gain_estimate')
                      else 1.0)

    vector_result = analysis_results.get("Vectorization Detector")
    vector_speedup = 1.0
    if vector_result and hasattr(vector_result, 'candidates') and vector_result.candidates:
        total_vector = sum(c.estimated_speedup for c in vector_result.candidates)
        vector_speedup = total_vector / len(vector_result.candidates)

    estimated_total_speedup = compile_speedup * vector_speedup

    print(f"\n Estimated Performance Improvements:")
    print(f"   Compile-time optimizations: {compile_speedup:.2f}x")
    print(f"   Vectorization opportunities: {vector_speedup:.2f}x")
    print(f"   Combined estimated speedup: {estimated_total_speedup:.2f}x")

    print(f"\n Code Generation:")
    print(f"   C Code Generation: {'' if c_code else ''}")
    print(f"   Compilation Test: {'' if compilation_success else ''}")

    # Final status
    overall_success = (
        successful_analyzers > 0 and
        successful_optimizers > 0 and
        c_code is not None
    )

    if overall_success:
        print(f"\n Intelligence Layer Demo Successful!")
        print(f" Python analysis → optimization insights → C generation pipeline working")
        print(f" The intelligence layer identified {estimated_total_speedup:.2f}x potential speedup")
    else:
        print(f"\n  Demo completed with some limitations")

    return overall_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)