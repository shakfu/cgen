#!/usr/bin/env python3
"""
CGen Intelligence Layer - Simple Feature Demonstration

A focused demonstration of the key capabilities of each implemented component.
"""

import ast
from src.cgen.intelligence.analyzers import StaticAnalyzer, SymbolicExecutor, BoundsChecker, CallGraphAnalyzer
from src.cgen.intelligence.optimizers import CompileTimeEvaluator, LoopAnalyzer, FunctionSpecializer, VectorizationDetector
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer


def create_context(code: str) -> AnalysisContext:
    """Create analysis context from code."""
    ast_node = ast.parse(code)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(code)

    return AnalysisContext(
        source_code=code,
        ast_node=ast_node,
        analysis_result=analysis_result,
        analysis_level=AnalysisLevel.BASIC,
        optimization_level=OptimizationLevel.MODERATE
    )


def demo_component(name: str, component, code: str, description: str):
    """Demo a single component."""
    print(f"\n🔬 {name}")
    print(f"📄 {description}")
    print("```python")
    print(code.strip())
    print("```")

    context = create_context(code)

    try:
        if hasattr(component, 'analyze'):
            # It's an analyzer
            result = component.analyze(context)
            print(f"✅ Success: {result.success}")
            print(f"🎯 Confidence: {result.confidence:.2f}")

            if result.findings:
                print("🔎 Key Findings:")
                for finding in result.findings[:3]:
                    print(f"  • {finding}")

            if result.warnings:
                print("⚠️  Warnings:")
                for warning in result.warnings[:2]:
                    print(f"  • {warning}")

        else:
            # It's an optimizer
            result = component.optimize(context)
            print(f"✅ Success: {result.success}")
            print(f"🚀 Performance Gain: {result.performance_gain_estimate:.2f}x")

            if result.transformations:
                print("🔄 Transformations:")
                for transform in result.transformations[:3]:
                    print(f"  • {transform}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_vectorization_direct():
    """Demo vectorization detector directly."""
    print(f"\n🔬 Vectorization Detector (Direct)")
    print(f"📄 SIMD optimization opportunity detection")

    code = """
def dot_product(a: list, b: list) -> float:
    result = 0.0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result
"""

    print("```python")
    print(code.strip())
    print("```")

    try:
        detector = VectorizationDetector()
        ast_node = ast.parse(code)
        report = detector.analyze(ast_node)

        print(f"✅ Success: True")
        print(f"🔄 Loops Analyzed: {report.total_loops_analyzed}")
        print(f"⚡ Vectorizable: {report.vectorizable_loops}")

        for candidate in report.candidates:
            print(f"  • Type: {candidate.vectorization_type.value}")
            print(f"    Vector Length: {candidate.vector_length}")
            print(f"    Confidence: {candidate.confidence:.2f}")
            print(f"    Speedup: {candidate.estimated_speedup:.2f}x")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run the demonstration."""
    print("🚀 CGen Intelligence Layer - Core Feature Demo")
    print("=" * 60)

    # 1. Static Analyzer
    code1 = """
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    demo_component("Static Analyzer", StaticAnalyzer(), code1,
                  "Control flow analysis and dead code detection")

    # 2. Symbolic Executor
    code2 = """
def check_value(x: int) -> str:
    if x > 10:
        return "large"
    elif x < 0:
        return "negative"
    return "small"
"""
    demo_component("Symbolic Executor", SymbolicExecutor(), code2,
                  "Path exploration and symbolic reasoning")

    # 3. Bounds Checker
    code3 = """
def safe_sum(arr: list) -> int:
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
"""
    demo_component("Bounds Checker", BoundsChecker(), code3,
                  "Memory safety and bounds checking")

    # 4. Call Graph Analyzer
    code4 = """
def helper(x: int) -> int:
    return x * 2

def main_func(data: list) -> list:
    return [helper(x) for x in data]
"""
    demo_component("Call Graph Analyzer", CallGraphAnalyzer(), code4,
                  "Function call relationships and dependencies")

    # 5. Compile-Time Evaluator
    code5 = """
def compute_area() -> float:
    pi = 3.14159
    radius = 5
    return pi * radius * radius
"""
    demo_component("Compile-Time Evaluator", CompileTimeEvaluator(), code5,
                  "Constant folding and expression optimization")

    # 6. Loop Analyzer
    code6 = """
def sum_squares(numbers: list) -> int:
    result = 0
    for num in numbers:
        result += num * num
    return result
"""
    demo_component("Loop Analyzer", LoopAnalyzer(), code6,
                  "Loop optimization and transformation opportunities")

    # 7. Function Specializer
    code7 = """
def multiply(a: int, b: int) -> int:
    return a * b

def double_values(data: list) -> list:
    return [multiply(x, 2) for x in data]
"""
    demo_component("Function Specializer", FunctionSpecializer(), code7,
                  "Function specialization and inlining opportunities")

    # 8. Vectorization Detector (Direct)
    demo_vectorization_direct()

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("All 8 Phase 3 Intelligence Layer components demonstrated.")
    print("Each component analyzes code and provides optimization insights.")
    print("=" * 60)


if __name__ == "__main__":
    main()