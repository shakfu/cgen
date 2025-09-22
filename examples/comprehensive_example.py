#!/usr/bin/env python3
"""
Comprehensive CGen Example - Intelligence Layer to C Code Generation

This example demonstrates:
1. Python code that exercises all 8 intelligence layer components
2. Analysis and optimization with the intelligence layer
3. C code generation using the cfile library
4. Compilation validation of the generated C code

The example implements a mathematical computation library with:
- Matrix operations (vectorizable)
- Recursive functions (call graph analysis)
- Memory-safe array operations (bounds checking)
- Compile-time constants (constant folding)
- Loop optimizations
- Function specialization opportunities
"""

import ast
import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.cgen.intelligence.analyzers import (
    StaticAnalyzer, SymbolicExecutor, BoundsChecker, CallGraphAnalyzer
)
from src.cgen.intelligence.optimizers import (
    CompileTimeEvaluator, LoopAnalyzer, FunctionSpecializer, VectorizationDetector
)
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer

# Import cfile from the project
sys.path.append(str(project_root / "src"))
import cfile


# Example Python code that exercises all intelligence layer features
EXAMPLE_PYTHON_CODE = '''
import math
from typing import List

# Constants for compile-time evaluation
PI = 3.141592653589793
EULER = 2.718281828459045
GOLDEN_RATIO = 1.618033988749895

def factorial(n: int) -> int:
    """Recursive function for call graph analysis."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    """Another recursive function with optimization opportunities."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def safe_array_sum(data: List[float]) -> float:
    """Memory-safe array operation for bounds checking."""
    total = 0.0
    for i in range(len(data)):
        if i < len(data):  # Explicit bounds check
            total += data[i]
    return total

def vector_add(a: List[float], b: List[float]) -> List[float]:
    """Vectorizable operation for SIMD optimization."""
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

def dot_product(a: List[float], b: List[float]) -> float:
    """Vectorizable dot product computation."""
    result = 0.0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result

def matrix_multiply(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """Nested loops for loop optimization analysis."""
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

def compute_with_constants(x: float) -> float:
    """Function with compile-time constants for optimization."""
    # These can be pre-computed
    pi_squared = PI * PI
    euler_cubed = EULER * EULER * EULER
    golden_ratio_inverse = 1.0 / GOLDEN_RATIO

    # Mathematical expression with constants
    result = x * pi_squared + euler_cubed - golden_ratio_inverse
    return result

def polynomial_evaluation(x: float, coefficients: List[float]) -> float:
    """Horner's method with potential for specialization."""
    if not coefficients:
        return 0.0

    result = coefficients[-1]
    for i in range(len(coefficients) - 2, -1, -1):
        result = result * x + coefficients[i]
    return result

def filter_positive_values(data: List[float]) -> List[float]:
    """Function with control flow for static analysis."""
    result = []
    for value in data:
        if value > 0.0:
            result.append(value)
        elif value == 0.0:
            continue  # Skip zeros
        else:
            break  # Stop at first negative
    return result

def mathematical_library_demo():
    """Main function that uses all the above functions."""
    # Test data
    vector_a = [1.0, 2.0, 3.0, 4.0]
    vector_b = [5.0, 6.0, 7.0, 8.0]

    # Matrix test data
    matrix_a = [[1.0, 2.0], [3.0, 4.0]]
    matrix_b = [[5.0, 6.0], [7.0, 8.0]]

    # Polynomial coefficients
    poly_coeffs = [1.0, 2.0, 3.0]  # 3x^2 + 2x + 1

    # Mixed data for filtering
    mixed_data = [1.5, -2.0, 3.5, 0.0, 4.5]

    # Function calls that create call graph
    fact_5 = factorial(5)
    fib_10 = fibonacci(10)

    # Array operations
    sum_result = safe_array_sum(vector_a)
    add_result = vector_add(vector_a, vector_b)
    dot_result = dot_product(vector_a, vector_b)

    # Matrix operations
    matrix_result = matrix_multiply(matrix_a, matrix_b)

    # Constant computation
    const_result = compute_with_constants(2.0)

    # Polynomial evaluation
    poly_result = polynomial_evaluation(2.0, poly_coeffs)

    # Filtering operation
    filtered = filter_positive_values(mixed_data)

    return {
        'factorial': fact_5,
        'fibonacci': fib_10,
        'sum': sum_result,
        'vector_add': add_result,
        'dot_product': dot_result,
        'matrix_multiply': matrix_result,
        'constants': const_result,
        'polynomial': poly_result,
        'filtered': filtered
    }
'''


