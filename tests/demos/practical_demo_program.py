#!/usr/bin/env python3
"""
Comprehensive Data Processing and Analysis System

This program demonstrates a practical Python application suitable for C translation.
It implements data processing, statistical analysis, and algorithmic computations
using only features currently supported by the CGen translation system.

Features tested:
- Static type annotations
- Basic data types (int, float, bool, str)
- Control flow (if/else, while, for loops)
- Function definitions with parameters and return types
- Variable declarations and assignments
- Arithmetic and comparison operations
- Function calls
- Multiple functions with different complexity levels

The program processes employee data, calculates statistics, and generates reports.
"""

def calculate_mean(values: list[float], count: int) -> float:
    """Calculate the arithmetic mean of a list of values."""
    if count == 0:
        return 0.0

    total: float = 0.0
    i: int = 0
    while i < count:
        total = total + values[i]
        i = i + 1

    return total / count

def calculate_variance(values: list[float], count: int, mean: float) -> float:
    """Calculate the variance of a list of values."""
    if count == 0:
        return 0.0

    sum_squared_diff: float = 0.0
    i: int = 0
    while i < count:
        diff: float = values[i] - mean
        sum_squared_diff = sum_squared_diff + (diff * diff)
        i = i + 1

    return sum_squared_diff / count

def find_maximum(values: list[float], count: int) -> float:
    """Find the maximum value in a list."""
    if count == 0:
        return 0.0

    max_value: float = values[0]
    i: int = 1
    while i < count:
        if values[i] > max_value:
            max_value = values[i]
        i = i + 1

    return max_value

def find_minimum(values: list[float], count: int) -> float:
    """Find the minimum value in a list."""
    if count == 0:
        return 0.0

    min_value: float = values[0]
    i: int = 1
    while i < count:
        if values[i] < min_value:
            min_value = values[i]
        i = i + 1

    return min_value

def count_above_threshold(values: list[float], count: int, threshold: float) -> int:
    """Count how many values are above a given threshold."""
    above_count: int = 0
    i: int = 0
    while i < count:
        if values[i] > threshold:
            above_count = above_count + 1
        i = i + 1

    return above_count

def calculate_grade_distribution(scores: list[float], count: int) -> list[int]:
    """Calculate grade distribution (A, B, C, D, F) from scores."""
    # Initialize grade counts: A, B, C, D, F
    grade_counts: list[int] = [0, 0, 0, 0, 0]

    i: int = 0
    while i < count:
        score: float = scores[i]

        if score >= 90.0:
            # A grade
            grade_counts[0] = grade_counts[0] + 1
        elif score >= 80.0:
            # B grade
            grade_counts[1] = grade_counts[1] + 1
        elif score >= 70.0:
            # C grade
            grade_counts[2] = grade_counts[2] + 1
        elif score >= 60.0:
            # D grade
            grade_counts[3] = grade_counts[3] + 1
        else:
            # F grade
            grade_counts[4] = grade_counts[4] + 1

        i = i + 1

    return grade_counts

