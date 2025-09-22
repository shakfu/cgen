"""Tests for Additional Operators (Bitwise, Logical, Increment, Decrement, Compound Assignment)."""

import pytest
from cgen.core import CFactory, Writer, StyleOptions


class TestBitwiseOperators:
    """Test bitwise operator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_bitwise_and_operator(self):
        """Test bitwise AND operator (&)."""
        bitwise_and = self.c.bitwise_and("a", "b")

        assert bitwise_and.left == "a"
        assert bitwise_and.operator == "&"
        assert bitwise_and.right == "b"

    def test_bitwise_or_operator(self):
        """Test bitwise OR operator (|)."""
        bitwise_or = self.c.bitwise_or("x", "y")

        assert bitwise_or.left == "x"
        assert bitwise_or.operator == "|"
        assert bitwise_or.right == "y"

    def test_bitwise_xor_operator(self):
        """Test bitwise XOR operator (^)."""
        bitwise_xor = self.c.bitwise_xor("m", "n")

        assert bitwise_xor.left == "m"
        assert bitwise_xor.operator == "^"
        assert bitwise_xor.right == "n"

    def test_bitwise_not_operator(self):
        """Test bitwise NOT operator (~)."""
        bitwise_not = self.c.bitwise_not("value")

        assert bitwise_not.left == "value"
        assert bitwise_not.operator == "~"
        assert bitwise_not.right is None

    def test_bitwise_left_shift_operator(self):
        """Test bitwise left shift operator (<<)."""
        left_shift = self.c.bitwise_left_shift("num", "2")

        assert left_shift.left == "num"
        assert left_shift.operator == "<<"
        assert left_shift.right == "2"

    def test_bitwise_right_shift_operator(self):
        """Test bitwise right shift operator (>>)."""
        right_shift = self.c.bitwise_right_shift("num", "3")

        assert right_shift.left == "num"
        assert right_shift.operator == ">>"
        assert right_shift.right == "3"

    def test_bitwise_operators_writing(self):
        """Test bitwise operators code generation."""
        # AND operator
        bitwise_and = self.c.bitwise_and("a", "b")
        output = self.writer.write_str_elem(bitwise_and)
        assert "a & b" in output

        # OR operator
        bitwise_or = self.c.bitwise_or("x", "y")
        output = self.writer.write_str_elem(bitwise_or)
        assert "x | y" in output

        # XOR operator
        bitwise_xor = self.c.bitwise_xor("m", "n")
        output = self.writer.write_str_elem(bitwise_xor)
        assert "m ^ n" in output

        # NOT operator (unary)
        bitwise_not = self.c.bitwise_not("value")
        output = self.writer.write_str_elem(bitwise_not)
        assert "~value" in output

        # Left shift operator
        left_shift = self.c.bitwise_left_shift("num", "2")
        output = self.writer.write_str_elem(left_shift)
        assert "num << 2" in output

        # Right shift operator
        right_shift = self.c.bitwise_right_shift("num", "3")
        output = self.writer.write_str_elem(right_shift)
        assert "num >> 3" in output

    def test_bitwise_operator_validation(self):
        """Test bitwise operator input validation."""
        # Valid operators should work
        self.c.bitwise_and("a", "b")
        self.c.bitwise_not("value")

        # Invalid operator should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import BitwiseOperator
            BitwiseOperator("a", "invalid", "b")

        # Unary operator with right operand should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import BitwiseOperator
            BitwiseOperator("a", "~", "b")

        # Binary operator without right operand should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import BitwiseOperator
            BitwiseOperator("a", "&")


class TestLogicalOperators:
    """Test logical operator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_logical_and_operator(self):
        """Test logical AND operator (&&)."""
        logical_and = self.c.logical_and("a", "b")

        assert logical_and.left == "a"
        assert logical_and.operator == "&&"
        assert logical_and.right == "b"

    def test_logical_or_operator(self):
        """Test logical OR operator (||)."""
        logical_or = self.c.logical_or("x", "y")

        assert logical_or.left == "x"
        assert logical_or.operator == "||"
        assert logical_or.right == "y"

    def test_logical_not_operator(self):
        """Test logical NOT operator (!)."""
        logical_not = self.c.logical_not("condition")

        assert logical_not.left == "condition"
        assert logical_not.operator == "!"
        assert logical_not.right is None

    def test_logical_operators_writing(self):
        """Test logical operators code generation."""
        # AND operator
        logical_and = self.c.logical_and("a", "b")
        output = self.writer.write_str_elem(logical_and)
        assert "a && b" in output

        # OR operator
        logical_or = self.c.logical_or("x", "y")
        output = self.writer.write_str_elem(logical_or)
        assert "x || y" in output

        # NOT operator (unary)
        logical_not = self.c.logical_not("condition")
        output = self.writer.write_str_elem(logical_not)
        assert "!condition" in output

    def test_logical_operator_validation(self):
        """Test logical operator input validation."""
        # Valid operators should work
        self.c.logical_and("a", "b")
        self.c.logical_not("condition")

        # Invalid operator should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import LogicalOperator
            LogicalOperator("a", "invalid", "b")

        # Unary operator with right operand should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import LogicalOperator
            LogicalOperator("a", "!", "b")

        # Binary operator without right operand should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import LogicalOperator
            LogicalOperator("a", "&&")


