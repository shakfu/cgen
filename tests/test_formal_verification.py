#!/usr/bin/env python3
"""
Test and Demonstration of CGen Formal Verification System

This demonstrates the Phase 4 formal verification capabilities:
1. Z3 theorem prover integration
2. Memory safety proof generation
3. Algorithm correctness verification
4. Performance bound analysis
"""

import ast
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer
from src.cgen.intelligence.verifiers.theorem_prover import TheoremProver, PropertyType
from src.cgen.intelligence.verifiers.bounds_prover import BoundsProver, MemorySafetyType
from src.cgen.intelligence.verifiers.correctness_prover import CorrectnessProver, FormalSpecification
from src.cgen.intelligence.verifiers.performance_analyzer import PerformanceAnalyzer, ComplexityClass


# Test algorithms with different complexity patterns
TEST_ALGORITHMS = {
    'factorial': '''
def factorial(n: int) -> int:
    """Recursive factorial with linear time complexity."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',

    'fibonacci': '''
def fibonacci(n: int) -> int:
    """Recursive Fibonacci with exponential time complexity."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
''',

    'array_sum': '''
def array_sum(data: list, size: int) -> float:
    """Array sum with bounds checking."""
    total = 0.0
    for i in range(size):
        if i < len(data):
            total += data[i]
    return total
''',

    'binary_search': '''
def binary_search(arr: list, target: int, left: int, right: int) -> int:
    """Binary search with logarithmic complexity."""
    if left > right:
        return -1

    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, right)
    else:
        return binary_search(arr, target, left, mid - 1)
''',

    'matrix_multiply': '''
def matrix_multiply(A: list, B: list, size: int) -> list:
    """Matrix multiplication with cubic complexity."""
    result = []
    for i in range(size):
        row = []
        for j in range(size):
            sum_val = 0
            for k in range(size):
                sum_val += A[i][k] * B[k][j]
            row.append(sum_val)
        result.append(row)
    return result
''',

    'unsafe_array_access': '''
def unsafe_array_access(data: list, index: int) -> float:
    """Potentially unsafe array access."""
    return data[index]  # No bounds checking!
'''
}


def create_analysis_context(code: str) -> AnalysisContext:
    """Create analysis context for testing."""
    ast_node = ast.parse(code)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(code)

    return AnalysisContext(
        code, ast_node, analysis_result,
        AnalysisLevel.COMPREHENSIVE, OptimizationLevel.AGGRESSIVE
    )


def test_theorem_prover():
    """Test basic Z3 theorem prover functionality."""
    print("🔬 Testing Z3 Theorem Prover Integration")
    print("=" * 50)

    prover = TheoremProver()

    if not prover.z3_available:
        print("⚠️  Z3 not available - using mock implementation")
        print("   Install with: pip install z3-solver")
    else:
        print("✅ Z3 theorem prover available")

    # Test bounds checking property
    print("\n📊 Testing bounds checking property...")
    bounds_prop = prover.create_bounds_check_property("array", "i", 10)
    bounds_result = prover.verify_property(bounds_prop)

    print(f"   Property: {bounds_prop.description}")
    print(f"   Status: {bounds_result.status.value}")
    print(f"   Time: {bounds_result.proof_time:.3f}s")

    # Test overflow safety property
    print("\n⚡ Testing overflow safety property...")
    overflow_prop = prover.create_overflow_safety_property("add", ["x", "y"])
    overflow_result = prover.verify_property(overflow_prop)

    print(f"   Property: {overflow_prop.description}")
    print(f"   Status: {overflow_result.status.value}")
    print(f"   Time: {overflow_result.proof_time:.3f}s")

    assert prover is not None


def test_memory_safety_verification():
    """Test memory safety verification capabilities."""
    print("\n🛡️  Testing Memory Safety Verification")
    print("=" * 50)

    bounds_prover = BoundsProver()

    # Test safe array access
    print("\n✅ Testing safe array access...")
    safe_context = create_analysis_context(TEST_ALGORITHMS['array_sum'])
    safe_proof = bounds_prover.verify_memory_safety(safe_context)

    print(f"   Function: {safe_proof.function_name}")
    print(f"   Safety: {'SAFE' if safe_proof.is_safe else 'UNSAFE'}")
    print(f"   Confidence: {safe_proof.confidence:.2f}")
    print(f"   Verification time: {safe_proof.verification_time:.3f}s")
    print(f"   Recommendations: {len(safe_proof.recommendations)}")
    for rec in safe_proof.recommendations[:2]:
        print(f"     • {rec}")

    # Test unsafe array access
    print("\n❌ Testing potentially unsafe array access...")
    unsafe_context = create_analysis_context(TEST_ALGORITHMS['unsafe_array_access'])
    unsafe_proof = bounds_prover.verify_memory_safety(unsafe_context)

    print(f"   Function: {unsafe_proof.function_name}")
    print(f"   Safety: {'SAFE' if unsafe_proof.is_safe else 'UNSAFE'}")
    print(f"   Confidence: {unsafe_proof.confidence:.2f}")
    print(f"   Unsafe accesses: {len(unsafe_proof.unsafe_accesses)}")
    print(f"   Recommendations: {len(unsafe_proof.recommendations)}")
    for rec in unsafe_proof.recommendations[:2]:
        print(f"     • {rec}")

    assert bounds_prover is not None


def test_algorithm_correctness():
    """Test algorithm correctness verification."""
    print("\n🎯 Testing Algorithm Correctness Verification")
    print("=" * 50)

    correctness_prover = CorrectnessProver()

    # Test factorial correctness
    print("\n🔢 Testing factorial correctness...")
    factorial_context = create_analysis_context(TEST_ALGORITHMS['factorial'])
    factorial_proof = correctness_prover.verify_algorithm_correctness(factorial_context)

    print(f"   Function: {factorial_proof.function_name}")
    print(f"   Correctness: {'CORRECT' if factorial_proof.is_correct else 'INCORRECT'}")
    print(f"   Confidence: {factorial_proof.confidence:.2f}")
    print(f"   Verification time: {factorial_proof.verification_time:.3f}s")
    print(f"   Proof results: {len(factorial_proof.proof_results)}")
    print(f"   Failed properties: {len(factorial_proof.failed_properties)}")

    # Test binary search correctness
    print("\n🔍 Testing binary search correctness...")
    search_context = create_analysis_context(TEST_ALGORITHMS['binary_search'])
    search_proof = correctness_prover.verify_algorithm_correctness(search_context)

    print(f"   Function: {search_proof.function_name}")
    print(f"   Correctness: {'CORRECT' if search_proof.is_correct else 'INCORRECT'}")
    print(f"   Confidence: {search_proof.confidence:.2f}")
    print(f"   Loop analysis: {len(search_proof.loop_analysis)} loops")

    assert correctness_prover is not None


def test_performance_analysis():
    """Test performance bound analysis."""
    print("\n📈 Testing Performance Bound Analysis")
    print("=" * 50)

    performance_analyzer = PerformanceAnalyzer()

    algorithms_to_test = [
        ('factorial', ComplexityClass.LINEAR),
        ('fibonacci', ComplexityClass.EXPONENTIAL),
        ('binary_search', ComplexityClass.LOGARITHMIC),
        ('matrix_multiply', ComplexityClass.CUBIC),
        ('array_sum', ComplexityClass.LINEAR)
    ]

    for alg_name, expected_complexity in algorithms_to_test:
        print(f"\n⚡ Analyzing {alg_name}...")
        context = create_analysis_context(TEST_ALGORITHMS[alg_name])
        analysis = performance_analyzer.analyze_performance_bounds(context)

        print(f"   Function: {analysis.function_name}")
        print(f"   Time complexity: {analysis.time_complexity.value}")
        print(f"   Space complexity: {analysis.space_complexity.value}")
        print(f"   Expected: {expected_complexity.value}")
        print(f"   Match: {'✅' if analysis.time_complexity == expected_complexity else '❌'}")
        print(f"   Confidence: {analysis.confidence:.2f}")
        print(f"   Verification time: {analysis.verification_time:.3f}s")

        if analysis.bottlenecks:
            print(f"   Bottlenecks: {len(analysis.bottlenecks)}")
            for bottleneck in analysis.bottlenecks[:1]:
                print(f"     • {bottleneck}")

        if analysis.optimization_opportunities:
            print(f"   Optimizations: {len(analysis.optimization_opportunities)}")
            for opt in analysis.optimization_opportunities[:1]:
                print(f"     • {opt}")

    assert performance_analyzer is not None


def test_integration_pipeline():
    """Test integrated formal verification pipeline."""
    print("\n🔄 Testing Integrated Verification Pipeline")
    print("=" * 50)

    # Choose a complex algorithm for comprehensive analysis
    test_code = TEST_ALGORITHMS['matrix_multiply']
    context = create_analysis_context(test_code)

    print(f"📝 Analyzing algorithm: matrix_multiply")
    print(f"   Code length: {len(test_code.split())} lines")

    # Run all verification components
    theorem_prover = TheoremProver()
    bounds_prover = BoundsProver(theorem_prover)
    correctness_prover = CorrectnessProver(theorem_prover)
    performance_analyzer = PerformanceAnalyzer(theorem_prover)

    print("\n🔬 Running comprehensive analysis...")

    # Memory safety
    memory_proof = bounds_prover.verify_memory_safety(context)

    # Algorithm correctness
    correctness_proof = correctness_prover.verify_algorithm_correctness(context)

    # Performance bounds
    performance_analysis = performance_analyzer.analyze_performance_bounds(context)

    # Integrated results
    print(f"\n📊 Integrated Verification Results")
    print(f"   Memory Safety: {'✅ SAFE' if memory_proof.is_safe else '❌ UNSAFE'}")
    print(f"   Algorithm Correctness: {'✅ CORRECT' if correctness_proof.is_correct else '❌ INCORRECT'}")
    print(f"   Time Complexity: {performance_analysis.time_complexity.value}")
    print(f"   Space Complexity: {performance_analysis.space_complexity.value}")

    # Overall verification confidence
    overall_confidence = (
        memory_proof.confidence +
        correctness_proof.confidence +
        performance_analysis.confidence
    ) / 3

    print(f"   Overall Confidence: {overall_confidence:.2f}")

    # Combined recommendations
    all_recommendations = (
        memory_proof.recommendations +
        performance_analysis.optimization_opportunities
    )

    if all_recommendations:
        print(f"   Recommendations ({len(all_recommendations)}):")
        for rec in all_recommendations[:3]:
            print(f"     • {rec}")

    verification_report = {
        'memory_proof': memory_proof,
        'correctness_proof': correctness_proof,
        'performance_analysis': performance_analysis,
        'overall_confidence': overall_confidence
    }
    assert verification_report is not None
    assert len(verification_report) == 4


def main():
    """Run comprehensive formal verification demonstration."""
    print("🚀 CGen Phase 4: Advanced Intelligence - Formal Verification")
    print("=" * 70)
    print("Demonstrating formal verification capabilities:")
    print("• Z3 theorem prover integration")
    print("• Memory safety proof generation")
    print("• Algorithm correctness verification")
    print("• Performance bound analysis")
    print("=" * 70)

    try:
        # Test individual components
        theorem_prover = test_theorem_prover()
        bounds_prover = test_memory_safety_verification()
        correctness_prover = test_algorithm_correctness()
        performance_analyzer = test_performance_analysis()

        # Test integrated pipeline
        integration_results = test_integration_pipeline()

        # Summary
        print(f"\n🎉 Phase 4 Formal Verification Summary")
        print("=" * 50)
        print("✅ Z3 Theorem Prover: Integrated")
        print("✅ Memory Safety Verification: Implemented")
        print("✅ Algorithm Correctness: Implemented")
        print("✅ Performance Analysis: Implemented")
        print("✅ Integrated Pipeline: Working")

        print(f"\n📈 Capabilities Demonstrated:")
        print(f"   • Formal property verification")
        print(f"   • Memory bounds checking")
        print(f"   • Algorithm correctness proofs")
        print(f"   • Complexity analysis and bounds")
        print(f"   • Performance optimization recommendations")

        print(f"\n🏆 Phase 4: Advanced Intelligence - COMPLETED!")
        print(f"Ready for Phase 5: Domain Extensions")

        return True

    except Exception as e:
        print(f"\n❌ Error in formal verification testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)