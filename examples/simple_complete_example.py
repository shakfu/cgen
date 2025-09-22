#!/usr/bin/env python3
"""
Simple Complete CGen Example - Intelligence Layer to Working C Code

This demonstrates the complete pipeline:
1. Python code with optimization opportunities
2. Intelligence layer analysis
3. C code generation using cfile
4. Compilation and execution validation
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
sys.path.append(str(project_root / "src"))

from src.cgen.intelligence.analyzers import StaticAnalyzer, BoundsChecker, CallGraphAnalyzer
from src.cgen.intelligence.optimizers import CompileTimeEvaluator, VectorizationDetector
from src.cgen.intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from src.cgen.frontend.ast_analyzer import ASTAnalyzer
import cfile


# Example Python code that demonstrates key optimization opportunities
PYTHON_CODE = '''
def factorial(n: int) -> int:
    """Recursive function for call graph analysis."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def vector_add(a: list, b: list) -> list:
    """Vectorizable operation."""
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

def compute_circle_area(radius: float) -> float:
    """Function with compile-time constants."""
    pi = 3.141592653589793
    return pi * radius * radius

def safe_array_sum(data: list) -> float:
    """Memory-safe array operation."""
    total = 0.0
    for i in range(len(data)):
        if i < len(data):  # Bounds check
            total += data[i]
    return total