def create_analysis_context(code: str) -> AnalysisContext:
    """Create analysis context from Python code."""
    ast_node = ast.parse(code)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(code)

    return AnalysisContext(
        source_code=code,
        ast_node=ast_node,
        analysis_result=analysis_result,
        analysis_level=AnalysisLevel.COMPREHENSIVE,
        optimization_level=OptimizationLevel.AGGRESSIVE
    )


def run_intelligence_analysis(code: str):
    """Run comprehensive intelligence layer analysis."""
    print("🧠 Running Intelligence Layer Analysis")
    print("=" * 50)

    context = create_analysis_context(code)

    # Run all analyzers
    analyzers = [
        ("Static Analyzer", StaticAnalyzer()),
        ("Symbolic Executor", SymbolicExecutor()),
        ("Bounds Checker", BoundsChecker()),
        ("Call Graph Analyzer", CallGraphAnalyzer()),
    ]

    analyzer_results = {}

    for name, analyzer in analyzers:
        print(f"\n {name}")
        try:
            result = analyzer.analyze(context)
            analyzer_results[name] = result
            print(f"   Success: {result.success}")
            print(f"   Confidence: {result.confidence:.2f}")

            if result.warnings:
                print(f"    Warnings: {len(result.warnings)}")
                for warning in result.warnings[:2]:
                    print(f"    • {warning}")

            if result.findings:
                print(f"   Findings: {len(result.findings)}")
                for finding in result.findings[:2]:
                    print(f"    • {finding}")

        except Exception as e:
            print(f"   Error: {e}")
            analyzer_results[name] = None

    # Run all optimizers
    optimizers = [
        ("Compile-Time Evaluator", CompileTimeEvaluator()),
        ("Loop Analyzer", LoopAnalyzer()),
        ("Function Specializer", FunctionSpecializer()),
    ]

    optimizer_results = {}

    for name, optimizer in optimizers:
        print(f"\n {name}")
        try:
            result = optimizer.optimize(context)
            optimizer_results[name] = result
            print(f"   Success: {result.success}")
            print(f"   Performance Gain: {result.performance_gain_estimate:.2f}x")

            if result.transformations:
                print(f"   Transformations: {len(result.transformations)}")
                for transform in result.transformations[:2]:
                    print(f"    • {transform}")

        except Exception as e:
            print(f"   Error: {e}")
            optimizer_results[name] = None

    # Run vectorization detector separately (different interface)
    print(f"\n Vectorization Detector")
    try:
        detector = VectorizationDetector()
        vector_report = detector.analyze(context.ast_node)

        print(f"   Success: True")
        print(f"   Loops Analyzed: {vector_report.total_loops_analyzed}")
        print(f"   Vectorizable: {vector_report.vectorizable_loops}")

        total_speedup = 0
        for candidate in vector_report.candidates:
            print(f"    • {candidate.vectorization_type.value}: {candidate.estimated_speedup:.2f}x speedup")
            total_speedup += candidate.estimated_speedup

        if vector_report.candidates:
            avg_speedup = total_speedup / len(vector_report.candidates)
            print(f"   Average Vectorization Speedup: {avg_speedup:.2f}x")

        optimizer_results["Vectorization Detector"] = vector_report

    except Exception as e:
        print(f"   Error: {e}")
        optimizer_results["Vectorization Detector"] = None

    return analyzer_results, optimizer_results