class TestIncrementOperators:
    """Test increment operator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_prefix_increment_operator(self):
        """Test prefix increment operator (++var)."""
        pre_inc = self.c.pre_increment("counter")

        assert pre_inc.operand == "counter"
        assert pre_inc.prefix is True

    def test_postfix_increment_operator(self):
        """Test postfix increment operator (var++)."""
        post_inc = self.c.post_increment("index")

        assert post_inc.operand == "index"
        assert post_inc.prefix is False

    def test_increment_operators_writing(self):
        """Test increment operators code generation."""
        # Prefix increment
        pre_inc = self.c.pre_increment("counter")
        output = self.writer.write_str_elem(pre_inc)
        assert "++counter" in output

        # Postfix increment
        post_inc = self.c.post_increment("index")
        output = self.writer.write_str_elem(post_inc)
        assert "index++" in output

    def test_increment_operator_validation(self):
        """Test increment operator input validation."""
        # Valid operands should work
        self.c.pre_increment("valid_var")
        self.c.post_increment("valid_var")

        # Empty operand should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import IncrementOperator
            IncrementOperator("")


class TestDecrementOperators:
    """Test decrement operator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_prefix_decrement_operator(self):
        """Test prefix decrement operator (--var)."""
        pre_dec = self.c.pre_decrement("counter")

        assert pre_dec.operand == "counter"
        assert pre_dec.prefix is True

    def test_postfix_decrement_operator(self):
        """Test postfix decrement operator (var--)."""
        post_dec = self.c.post_decrement("index")

        assert post_dec.operand == "index"
        assert post_dec.prefix is False

    def test_decrement_operators_writing(self):
        """Test decrement operators code generation."""
        # Prefix decrement
        pre_dec = self.c.pre_decrement("counter")
        output = self.writer.write_str_elem(pre_dec)
        assert "--counter" in output

        # Postfix decrement
        post_dec = self.c.post_decrement("index")
        output = self.writer.write_str_elem(post_dec)
        assert "index--" in output

    def test_decrement_operator_validation(self):
        """Test decrement operator input validation."""
        # Valid operands should work
        self.c.pre_decrement("valid_var")
        self.c.post_decrement("valid_var")

        # Empty operand should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import DecrementOperator
            DecrementOperator("")