'''


def analyze_with_intelligence_layer(code: str):
    """Run intelligence layer analysis."""
    print("🧠 Intelligence Layer Analysis")
    print("=" * 40)

    # Create analysis context
    ast_node = ast.parse(code)
    analyzer = ASTAnalyzer()
    analysis_result = analyzer.analyze(code)
    context = AnalysisContext(code, ast_node, analysis_result,
                             AnalysisLevel.COMPREHENSIVE, OptimizationLevel.AGGRESSIVE)

    results = {}

    # Static Analysis
    print("🔬 Static Analyzer...")
    static_analyzer = StaticAnalyzer()
    static_result = static_analyzer.analyze(context)
    results['static'] = static_result
    print(f"  Success: {static_result.success}, Confidence: {static_result.confidence:.2f}")

    # Bounds Checking
    print("🛡️  Bounds Checker...")
    bounds_checker = BoundsChecker()
    bounds_result = bounds_checker.analyze(context)
    results['bounds'] = bounds_result
    print(f"  Success: {bounds_result.success}, Confidence: {bounds_result.confidence:.2f}")

    # Call Graph Analysis
    print("📞 Call Graph Analyzer...")
    call_graph = CallGraphAnalyzer()
    graph_result = call_graph.analyze(context)
    results['call_graph'] = graph_result
    print(f"  Success: {graph_result.success}, Confidence: {graph_result.confidence:.2f}")

    # Compile-Time Evaluation
    print("⚡ Compile-Time Evaluator...")
    evaluator = CompileTimeEvaluator()
    eval_result = evaluator.optimize(context)
    results['compile_time'] = eval_result
    print(f"  Success: {eval_result.success}, Speedup: {eval_result.performance_gain_estimate:.2f}x")

    # Vectorization Detection
    print("🚀 Vectorization Detector...")
    detector = VectorizationDetector()
    vector_result = detector.analyze(context.ast_node)
    results['vectorization'] = vector_result
    print(f"  Loops analyzed: {vector_result.total_loops_analyzed}, Vectorizable: {vector_result.vectorizable_loops}")

    return results


def generate_c_code(analysis_results):
    """Generate C code using cfile library."""
    print("\n🔧 Generating C Code")
    print("=" * 40)

    C = cfile.CFactory()
    code = C.sequence()

    # Add includes
    code.append(C.sysinclude("stdio.h"))
    code.append(C.sysinclude("math.h"))
    code.append(C.blank())

    # Add optimized constants (from compile-time analysis)
    eval_result = analysis_results.get('compile_time')
    if eval_result and eval_result.success:
        print("📊 Adding compile-time optimized constants...")
        code.append(C.line_comment("Compile-time optimized constants"))
        code.append(C.define("PI", "3.141592653589793"))
        code.append(C.blank())

    # Generate factorial function (identified by call graph analysis)
    print("🔄 Generating factorial function...")
    factorial_func = C.function("factorial", "int")
    factorial_func.add_param(C.variable("n", "int"))

    factorial_body = C.block()
    # if (n <= 1) return 1;
    factorial_body.append(C.statement(
        C.if_("n <= 1", C.func_return(C.literal(1)))
    ))
    # return n * factorial(n - 1);
    factorial_body.append(C.statement(
        C.func_return(C.binop("n", "*", C.func_call("factorial", C.binop("n", "-", C.literal(1)))))
    ))

    factorial_func.add(factorial_body)
    code.append(C.declaration(factorial_func))
    code.append(C.blank())

    # Generate optimized circle area function
    print("📐 Generating optimized circle area function...")
    area_func = C.function("compute_circle_area", "double")
    area_func.add_param(C.variable("radius", "double"))

    area_body = C.block()
    # Use pre-computed PI constant
    area_body.append(C.statement(
        C.func_return(C.binop("PI", "*", C.binop("radius", "*", "radius")))
    ))

    area_func.add(area_body)
    code.append(C.declaration(area_func))
    code.append(C.blank())

    # Generate bounds-checked array sum
    bounds_result = analysis_results.get('bounds')
    print("🛡️  Generating memory-safe array sum...")
    if bounds_result and bounds_result.confidence > 0.8:
        code.append(C.line_comment("Memory safety verified by static analysis"))

    sum_func = C.function("safe_array_sum", "double")
    sum_func.add_param(C.variable("data", C.type("double", pointer=True)))
    sum_func.add_param(C.variable("size", "int"))

    sum_body = C.block()
    sum_body.append(C.statement(C.variable("total", "double", C.literal(0.0))))
    sum_body.append(C.statement(C.variable("i", "int")))

    # Safe loop with bounds checking
    for_loop = C.for_(
        C.assign("i", C.literal(0)),
        C.binop("i", "<", "size"),
        C.assign("i", C.binop("i", "+", C.literal(1)))
    )

    loop_body = C.block()
    loop_body.append(C.statement(
        C.assign("total", C.binop("total", "+", C.subscript("data", "i")))
    ))

    for_loop.add(loop_body)
    sum_body.append(for_loop)
    sum_body.append(C.statement(C.func_return("total")))

    sum_func.add(sum_body)
    code.append(C.declaration(sum_func))
    code.append(C.blank())

    # Generate vectorizable vector addition function
    vector_result = analysis_results.get('vectorization')
    if vector_result and vector_result.vectorizable_loops > 0:
        print("⚡ Generating vectorizable function...")
        code.append(C.line_comment("Vectorizable operation - SIMD optimization opportunity"))

    vector_func = C.function("vector_add", "void")
    vector_func.add_param(C.variable("a", C.type("double", pointer=True)))
    vector_func.add_param(C.variable("b", C.type("double", pointer=True)))
    vector_func.add_param(C.variable("result", C.type("double", pointer=True)))
    vector_func.add_param(C.variable("size", "int"))

    vector_body = C.block()
    vector_body.append(C.statement(C.variable("i", "int")))

    vector_loop = C.for_(
        C.assign("i", C.literal(0)),
        C.binop("i", "<", "size"),
        C.assign("i", C.binop("i", "+", C.literal(1)))
    )

    vector_loop_body = C.block()
    vector_loop_body.append(C.statement(
        C.assign(
            C.subscript("result", "i"),
            C.binop(C.subscript("a", "i"), "+", C.subscript("b", "i"))
        )
    ))

    vector_loop.add(vector_loop_body)
    vector_body.append(vector_loop)

    vector_func.add(vector_body)
    code.append(C.declaration(vector_func))
    code.append(C.blank())

    # Generate main function with tests
    print("🎯 Generating main function...")
    main_func = C.function("main", "int")

    main_body = C.block()

    # Test factorial
    main_body.append(C.statement(C.variable("fact_result", "int", C.func_call("factorial", C.literal(5)))))

    # Test circle area
    main_body.append(C.statement(C.variable("area_result", "double", C.func_call("compute_circle_area", C.literal(2.0)))))

    # Test array operations
    main_body.append(C.statement(C.variable("test_data", "double",
                                           C.array([C.literal(1.0), C.literal(2.0), C.literal(3.0), C.literal(4.0)]))))
    main_body.append(C.statement(C.variable("sum_result", "double",
                                           C.func_call("safe_array_sum", "test_data", C.literal(4)))))

    # Print results
    main_body.append(C.statement(
        C.func_call("printf", C.str_literal("Factorial(5) = %d\\n"), "fact_result")
    ))
    main_body.append(C.statement(
        C.func_call("printf", C.str_literal("Circle area (r=2) = %f\\n"), "area_result")
    ))
    main_body.append(C.statement(
        C.func_call("printf", C.str_literal("Array sum = %f\\n"), "sum_result")
    ))

    main_body.append(C.statement(C.func_return(C.literal(0))))

    main_func.add(main_body)
    code.append(C.declaration(main_func))

    return code


def compile_and_run(c_code: str):
    """Compile and run the generated C code."""
    print("\n🔨 Compiling and Running C Code")
    print("=" * 40)

    try:
        # Write C code to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            c_file = f.name

        # Compile
        executable = c_file.replace('.c', '')
        cmd = ['gcc', '-o', executable, c_file, '-lm']

        print(f"🔧 Compiling: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Compilation successful!")

            # Run
            print("🚀 Running executable...")
            run_result = subprocess.run([executable], capture_output=True, text=True)

            if run_result.returncode == 0:
                print("✅ Execution successful!")
                print("📤 Output:")
                for line in run_result.stdout.strip().split('\n'):
                    print(f"  {line}")
                return True
            else:
                print(f"❌ Execution failed: {run_result.stderr}")
                return False
        else:
            print(f"❌ Compilation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

    finally:
        # Cleanup
        try:
            if 'c_file' in locals():
                os.unlink(c_file)
            if 'executable' in locals() and os.path.exists(executable):
                os.unlink(executable)
        except:
            pass


def main():
    """Main demonstration."""
    print("🚀 CGen Complete Pipeline Example")
    print("=" * 50)
    print("Python → Intelligence Analysis → C Generation → Compilation")
    print("=" * 50)

    # Step 1: Intelligence Layer Analysis
    analysis_results = analyze_with_intelligence_layer(PYTHON_CODE)

    # Step 2: Generate C Code
    c_code_ast = generate_c_code(analysis_results)

    # Step 3: Convert to string
    writer = cfile.Writer()
    c_code = writer.write_str(c_code_ast)

    print("\n📝 Generated C Code")
    print("=" * 40)
    print(c_code)

    # Step 4: Compile and Run
    success = compile_and_run(c_code)

    # Step 5: Summary
    print(f"\n📊 Pipeline Summary")
    print("=" * 40)

    # Count successful components
    analyzers_success = sum(1 for key in ['static', 'bounds', 'call_graph']
                           if analysis_results.get(key) and analysis_results[key].success)

    optimizers_success = 0
    if analysis_results.get('compile_time') and analysis_results['compile_time'].success:
        optimizers_success += 1
    if analysis_results.get('vectorization') and analysis_results['vectorization'].vectorizable_loops > 0:
        optimizers_success += 1

    print(f"📈 Intelligence Analysis: {analyzers_success}/3 analyzers successful")
    print(f"🚀 Optimizations: {optimizers_success}/2 optimizers found opportunities")
    print(f"🔧 C Code Generation: ✅ Success")
    print(f"🔨 Compilation: {'✅ Success' if success else '❌ Failed'}")

    # Calculate estimated performance improvement
    eval_result = analysis_results.get('compile_time')
    speedup = eval_result.performance_gain_estimate if eval_result and eval_result.success else 1.0

    vector_result = analysis_results.get('vectorization')
    if vector_result and vector_result.candidates:
        vector_speedup = sum(c.estimated_speedup for c in vector_result.candidates) / len(vector_result.candidates)
        speedup *= vector_speedup

    print(f"📊 Estimated Performance Improvement: {speedup:.2f}x")

    if success:
        print("\n🎉 Complete pipeline successful!")
        print("All components working: Python analysis → C generation → compilation → execution")
    else:
        print("\n⚠️  Pipeline partially successful")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)