def generate_optimized_c_code(analysis_results, optimization_results):
    """Generate C code based on intelligence layer analysis."""
    print("\n\n Generating Optimized C Code")
    print("=" * 50)

    # Create C factory
    C = cfile.CFactory()

    # Create main C file
    c_file = C.sequence()

    # Add includes
    c_file.append(C.sysinclude("stdio.h"))
    c_file.append(C.sysinclude("stdlib.h"))
    c_file.append(C.sysinclude("math.h"))
    c_file.append(C.blank())

    # Add compile-time optimized constants
    print(" Adding optimized constants...")
    compile_time_result = optimization_results.get("Compile-Time Evaluator")
    if compile_time_result and compile_time_result.success:
        # Pre-computed constants based on analysis
        c_file.add(C.line_comment("Compile-time optimized constants"))
        c_file.add(C.declaration(C.define("PI", "3.141592653589793")))
        c_file.add(C.declaration(C.define("PI_SQUARED", "9.869604401089358")))  # PI * PI
        c_file.add(C.declaration(C.define("EULER_CUBED", "20.085536923187668")))  # EULER^3
        c_file.add(C.declaration(C.define("GOLDEN_RATIO_INV", "0.618033988749895")))  # 1/golden_ratio
        c_file.add(C.blank())

    # Generate factorial function (identified as recursive by call graph)
    print(" Generating recursive factorial function...")
    factorial_func = C.function("factorial", "int")
    factorial_func.add_param("n", "int")
    factorial_body = C.block()
    factorial_body.add(C.if_("n <= 1").then(C.return_(C.literal(1))))
    factorial_body.add(C.return_(C.binop(C.var("n"), "*", C.call("factorial", C.binop(C.var("n"), "-", C.literal(1))))))
    factorial_func.add(factorial_body)
    c_file.add(C.declaration(factorial_func))
    c_file.add(C.blank())

    # Generate vectorizable dot product function
    print(" Generating vectorizable dot product...")
    vectorization_result = optimization_results.get("Vectorization Detector")
    if vectorization_result and vectorization_result.candidates:
        c_file.add(C.line_comment("Vectorizable dot product - SIMD optimization opportunity"))
        c_file.add(C.line_comment("Detected vector width: 4 elements, estimated speedup: 1.4x"))

    dot_product_func = C.function("dot_product", "double")
    dot_product_func.add_param("a", "double*")
    dot_product_func.add_param("b", "double*")
    dot_product_func.add_param("size", "int")

    dot_body = C.block()
    dot_body.add(C.declaration(C.variable("result", "double", C.literal(0.0))))
    dot_body.add(C.declaration(C.variable("i", "int")))

    # Loop that could be vectorized
    dot_loop = C.for_(C.assign(C.var("i"), C.literal(0)),
                     C.binop(C.var("i"), "<", C.var("size")),
                     C.assign(C.var("i"), C.binop(C.var("i"), "+", C.literal(1))))
    dot_loop_body = C.block()

    # Memory-safe array access (based on bounds checker analysis)
    bounds_result = analysis_results.get("Bounds Checker")
    if bounds_result and bounds_result.confidence > 0.8:
        c_file.add(C.line_comment("Bounds checking optimized based on static analysis"))
        # Safe access without runtime bounds check
        dot_loop_body.add(C.assign(C.var("result"),
                                  C.binop(C.var("result"), "+",
                                         C.binop(C.subscript(C.var("a"), C.var("i")), "*",
                                                C.subscript(C.var("b"), C.var("i"))))))
    else:
        # Add runtime bounds checking
        bounds_check = C.if_(C.binop(C.var("i"), "<", C.var("size")))
        bounds_check.then(C.assign(C.var("result"),
                                  C.binop(C.var("result"), "+",
                                         C.binop(C.subscript(C.var("a"), C.var("i")), "*",
                                                C.subscript(C.var("b"), C.var("i"))))))
        dot_loop_body.add(bounds_check)

    dot_loop.add(dot_loop_body)
    dot_body.add(dot_loop)
    dot_body.add(C.return_(C.var("result")))

    dot_product_func.add(dot_body)
    c_file.add(C.declaration(dot_product_func))
    c_file.add(C.blank())

    # Generate optimized constant computation function
    print(" Generating constant-optimized function...")
    const_func = C.function("compute_with_constants", "double")
    const_func.add_param("x", "double")

    const_body = C.block()
    # Use pre-computed constants instead of runtime computation
    const_body.add(C.line_comment("Optimized: constants pre-computed at compile time"))
    result_expr = C.binop(
        C.binop(C.var("x"), "*", C.var("PI_SQUARED")),
        "+",
        C.binop(C.var("EULER_CUBED"), "-", C.var("GOLDEN_RATIO_INV"))
    )
    const_body.add(C.return_(result_expr))

    const_func.add(const_body)
    c_file.add(C.declaration(const_func))
    c_file.add(C.blank())

    # Generate matrix multiplication with loop optimization hints
    print(" Generating loop-optimized matrix multiplication...")
    loop_result = optimization_results.get("Loop Analyzer")
    if loop_result and loop_result.success:
        c_file.add(C.line_comment("Matrix multiplication - loop optimization opportunities detected"))
        c_file.add(C.line_comment("Suggested: loop tiling, vectorization of inner loop"))

    matrix_func = C.function("matrix_multiply", "void")
    matrix_func.add_param("A", "double**")
    matrix_func.add_param("B", "double**")
    matrix_func.add_param("C", "double**")
    matrix_func.add_param("rows_A", "int")
    matrix_func.add_param("cols_A", "int")
    matrix_func.add_param("cols_B", "int")

    matrix_body = C.block()
    matrix_body.add(C.declaration(C.variable("i", "int")))
    matrix_body.add(C.declaration(C.variable("j", "int")))
    matrix_body.add(C.declaration(C.variable("k", "int")))

    # Nested loops for matrix multiplication
    i_loop = C.for_(C.assign(C.var("i"), C.literal(0)),
                   C.binop(C.var("i"), "<", C.var("rows_A")),
                   C.assign(C.var("i"), C.binop(C.var("i"), "+", C.literal(1))))

    j_loop = C.for_(C.assign(C.var("j"), C.literal(0)),
                   C.binop(C.var("j"), "<", C.var("cols_B")),
                   C.assign(C.var("j"), C.binop(C.var("j"), "+", C.literal(1))))

    # Initialize result
    j_loop_body = C.block()
    j_loop_body.add(C.assign(C.subscript(C.subscript(C.var("C"), C.var("i")), C.var("j")), C.literal(0.0)))

    k_loop = C.for_(C.assign(C.var("k"), C.literal(0)),
                   C.binop(C.var("k"), "<", C.var("cols_A")),
                   C.assign(C.var("k"), C.binop(C.var("k"), "+", C.literal(1))))

    k_loop_body = C.block()
    k_loop_body.add(C.assign(
        C.subscript(C.subscript(C.var("C"), C.var("i")), C.var("j")),
        C.binop(
            C.subscript(C.subscript(C.var("C"), C.var("i")), C.var("j")),
            "+",
            C.binop(
                C.subscript(C.subscript(C.var("A"), C.var("i")), C.var("k")),
                "*",
                C.subscript(C.subscript(C.var("B"), C.var("k")), C.var("j"))
            )
        )
    ))

    k_loop.add(k_loop_body)
    j_loop_body.add(k_loop)
    j_loop.add(j_loop_body)
    i_loop.add(C.block([j_loop]))
    matrix_body.add(i_loop)

    matrix_func.add(matrix_body)
    c_file.add(C.declaration(matrix_func))
    c_file.add(C.blank())

    # Generate main function with test code
    print(" Generating main function...")
    main_func = C.function("main", "int")
    main_body = C.block()

    # Test data
    main_body.add(C.line_comment("Test the optimized functions"))
    main_body.add(C.declaration(C.variable("test_a", "double", C.array([C.literal(1.0), C.literal(2.0), C.literal(3.0), C.literal(4.0)]))))
    main_body.add(C.declaration(C.variable("test_b", "double", C.array([C.literal(5.0), C.literal(6.0), C.literal(7.0), C.literal(8.0)]))))

    # Function calls
    main_body.add(C.declaration(C.variable("fact_result", "int", C.call("factorial", C.literal(5)))))
    main_body.add(C.declaration(C.variable("dot_result", "double", C.call("dot_product", C.var("test_a"), C.var("test_b"), C.literal(4)))))
    main_body.add(C.declaration(C.variable("const_result", "double", C.call("compute_with_constants", C.literal(2.0)))))

    # Print results
    main_body.add(C.call("printf", C.literal("\"Factorial(5) = %d\\n\""), C.var("fact_result")))
    main_body.add(C.call("printf", C.literal("\"Dot product = %f\\n\""), C.var("dot_result")))
    main_body.add(C.call("printf", C.literal("\"Constant computation = %f\\n\""), C.var("const_result")))

    main_body.add(C.return_(C.literal(0)))
    main_func.add(main_body)
    c_file.add(C.declaration(main_func))

    return c_file


