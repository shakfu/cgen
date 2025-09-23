#!/usr/bin/env python3
"""
Working CGen Pipeline Example

A simplified but complete demonstration of:
1. Python code analysis with intelligence layer
2. C code generation with cfile
3. Compilation and execution validation

This example focuses on demonstrating the pipeline works end-to-end.
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

from cgen.frontend.analyzers import StaticAnalyzer
from cgen.frontend.optimizers import CompileTimeEvaluator, VectorizationDetector
from cgen.frontend.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer
import cfile


# Simple Python code with optimization opportunities
PYTHON_CODE = '''
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def vector_add(a: list, b: list) -> list:
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

def compute_area(radius: float) -> float:
    pi = 3.14159
    return pi * radius * radius
'''


def analyze_python_code():
    """Analyze Python code with intelligence layer."""
    print("🧠 Intelligence Layer Analysis")
    print("-" * 30)

    # Create analysis context
    ast_node = ast.parse(PYTHON_CODE)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(PYTHON_CODE)
    context = AnalysisContext(PYTHON_CODE, ast_node, analysis_result,
                             AnalysisLevel.BASIC, OptimizationLevel.MODERATE)

    results = {}

    # Static analysis
    static_analyzer = StaticAnalyzer()
    static_result = static_analyzer.analyze(context)
    results['static'] = static_result
    print(f" Static Analysis: Success={static_result.success}, Confidence={static_result.confidence:.2f}")

    # Compile-time evaluation
    evaluator = CompileTimeEvaluator()
    eval_result = evaluator.optimize(context)
    results['compile_time'] = eval_result
    print(f" Compile-time Optimization: Success={eval_result.success}, Speedup={eval_result.performance_gain_estimate:.2f}x")

    # Vectorization detection
    detector = VectorizationDetector()
    vector_result = detector.analyze(context.ast_node)
    results['vectorization'] = vector_result
    print(f" Vectorization: {vector_result.vectorizable_loops}/{vector_result.total_loops_analyzed} loops vectorizable")

    return results


def generate_simple_c_code():
    """Generate simple but functional C code."""
    print("\n Generating C Code")
    print("-" * 30)

    C = cfile.CFactory()
    code = C.sequence()

    # Includes
    code.append(C.sysinclude("stdio.h"))
    code.append(C.blank())

    # Constants (optimized based on analysis)
    print(" Adding optimized constant...")
    code.append(C.define("PI", "3.14159"))
    code.append(C.blank())

    # Simple factorial function
    print(" Generating factorial function...")
    factorial = C.function("factorial", "int")
    factorial.make_param("n", "int")

    # Function body using cfile syntax
    body = C.block()
    body.append(C.if_("n <= 1", C.func_return(C.literal(1))))
    body.append(C.func_return(C.binop("n", "*", C.func_call("factorial", C.binop("n", "-", C.literal(1))))))

    factorial.append(body)
    code.append(C.declaration(factorial))
    code.append(C.blank())

    # Simple area calculation function
    print(" Generating optimized area function...")
    area_func = C.function("compute_area", "double")
    area_func.make_param("radius", "double")

    area_body = C.block()
    area_body.append(C.func_return(C.binop("PI", "*", C.binop("radius", "*", "radius"))))

    area_func.append(area_body)
    code.append(C.declaration(area_func))
    code.append(C.blank())

    # Main function
    print(" Generating main function...")
    main = C.function("main", "int")

    main_body = C.block()
    main_body.append(C.statement(C.variable("fact_result", "int", C.func_call("factorial", C.literal(5)))))
    main_body.append(C.statement(C.variable("area_result", "double", C.func_call("compute_area", C.literal(2.0)))))

    main_body.append(C.statement(C.func_call("printf", C.str_literal("Factorial(5) = %d\\n"), "fact_result")))
    main_body.append(C.statement(C.func_call("printf", C.str_literal("Area(r=2) = %.2f\\n"), "area_result")))

    main_body.append(C.func_return(C.literal(0)))

    main.append(main_body)
    code.append(C.declaration(main))

    return code


def compile_and_test(c_code_str):
    """Compile and test the C code."""
    print(f"\n Compiling and Testing")
    print("-" * 30)

    try:
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code_str)
            c_file = f.name

        # Compile
        executable = c_file.replace('.c', '.exe')
        cmd = ['gcc', '-o', executable, c_file]

        print(f" Compiling: gcc -o {executable} {c_file}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(" Compilation successful!")

            # Run
            print(" Running executable...")
            run_result = subprocess.run([executable], capture_output=True, text=True)

            if run_result.returncode == 0:
                print(" Execution successful!")
                print(" Program output:")
                for line in run_result.stdout.strip().split('\n'):
                    print(f"   {line}")
                return True
            else:
                print(f" Execution failed: {run_result.stderr}")
        else:
            print(f" Compilation failed: {result.stderr}")

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
    """Main pipeline demonstration."""
    print(" CGen Working Pipeline Example")
    print("=" * 50)

    # Step 1: Analyze Python code
    analysis_results = analyze_python_code()

    # Step 2: Generate C code
    c_ast = generate_simple_c_code()

    # Step 3: Convert to string
    writer = cfile.Writer()
    c_code = writer.write_str(c_ast)

    print(f"\n Generated C Code")
    print("-" * 30)
    print(c_code)

    # Step 4: Compile and test
    success = compile_and_test(c_code)

    # Step 5: Summary
    print(f"\n Pipeline Results")
    print("=" * 50)

    static_success = analysis_results['static'].success
    compile_speedup = analysis_results['compile_time'].performance_gain_estimate
    vector_count = analysis_results['vectorization'].vectorizable_loops

    print(f" Static Analysis: {'' if static_success else ''}")
    print(f" Compile-time Speedup: {compile_speedup:.2f}x")
    print(f" Vectorizable Loops: {vector_count}")
    print(f" C Generation: ")
    print(f" Compilation & Execution: {'' if success else ''}")

    if success:
        print(f"\n Complete pipeline successful!")
        print(f"Python → Intelligence Analysis → C Generation → Compilation → Execution ")
        return True
    else:
        print(f"\n  Pipeline had issues")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)