#!/usr/bin/env python3
"""
Simple Mathematical Calculator - C-Compatible Version

A simplified mathematical calculator that demonstrates CGen capabilities
while staying within the static Python subset suitable for C translation.

Features:
- Basic arithmetic operations (+, -, *, /, **, %)
- Mathematical functions (sin, cos, sqrt, abs, log, exp)
- Simple expression evaluation
- Variable storage and retrieval
- Batch calculation mode

This version avoids Python features that cannot be easily translated to C:
- No classes or complex object-oriented features
- No exception handling (uses return codes instead)
- No dynamic string manipulation
- No list comprehensions or advanced Python features
- Uses simple control flow suitable for C translation
"""

import math
from typing import Dict, List, Tuple, Optional


# Error codes for operation results
ERROR_NONE: int = 0
ERROR_DIVISION_BY_ZERO: int = 1
ERROR_INVALID_OPERATION: int = 2
ERROR_DOMAIN_ERROR: int = 3
ERROR_UNKNOWN_VARIABLE: int = 4
ERROR_UNKNOWN_FUNCTION: int = 5


def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract_numbers(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide_numbers(a: float, b: float) -> Tuple[float, int]:
    """Divide two numbers. Returns (result, error_code)."""
    if b == 0.0:
        return 0.0, ERROR_DIVISION_BY_ZERO
    return a / b, ERROR_NONE


def power_numbers(a: float, b: float) -> float:
    """Raise a to the power of b."""
    return a ** b


def modulo_numbers(a: float, b: float) -> Tuple[float, int]:
    """Calculate a modulo b. Returns (result, error_code)."""
    if b == 0.0:
        return 0.0, ERROR_DIVISION_BY_ZERO
    return a % b, ERROR_NONE


def calculate_sin(x: float) -> float:
    """Calculate sine of x."""
    return math.sin(x)


def calculate_cos(x: float) -> float:
    """Calculate cosine of x."""
    return math.cos(x)


def calculate_tan(x: float) -> float:
    """Calculate tangent of x."""
    return math.tan(x)


def calculate_sqrt(x: float) -> Tuple[float, int]:
    """Calculate square root of x. Returns (result, error_code)."""
    if x < 0.0:
        return 0.0, ERROR_DOMAIN_ERROR
    return math.sqrt(x), ERROR_NONE


def calculate_abs(x: float) -> float:
    """Calculate absolute value of x."""
    if x < 0.0:
        return -x
    return x


def calculate_log(x: float) -> Tuple[float, int]:
    """Calculate natural logarithm of x. Returns (result, error_code)."""
    if x <= 0.0:
        return 0.0, ERROR_DOMAIN_ERROR
    return math.log(x), ERROR_NONE


def calculate_exp(x: float) -> float:
    """Calculate e raised to the power of x."""
    return math.exp(x)


def find_minimum(values: List[float], count: int) -> float:
    """Find minimum value in array."""
    if count <= 0:
        return 0.0

    min_val: float = values[0]
    i: int = 1
    while i < count:
        if values[i] < min_val:
            min_val = values[i]
        i = i + 1

    return min_val


def find_maximum(values: List[float], count: int) -> float:
    """Find maximum value in array."""
    if count <= 0:
        return 0.0

    max_val: float = values[0]
    i: int = 1
    while i < count:
        if values[i] > max_val:
            max_val = values[i]
        i = i + 1

    return max_val


def calculate_average(values: List[float], count: int) -> float:
    """Calculate average of values."""
    if count <= 0:
        return 0.0

    sum_val: float = 0.0
    i: int = 0
    while i < count:
        sum_val = sum_val + values[i]
        i = i + 1

    return sum_val / count


def calculate_sum(values: List[float], count: int) -> float:
    """Calculate sum of values."""
    sum_val: float = 0.0
    i: int = 0
    while i < count:
        sum_val = sum_val + values[i]
        i = i + 1

    return sum_val


def calculate_factorial(n: int) -> float:
    """Calculate factorial of n (iterative version)."""
    if n < 0:
        return 0.0

    if n == 0 or n == 1:
        return 1.0

    result: float = 1.0
    i: int = 2
    while i <= n:
        result = result * i
        i = i + 1

    return result


def calculate_fibonacci(n: int) -> float:
    """Calculate nth Fibonacci number (iterative version)."""
    if n < 0:
        return 0.0

    if n == 0:
        return 0.0

    if n == 1:
        return 1.0

    prev: float = 0.0
    curr: float = 1.0
    i: int = 2

    while i <= n:
        next_val: float = prev + curr
        prev = curr
        curr = next_val
        i = i + 1

    return curr


def is_prime(n: int) -> int:
    """Check if n is prime. Returns 1 if prime, 0 if not."""
    if n < 2:
        return 0

    if n == 2:
        return 1

    if n % 2 == 0:
        return 0

    i: int = 3
    while i * i <= n:
        if n % i == 0:
            return 0
        i = i + 2

    return 1


def calculate_gcd(a: int, b: int) -> int:
    """Calculate greatest common divisor using Euclidean algorithm."""
    if b == 0:
        return a

    while b != 0:
        temp: int = b
        b = a % b
        a = temp

    return a


def calculate_lcm(a: int, b: int) -> int:
    """Calculate least common multiple."""
    if a == 0 or b == 0:
        return 0

    gcd_val: int = calculate_gcd(a, b)
    return (a * b) // gcd_val


def calculate_power_iterative(base: float, exponent: int) -> float:
    """Calculate base^exponent using iterative method."""
    if exponent < 0:
        return 0.0  # Simplified for this demo

    if exponent == 0:
        return 1.0

    result: float = 1.0
    i: int = 0
    while i < exponent:
        result = result * base
        i = i + 1

    return result


def evaluate_polynomial(coefficients: List[float], degree: int, x: float) -> float:
    """Evaluate polynomial using Horner's method."""
    if degree < 0:
        return 0.0

    result: float = coefficients[degree]
    i: int = degree - 1

    while i >= 0:
        result = result * x + coefficients[i]
        i = i - 1

    return result


def numerical_integration_trapezoidal(start: float, end: float, steps: int) -> float:
    """Numerical integration using trapezoidal rule for f(x) = x^2."""
    if steps <= 0:
        return 0.0

    h: float = (end - start) / steps
    sum_val: float = 0.0

    # f(x) = x^2 for this example
    x: float = start
    sum_val = sum_val + (x * x)  # f(start)

    i: int = 1
    while i < steps:
        x = start + i * h
        sum_val = sum_val + 2.0 * (x * x)  # 2 * f(x)
        i = i + 1

    x = end
    sum_val = sum_val + (x * x)  # f(end)

    return (h / 2.0) * sum_val


def monte_carlo_pi_estimation(iterations: int) -> float:
    """Estimate pi using Monte Carlo method (simplified)."""
    if iterations <= 0:
        return 0.0

    inside_circle: int = 0
    i: int = 0

    # Simplified random number generation for demo
    x: float = 0.5
    y: float = 0.5

    while i < iterations:
        # Simple pseudo-random number generation
        x = (x * 9973.0) % 1.0
        y = (y * 9973.0) % 1.0

        # Convert to range [-1, 1]
        x_coord: float = 2.0 * x - 1.0
        y_coord: float = 2.0 * y - 1.0

        # Check if point is inside unit circle
        distance_squared: float = x_coord * x_coord + y_coord * y_coord
        if distance_squared <= 1.0:
            inside_circle = inside_circle + 1

        i = i + 1

    return 4.0 * inside_circle / iterations


def demonstrate_basic_operations() -> None:
    """Demonstrate basic mathematical operations."""
    print("Basic Mathematical Operations Demo")
    print("=" * 50)

    a: float = 15.5
    b: float = 4.2

    print(f"a = {a}")
    print(f"b = {b}")
    print()

    # Basic arithmetic
    result_add: float = add_numbers(a, b)
    print(f"Addition: {a} + {b} = {result_add}")

    result_sub: float = subtract_numbers(a, b)
    print(f"Subtraction: {a} - {b} = {result_sub}")

    result_mul: float = multiply_numbers(a, b)
    print(f"Multiplication: {a} * {b} = {result_mul}")

    result_div: float
    error_code: int
    result_div, error_code = divide_numbers(a, b)
    if error_code == ERROR_NONE:
        print(f"Division: {a} / {b} = {result_div}")
    else:
        print(f"Division error: {error_code}")

    result_pow: float = power_numbers(a, 2.0)
    print(f"Power: {a}^2 = {result_pow}")

    result_mod: float
    result_mod, error_code = modulo_numbers(a, b)
    if error_code == ERROR_NONE:
        print(f"Modulo: {a} % {b} = {result_mod}")

    print()


def demonstrate_trigonometric_functions() -> None:
    """Demonstrate trigonometric functions."""
    print("Trigonometric Functions Demo")
    print("=" * 50)

    angle: float = 1.5708  # approximately pi/2
    print(f"angle = {angle} radians")
    print()

    sin_result: float = calculate_sin(angle)
    print(f"sin({angle}) = {sin_result}")

    cos_result: float = calculate_cos(angle)
    print(f"cos({angle}) = {cos_result}")

    tan_result: float = calculate_tan(angle)
    print(f"tan({angle}) = {tan_result}")

    print()


def demonstrate_mathematical_functions() -> None:
    """Demonstrate various mathematical functions."""
    print("Mathematical Functions Demo")
    print("=" * 50)

    x: float = 16.0
    print(f"x = {x}")
    print()

    sqrt_result: float
    error_code: int
    sqrt_result, error_code = calculate_sqrt(x)
    if error_code == ERROR_NONE:
        print(f"sqrt({x}) = {sqrt_result}")

    abs_result: float = calculate_abs(-x)
    print(f"abs({-x}) = {abs_result}")

    log_result: float
    log_result, error_code = calculate_log(x)
    if error_code == ERROR_NONE:
        print(f"log({x}) = {log_result}")

    exp_result: float = calculate_exp(2.0)
    print(f"exp(2.0) = {exp_result}")

    print()


def demonstrate_array_operations() -> None:
    """Demonstrate operations on arrays of numbers."""
    print("Array Operations Demo")
    print("=" * 50)

    # Create test array
    values: List[float] = [3.5, 1.2, 7.8, 2.1, 9.4, 0.6, 5.3]
    count: int = 7

    print("Array values:")
    i: int = 0
    while i < count:
        print(f"  [{i}] = {values[i]}")
        i = i + 1
    print()

    min_val: float = find_minimum(values, count)
    print(f"Minimum: {min_val}")

    max_val: float = find_maximum(values, count)
    print(f"Maximum: {max_val}")

    avg_val: float = calculate_average(values, count)
    print(f"Average: {avg_val}")

    sum_val: float = calculate_sum(values, count)
    print(f"Sum: {sum_val}")

    print()


def demonstrate_number_theory() -> None:
    """Demonstrate number theory functions."""
    print("Number Theory Demo")
    print("=" * 50)

    n: int = 10
    factorial_result: float = calculate_factorial(n)
    print(f"Factorial of {n}: {factorial_result}")

    fibonacci_result: float = calculate_fibonacci(n)
    print(f"Fibonacci number {n}: {fibonacci_result}")

    # Test primality for several numbers
    test_numbers: List[int] = [2, 3, 4, 5, 17, 25, 29]
    i: int = 0
    while i < 7:
        num: int = test_numbers[i]
        is_prime_result: int = is_prime(num)
        if is_prime_result == 1:
            print(f"{num} is prime")
        else:
            print(f"{num} is not prime")
        i = i + 1

    a: int = 48
    b: int = 18
    gcd_result: int = calculate_gcd(a, b)
    lcm_result: int = calculate_lcm(a, b)
    print(f"GCD of {a} and {b}: {gcd_result}")
    print(f"LCM of {a} and {b}: {lcm_result}")

    print()


def demonstrate_advanced_calculations() -> None:
    """Demonstrate advanced mathematical calculations."""
    print("Advanced Calculations Demo")
    print("=" * 50)

    # Polynomial evaluation: 2x^3 + 3x^2 - 5x + 1
    coeffs: List[float] = [1.0, -5.0, 3.0, 2.0]  # [constant, x, x^2, x^3]
    x_val: float = 2.5
    poly_result: float = evaluate_polynomial(coeffs, 3, x_val)
    print(f"Polynomial 2x³ + 3x² - 5x + 1 at x={x_val}: {poly_result}")

    # Numerical integration
    integral_result: float = numerical_integration_trapezoidal(0.0, 2.0, 1000)
    print(f"Integral of x² from 0 to 2 (trapezoidal rule): {integral_result}")
    print(f"Analytical result: {8.0/3.0}")

    # Monte Carlo pi estimation
    pi_estimate: float = monte_carlo_pi_estimation(10000)
    print(f"Pi estimation (Monte Carlo, 10000 iterations): {pi_estimate}")
    print(f"Actual pi: {math.pi}")

    # Power calculation
    base: float = 2.0
    exp: int = 10
    power_result: float = calculate_power_iterative(base, exp)
    print(f"{base}^{exp} = {power_result}")

    print()


def run_comprehensive_demo() -> None:
    """Run comprehensive demonstration of all calculator features."""
    print("Simple Mathematical Calculator - Comprehensive Demo")
    print("=" * 60)
    print()

    demonstrate_basic_operations()
    demonstrate_trigonometric_functions()
    demonstrate_mathematical_functions()
    demonstrate_array_operations()
    demonstrate_number_theory()
    demonstrate_advanced_calculations()

    print("Demo completed successfully!")
    print("All calculations performed using static Python suitable for C translation.")


def main() -> None:
    """Main function to run the calculator demonstration."""
    run_comprehensive_demo()


if __name__ == "__main__":
    main()