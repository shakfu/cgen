#!/usr/bin/env python3
"""
Test Control Flow Implementation

Simple test program to verify if/while/for control flow works correctly.
"""

def test_control_flow() -> int:
    """
    Test function with control flow statements.

    Returns:
        Success result
    """
    result: int = 0

    # Test if statement
    if result == 0:
        result = result + 1

    # Test while loop
    counter: int = 0
    while counter < 3:
        result = result + 1
        counter = counter + 1

    # Test for loop
    for i in range(5):
        result = result + 1

    return result


if __name__ == "__main__":
    final_result: int = test_control_flow()
    print("Result:", final_result)
    exit(0)