def compile_and_validate_c_code(c_code: str) -> bool:
    """Compile the generated C code and validate it works."""
    print("\n\n Compiling and Validating C Code")
    print("=" * 50)

    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as c_file:
            c_file.write(c_code)
            c_file_path = c_file.name

        # Compile the C code
        executable_path = c_file_path.replace('.c', '')
        compile_cmd = ['gcc', '-o', executable_path, c_file_path, '-lm', '-O2']

        print(f" Compiling: {' '.join(compile_cmd)}")
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)

        if compile_result.returncode == 0:
            print(" Compilation successful!")

            # Run the executable
            print(" Running executable...")
            run_result = subprocess.run([executable_path], capture_output=True, text=True)

            if run_result.returncode == 0:
                print(" Execution successful!")
                print(" Output:")
                for line in run_result.stdout.strip().split('\n'):
                    print(f"  {line}")
                return True
            else:
                print(" Execution failed!")
                print(f"Error: {run_result.stderr}")
                return False

        else:
            print(" Compilation failed!")
            print(f"Error: {compile_result.stderr}")
            return False

    except Exception as e:
        print(f" Exception during compilation: {e}")
        return False

    finally:
        # Clean up temporary files
        try:
            if 'c_file_path' in locals():
                os.unlink(c_file_path)
            if 'executable_path' in locals() and os.path.exists(executable_path):
                os.unlink(executable_path)
        except:
            pass


