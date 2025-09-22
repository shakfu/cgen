#!/usr/bin/env python3
"""
TIER 2 Syntactical Elements Demonstration

This script demonstrates the usage of TIER 2 syntactical elements in CGen,
including break/continue statements, do-while loops, ternary operators,
sizeof operators, and address-of/dereference operators.
"""

import cgen.core as cfile


def demonstrate_break_continue():
    """Demonstrate break and continue statements."""
    print("=== Break and Continue Statements ===")

    C = cfile.CFactory()
    writer = cfile.Writer(cfile.StyleOptions())

    # Create a function with break and continue
    func_body = C.block()

    # For loop with break and continue
    loop_body = C.block()
    loop_body.append(C.statement("if (i % 2 == 0)"))
    loop_body.append(C.continue_statement())
    loop_body.append(C.statement("if (i > 8)"))
    loop_body.append(C.break_statement())
    loop_body.append(C.statement("printf(\"%d \", i)"))

    for_loop = C.for_loop("int i = 0", "i < 10", "i++", loop_body)
    func_body.append(for_loop)

    func = C.function("demo_break_continue", "void")
    func_decl = C.declaration(func)

    seq = C.sequence()
    seq.append(func_decl)
    seq.append(C.block([for_loop]))

    print(writer.write_str(seq))
    print()


def demonstrate_do_while():
    """Demonstrate do-while loops."""
    print("=== Do-While Loops ===")

    C = cfile.CFactory()
    writer = cfile.Writer(cfile.StyleOptions())

    # Simple do-while loop
    loop_body = C.block()
    loop_body.append(C.statement("printf(\"Count: %d\\n\", count)"))
    loop_body.append(C.statement("count++"))

    do_while = C.do_while_loop(loop_body, "count < 5")

    # Function with do-while
    func_body = C.block()
    func_body.append(C.statement("int count = 0"))
    func_body.append(do_while)

    func = C.function("demo_do_while", "void")
    func_decl = C.declaration(func)

    seq = C.sequence()
    seq.append(func_decl)
    seq.append(func_body)

    print(writer.write_str(seq))
    print()


def demonstrate_ternary():
    """Demonstrate ternary operators."""
    print("=== Ternary Operators ===")

    C = cfile.CFactory()
    writer = cfile.Writer(cfile.StyleOptions())

    # Simple ternary
    ternary = C.ternary("x > 0", "x", "-x")

    # Nested ternary
    inner_ternary = C.ternary("y != 0", "y", "1")
    outer_ternary = C.ternary("x > 0", inner_ternary, "0")

    # Function using ternary operators
    func_body = C.block()
    func_body.append(C.statement(f"int abs_x = {writer.write_str_elem(ternary)}"))
    func_body.append(C.statement(f"int safe_div = x / {writer.write_str_elem(inner_ternary)}"))
    func_body.append(C.statement(f"int complex_result = {writer.write_str_elem(outer_ternary)}"))
    func_body.append(C.statement("return abs_x + safe_div + complex_result"))

    func = C.function("demo_ternary", "int", params=[
        C.variable("x", "int"),
        C.variable("y", "int")
    ])
    func_decl = C.declaration(func)

    seq = C.sequence()
    seq.append(func_decl)
    seq.append(func_body)

    print(writer.write_str(seq))
    print()


def demonstrate_sizeof():
    """Demonstrate sizeof operators."""
    print("=== Sizeof Operators ===")

    C = cfile.CFactory()
    writer = cfile.Writer(cfile.StyleOptions())

    # Different sizeof usages
    sizeof_int = C.sizeof("int")
    sizeof_double = C.sizeof("double")
    sizeof_var = C.sizeof("array")

    # Function using sizeof
    func_body = C.block()
    func_body.append(C.statement(f"size_t int_size = {writer.write_str_elem(sizeof_int)}"))
    func_body.append(C.statement(f"size_t double_size = {writer.write_str_elem(sizeof_double)}"))
    func_body.append(C.statement(f"size_t array_size = {writer.write_str_elem(sizeof_var)}"))
    func_body.append(C.statement("printf(\"int: %zu, double: %zu, array: %zu\\n\", int_size, double_size, array_size)"))

    # Add parameter for array
    func = C.function("demo_sizeof", "void", params=[
        C.variable("array", "int", array=10)
    ])
    func_decl = C.declaration(func)

    seq = C.sequence()
    seq.append(C.sysinclude("stdio.h"))
    seq.append(C.sysinclude("stddef.h"))
    seq.append(func_decl)
    seq.append(func_body)

    print(writer.write_str(seq))
    print()


