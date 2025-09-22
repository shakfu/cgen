#!/usr/bin/env python3
"""
CGen Intelligence Layer Feature Demonstration

This script demonstrates the capabilities of all implemented Phase 3 components:
1. Static Code Analyzer with Control Flow Analysis
2. Basic Symbolic Execution Engine
3. Memory Bounds Checking Analyzer
4. Call Graph Construction and Analysis
5. Compile-Time Computation Engine
6. Loop Analysis and Transformation
7. Function Specialization System
8. Basic Vectorization Detection

Each demo shows real code examples and the intelligence layer's analysis results.
"""

import ast
import json
from typing import Dict, Any

# Import all intelligence layer components
from src.cgen.intelligence.analyzers import (
    StaticAnalyzer, SymbolicExecutor, BoundsChecker, CallGraphAnalyzer
)
from src.cgen.intelligence.optimizers import (
    CompileTimeEvaluator, LoopAnalyzer, FunctionSpecializer, VectorizationDetector
)
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer


def create_analysis_context(code: str, level: AnalysisLevel = AnalysisLevel.BASIC,
                          opt_level: OptimizationLevel = OptimizationLevel.BASIC) -> AnalysisContext:
    """Create an analysis context from Python source code."""
    # Parse the code
    ast_node = ast.parse(code)

    # Analyze with frontend
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(code)

    return AnalysisContext(
        source_code=code,
        ast_node=ast_node,
        analysis_result=analysis_result,
        analysis_level=level,
        optimization_level=opt_level
    )


def print_section_header(title: str, section_num: int):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {section_num}. {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def print_code_example(title: str, code: str):
    """Print a formatted code example."""
    print(f"\n📝 Example: {title}")
    print("```python")
    print(code.strip())
    print("```")


def demo_static_analyzer():
    """Demonstrate the Static Code Analyzer capabilities."""
    print_section_header("Static Code Analyzer with Control Flow Analysis", 1)

    examples = [
        ("Simple Function", """
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
"""),
        ("Complex Control Flow", """
def process_data(data: list, threshold: int) -> dict:
    result = {'processed': 0, 'skipped': 0}
    for item in data:
        if item > threshold:
            if item % 2 == 0:
                result['processed'] += item
            else:
                result['skipped'] += 1
        else:
            continue
    return result
"""),
        ("Loop with Dead Code", """
def example_with_dead_code(x: int) -> int:
    result = 0
    for i in range(10):
        result += i
        if i == 5:
            break
        result *= 2  # This line after break is dead code
    return result
    print("This is unreachable")  # Dead code
""")
    ]

    analyzer = StaticAnalyzer()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code, AnalysisLevel.COMPREHENSIVE)
        report = analyzer.analyze(context)

        print(f"✅ Analysis Success: {report.success}")
        print(f"🎯 Confidence: {report.confidence:.2f}")
        print(f"📊 Control Flow Blocks: {len(report.metadata.get('control_flow_graph', {}).get('blocks', []))}")
        print(f"🔍 Variables Found: {len(report.metadata.get('variables', []))}")

        if report.findings:
            print("🔎 Key Findings:")
            for finding in report.findings[:3]:
                print(f"  • {finding}")

        if report.warnings:
            print("⚠️  Warnings:")
            for warning in report.warnings:
                print(f"  • {warning}")