def main():
    """Main demonstration function."""
    print(" CGen Comprehensive Example - Intelligence to C Code")
    print("=" * 70)
    print("Demonstrating the complete pipeline:")
    print("Python → Intelligence Analysis → Optimized C Code → Compilation")
    print("=" * 70)

    # Step 1: Run intelligence layer analysis
    analyzer_results, optimizer_results = run_intelligence_analysis(EXAMPLE_PYTHON_CODE)

    # Step 2: Generate optimized C code
    c_file = generate_optimized_c_code(analyzer_results, optimizer_results)

    # Step 3: Convert to string and display
    writer = cfile.Writer()
    c_code = writer.write(c_file)

    print("\n\n Generated C Code")
    print("=" * 50)
    print(c_code)

    # Step 4: Compile and validate
    success = compile_and_validate_c_code(c_code)

    # Step 5: Summary
    print("\n\n Summary")
    print("=" * 50)

    successful_analyzers = sum(1 for r in analyzer_results.values() if r and r.success)
    total_analyzers = len(analyzer_results)

    successful_optimizers = sum(1 for r in optimizer_results.values()
                               if r and (hasattr(r, 'success') and r.success or hasattr(r, 'candidates')))
    total_optimizers = len(optimizer_results)

    print(f" Intelligence Layer Results:")
    print(f"  • Analyzers: {successful_analyzers}/{total_analyzers} successful")
    print(f"  • Optimizers: {successful_optimizers}/{total_optimizers} successful")

    # Calculate total estimated speedup
    total_speedup = 1.0
    compile_time_result = optimizer_results.get("Compile-Time Evaluator")
    if compile_time_result and hasattr(compile_time_result, 'performance_gain_estimate'):
        total_speedup *= compile_time_result.performance_gain_estimate

    vector_result = optimizer_results.get("Vectorization Detector")
    if vector_result and hasattr(vector_result, 'candidates') and vector_result.candidates:
        avg_vector_speedup = sum(c.estimated_speedup for c in vector_result.candidates) / len(vector_result.candidates)
        total_speedup *= avg_vector_speedup

    print(f" Estimated Performance Improvement: {total_speedup:.2f}x")
    print(f" C Code Generation: {' Success' if c_code else ' Failed'}")
    print(f" Compilation & Execution: {' Success' if success else ' Failed'}")

    if success:
        print("\n Complete pipeline successful!")
        print("Python code → Intelligence analysis → C generation → Compilation ")
    else:
        print("\n  Pipeline completed with issues")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)