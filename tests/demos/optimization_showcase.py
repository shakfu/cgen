#!/usr/bin/env python3
"""
CGen Intelligence Layer - Optimization Showcase

Real-world examples showing the practical benefits of each intelligence component.
This demonstrates how the analysis results would guide C code generation.
"""

import ast
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cgen.frontend.analyzers import StaticAnalyzer, BoundsChecker, CallGraphAnalyzer
from src.cgen.frontend.optimizers import CompileTimeEvaluator, LoopAnalyzer, VectorizationDetector
from src.cgen.frontend.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer


def create_context(code: str, opt_level=OptimizationLevel.AGGRESSIVE) -> AnalysisContext:
    """Create analysis context."""
    ast_node = ast.parse(code)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(code)
    return AnalysisContext(code, ast_node, analysis_result, AnalysisLevel.COMPREHENSIVE, opt_level)


def showcase_compile_time_optimization():
    """Show compile-time constant folding benefits."""
    print("🚀 COMPILE-TIME OPTIMIZATION SHOWCASE")
    print("=" * 50)

    # Example with lots of compile-time constants
    code = """
def physics_calculation(mass: float, velocity: float) -> float:
    # Physical constants
    gravity = 9.81
    conversion_factor = 3.6
    safety_margin = 1.15

    # Calculations with constants
    kinetic_energy = 0.5 * mass * velocity * velocity
    potential_drop = mass * gravity * 10.0
    adjusted_energy = kinetic_energy * safety_margin

    return adjusted_energy + potential_drop
"""

    print("📝 Original Python Code:")
    print("```python")
    print(code.strip())
    print("```")

    context = create_context(code)
    evaluator = CompileTimeEvaluator()
    result = evaluator.optimize(context)

    print(f"\n✅ Optimization Results:")
    print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")
    print(f"🔧 Transformations Applied: {len(result.transformations)}")

    report = result.metadata.get('compile_time_report')
    if report:
        print(f"\n💡 Constant Folding Opportunities:")
        for candidate in report.candidates[:5]:
            print(f"  • {candidate.optimization_type}: {candidate.description}")

    print(f"\n📈 Expected C Code Benefits:")
    print("  • Pre-calculated constants reduce CPU operations")
    print("  • Smaller binary size due to fewer runtime calculations")
    print("  • Better compiler optimization opportunities")
    print("  • Reduced floating-point precision errors")


def showcase_vectorization_opportunities():
    """Show SIMD vectorization benefits."""
    print("\n\n⚡ VECTORIZATION OPTIMIZATION SHOWCASE")
    print("=" * 50)

    examples = [
        ("Element-wise Vector Addition", """
def vector_add(a: list, b: list, c: list) -> list:
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i] + c[i])
    return result
"""),
        ("Dot Product Computation", """
def dot_product(vector_a: list, vector_b: list) -> float:
    result = 0.0
    for i in range(len(vector_a)):
        result += vector_a[i] * vector_b[i]
    return result
"""),
        ("Array Scaling", """
def scale_array(data: list, factor: float) -> list:
    result = []
    for i in range(len(data)):
        result.append(data[i] * factor)
    return result
""")
    ]

    detector = VectorizationDetector(target_arch="x86_64", vector_width=8)

    for title, code in examples:
        print(f"\n📝 {title}:")
        print("```python")
        print(code.strip())
        print("```")

        ast_node = ast.parse(code)
        report = detector.analyze(ast_node)

        if report.candidates:
            candidate = report.candidates[0]
            print(f"✅ Vectorizable: {candidate.vectorization_type.value}")
            print(f"📊 Vector Width: {candidate.vector_length} elements")
            print(f"🚀 Speedup: {candidate.estimated_speedup:.2f}x")
            print(f"🎯 Confidence: {candidate.confidence:.2f}")

            print(f"\n📈 Expected SIMD Benefits:")
            if candidate.vectorization_type.value == "dot_product":
                print("  • SSE/AVX dot product instructions")
                print("  • Parallel multiply-accumulate operations")
            elif candidate.vectorization_type.value == "element_wise":
                print("  • Parallel arithmetic on multiple elements")
                print("  • Memory bandwidth optimization")
            else:
                print("  • SIMD load/store operations")
                print("  • Reduced loop overhead")

            if candidate.required_intrinsics:
                print(f"  • Suggested intrinsics: {', '.join(candidate.required_intrinsics[:3])}")


