"""Tests for TIER 4 Language Elements (Advanced C11 Features)."""

import pytest
from cgen.generator import CFactory, Writer, StyleOptions


class TestFunctionPointers:
    """Test function pointer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_function_pointer_basic(self):
        """Test basic function pointer creation."""
        func_ptr = self.c.function_pointer("callback", "int", [self.c.variable("x", "int")])

        assert func_ptr.name == "callback"
        assert func_ptr.return_type == "int"
        assert len(func_ptr.parameters) == 1
        assert not func_ptr.const
        assert not func_ptr.volatile

    def test_function_pointer_with_qualifiers(self):
        """Test function pointer with const and volatile qualifiers."""
        func_ptr = self.c.function_pointer("callback", "void", None, const=True, volatile=True)

        assert func_ptr.const
        assert func_ptr.volatile

    def test_function_pointer_writing(self):
        """Test function pointer code generation."""
        # Basic function pointer
        func_ptr = self.c.function_pointer("callback", "int", [self.c.variable("x", "int")])
        output = self.writer.write_str_elem(func_ptr)
        assert "int (*callback)(int x)" in output

        # Function pointer with no parameters
        func_ptr = self.c.function_pointer("simple_callback", "void", None)
        output = self.writer.write_str_elem(func_ptr)
        assert "void (*simple_callback)(void)" in output

        # Function pointer with qualifiers
        func_ptr = self.c.function_pointer("const_callback", "int", None, const=True, volatile=True)
        output = self.writer.write_str_elem(func_ptr)
        assert "const volatile int (*const_callback)(void)" in output

    def test_function_pointer_declaration(self):
        """Test function pointer variable declaration."""
        func_ptr_decl = self.c.function_pointer_declaration("my_callback", "int", [self.c.variable("x", "int")])

        assert func_ptr_decl.pointer_name == "my_callback"
        assert func_ptr_decl.return_type == "int"
        assert len(func_ptr_decl.parameters) == 1

    def test_function_pointer_declaration_writing(self):
        """Test function pointer declaration code generation."""
        # Basic declaration
        func_ptr_decl = self.c.function_pointer_declaration("my_callback", "int", [self.c.variable("x", "int")])
        output = self.writer.write_str_elem(func_ptr_decl)
        assert "int (*my_callback)(int x)" in output

        # Static function pointer declaration
        func_ptr_decl = self.c.function_pointer_declaration("static_callback", "void", None, static=True)
        output = self.writer.write_str_elem(func_ptr_decl)
        assert "static void (*static_callback)(void)" in output

        # Const function pointer declaration
        func_ptr_decl = self.c.function_pointer_declaration("const_callback", "int", None, const=True)
        output = self.writer.write_str_elem(func_ptr_decl)
        assert "const int (*const_callback)(void)" in output


class TestVariadicFunctions:
    """Test variadic function functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_variadic_function_basic(self):
        """Test basic variadic function creation."""
        variadic_func = self.c.variadic_function("printf", "int", [self.c.variable("format", "char", pointer=True)])

        assert variadic_func.name == "printf"
        assert variadic_func.return_type == "int"
        assert len(variadic_func.fixed_params) == 1
        assert not variadic_func.static
        assert not variadic_func.extern

    def test_variadic_function_with_qualifiers(self):
        """Test variadic function with storage class specifiers."""
        variadic_func = self.c.variadic_function("debug_log", "void", None, static=True, extern=False)

        assert variadic_func.static
        assert not variadic_func.extern

    def test_variadic_function_writing(self):
        """Test variadic function code generation."""
        # Basic variadic function
        variadic_func = self.c.variadic_function("printf", "int", [self.c.variable("format", "char", pointer=True)])
        output = self.writer.write_str_elem(variadic_func)
        assert "int printf(char* format, ...)" in output

        # Variadic function with no fixed parameters
        variadic_func = self.c.variadic_function("log_message", "void", None)
        output = self.writer.write_str_elem(variadic_func)
        assert "void log_message(...)" in output

        # Static variadic function
        variadic_func = self.c.variadic_function("debug_log", "void", [self.c.variable("level", "int")], static=True)
        output = self.writer.write_str_elem(variadic_func)
        assert "static void debug_log(int level, ...)" in output

        # Extern variadic function
        variadic_func = self.c.variadic_function("external_func", "int", None, extern=True)
        output = self.writer.write_str_elem(variadic_func)
        assert "extern int external_func(...)" in output


