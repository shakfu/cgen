#include <stdio.h>
#include <stdbool.h>

"
Test program to verify TIER 1 operator implementations.

Tests the newly implemented operators:
- Logical operators (&&, ||, !)
- Bitwise operators (&, |, ^, ~, <<, >>)
- Compound assignment operators (+=, -=, *=, /=, %=, &=, |=, ^=, <<=, >>=)
- Unary operators (+, -, !, ~)
";
bool test_logical_operators(bool a, bool b)
{
    bool result1;
    result1 = (a && b);
    bool result2;
    result2 = (a || b);
    bool result3;
    result3 = !a;
    bool result4;
    result4 = !b;
    bool complex_result;
    complex_result = ((a && b) || (!a && !b));
    return complex_result;
}

int test_bitwise_operators(int x, int y)
{
    int and_result;
    and_result = x & y;
    int or_result;
    or_result = x | y;
    int xor_result;
    xor_result = x ^ y;
    int not_x;
    not_x = ~x;
    int not_y;
    not_y = ~y;
    int left_shift;
    left_shift = x << 2;
    int right_shift;
    right_shift = y >> 1;
    return and_result + or_result + xor_result;
}

int test_compound_assignment(void)
{
    int value;
    value = 10;
    value += 5;
    value -= 3;
    value *= 2;
    value /= 3;
    value %= 5;
    int bit_value;
    bit_value = 15;
    bit_value &= 7;
    bit_value |= 8;
    bit_value ^= 3;
    bit_value <<= 1;
    bit_value >>= 2;
    return value + bit_value;
}

int test_unary_operators(int num)
{
    int positive;
    positive = +num;
    int negative;
    negative = -num;
    int inverted;
    inverted = ~num;
    return positive + negative + inverted;
}

bool test_complex_expressions(int a, int b, bool flag)
{
    int result1;
    result1 = a + b & 255;
    int result2;
    result2 = a << 1 | b >> 1;
    bool condition1;
    condition1 = (result1 > 50 && result2 < 100);
    bool condition2;
    condition2 = (flag || a != b);
    bool condition3;
    condition3 = (!flag && result1 == result2);
    bool final_result;
    final_result = (condition1 || condition2 || condition3);
    return final_result;
}

int main(void)
{
    print("Testing TIER 1 operators...");
    bool logical_result;
    logical_result = test_logical_operators(true, false);
    print("Logical operators test result:", logical_result);
    int bitwise_result;
    bitwise_result = test_bitwise_operators(10, 12);
    print("Bitwise operators test result:", bitwise_result);
    int compound_result;
    compound_result = test_compound_assignment();
    print("Compound assignment test result:", compound_result);
    int unary_result;
    unary_result = test_unary_operators(42);
    print("Unary operators test result:", unary_result);
    bool complex_result;
    complex_result = test_complex_expressions(25, 17, true);
    print("Complex expressions test result:", complex_result);
    return 0;
}

if (__name__ == "__main__")
{
    int exit_code; exit_code = main();
    print("Program completed with exit code:", exit_code);
}
