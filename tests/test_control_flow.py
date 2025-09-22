#!/usr/bin/env python3
"""
Test Control Flow Implementation

Simple test program to verify if/while/for control flow works correctly.
"""

def test_control_flow() -> None:
    """
    Test function with control flow statements.

    Tests basic control flow constructs and verifies expected behavior.
    """
    result: int = 0

    # Test if statement
    if result == 0:
        result = result + 1

    # Verify if statement worked
    assert result == 1, "If statement should increment result to 1"

    # Test while loop
    counter: int = 0
    while counter < 3:
        result = result + 1
        counter = counter + 1

    # Verify while loop worked (1 + 3 = 4)
    assert result == 4, "While loop should increment result to 4"

    # Test for loop
    for i in range(5):
        result = result + 1

    # Verify for loop worked (4 + 5 = 9)
    assert result == 9, "For loop should increment result to 9"


if __name__ == "__main__":
    test_control_flow()
    print("Control flow test completed successfully")
    exit(0)