class TestCompoundAssignmentOperators:
    """Test compound assignment operator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_arithmetic_compound_assignments(self):
        """Test arithmetic compound assignment operators."""
        # Addition assignment
        add_assign = self.c.add_assign("x", "5")
        assert add_assign.left == "x"
        assert add_assign.operator == "+="
        assert add_assign.right == "5"

        # Subtraction assignment
        sub_assign = self.c.sub_assign("y", "3")
        assert sub_assign.operator == "-="

        # Multiplication assignment
        mul_assign = self.c.mul_assign("z", "2")
        assert mul_assign.operator == "*="

        # Division assignment
        div_assign = self.c.div_assign("w", "4")
        assert div_assign.operator == "/="

        # Modulo assignment
        mod_assign = self.c.mod_assign("a", "7")
        assert mod_assign.operator == "%="

    def test_bitwise_compound_assignments(self):
        """Test bitwise compound assignment operators."""
        # Bitwise AND assignment
        and_assign = self.c.bitwise_and_assign("flags", "mask")
        assert and_assign.operator == "&="

        # Bitwise OR assignment
        or_assign = self.c.bitwise_or_assign("flags", "bit")
        assert or_assign.operator == "|="

        # Bitwise XOR assignment
        xor_assign = self.c.bitwise_xor_assign("data", "key")
        assert xor_assign.operator == "^="

        # Left shift assignment
        lshift_assign = self.c.left_shift_assign("value", "2")
        assert lshift_assign.operator == "<<="

        # Right shift assignment
        rshift_assign = self.c.right_shift_assign("value", "1")
        assert rshift_assign.operator == ">>="

    def test_compound_assignment_writing(self):
        """Test compound assignment operators code generation."""
        # Arithmetic assignments
        add_assign = self.c.add_assign("x", "5")
        output = self.writer.write_str_elem(add_assign)
        assert "x += 5" in output

        sub_assign = self.c.sub_assign("y", "3")
        output = self.writer.write_str_elem(sub_assign)
        assert "y -= 3" in output

        mul_assign = self.c.mul_assign("z", "2")
        output = self.writer.write_str_elem(mul_assign)
        assert "z *= 2" in output

        div_assign = self.c.div_assign("w", "4")
        output = self.writer.write_str_elem(div_assign)
        assert "w /= 4" in output

        mod_assign = self.c.mod_assign("a", "7")
        output = self.writer.write_str_elem(mod_assign)
        assert "a %= 7" in output

        # Bitwise assignments
        and_assign = self.c.bitwise_and_assign("flags", "mask")
        output = self.writer.write_str_elem(and_assign)
        assert "flags &= mask" in output

        or_assign = self.c.bitwise_or_assign("flags", "bit")
        output = self.writer.write_str_elem(or_assign)
        assert "flags |= bit" in output

        xor_assign = self.c.bitwise_xor_assign("data", "key")
        output = self.writer.write_str_elem(xor_assign)
        assert "data ^= key" in output

        lshift_assign = self.c.left_shift_assign("value", "2")
        output = self.writer.write_str_elem(lshift_assign)
        assert "value <<= 2" in output

        rshift_assign = self.c.right_shift_assign("value", "1")
        output = self.writer.write_str_elem(rshift_assign)
        assert "value >>= 1" in output

    def test_compound_assignment_validation(self):
        """Test compound assignment operator input validation."""
        # Valid operators should work
        self.c.add_assign("x", "5")
        self.c.bitwise_and_assign("flags", "mask")

        # Invalid operator should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import CompoundAssignmentOperator
            CompoundAssignmentOperator("x", "invalid", "5")

        # Empty operands should raise ValueError
        with pytest.raises(ValueError):
            from cgen.core.core import CompoundAssignmentOperator
            CompoundAssignmentOperator("", "+=", "5")

        with pytest.raises(ValueError):
            from cgen.core.core import CompoundAssignmentOperator
            CompoundAssignmentOperator("x", "+=", "")


class TestOperatorIntegration:
    """Integration tests for all operator types."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_complex_expression_with_operators(self):
        """Test complex expressions using multiple operator types."""
        # Create a sequence with various operators
        seq = self.c.sequence()

        # Variable declarations
        seq.append(self.c.declaration(self.c.variable("result", "int"), "0"))
        seq.append(self.c.declaration(self.c.variable("flags", "unsigned int"), "0xFF"))
        seq.append(self.c.declaration(self.c.variable("counter", "int"), "10"))

        # Compound assignments
        seq.append(self.c.statement(self.c.add_assign("result", "5")))
        seq.append(self.c.statement(self.c.bitwise_and_assign("flags", "0x0F")))

        # Increment/decrement operations
        seq.append(self.c.statement(self.c.pre_increment("counter")))
        seq.append(self.c.statement(self.c.post_decrement("result")))

        # Bitwise operations
        seq.append(self.c.statement(self.c.assignment("flags", self.c.bitwise_or("flags", "0x80"))))

        # Logical operations
        condition = self.c.logical_and("result > 0", "counter < 20")
        if_stmt = self.c.if_statement(condition, self.c.statement("printf(\"Success\")"))
        seq.append(if_stmt)

        output = self.writer.write_str(seq)

        assert "result += 5" in output
        assert "flags &= 0x0F" in output
        assert "++counter" in output
        assert "result--" in output
        assert "flags | 0x80" in output
        assert "result > 0 && counter < 20" in output

    def test_nested_operators(self):
        """Test nested operator expressions."""
        # Create nested bitwise and logical operations
        bitwise_expr = self.c.bitwise_and("value", "mask")
        logical_expr = self.c.logical_not(bitwise_expr)

        output = self.writer.write_str_elem(logical_expr)
        assert "!" in output
        assert "value & mask" in output

    def test_operators_in_control_flow(self):
        """Test operators within control flow structures."""
        # Switch statement with bitwise operations
        case1 = self.c.case_statement(1, [
            self.c.statement(self.c.bitwise_or_assign("flags", "FLAG_SET")),
            self.c.break_statement()
        ])

        case2 = self.c.case_statement(2, [
            self.c.statement(self.c.bitwise_and_assign("flags", "~FLAG_CLEAR")),
            self.c.break_statement()
        ])

        switch = self.c.switch_statement(self.c.bitwise_and("input", "0x0F"), [case1, case2])
        output = self.writer.write_str_elem(switch)

        assert "switch (input & 0x0F)" in output
        assert "flags |= FLAG_SET" in output
        assert "flags &= ~FLAG_CLEAR" in output

    def test_loop_with_increment_operators(self):
        """Test increment operators in loop constructs."""
        # For loop with pre-increment
        init = self.c.assignment("i", "0")
        condition = "i < 10"
        increment = self.c.pre_increment("i")
        body = self.c.statement(self.c.add_assign("sum", "i"))

        for_loop = self.c.for_loop(init, condition, increment, body)
        output = self.writer.write_str_elem(for_loop)

        assert "i = 0" in output
        assert "i < 10" in output
        assert "++i" in output
        assert "sum += i" in output

    def test_operator_precedence_handling(self):
        """Test that operators are written correctly for precedence."""
        # Test that parentheses and spacing are handled correctly
        expr1 = self.c.bitwise_and("a", "b")
        expr2 = self.c.bitwise_or(expr1, "c")

        output = self.writer.write_str_elem(expr2)
        # Should contain both operations properly formatted
        assert "&" in output
        assert "|" in output