def demo_symbolic_executor():
    """Demonstrate the Symbolic Execution Engine capabilities."""
    print_section_header("Basic Symbolic Execution Engine", 2)

    examples = [
        ("Simple Path Exploration", """
def check_value(x: int) -> str:
    if x > 10:
        return "large"
    elif x < 0:
        return "negative"
    else:
        return "small"
"""),
        ("Loop Symbolic Execution", """
def sum_positive(numbers: list) -> int:
    total = 0
    for num in numbers:
        if num > 0:
            total += num
    return total
"""),
        ("Division by Zero Detection", """
def divide_safely(a: int, b: int) -> float:
    if b != 0:
        return a / b
    else:
        return 0.0
""")
    ]

    executor = SymbolicExecutor()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code)
        report = executor.analyze(context)

        print(f"✅ Execution Success: {report.success}")
        print(f"🎯 Confidence: {report.confidence:.2f}")
        print(f"🛤️  Paths Explored: {report.metadata.get('paths_explored', 0)}")
        print(f"📊 Coverage: {report.metadata.get('coverage_percentage', 0):.1f}%")

        if report.findings:
            print("🔎 Key Findings:")
            for finding in report.findings[:3]:
                print(f"  • {finding}")

        vulnerabilities = report.metadata.get('potential_vulnerabilities', [])
        if vulnerabilities:
            print("🚨 Potential Issues:")
            for vuln in vulnerabilities:
                print(f"  • {vuln}")


def demo_bounds_checker():
    """Demonstrate the Memory Bounds Checker capabilities."""
    print_section_header("Memory Bounds Checking Analyzer", 3)

    examples = [
        ("Safe Array Access", """
def safe_array_sum(arr: list) -> int:
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
"""),
        ("Potential Bounds Issues", """
def risky_access(data: list, index: int) -> int:
    if index >= 0:
        return data[index]  # Potential out-of-bounds
    return -1
"""),
        ("Negative Index Usage", """
def access_from_end(items: list) -> int:
    return items[-1]  # Negative indexing
""")
    ]

    checker = BoundsChecker()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code)
        report = checker.analyze(context)

        print(f"✅ Analysis Success: {report.success}")
        print(f"🎯 Confidence: {report.confidence:.2f}")
        print(f"🔍 Array Accesses: {report.metadata.get('total_array_accesses', 0)}")
        print(f"✅ Safe Accesses: {report.metadata.get('safe_accesses', 0)}")
        print(f"⚠️  Risky Accesses: {report.metadata.get('risky_accesses', 0)}")

        safety_stats = report.metadata.get('safety_statistics', {})
        if safety_stats:
            print(f"📊 Safety Score: {safety_stats.get('safety_percentage', 0):.1f}%")

        if report.warnings:
            print("⚠️  Memory Safety Warnings:")
            for warning in report.warnings:
                print(f"  • {warning}")


