#!/usr/bin/env python3
"""Demo script showcasing the CGen Frontend capabilities."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from cgen.frontend import (
    analyze_python_code,
    StaticConstraintChecker,
    StaticPythonSubsetValidator,
    build_ir_from_code
)


def main():
    """Demonstrate frontend analysis capabilities."""
    print("🔍 CGen Frontend - Static Python Analysis Demo")
    print("=" * 60)

    # Sample Python code to analyze
    sample_codes = {
        "Simple Function": '''
def add_numbers(x: int, y: int) -> int:
    result: int = x + y
    return result
''',

        "Control Flow": '''
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    a: int = 0
    b: int = 1
    for i in range(2, n + 1):
        temp: int = a + b
        a = b
        b = temp
    return b
''',

        "Problematic Code": '''
def bad_example(x):  # Missing type annotation
    result = eval("x * 2")  # Dynamic execution
    return [i*2 for i in range(10)]  # List comprehension
'''
    }

    for name, code in sample_codes.items():
        print(f"\n📋 Analyzing: {name}")
        print("-" * 40)

        analyze_sample(code)

    print(f"\n🎉 Frontend analysis demo completed!")


def analyze_sample(code: str):
    """Analyze a code sample with all frontend components."""

    # 1. AST Analysis
    print("1️⃣ AST Analysis:")
    try:
        ast_result = analyze_python_code(code)
        print(f"   ✅ Convertible: {ast_result.convertible}")
        print(f"   📊 Functions found: {len(ast_result.functions)}")
        print(f"   ⚠️  Errors: {len(ast_result.errors)}")
        print(f"   🔧 Complexity: {ast_result.complexity.name}")

        if ast_result.errors:
            print(f"   ❌ First error: {ast_result.errors[0]}")

    except Exception as e:
        print(f"   💥 Error: {e}")

    # 2. Constraint Checking
    print("\n2️⃣ Constraint Checking:")
    try:
        checker = StaticConstraintChecker()
        constraint_report = checker.check_code(code)
        print(f"   ✅ Conversion safe: {constraint_report.conversion_safe}")
        print(f"   🎯 Confidence: {constraint_report.confidence_score:.2f}")

        errors = constraint_report.get_violations_by_severity(constraint_report.violations[0].severity if constraint_report.violations else None)
        if constraint_report.violations:
            print(f"   ⚠️  Violations: {len(constraint_report.violations)}")
            print(f"   📝 First violation: {constraint_report.violations[0].message}")

    except Exception as e:
        print(f"   💥 Error: {e}")

    # 3. Subset Validation
    print("\n3️⃣ Subset Validation:")
    try:
        validator = StaticPythonSubsetValidator()
        validation_result = validator.validate_code(code)
        print(f"   ✅ Valid subset: {validation_result.is_valid}")
        print(f"   🏷️  Tier: {validation_result.tier.name}")
        print(f"   🔧 Strategy: {validation_result.conversion_strategy}")

        if validation_result.violations:
            print(f"   ❌ Violations: {len(validation_result.violations)}")
        if validation_result.supported_features:
            print(f"   ✨ Supported features: {len(validation_result.supported_features)}")

    except Exception as e:
        print(f"   💥 Error: {e}")

    # 4. IR Generation
    print("\n4️⃣ IR Generation:")
    try:
        ir_module = build_ir_from_code(code)
        print(f"   ✅ IR created: {ir_module.name}")
        print(f"   🔧 Functions: {len(ir_module.functions)}")

        if ir_module.functions:
            func = ir_module.functions[0]
            print(f"   📝 First function: {func.name}")
            print(f"   🔧 Parameters: {len(func.parameters)}")
            print(f"   📋 Local vars: {len(func.local_variables)}")
            print(f"   📜 Statements: {len(func.body)}")

    except Exception as e:
        print(f"   💥 Error: {e}")


if __name__ == "__main__":
    main()