class TestStaticAssertions:
    """Test static assertion functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_static_assert_basic(self):
        """Test basic static assertion creation."""
        static_assert = self.c.static_assert("sizeof(int) == 4", "int must be 4 bytes")

        assert static_assert.condition == "sizeof(int) == 4"
        assert static_assert.message == "int must be 4 bytes"

    def test_static_assert_writing(self):
        """Test static assertion code generation."""
        # Basic static assertion
        static_assert = self.c.static_assert("sizeof(int) == 4", "int must be 4 bytes")
        output = self.writer.write_str_elem(static_assert)
        assert '_Static_assert(sizeof(int) == 4, "int must be 4 bytes")' in output

        # Complex condition
        static_assert = self.c.static_assert("BUFFER_SIZE > 0", "Buffer size must be positive")
        output = self.writer.write_str_elem(static_assert)
        assert '_Static_assert(BUFFER_SIZE > 0, "Buffer size must be positive")' in output

    def test_static_assert_validation(self):
        """Test static assertion input validation."""
        # Valid inputs should work
        static_assert = self.c.static_assert("1 == 1", "Always true")
        assert static_assert.condition == "1 == 1"
        assert static_assert.message == "Always true"


class TestGenericSelection:
    """Test generic selection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_generic_selection_basic(self):
        """Test basic generic selection creation."""
        type_assocs = {"int": "process_int", "float": "process_float"}
        generic_sel = self.c.generic_selection("value", type_assocs)

        assert generic_sel.controlling_expr == "value"
        assert generic_sel.type_associations == type_assocs
        assert generic_sel.default_expr is None

    def test_generic_selection_with_default(self):
        """Test generic selection with default case."""
        type_assocs = {"int": "process_int", "float": "process_float"}
        generic_sel = self.c.generic_selection("value", type_assocs, "process_default")

        assert generic_sel.default_expr == "process_default"

    def test_generic_selection_writing(self):
        """Test generic selection code generation."""
        # Basic generic selection
        type_assocs = {"int": "process_int", "float": "process_float"}
        generic_sel = self.c.generic_selection("value", type_assocs)
        output = self.writer.write_str_elem(generic_sel)
        expected = "_Generic(value, int: process_int, float: process_float)"
        assert expected in output

        # Generic selection with default
        generic_sel = self.c.generic_selection("value", type_assocs, "process_default")
        output = self.writer.write_str_elem(generic_sel)
        expected = "_Generic(value, int: process_int, float: process_float, default: process_default)"
        assert expected in output

        # Single type association
        type_assocs = {"char*": "process_string"}
        generic_sel = self.c.generic_selection("input", type_assocs)
        output = self.writer.write_str_elem(generic_sel)
        expected = "_Generic(input, char*: process_string)"
        assert expected in output


class TestTier4Integration:
    """Integration tests for TIER 4 elements."""

    def setup_method(self):
        """Set up test fixtures."""
        self.c = CFactory()
        self.writer = Writer(StyleOptions())

    def test_function_pointer_in_declaration(self):
        """Test function pointer wrapped in declaration."""
        func_ptr = self.c.function_pointer("callback", "int", [self.c.variable("x", "int")])
        decl = self.c.declaration(func_ptr)
        output = self.writer.write_str_elem(decl)
        assert "int (*callback)(int x)" in output

    def test_variadic_function_in_declaration(self):
        """Test variadic function wrapped in declaration."""
        variadic_func = self.c.variadic_function("printf", "int", [self.c.variable("format", "char", pointer=True)])
        decl = self.c.declaration(variadic_func)
        output = self.writer.write_str_elem(decl)
        assert "int printf(char* format, ...)" in output

    def test_complex_function_pointer(self):
        """Test complex function pointer with multiple parameters."""
        params = [
            self.c.variable("x", "int"),
            self.c.variable("y", "float"),
            self.c.variable("callback", "void", pointer=True)
        ]
        func_ptr = self.c.function_pointer("complex_callback", "double", params)
        output = self.writer.write_str_elem(func_ptr)
        assert "double (*complex_callback)(int x, float y, void* callback)" in output

    def test_tier4_in_sequence(self):
        """Test TIER 4 elements in a sequence."""
        seq = self.c.sequence()

        # Add various TIER 4 elements
        seq.append(self.c.statement(self.c.static_assert("sizeof(int) >= 4", "int size check")))
        seq.append(self.c.declaration(self.c.function_pointer("callback", "void", None)))
        seq.append(self.c.declaration(self.c.variadic_function("log_func", "void", None)))

        output = self.writer.write_str(seq)
        assert '_Static_assert(sizeof(int) >= 4, "int size check");' in output
        assert "void (*callback)(void)" in output
        assert "void log_func(...)" in output

    def test_function_pointer_with_struct_params(self):
        """Test function pointer with struct parameters."""
        # Create a struct first
        point_struct = self.c.struct("Point", [
            self.c.struct_member("x", "int"),
            self.c.struct_member("y", "int")
        ])

        # Function pointer that takes struct parameter
        func_ptr = self.c.function_pointer("point_processor", "void", [self.c.variable("p", point_struct, pointer=True)])
        output = self.writer.write_str_elem(func_ptr)
        assert "void (*point_processor)(struct Point* p)" in output