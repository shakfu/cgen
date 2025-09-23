"""Tests for Additional Control Flow Elements (Switch, Goto, Labels)."""

import pytest
from cgen.generator import CFactory, Writer, StyleOptions


class TestSwitchStatements:
    """Test switch statement functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_switch_statement_basic(self):
        """Test basic switch statement creation."""
        switch = self.c.switch_statement("x")

        assert switch.expression == "x"
        assert len(switch.cases) == 0
        assert switch.default_case is None

    def test_switch_statement_with_cases(self):
        """Test switch statement with cases."""
        case1 = self.c.case_statement(1, ["printf(\"one\")"])
        case2 = self.c.case_statement(2, ["printf(\"two\")"])
        default = self.c.default_case(["printf(\"other\")"])

        switch = self.c.switch_statement("value", [case1, case2], default)

        assert len(switch.cases) == 2
        assert switch.default_case == default

    def test_switch_statement_writing(self):
        """Test switch statement code generation."""
        # Basic switch with no cases
        switch = self.c.switch_statement("x")
        output = self.writer.write_str_elem(switch)
        assert "switch (x)" in output
        assert "{" in output and "}" in output

        # Switch with cases and default
        case1 = self.c.case_statement(1, [self.c.statement("printf(\"one\")")])
        case2 = self.c.case_statement(2, [self.c.statement("printf(\"two\")")])
        default = self.c.default_case([self.c.statement("printf(\"other\")")])

        switch = self.c.switch_statement("value", [case1, case2], default)
        output = self.writer.write_str_elem(switch)

        assert "switch (value)" in output
        assert "case 1:" in output
        assert "case 2:" in output
        assert "default:" in output
        assert "printf(\"one\")" in output
        assert "printf(\"two\")" in output
        assert "printf(\"other\")" in output

    def test_switch_with_break_statements(self):
        """Test switch with break statements."""
        case1 = self.c.case_statement("'a'", [
            self.c.statement("printf(\"Letter A\")"),
            self.c.break_statement()
        ])
        case2 = self.c.case_statement("'b'", [
            self.c.statement("printf(\"Letter B\")"),
            self.c.break_statement()
        ])
        default = self.c.default_case([
            self.c.statement("printf(\"Unknown\")"),
            self.c.break_statement()
        ])

        switch = self.c.switch_statement("ch", [case1, case2], default)
        output = self.writer.write_str_elem(switch)

        assert "switch (ch)" in output
        assert "case 'a':" in output
        assert "case 'b':" in output
        assert "default:" in output
        assert "break;" in output

    def test_switch_add_case_method(self):
        """Test adding cases dynamically."""
        switch = self.c.switch_statement("x")
        case1 = self.c.case_statement(1, ["return 1"])

        switch.add_case(case1)
        assert len(switch.cases) == 1
        assert switch.cases[0] == case1

    def test_switch_set_default_method(self):
        """Test setting default case dynamically."""
        switch = self.c.switch_statement("x")
        default = self.c.default_case(["return -1"])

        switch.set_default(default)
        assert switch.default_case == default


class TestCaseStatements:
    """Test case statement functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_case_statement_basic(self):
        """Test basic case statement creation."""
        case = self.c.case_statement(42)

        assert case.value == 42
        assert len(case.statements) == 0

    def test_case_statement_with_statements(self):
        """Test case statement with statements."""
        statements = ["printf(\"forty-two\")", "break"]
        case = self.c.case_statement(42, statements)

        assert case.value == 42
        assert len(case.statements) == 2

    def test_case_statement_writing(self):
        """Test case statement code generation."""
        # Basic case with no statements
        case = self.c.case_statement(42)
        output = self.writer.write_str_elem(case)
        assert "case 42:" in output

        # Case with statements
        case = self.c.case_statement("'x'", [
            self.c.statement("printf(\"X pressed\")"),
            self.c.break_statement()
        ])
        output = self.writer.write_str_elem(case)
        assert "case 'x':" in output
        assert "printf(\"X pressed\")" in output
        assert "break;" in output

    def test_case_add_statement_method(self):
        """Test adding statements dynamically."""
        case = self.c.case_statement(1)
        case.add_statement("printf(\"one\")")

        assert len(case.statements) == 1
        assert case.statements[0] == "printf(\"one\")"

    def test_case_statement_validation(self):
        """Test case statement input validation."""
        # Valid inputs should work
        case = self.c.case_statement(123)
        assert case.value == 123

        # String values should work
        case = self.c.case_statement("'A'")
        assert case.value == "'A'"