def demonstrate_address_dereference():
    """Demonstrate address-of and dereference operators."""
    print("=== Address-of and Dereference Operators ===")

    C = cfile.CFactory()
    writer = cfile.Writer(cfile.StyleOptions())

    # Address-of and dereference operations
    addr_x = C.address_of("x")
    deref_ptr = C.dereference("ptr")
    addr_array = C.address_of("array[0]")

    # Function using pointer operations
    func_body = C.block()
    func_body.append(C.statement(f"int *ptr = {writer.write_str_elem(addr_x)}"))
    func_body.append(C.statement(f"int value = {writer.write_str_elem(deref_ptr)}"))
    func_body.append(C.statement(f"int *first_elem = {writer.write_str_elem(addr_array)}"))
    func_body.append(C.statement("printf(\"Address of x: %p\\n\", (void*)ptr)"))
    func_body.append(C.statement("printf(\"Value at ptr: %d\\n\", value)"))
    func_body.append(C.statement("printf(\"Address of array[0]: %p\\n\", (void*)first_elem)"))

    func = C.function("demo_pointers", "void", params=[
        C.variable("x", "int"),
        C.variable("array", "int", array=5)
    ])
    func_decl = C.declaration(func)

    seq = C.sequence()
    seq.append(C.sysinclude("stdio.h"))
    seq.append(func_decl)
    seq.append(func_body)

    print(writer.write_str(seq))
    print()


def demonstrate_complex_example():
    """Demonstrate a complex example using multiple TIER 2 elements."""
    print("=== Complex Example with Multiple TIER 2 Elements ===")

    C = cfile.CFactory()
    writer = cfile.Writer(cfile.StyleOptions())

    # Complex function combining all TIER 2 elements
    func_body = C.block()

    # Variable declarations
    func_body.append(C.statement("int *ptr = NULL"))
    func_body.append(C.statement("int count = 0"))
    func_body.append(C.statement("int i"))

    # Do-while loop with break/continue and ternary
    do_while_body = C.block()

    # Use ternary operator in assignment
    ternary = C.ternary("count % 3 == 0", "count * 2", "count")
    do_while_body.append(C.statement(f"i = {writer.write_str_elem(ternary)}"))

    # Use address-of operator
    addr_i = C.address_of("i")
    do_while_body.append(C.statement(f"ptr = {writer.write_str_elem(addr_i)}"))

    # Use dereference operator
    deref_ptr = C.dereference("ptr")
    do_while_body.append(C.statement("if (count > 0 && count % 2 == 0)"))
    do_while_body.append(C.continue_statement())

    # Use sizeof operator
    sizeof_int = C.sizeof("int")
    do_while_body.append(C.statement(f"printf(\"Value: %d, Size: %zu\\n\", {writer.write_str_elem(deref_ptr)}, {writer.write_str_elem(sizeof_int)})"))

    do_while_body.append(C.statement("count++"))
    do_while_body.append(C.statement("if (count > 10)"))
    do_while_body.append(C.break_statement())

    do_while = C.do_while_loop(do_while_body, "count < 20")
    func_body.append(do_while)

    func_body.append(C.statement("return count"))

    func = C.function("complex_demo", "int")
    func_decl = C.declaration(func)

    seq = C.sequence()
    seq.append(C.sysinclude("stdio.h"))
    seq.append(C.sysinclude("stddef.h"))
    seq.append(func_decl)
    seq.append(func_body)

    print(writer.write_str(seq))
    print()


def main():
    """Main demonstration function."""
    print("CGen TIER 2 Syntactical Elements Demonstration")
    print("=" * 50)
    print()

    demonstrate_break_continue()
    demonstrate_do_while()
    demonstrate_ternary()
    demonstrate_sizeof()
    demonstrate_address_dereference()
    demonstrate_complex_example()

    print("Demonstration complete!")
    print("All TIER 2 elements are now available in CGen!")


if __name__ == "__main__":
    main()