def showcase_loop_optimizations():
    """Show loop transformation benefits."""
    print("\n\n🔄 LOOP OPTIMIZATION SHOWCASE")
    print("=" * 50)

    examples = [
        ("Matrix Multiplication", """
def matrix_multiply(A: list, B: list) -> list:
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])

    result = []
    for i in range(rows_A):
        row = []
        for j in range(cols_B):
            sum_val = 0
            for k in range(cols_A):
                sum_val += A[i][k] * B[k][j]
            row.append(sum_val)
        result.append(row)
    return result
"""),
        ("Image Convolution", """
def convolution_2d(image: list, kernel: list) -> list:
    height, width = len(image), len(image[0])
    k_size = len(kernel)
    result = []

    for y in range(height - k_size + 1):
        row = []
        for x in range(width - k_size + 1):
            total = 0
            for ky in range(k_size):
                for kx in range(k_size):
                    total += image[y + ky][x + kx] * kernel[ky][kx]
            row.append(total)
        result.append(row)
    return result
""")
    ]

    analyzer = LoopAnalyzer()

    for title, code in examples:
        print(f"\n📝 {title}:")
        print("```python")
        print(code.strip())
        print("```")

        context = create_context(code)
        result = analyzer.optimize(context)

        print(f"✅ Analysis Results:")
        print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")

        report = result.metadata.get('loop_analysis_report')
        if report:
            print(f"🔄 Loops Detected: {len(report.loops)}")

            for i, loop in enumerate(report.loops[:3]):
                print(f"  • Loop {i+1}: {loop.loop_type}")
                print(f"    Complexity: {loop.estimated_complexity}")
                print(f"    Parallelizable: {loop.is_parallelizable}")
                print(f"    Vectorizable: {loop.is_vectorizable}")

        print(f"\n📈 Expected C Optimizations:")
        if "matrix" in title.lower():
            print("  • Loop tiling for cache efficiency")
            print("  • Loop interchange for memory access patterns")
            print("  • Vectorization of inner loops")
        else:
            print("  • Loop unrolling for reduced overhead")
            print("  • Memory access optimization")
            print("  • SIMD instruction utilization")


def showcase_memory_safety():
    """Show memory bounds checking benefits."""
    print("\n\n🛡️ MEMORY SAFETY SHOWCASE")
    print("=" * 50)

    examples = [
        ("Potential Buffer Overflow", """
def unsafe_copy(source: list, dest: list, count: int) -> None:
    for i in range(count):
        dest[i] = source[i]  # No bounds checking!
"""),
        ("Safe Array Processing", """
def safe_process(data: list, indices: list) -> list:
    result = []
    for idx in indices:
        if 0 <= idx < len(data):
            result.append(data[idx] * 2)
    return result
"""),
        ("Ring Buffer Implementation", """
def ring_buffer_add(buffer: list, item: int, head: int) -> int:
    buffer[head % len(buffer)] = item
    return (head + 1) % len(buffer)
""")
    ]

    checker = BoundsChecker()

    for title, code in examples:
        print(f"\n📝 {title}:")
        print("```python")
        print(code.strip())
        print("```")

        context = create_context(code)
        report = checker.analyze(context)

        print(f"✅ Safety Analysis:")
        print(f"🎯 Confidence: {report.confidence:.2f}")

        safety_stats = report.metadata.get('safety_statistics', {})
        if safety_stats:
            print(f"📊 Safety Score: {safety_stats.get('safety_percentage', 0):.1f}%")

        if report.warnings:
            print("⚠️  Memory Safety Issues:")
            for warning in report.warnings[:3]:
                print(f"  • {warning}")

        print(f"\n📈 Expected C Safety Benefits:")
        if "unsafe" in title.lower():
            print("  • Generate bounds checking code")
            print("  • Add buffer overflow protection")
            print("  • Insert runtime safety assertions")
        else:
            print("  • Optimize safe access patterns")
            print("  • Remove redundant bounds checks")
            print("  • Generate efficient safe code")


def showcase_call_graph_insights():
    """Show call graph analysis benefits."""
    print("\n\n📞 CALL GRAPH ANALYSIS SHOWCASE")
    print("=" * 50)

    code = """
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b)

def math_operations(x: int, y: int) -> dict:
    return {
        'factorial_x': factorial(x),
        'fibonacci_y': fibonacci(y),
        'gcd': gcd(x, y),
        'lcm': lcm(x, y)
    }
"""

    print("📝 Mathematical Functions Example:")
    print("```python")
    print(code.strip())
    print("```")

    context = create_context(code)
    analyzer = CallGraphAnalyzer()
    report = analyzer.analyze(context)

    print(f"\n✅ Call Graph Analysis:")
    print(f"🎯 Confidence: {report.confidence:.2f}")

    graph_stats = report.metadata.get('graph_statistics', {})
    print(f"🏗️  Functions: {graph_stats.get('total_functions', 0)}")
    print(f"📞 Call Sites: {graph_stats.get('total_call_sites', 0)}")
    print(f"🔄 Recursive Functions: {graph_stats.get('recursive_functions', 0)}")
    print(f"📏 Max Call Depth: {graph_stats.get('max_call_depth', 0)}")

    cycles = report.metadata.get('cycles', [])
    if cycles:
        print(f"\n🔄 Recursive Patterns:")
        for cycle in cycles:
            print(f"  • {' → '.join(cycle)}")

    print(f"\n📈 Expected C Generation Benefits:")
    print("  • Optimal function ordering for better cache locality")
    print("  • Inlining decisions based on call frequency")
    print("  • Stack overflow protection for recursive functions")
    print("  • Dead code elimination for unreachable functions")
    print("  • Tail recursion optimization opportunities")


def main():
    """Run the optimization showcase."""
    print("🎯 CGen Intelligence Layer - Optimization Showcase")
    print("=" * 70)
    print("Real-world examples showing practical optimization benefits")
    print("=" * 70)

    showcase_compile_time_optimization()
    showcase_vectorization_opportunities()
    showcase_loop_optimizations()
    showcase_memory_safety()
    showcase_call_graph_insights()

    print("\n\n" + "=" * 70)
    print("🏆 SHOWCASE COMPLETE!")
    print("The intelligence layer provides comprehensive code analysis")
    print("enabling sophisticated optimizations for efficient C generation.")
    print("=" * 70)


if __name__ == "__main__":
    main()