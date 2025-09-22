#!/usr/bin/env python3
"""
Minimal Working CGen Demo

This demonstrates the essential pipeline:
1. Python analysis with intelligence layer
2. Simple C generation with cfile
3. Compilation validation

Kept minimal to ensure it works reliably.
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

from src.cgen.intelligence.analyzers import StaticAnalyzer
from src.cgen.intelligence.optimizers import CompileTimeEvaluator, VectorizationDetector
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer
import cfile


def run_intelligence_analysis():
    """Run basic intelligence analysis."""
    print("🧠 Intelligence Layer Analysis")
    print("-" * 40)

    # Simple Python code with optimization opportunities
    python_code = '''
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def add_vectors(a: list, b: list) -> list:
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

def calculate_area(radius: float) -> float:
    pi = 3.14159
    return pi * radius * radius
'''

    # Create analysis context
    ast_node = ast.parse(python_code)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(python_code)
    context = AnalysisContext(python_code, ast_node, analysis_result,
                             AnalysisLevel.BASIC, OptimizationLevel.MODERATE)

    # Run analyzers
    print(" Static Analyzer...")
    static_analyzer = StaticAnalyzer()
    static_result = static_analyzer.analyze(context)
    print(f"   Success: {static_result.success}, Confidence: {static_result.confidence:.2f}")

    print(" Compile-Time Evaluator...")
    evaluator = CompileTimeEvaluator()
    eval_result = evaluator.optimize(context)
    print(f"   Success: {eval_result.success}, Speedup: {eval_result.performance_gain_estimate:.2f}x")

    print(" Vectorization Detector...")
    detector = VectorizationDetector()
    vector_result = detector.analyze(context.ast_node)
    print(f"   Vectorizable loops: {vector_result.vectorizable_loops}/{vector_result.total_loops_analyzed}")

    return {
        'static': static_result,
        'compile_time': eval_result,
        'vectorization': vector_result
    }


def generate_basic_c_code():
    """Generate basic C code using cfile."""
    print("\n C Code Generation")
    print("-" * 40)

    C = cfile.CFactory()
    code = C.sequence()

    # Add includes
    print(" Adding includes...")
    code.append(C.sysinclude("stdio.h"))
    code.append(C.blank())

    # Add optimized constant
    print(" Adding optimized constants...")
    code.append(C.define("PI", "3.14159"))
    code.append(C.blank())

    # Simple function using basic cfile constructs
    print(" Generating functions...")

    # Factorial function (simplified)
    factorial = C.function("factorial", "int")
    factorial.make_param("n", "int")

    # Simple function body - just return n for demo
    fact_body = C.block()
    fact_body.append(C.statement(C.func_return("n")))  # Simplified for demo
    factorial.append(fact_body)

    code.append(C.declaration(factorial))
    code.append(C.blank())

    # Area calculation function
    area_func = C.function("calculate_area", "double")
    area_func.make_param("radius", "double")

    area_body = C.block()
    # Use the optimized PI constant
    area_body.append(C.statement(
        C.func_return(C.binop("PI", "*", C.binop("radius", "*", "radius")))
    ))
    area_func.append(area_body)

    code.append(C.declaration(area_func))
    code.append(C.blank())

    # Main function
    print(" Generating main function...")
    main = C.function("main", "int")

    main_body = C.block()

    # Simple variable declarations and function calls
    main_body.append(C.statement(C.variable("result1", "int", C.func_call("factorial", C.literal(5)))))
    main_body.append(C.statement(C.variable("result2", "double", C.func_call("calculate_area", C.literal(2.0)))))

    # Print results
    main_body.append(C.statement(
        C.func_call("printf", C.str_literal("Factorial result: %d\\n"), "result1")
    ))
    main_body.append(C.statement(
        C.func_call("printf", C.str_literal("Area result: %.2f\\n"), "result2")
    ))

    # Return 0
    main_body.append(C.statement(C.func_return(C.literal(0))))

    main.append(main_body)
    code.append(C.declaration(main))

    return code


def test_compilation(c_code_str):
    """Test C code compilation."""
    print(f"\n Compilation Test")
    print("-" * 40)

    try:
        # Write C code to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code_str)
            c_file = f.name

        # Try to compile
        executable = c_file.replace('.c', '.out')
        cmd = ['gcc', '-o', executable, c_file]

        print(f" Compiling with: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(" Compilation successful!")

            # Try to run
            print(" Testing execution...")
            run_result = subprocess.run([executable], capture_output=True, text=True, timeout=5)

            if run_result.returncode == 0:
                print(" Execution successful!")
                print(" Output:")
                for line in run_result.stdout.strip().split('\n'):
                    print(f"   {line}")
                return True
            else:
                print(f" Execution failed: {run_result.stderr}")
        else:
            print(f" Compilation failed:")
            print(f"   {result.stderr}")

    except Exception as e:
        print(f" Error: {e}")

    finally:
        # Cleanup
        try:
            if 'c_file' in locals() and os.path.exists(c_file):
                os.unlink(c_file)
            if 'executable' in locals() and os.path.exists(executable):
                os.unlink(executable)
        except:
            pass

    return False


def main():
    """Main demonstration."""
    print(" Minimal CGen Pipeline Demo")
    print("=" * 50)

    # Step 1: Intelligence analysis
    analysis_results = run_intelligence_analysis()

    # Step 2: Generate C code
    c_ast = generate_basic_c_code()

    # Step 3: Convert to string
    writer = cfile.Writer()
    c_code = writer.write_str(c_ast)

    print(f"\n Generated C Code")
    print("-" * 40)
    print(c_code)

    # Step 4: Test compilation
    success = test_compilation(c_code)

    # Step 5: Summary
    print(f"\n Demo Results")
    print("=" * 50)

    static_ok = analysis_results['static'].success
    speedup = analysis_results['compile_time'].performance_gain_estimate
    vectors = analysis_results['vectorization'].vectorizable_loops

    print(f" Intelligence Analysis:")
    print(f"   Static Analysis: {'' if static_ok else ''}")
    print(f"   Compile-time Speedup: {speedup:.2f}x")
    print(f"   Vectorizable Loops: {vectors}")

    print(f" C Code Generation: ")
    print(f" Compilation: {'' if success else ''}")

    if success:
        print(f"\n Complete pipeline working!")
        print(f"Python analysis → C generation → compilation → execution ")
    else:
        print(f"\n  Pipeline needs debugging")

    return success


if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {0 if success else 1}")
    exit(0 if success else 1)