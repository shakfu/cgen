"""Pytest-style tests for TIER 2 syntactical elements."""

import pytest
import cgen.generator as cfile
from cgen.generator.core import (
    BreakStatement,
    ContinueStatement,
    DoWhileLoop,
    TernaryOperator,
    SizeofOperator,
    AddressOfOperator,
    DereferenceOperator,
)


class TestBreakStatement:
    """Test break statement functionality."""

    def test_break_statement_creation(self):
        """Test basic break statement creation."""
        stmt = BreakStatement()
        assert stmt is not None

    def test_break_statement_writer(self):
        """Test break statement code generation."""
        stmt = BreakStatement()
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(stmt)
        assert output == "break"

    def test_break_statement_in_sequence(self):
        """Test break statement in a sequence."""
        C = cfile.CFactory()
        seq = C.sequence()
        seq.append(C.break_statement())
        seq.append(C.statement(";"))

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str(seq)
        assert "break;" in output


class TestContinueStatement:
    """Test continue statement functionality."""

    def test_continue_statement_creation(self):
        """Test basic continue statement creation."""
        stmt = ContinueStatement()
        assert stmt is not None

    def test_continue_statement_writer(self):
        """Test continue statement code generation."""
        stmt = ContinueStatement()
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(stmt)
        assert output == "continue"

    def test_continue_statement_in_sequence(self):
        """Test continue statement in a sequence."""
        C = cfile.CFactory()
        seq = C.sequence()
        seq.append(C.continue_statement())
        seq.append(C.statement(";"))

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str(seq)
        assert "continue;" in output


class TestDoWhileLoop:
    """Test do-while loop functionality."""

    def test_do_while_creation(self):
        """Test basic do-while loop creation."""
        body = "printf(\"Hello\");"
        condition = "i < 10"
        loop = DoWhileLoop(body, condition)
        assert loop is not None
        assert loop.condition == condition

    def test_do_while_writer_simple(self):
        """Test do-while loop code generation with simple body."""
        body = "i++"
        condition = "i < 10"
        loop = DoWhileLoop(body, condition)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(loop)

        assert "do" in output
        assert "while (i < 10)" in output
        assert "i++" in output

    def test_do_while_with_block_body(self):
        """Test do-while loop with block body."""
        C = cfile.CFactory()
        body = C.block()
        body.append(C.statement("i++"))
        body.append(C.statement("printf(\"Hello\")"))

        condition = "i < 10"
        loop = DoWhileLoop(body, condition)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(loop)

        assert "do" in output
        assert "while (i < 10)" in output
        assert "i++" in output
        assert "printf" in output

    def test_do_while_factory_method(self):
        """Test do-while loop creation via factory."""
        C = cfile.CFactory()
        loop = C.do_while_loop("i++", "i < 10")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(loop)

        assert "do" in output
        assert "while (i < 10)" in output


class TestTernaryOperator:
    """Test ternary operator functionality."""

    def test_ternary_creation(self):
        """Test basic ternary operator creation."""
        ternary = TernaryOperator("x > 0", "1", "0")
        assert ternary is not None
        assert ternary.condition == "x > 0"
        assert ternary.true_expr == "1"
        assert ternary.false_expr == "0"

    def test_ternary_writer(self):
        """Test ternary operator code generation."""
        ternary = TernaryOperator("x > 0", "1", "0")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(ternary)

        assert output == "x > 0 ? 1 : 0"

    def test_ternary_complex_expressions(self):
        """Test ternary operator with complex expressions."""
        ternary = TernaryOperator("a + b > c", "func1()", "func2()")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(ternary)

        assert output == "a + b > c ? func1() : func2()"

    def test_ternary_factory_method(self):
        """Test ternary operator creation via factory."""
        C = cfile.CFactory()
        ternary = C.ternary("x > 0", "positive", "negative")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(ternary)

        assert output == "x > 0 ? positive : negative"

    def test_ternary_nested(self):
        """Test nested ternary operators."""
        inner_ternary = TernaryOperator("y > 0", "1", "-1")
        outer_ternary = TernaryOperator("x > 0", inner_ternary, "0")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(outer_ternary)

        assert "x > 0 ?" in output
        assert "y > 0 ? 1 : -1" in output
        assert ": 0" in output