def fibonacci_sequence(n: int) -> int:
    """Calculate the nth Fibonacci number using iteration."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    prev: int = 0
    curr: int = 1
    i: int = 2

    while i <= n:
        next_val: int = prev + curr
        prev = curr
        curr = next_val
        i = i + 1

    return curr

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    elif num == 2:
        return True
    elif num % 2 == 0:
        return False

    i: int = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i = i + 2

    return True

def count_primes_up_to(limit: int) -> int:
    """Count the number of prime numbers up to a given limit."""
    prime_count: int = 0
    i: int = 2

    while i <= limit:
        if is_prime(i):
            prime_count = prime_count + 1
        i = i + 1

    return prime_count

def bubble_sort(values: list[float], count: int) -> list[float]:
    """Sort a list of values using bubble sort algorithm."""
    # Create a copy of the input list
    sorted_values: list[float] = [0.0] * count
    i: int = 0
    while i < count:
        sorted_values[i] = values[i]
        i = i + 1

    # Bubble sort implementation
    i = 0
    while i < count - 1:
        j: int = 0
        while j < count - 1 - i:
            if sorted_values[j] > sorted_values[j + 1]:
                # Swap elements
                temp: float = sorted_values[j]
                sorted_values[j] = sorted_values[j + 1]
                sorted_values[j + 1] = temp
            j = j + 1
        i = i + 1

    return sorted_values

def linear_search(values: list[float], count: int, target: float) -> int:
    """Search for a target value in a list. Returns index or -1 if not found."""
    i: int = 0
    while i < count:
        if values[i] == target:
            return i
        i = i + 1

    return -1

def binary_search(sorted_values: list[float], count: int, target: float) -> int:
    """Binary search in a sorted list. Returns index or -1 if not found."""
    left: int = 0
    right: int = count - 1

    while left <= right:
        mid: int = (left + right) // 2

        if sorted_values[mid] == target:
            return mid
        elif sorted_values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

def process_employee_salaries() -> int:
    """
    Main data processing function that demonstrates practical algorithms.
    Processes employee salary data with comprehensive analysis.
    """
    # Sample employee salary data
    salaries: list[float] = [
        45000.0, 52000.0, 48000.0, 65000.0, 58000.0,
        72000.0, 39000.0, 61000.0, 55000.0, 67000.0,
        43000.0, 59000.0, 64000.0, 51000.0, 56000.0,
        70000.0, 42000.0, 63000.0, 49000.0, 68000.0
    ]

    salary_count: int = 20

    print("Employee Salary Analysis System")
    print("================================")

    # Calculate basic statistics
    mean_salary: float = calculate_mean(salaries, salary_count)
    print("Mean salary:", mean_salary)

    variance: float = calculate_variance(salaries, salary_count, mean_salary)
    print("Salary variance:", variance)

    max_salary: float = find_maximum(salaries, salary_count)
    print("Maximum salary:", max_salary)

    min_salary: float = find_minimum(salaries, salary_count)
    print("Minimum salary:", min_salary)

    # Analyze salary ranges
    high_earners: int = count_above_threshold(salaries, salary_count, 60000.0)
    print("Employees earning above $60,000:", high_earners)

    mid_earners: int = count_above_threshold(salaries, salary_count, 50000.0)
    mid_earners = mid_earners - high_earners  # Subtract high earners
    print("Employees earning $50,000-$60,000:", mid_earners)

    # Sort salaries for additional analysis
    sorted_salaries: list[float] = bubble_sort(salaries, salary_count)
    print("Salaries sorted (first 5):")
    i: int = 0
    while i < 5:
        print("Position", i + 1, ":", sorted_salaries[i])
        i = i + 1

    # Search operations
    search_target: float = 58000.0
    linear_result: int = linear_search(salaries, salary_count, search_target)
    binary_result: int = binary_search(sorted_salaries, salary_count, search_target)

    if linear_result != -1:
        print("Salary", search_target, "found at position", linear_result, "(linear search)")

    if binary_result != -1:
        print("Salary", search_target, "found at position", binary_result, "(binary search)")

    # Mathematical computations
    print("\nMathematical Analysis:")
    fib_10: int = fibonacci_sequence(10)
    print("10th Fibonacci number:", fib_10)

    primes_up_to_100: int = count_primes_up_to(100)
    print("Prime numbers up to 100:", primes_up_to_100)

    # Validate data processing
    is_data_valid: bool = True
    if mean_salary < 0.0 or max_salary < min_salary:
        is_data_valid = False

    if is_data_valid:
        print("Data validation: PASSED")
        return 0
    else:
        print("Data validation: FAILED")
        return 1

def performance_testing() -> int:
    """Performance testing function with computational workload."""
    print("\nPerformance Testing:")
    print("===================")

    # Test large computation
    large_computation: int = 0
    i: int = 0
    while i < 10000:
        large_computation = large_computation + (i * i) % 1000
        i = i + 1

    print("Large computation result:", large_computation)

    # Test prime number generation
    prime_limit: int = 500
    prime_count: int = count_primes_up_to(prime_limit)
    print("Primes up to", prime_limit, ":", prime_count)

    # Test Fibonacci sequence
    fib_limit: int = 20
    print("Fibonacci sequence up to", fib_limit, ":")
    i = 1
    while i <= fib_limit:
        fib_value: int = fibonacci_sequence(i)
        if i <= 10:  # Only print first 10 to avoid too much output
            print("F(", i, ") =", fib_value)
        i = i + 1

    return 0

def main() -> int:
    """Main program entry point."""
    print("Comprehensive Data Processing System")
    print("===================================")

    # Run employee salary analysis
    salary_result: int = process_employee_salaries()

    # Run performance testing
    performance_result: int = performance_testing()

    # Final status
    if salary_result == 0 and performance_result == 0:
        print("\nProgram completed successfully!")
        return 0
    else:
        print("\nProgram encountered errors.")
        return 1

if __name__ == "__main__":
    exit_code: int = main()
    print("Exit code:", exit_code)