class TestDefaultCase:
    """Test default case functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_default_case_basic(self):
        """Test basic default case creation."""
        default = self.c.default_case()

        assert len(default.statements) == 0

    def test_default_case_with_statements(self):
        """Test default case with statements."""
        statements = ["printf(\"default case\")", "break"]
        default = self.c.default_case(statements)

        assert len(default.statements) == 2

    def test_default_case_writing(self):
        """Test default case code generation."""
        # Basic default with no statements
        default = self.c.default_case()
        output = self.writer.write_str_elem(default)
        assert "default:" in output

        # Default with statements
        default = self.c.default_case([
            self.c.statement("printf(\"default case\")"),
            self.c.break_statement()
        ])
        output = self.writer.write_str_elem(default)
        assert "default:" in output
        assert "printf(\"default case\")" in output
        assert "break;" in output

    def test_default_add_statement_method(self):
        """Test adding statements dynamically."""
        default = self.c.default_case()
        default.add_statement("printf(\"default\")")

        assert len(default.statements) == 1
        assert default.statements[0] == "printf(\"default\")"


class TestGotoStatements:
    """Test goto statement functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_goto_statement_basic(self):
        """Test basic goto statement creation."""
        goto = self.c.goto_statement("error_exit")

        assert goto.label == "error_exit"

    def test_goto_statement_writing(self):
        """Test goto statement code generation."""
        goto = self.c.goto_statement("cleanup")
        output = self.writer.write_str_elem(goto)
        assert "goto cleanup" in output

    def test_goto_statement_validation(self):
        """Test goto statement input validation."""
        # Valid label should work
        goto = self.c.goto_statement("valid_label")
        assert goto.label == "valid_label"

        # Invalid labels should raise ValueError
        with pytest.raises(ValueError):
            self.c.goto_statement("")

        with pytest.raises(ValueError):
            self.c.goto_statement("123invalid")  # starts with number


class TestLabels:
    """Test label functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_label_basic(self):
        """Test basic label creation."""
        label = self.c.label("start")

        assert label.name == "start"

    def test_label_writing(self):
        """Test label code generation."""
        label = self.c.label("error_exit")
        output = self.writer.write_str_elem(label)
        assert "error_exit:" in output

    def test_label_validation(self):
        """Test label input validation."""
        # Valid label should work
        label = self.c.label("valid_label")
        assert label.name == "valid_label"

        # Invalid labels should raise ValueError
        with pytest.raises(ValueError):
            self.c.label("")

        with pytest.raises(ValueError):
            self.c.label("123invalid")  # starts with number


class TestControlFlowIntegration:
    """Integration tests for control flow elements."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_complete_switch_example(self):
        """Test complete switch statement example."""
        # Create a complete switch with multiple cases, fallthrough, and goto
        case1 = self.c.case_statement(1, [
            self.c.statement("printf(\"Case 1\")")
            # No break - fallthrough to case 2
        ])

        case2 = self.c.case_statement(2, [
            self.c.statement("printf(\"Case 1 or 2\")"),
            self.c.break_statement()
        ])

        case3 = self.c.case_statement(3, [
            self.c.statement("printf(\"Case 3\")"),
            self.c.goto_statement("cleanup")
        ])

        default = self.c.default_case([
            self.c.statement("printf(\"Unknown case\")"),
            self.c.goto_statement("error")
        ])

        switch = self.c.switch_statement("value", [case1, case2, case3], default)
        output = self.writer.write_str_elem(switch)

        assert "switch (value)" in output
        assert "case 1:" in output
        assert "case 2:" in output
        assert "case 3:" in output
        assert "default:" in output
        assert "goto cleanup" in output
        assert "goto error" in output

    def test_function_with_switch_and_labels(self):
        """Test function containing switch and labels."""
        # Create labels
        cleanup_label = self.c.label("cleanup")
        error_label = self.c.label("error")

        # Create switch
        case1 = self.c.case_statement(0, [
            self.c.statement("result = 0"),
            self.c.goto_statement("cleanup")
        ])

        default = self.c.default_case([
            self.c.statement("result = -1"),
            self.c.goto_statement("error")
        ])

        switch = self.c.switch_statement("input", [case1], default)

        # Create a sequence with switch and labels (simulating function body)
        seq = self.c.sequence()
        seq.append(self.c.declaration(self.c.variable("result", "int")))
        seq.append(switch)
        seq.append(cleanup_label)
        seq.append(self.c.statement("printf(\"Cleanup\")"))
        seq.append(self.c.func_return("result"))
        seq.append(error_label)
        seq.append(self.c.statement("printf(\"Error\")"))
        seq.append(self.c.func_return("-1"))

        output = self.writer.write_str(seq)

        assert "int result" in output
        assert "switch (input)" in output
        assert "cleanup:" in output
        assert "error:" in output
        assert "goto cleanup" in output
        assert "goto error" in output

    def test_nested_switch_statements(self):
        """Test nested switch statements."""
        # Inner switch
        inner_case = self.c.case_statement("'a'", [
            self.c.statement("printf(\"Letter a\")"),
            self.c.break_statement()
        ])
        inner_switch = self.c.switch_statement("ch", [inner_case])

        # Outer switch
        outer_case = self.c.case_statement(1, [
            self.c.statement("printf(\"Type 1\")"),
            inner_switch,
            self.c.break_statement()
        ])
        outer_switch = self.c.switch_statement("type", [outer_case])

        output = self.writer.write_str_elem(outer_switch)
        assert "switch (type)" in output
        assert "case 1:" in output
        assert "switch (ch)" in output
        assert "case 'a':" in output

    def test_switch_in_sequence(self):
        """Test switch statement in a sequence."""
        seq = self.c.sequence()

        # Add various elements including switch
        seq.append(self.c.statement(self.c.static_assert("sizeof(int) >= 4", "int size check")))

        case1 = self.c.case_statement(1, [self.c.statement("printf(\"one\")")])
        switch = self.c.switch_statement("x", [case1])
        seq.append(switch)

        seq.append(self.c.label("end"))
        seq.append(self.c.goto_statement("end"))

        output = self.writer.write_str(seq)
        assert '_Static_assert(sizeof(int) >= 4, "int size check");' in output
        assert "switch (x)" in output
        assert "end:" in output
        assert "goto end" in output