class TestSizeofOperator:
    """Test sizeof operator functionality."""

    def test_sizeof_creation_string(self):
        """Test sizeof operator creation with string operand."""
        sizeof = SizeofOperator("int")
        assert sizeof is not None
        assert sizeof.operand == "int"
        assert sizeof.is_type == True

    def test_sizeof_creation_variable(self):
        """Test sizeof operator creation with variable operand."""
        sizeof = SizeofOperator("myvar")
        assert sizeof is not None
        assert sizeof.operand == "myvar"

    def test_sizeof_writer_type(self):
        """Test sizeof operator code generation with type."""
        sizeof = SizeofOperator("int")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(sizeof)

        assert output == "sizeof(int)"

    def test_sizeof_writer_variable(self):
        """Test sizeof operator code generation with variable."""
        sizeof = SizeofOperator("myarray")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(sizeof)

        assert output == "sizeof(myarray)"

    def test_sizeof_factory_method(self):
        """Test sizeof operator creation via factory."""
        C = cfile.CFactory()
        sizeof = C.sizeof("double")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(sizeof)

        assert output == "sizeof(double)"

    def test_sizeof_with_type_object(self):
        """Test sizeof operator with Type object."""
        C = cfile.CFactory()
        int_type = C.type("int")
        sizeof = SizeofOperator(int_type)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(sizeof)

        assert "sizeof(" in output


class TestAddressOfOperator:
    """Test address-of operator functionality."""

    def test_address_of_creation(self):
        """Test basic address-of operator creation."""
        addr = AddressOfOperator("myvar")
        assert addr is not None
        assert addr.operand == "myvar"

    def test_address_of_writer(self):
        """Test address-of operator code generation."""
        addr = AddressOfOperator("myvar")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(addr)

        assert output == "&myvar"

    def test_address_of_factory_method(self):
        """Test address-of operator creation via factory."""
        C = cfile.CFactory()
        addr = C.address_of("variable")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(addr)

        assert output == "&variable"

    def test_address_of_invalid_identifier(self):
        """Test address-of operator with invalid identifier."""
        # Complex expressions are allowed, but empty strings should fail
        with pytest.raises((ValueError, TypeError)):
            AddressOfOperator("")

    def test_address_of_complex_expression(self):
        """Test address-of operator with array element."""
        addr = AddressOfOperator("array[0]")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(addr)

        assert output == "&array[0]"


class TestDereferenceOperator:
    """Test dereference operator functionality."""

    def test_dereference_creation(self):
        """Test basic dereference operator creation."""
        deref = DereferenceOperator("ptr")
        assert deref is not None
        assert deref.operand == "ptr"

    def test_dereference_writer(self):
        """Test dereference operator code generation."""
        deref = DereferenceOperator("ptr")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(deref)

        assert output == "*ptr"

    def test_dereference_factory_method(self):
        """Test dereference operator creation via factory."""
        C = cfile.CFactory()
        deref = C.dereference("pointer")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(deref)

        assert output == "*pointer"

    def test_dereference_complex_expression(self):
        """Test dereference operator with complex expression."""
        deref = DereferenceOperator("(ptr + 1)")

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(deref)

        assert output == "*(ptr + 1)"

    def test_multiple_dereference(self):
        """Test multiple dereference operations."""
        deref1 = DereferenceOperator("ptr_to_ptr")
        deref2 = DereferenceOperator(deref1)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(deref2)

        assert "**" in output or "*(*" in output