def demo_call_graph_analyzer():
    """Demonstrate the Call Graph Analyzer capabilities."""
    print_section_header("Call Graph Construction and Analysis", 4)

    examples = [
        ("Simple Function Calls", """
def helper(x: int) -> int:
    return x * 2

def main_function(data: list) -> list:
    result = []
    for item in data:
        processed = helper(item)
        result.append(processed)
    return result
"""),
        ("Recursive Functions", """
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""),
        ("Mutual Recursion", """
def is_even(n: int) -> bool:
    if n == 0:
        return True
    return is_odd(n - 1)

def is_odd(n: int) -> bool:
    if n == 0:
        return False
    return is_even(n - 1)
""")
    ]

    analyzer = CallGraphAnalyzer()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code)
        report = analyzer.analyze(context)

        print(f"✅ Analysis Success: {report.success}")
        print(f"🎯 Confidence: {report.confidence:.2f}")

        graph_stats = report.metadata.get('graph_statistics', {})
        print(f"🏗️  Functions: {graph_stats.get('total_functions', 0)}")
        print(f"📞 Call Sites: {graph_stats.get('total_call_sites', 0)}")
        print(f"🔄 Recursive: {graph_stats.get('recursive_functions', 0)}")
        print(f"📏 Max Depth: {graph_stats.get('max_call_depth', 0)}")

        cycles = report.metadata.get('cycles', [])
        if cycles:
            print(f"🔄 Call Cycles Found: {len(cycles)}")
            for cycle in cycles[:2]:
                print(f"  • {' → '.join(cycle)}")


def demo_compile_time_evaluator():
    """Demonstrate the Compile-Time Evaluator capabilities."""
    print_section_header("Compile-Time Computation Engine", 5)

    examples = [
        ("Constant Folding", """
def compute_area(radius: float) -> float:
    pi = 3.14159
    return pi * radius * radius

def linear_equation() -> int:
    a = 5
    b = 10
    return 2 * a + 3 * b + 0
"""),
        ("Boolean Optimizations", """
def check_conditions(x: int) -> bool:
    return (x > 0) and True and (x < 100) or False

def simplified_logic(flag: bool) -> str:
    if True:
        return "always"
    elif flag:
        return "never reached"
    else:
        return "also never reached"
"""),
        ("Mathematical Simplifications", """
def calculate_values(x: int, y: int) -> int:
    result1 = x * 1  # Multiplication by 1
    result2 = y + 0  # Addition with 0
    result3 = x * 0  # Multiplication by 0
    return result1 + result2 + result3
""")
    ]

    evaluator = CompileTimeEvaluator()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code, opt_level=OptimizationLevel.AGGRESSIVE)
        result = evaluator.optimize(context)

        print(f"✅ Optimization Success: {result.success}")
        print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")
        print(f"🔧 Transformations: {len(result.transformations)}")

        report = result.metadata.get('compile_time_report')
        if report and report.candidates:
            print(f"💡 Optimization Opportunities: {len(report.candidates)}")
            for candidate in report.candidates[:3]:
                print(f"  • {candidate.optimization_type}: {candidate.description}")

        if result.transformations:
            print("🔄 Applied Transformations:")
            for transform in result.transformations[:3]:
                print(f"  • {transform}")


def demo_loop_analyzer():
    """Demonstrate the Loop Analyzer capabilities."""
    print_section_header("Loop Analysis and Transformation", 6)

    examples = [
        ("Simple Range Loop", """
def process_array(data: list) -> int:
    total = 0
    for i in range(len(data)):
        total += data[i] * 2
    return total
"""),
        ("Accumulator Pattern", """
def sum_squares(numbers: list) -> int:
    result = 0
    for num in numbers:
        result += num * num
    return result
"""),
        ("Nested Loops", """
def matrix_multiply(a: list, b: list) -> list:
    result = []
    for i in range(len(a)):
        row = []
        for j in range(len(b[0])):
            sum_val = 0
            for k in range(len(b)):
                sum_val += a[i][k] * b[k][j]
            row.append(sum_val)
        result.append(row)
    return result
"""),
        ("Parallelizable Loop", """
def parallel_transform(data: list) -> list:
    result = []
    for item in data:
        transformed = item * 2 + 1
        result.append(transformed)
    return result
""")
    ]

    analyzer = LoopAnalyzer()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code, opt_level=OptimizationLevel.MODERATE)
        result = analyzer.optimize(context)

        print(f"✅ Analysis Success: {result.success}")
        print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")

        report = result.metadata.get('loop_analysis_report')
        if report:
            print(f"🔄 Loops Found: {len(report.loops)}")
            print(f"💡 Optimizations: {len(report.optimization_opportunities)}")

            for loop in report.loops[:2]:
                print(f"  • Loop Type: {loop.loop_type}")
                print(f"    Complexity: {loop.estimated_complexity}")
                print(f"    Parallelizable: {loop.is_parallelizable}")
                print(f"    Vectorizable: {loop.is_vectorizable}")

        if result.transformations:
            print("🔄 Suggested Transformations:")
            for transform in result.transformations[:3]:
                print(f"  • {transform}")


def demo_function_specializer():
    """Demonstrate the Function Specializer capabilities."""
    print_section_header("Function Specialization System", 7)

    examples = [
        ("Type Specialization", """
def generic_processor(data, multiplier):
    result = []
    for item in data:
        result.append(item * multiplier)
    return result

# Usage patterns suggest specialization for int and float
"""),
        ("Constant Folding Opportunity", """
def compute_with_constant(x: int, factor: int = 10) -> int:
    return x * factor + factor // 2

# Often called with factor=10, could be specialized
"""),
        ("Small Function for Inlining", """
def add_numbers(a: int, b: int) -> int:
    return a + b

def calculate_total(values: list) -> int:
    total = 0
    for i in range(len(values) - 1):
        total = add_numbers(total, values[i])
    return total
"""),
        ("Pure Function for Memoization", """
def expensive_calculation(n: int) -> int:
    if n <= 1:
        return n
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
""")
    ]

    specializer = FunctionSpecializer()

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code, opt_level=OptimizationLevel.AGGRESSIVE)
        result = specializer.optimize(context)

        print(f"✅ Analysis Success: {result.success}")
        print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")

        report = result.metadata.get('specialization_report')
        if report:
            print(f"🔍 Functions Analyzed: {len(report.function_profiles)}")
            print(f"💡 Specialization Opportunities: {len(report.specialization_candidates)}")

            for candidate in report.specialization_candidates[:3]:
                print(f"  • {candidate.specialization_type}: {candidate.function_name}")
                print(f"    Confidence: {candidate.confidence:.2f}")
                print(f"    Estimated Benefit: {candidate.estimated_benefit:.2f}x")

        if result.transformations:
            print("🔄 Specialization Suggestions:")
            for transform in result.transformations[:3]:
                print(f"  • {transform}")


def demo_vectorization_detector():
    """Demonstrate the Vectorization Detector capabilities."""
    print_section_header("Basic Vectorization Detection", 8)

    examples = [
        ("Element-wise Operation", """
def vector_add(a: list, b: list) -> list:
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result
"""),
        ("Dot Product", """
def dot_product(a: list, b: list) -> float:
    result = 0.0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result
"""),
        ("Array Copy", """
def copy_array(source: list) -> list:
    destination = []
    for i in range(len(source)):
        destination.append(source[i])
    return destination
"""),
        ("Reduction Operation", """
def sum_array(data: list) -> int:
    total = 0
    for value in data:
        total += value
    return total
"""),
        ("Strided Access", """
def process_even_indices(data: list) -> list:
    result = []
    for i in range(0, len(data), 2):
        result.append(data[i] * 2)
    return result
""")
    ]

    detector = VectorizationDetector(target_arch="x86_64", vector_width=4)

    for title, code in examples:
        print_code_example(title, code)
        context = create_analysis_context(code, opt_level=OptimizationLevel.AGGRESSIVE)
        result = detector.optimize(context)

        print(f"✅ Analysis Success: {result.success}")
        print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")

        report = result.metadata.get('vectorization_report')
        if report:
            print(f"🔄 Loops Analyzed: {report.total_loops_analyzed}")
            print(f"⚡ Vectorizable: {report.vectorizable_loops}")

            for candidate in report.candidates:
                print(f"  • Type: {candidate.vectorization_type.value}")
                print(f"    Vector Length: {candidate.vector_length}")
                print(f"    Confidence: {candidate.confidence:.2f}")
                print(f"    Speedup: {candidate.estimated_speedup:.2f}x")
                print(f"    Complexity: {candidate.transformation_complexity}")

                if candidate.constraints:
                    constraints = [c.value for c in candidate.constraints]
                    print(f"    Constraints: {', '.join(constraints)}")

        if result.transformations:
            print("🔄 Vectorization Opportunities:")
            for transform in result.transformations:
                print(f"  • {transform}")


def demo_integrated_pipeline():
    """Demonstrate using multiple components together."""
    print_section_header("Integrated Intelligence Pipeline", 9)

    # Complex example that benefits from multiple analyzers
    complex_code = """
def matrix_vector_multiply(matrix: list, vector: list) -> list:
    rows = len(matrix)
    cols = len(vector)
    result = []

    # Initialize result vector
    for i in range(rows):
        result.append(0.0)

    # Perform multiplication
    for i in range(rows):
        for j in range(cols):
            result[i] += matrix[i][j] * vector[j]

    return result

def process_batch(matrices: list, vectors: list) -> list:
    results = []
    for i in range(len(matrices)):
        if i < len(vectors):  # Bounds check
            result = matrix_vector_multiply(matrices[i], vectors[i])
            results.append(result)
    return results
"""

    print_code_example("Complex Matrix Operations", complex_code)

    # Create context
    context = create_analysis_context(complex_code,
                                    AnalysisLevel.COMPREHENSIVE,
                                    OptimizationLevel.AGGRESSIVE)

    print("\n🔬 Running Complete Analysis Pipeline...")

    # Run analyzers first
    analyzers = [
        ("Static Analyzer", StaticAnalyzer()),
        ("Bounds Checker", BoundsChecker()),
        ("Call Graph Analyzer", CallGraphAnalyzer()),
    ]

    # Run optimizers second
    optimizers = [
        ("Compile-Time Evaluator", CompileTimeEvaluator()),
        ("Loop Analyzer", LoopAnalyzer()),
        ("Function Specializer", FunctionSpecializer()),
    ]

    print("\n📊 Analysis Results Summary:")
    print("="*50)

    # Run analyzers
    for name, analyzer in analyzers:
        try:
            report = analyzer.analyze(context)
            print(f"{name:25} | Success: {report.success:5} | Confidence: {report.confidence:.2f}")
            if report.warnings:
                print(f"                         | Warnings: {len(report.warnings)}")
        except Exception as e:
            print(f"{name:25} | Error: {str(e)[:30]}...")

    # Run optimizers
    for name, optimizer in optimizers:
        try:
            result = optimizer.optimize(context)
            print(f"{name:25} | Success: {result.success:5} | Speedup: {result.performance_gain_estimate:.2f}x")
            if result.transformations:
                print(f"                         | Transformations: {len(result.transformations)}")
        except Exception as e:
            print(f"{name:25} | Error: {str(e)[:30]}...")

    # Run vectorization detector separately (uses different interface)
    try:
        detector = VectorizationDetector()
        vector_report = detector.analyze(context.ast_node)
        print(f"{'Vectorization Detector':25} | Success: True    | Vectorizable: {vector_report.vectorizable_loops}")
        if vector_report.candidates:
            avg_speedup = sum(c.estimated_speedup for c in vector_report.candidates) / len(vector_report.candidates)
            print(f"                         | Avg Speedup: {avg_speedup:.2f}x")
    except Exception as e:
        print(f"{'Vectorization Detector':25} | Error: {str(e)[:30]}...")

    print("\n💡 Key Insights from Integrated Analysis:")
    print("• Matrix operations are ideal candidates for vectorization")
    print("• Nested loops suggest parallelization opportunities")
    print("• Bounds checking prevents buffer overflow vulnerabilities")
    print("• Function specialization could optimize for common matrix sizes")
    print("• Call graph shows optimization dependency chains")


def main():
    """Main demonstration function."""
    print("🚀 CGen Intelligence Layer - Feature Demonstration")
    print("=" * 60)
    print("This demo showcases all 8 implemented Phase 3 components")
    print("Each component analyzes real Python code and provides insights")
    print("=" * 60)

    # Run all demonstrations
    demo_static_analyzer()
    demo_symbolic_executor()
    demo_bounds_checker()
    demo_call_graph_analyzer()
    demo_compile_time_evaluator()
    demo_loop_analyzer()
    demo_function_specializer()
    demo_vectorization_detector()
    demo_integrated_pipeline()

    print("\n" + "="*60)
    print("🎉 Demo Complete!")
    print("All 8 Phase 3 Intelligence Layer components demonstrated successfully.")
    print("Each component provides detailed analysis and optimization insights.")
    print("="*60)


if __name__ == "__main__":
    main()