class TestTier2Integration:
    """Test integration of TIER 2 elements with existing code."""

    def test_break_in_for_loop(self):
        """Test break statement inside for loop."""
        C = cfile.CFactory()

        # Create for loop with break
        loop_body = C.block()
        loop_body.append(C.statement("if (i == 5)"))
        loop_body.append(C.break_statement())

        for_loop = C.for_loop("int i = 0", "i < 10", "i++", loop_body)

        writer = cfile.Writer(cfile.StyleOptions())
        seq = C.sequence()
        seq.append(for_loop)
        output = writer.write_str(seq)

        assert "for (" in output
        assert "break" in output

    def test_continue_in_while_loop(self):
        """Test continue statement inside while loop."""
        C = cfile.CFactory()

        # Create while loop with continue
        loop_body = C.block()
        loop_body.append(C.statement("if (i % 2 == 0)"))
        loop_body.append(C.continue_statement())
        loop_body.append(C.statement("printf(\"%d\", i)"))

        while_loop = C.while_loop("i < 10", loop_body)

        writer = cfile.Writer(cfile.StyleOptions())
        seq = C.sequence()
        seq.append(while_loop)
        output = writer.write_str(seq)

        assert "while (" in output
        assert "continue" in output

    def test_ternary_in_assignment(self):
        """Test ternary operator in variable assignment."""
        C = cfile.CFactory()

        ternary = C.ternary("x > 0", "x", "-x")

        writer = cfile.Writer(cfile.StyleOptions())
        ternary_output = writer.write_str_elem(ternary)
        assignment = C.statement(f"int abs_x = {ternary_output}")
        output = writer.write_str_elem(assignment)

        assert "x > 0 ? x : -x" in output

    def test_sizeof_with_pointer_arithmetic(self):
        """Test sizeof operator with pointer arithmetic."""
        C = cfile.CFactory()

        sizeof_op = C.sizeof("int")

        writer = cfile.Writer(cfile.StyleOptions())
        sizeof_output = writer.write_str_elem(sizeof_op)
        assignment = C.statement(f"ptr += {sizeof_output}")
        output = writer.write_str_elem(assignment)

        assert "sizeof(int)" in output

    def test_address_and_dereference_combo(self):
        """Test combination of address-of and dereference operators."""
        C = cfile.CFactory()

        # Create: *(&var) (identity operation)
        addr = C.address_of("var")
        deref = C.dereference(addr)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(deref)

        assert "*" in output and "&" in output

    def test_complex_control_flow(self):
        """Test complex control flow with TIER 2 elements."""
        C = cfile.CFactory()
        seq = C.sequence()

        # Create a complex function with TIER 2 elements
        func_body = C.block()

        # Do-while loop with break and continue
        do_while_body = C.block()
        do_while_body.append(C.statement("if (flag) continue"))
        do_while_body.append(C.statement("count++"))
        do_while_body.append(C.statement("if (count > 10)"))
        do_while_body.append(C.break_statement())

        do_while = C.do_while_loop(do_while_body, "true")
        func_body.append(do_while)

        # Just test the do-while loop itself
        seq.append(do_while)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str(seq)

        assert "do" in output
        assert "while (true)" in output
        assert "break" in output


class TestTier2ErrorHandling:
    """Test error handling for TIER 2 elements."""

    def test_invalid_operand_types(self):
        """Test error handling for invalid operand types."""
        with pytest.raises((ValueError, TypeError, NotImplementedError)):
            TernaryOperator(None, "true", "false")

    def test_empty_operands(self):
        """Test error handling for empty operands."""
        with pytest.raises((ValueError, TypeError)):
            AddressOfOperator("")

    def test_complex_nested_structures(self):
        """Test deeply nested TIER 2 structures."""
        # This should work without errors
        ternary1 = TernaryOperator("a > b", "a", "b")
        ternary2 = TernaryOperator("c > d", ternary1, "d")

        sizeof_op = SizeofOperator("int")
        addr_op = AddressOfOperator("var")
        deref_op = DereferenceOperator(addr_op)

        # All should be creatable without errors
        assert ternary1 is not None
        assert ternary2 is not None
        assert sizeof_op is not None
        assert addr_op is not None
        assert deref_op is not None


if __name__ == "__main__":
    pytest.main([__file__])