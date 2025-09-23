"""Test C11 Advanced Features Implementation"""

import unittest
from cgen.core import CFactory, Writer, StyleOptions


class TestC11AtomicFeatures(unittest.TestCase):
    """Test C11 atomic types and operations."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_atomic_type_creation(self):
        """Test creation of atomic types."""
        atomic_int = self.factory.atomic_type("int")
        self.assertEqual(atomic_int.__class__.__name__, "AtomicType")
        self.assertEqual(atomic_int.base_type, "int")

    def test_atomic_type_writing(self):
        """Test writing atomic types."""
        atomic_int = self.factory.atomic_type("int")
        sequence = self.factory.sequence()
        sequence.append(atomic_int)
        output = self.writer.write_str(sequence)
        self.assertIn("_Atomic(int)", output)

    def test_atomic_type_validation(self):
        """Test atomic type validation."""
        with self.assertRaises(ValueError):
            self.factory.atomic_type("")


class TestC11AlignmentFeatures(unittest.TestCase):
    """Test C11 alignment specifiers and operators."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_alignas_specifier_integer(self):
        """Test _Alignas with integer alignment."""
        alignas = self.factory.alignas_specifier(16)
        sequence = self.factory.sequence()
        sequence.append(alignas)
        output = self.writer.write_str(sequence)
        self.assertIn("_Alignas(16)", output)

    def test_alignas_specifier_string(self):
        """Test _Alignas with string alignment."""
        alignas = self.factory.alignas_specifier("sizeof(double)")
        sequence = self.factory.sequence()
        sequence.append(alignas)
        output = self.writer.write_str(sequence)
        self.assertIn("_Alignas(sizeof(double))", output)

    def test_alignas_validation(self):
        """Test _Alignas validation."""
        with self.assertRaises(ValueError):
            self.factory.alignas_specifier(0)
        with self.assertRaises(TypeError):
            self.factory.alignas_specifier([1, 2])

    def test_alignof_operator(self):
        """Test _Alignof operator."""
        alignof = self.factory.alignof_operator("int")
        sequence = self.factory.sequence()
        sequence.append(alignof)
        output = self.writer.write_str(sequence)
        self.assertIn("_Alignof(int)", output)

    def test_alignof_validation(self):
        """Test _Alignof validation."""
        with self.assertRaises(ValueError):
            self.factory.alignof_operator("")


class TestC11ThreadLocalFeatures(unittest.TestCase):
    """Test C11 thread-local storage."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_thread_local_specifier(self):
        """Test _Thread_local specifier."""
        thread_local = self.factory.thread_local_specifier("my_var")
        sequence = self.factory.sequence()
        sequence.append(thread_local)
        output = self.writer.write_str(sequence)
        self.assertIn("_Thread_local my_var", output)

    def test_thread_local_validation(self):
        """Test _Thread_local validation."""
        with self.assertRaises(ValueError):
            self.factory.thread_local_specifier("")


class TestComplexTypes(unittest.TestCase):
    """Test C11 complex number types."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_complex_type_default(self):
        """Test default complex type (double _Complex)."""
        complex_type = self.factory.complex_type()
        self.assertEqual(complex_type.base_type, "double _Complex")

    def test_complex_type_float(self):
        """Test float complex type."""
        complex_type = self.factory.complex_type("float")
        self.assertEqual(complex_type.base_type, "float _Complex")

    def test_complex_type_long_double(self):
        """Test long double complex type."""
        complex_type = self.factory.complex_type("long double")
        self.assertEqual(complex_type.base_type, "long double _Complex")

    def test_complex_type_writing(self):
        """Test writing complex types."""
        complex_type = self.factory.complex_type("float")
        sequence = self.factory.sequence()
        sequence.append(complex_type)
        output = self.writer.write_str(sequence)
        self.assertIn("float _Complex", output)

    def test_complex_type_validation(self):
        """Test complex type validation."""
        with self.assertRaises(ValueError):
            self.factory.complex_type("invalid")


class TestFixedWidthIntegers(unittest.TestCase):
    """Test C11 fixed-width integer types."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_int8_t(self):
        """Test int8_t type."""
        int8_type = self.factory.int8_t()
        self.assertEqual(int8_type.base_type, "int8_t")
        self.assertEqual(int8_type.width, 8)
        self.assertTrue(int8_type.signed)

    def test_uint32_t(self):
        """Test uint32_t type."""
        uint32_type = self.factory.uint32_t()
        self.assertEqual(uint32_type.base_type, "uint32_t")
        self.assertEqual(uint32_type.width, 32)
        self.assertFalse(uint32_type.signed)

    def test_fixed_width_integer_writing(self):
        """Test writing fixed-width integers."""
        int16_type = self.factory.int16_t()
        sequence = self.factory.sequence()
        sequence.append(int16_type)
        output = self.writer.write_str(sequence)
        self.assertIn("int16_t", output)

    def test_fixed_width_validation(self):
        """Test fixed-width integer validation."""
        with self.assertRaises(ValueError):
            self.factory.fixed_width_integer_type(12)  # Invalid width


class TestAdvancedStorageClasses(unittest.TestCase):
    """Test advanced storage class specifiers."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_auto_specifier(self):
        """Test auto storage class specifier."""
        auto = self.factory.auto_specifier("my_var")
        sequence = self.factory.sequence()
        sequence.append(auto)
        output = self.writer.write_str(sequence)
        self.assertIn("auto my_var", output)

    def test_register_specifier(self):
        """Test register storage class specifier."""
        register = self.factory.register_specifier("i")
        sequence = self.factory.sequence()
        sequence.append(register)
        output = self.writer.write_str(sequence)
        self.assertIn("register i", output)

    def test_restrict_specifier(self):
        """Test restrict type qualifier."""
        restrict = self.factory.restrict_specifier("ptr")
        sequence = self.factory.sequence()
        sequence.append(restrict)
        output = self.writer.write_str(sequence)
        self.assertIn("restrict ptr", output)

    def test_storage_class_validation(self):
        """Test storage class validation."""
        with self.assertRaises(ValueError):
            self.factory.auto_specifier("")
        with self.assertRaises(ValueError):
            self.factory.register_specifier("")
        with self.assertRaises(ValueError):
            self.factory.restrict_specifier("")


class TestAdvancedConstructs(unittest.TestCase):
    """Test advanced C11 constructs."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_inline_specifier(self):
        """Test inline function specifier."""
        inline = self.factory.inline_specifier("my_function")
        sequence = self.factory.sequence()
        sequence.append(inline)
        output = self.writer.write_str(sequence)
        self.assertIn("inline my_function", output)

    def test_flexible_array_member(self):
        """Test flexible array member."""
        flex_array = self.factory.flexible_array_member("data", "int")
        sequence = self.factory.sequence()
        sequence.append(flex_array)
        output = self.writer.write_str(sequence)
        self.assertIn("int data[]", output)  # Flexible array shows as []

    def test_designated_initializer_array(self):
        """Test designated initializer for arrays."""
        designated = self.factory.designated_initializer([0, 2], "42")
        sequence = self.factory.sequence()
        sequence.append(designated)
        output = self.writer.write_str(sequence)
        self.assertIn("[0][2] = 42", output)

    def test_designated_initializer_struct(self):
        """Test designated initializer for structs."""
        designated = self.factory.designated_initializer(["x", "y"], "10")
        sequence = self.factory.sequence()
        sequence.append(designated)
        output = self.writer.write_str(sequence)
        self.assertIn(".x.y = 10", output)

    def test_designated_initializer_mixed(self):
        """Test designated initializer with mixed designators."""
        designated = self.factory.designated_initializer([0, "field"], "value")
        sequence = self.factory.sequence()
        sequence.append(designated)
        output = self.writer.write_str(sequence)
        self.assertIn("[0].field = value", output)

    def test_constructs_validation(self):
        """Test advanced constructs validation."""
        with self.assertRaises(ValueError):
            self.factory.inline_specifier("")
        with self.assertRaises(ValueError):
            self.factory.flexible_array_member("", "int")
        with self.assertRaises(ValueError):
            self.factory.designated_initializer([], "value")


class TestComplexPointerTypes(unittest.TestCase):
    """Test complex pointer types."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_pointer_to_pointer_default(self):
        """Test default pointer-to-pointer (2 levels)."""
        ptr_ptr = self.factory.pointer_to_pointer("int")
        self.assertEqual(ptr_ptr.levels, 2)
        self.assertEqual(ptr_ptr.pointer_levels, "**")

    def test_pointer_to_pointer_triple(self):
        """Test triple pointer."""
        ptr_ptr_ptr = self.factory.pointer_to_pointer("char", 3)
        self.assertEqual(ptr_ptr_ptr.levels, 3)
        self.assertEqual(ptr_ptr_ptr.pointer_levels, "***")

    def test_pointer_to_pointer_writing(self):
        """Test writing pointer-to-pointer types."""
        ptr_ptr = self.factory.pointer_to_pointer("int", 2)
        sequence = self.factory.sequence()
        sequence.append(ptr_ptr)
        output = self.writer.write_str(sequence)
        self.assertIn("int**", output)

    def test_pointer_to_pointer_validation(self):
        """Test pointer-to-pointer validation."""
        with self.assertRaises(ValueError):
            self.factory.pointer_to_pointer("int", 1)  # Must be at least 2 levels
        with self.assertRaises(ValueError):
            self.factory.pointer_to_pointer("int", 6)  # Should not exceed 5 levels
        with self.assertRaises(ValueError):
            self.factory.pointer_to_pointer("", 2)


class TestAdvancedPreprocessor(unittest.TestCase):
    """Test advanced preprocessor features."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_pragma_directive(self):
        """Test pragma directive."""
        pragma = self.factory.pragma_directive("pack(1)")
        sequence = self.factory.sequence()
        sequence.append(pragma)
        output = self.writer.write_str(sequence)
        self.assertIn("#pragma pack(1)", output)

    def test_function_like_macro(self):
        """Test function-like macro."""
        macro = self.factory.function_like_macro("MAX", ["a", "b"], "((a) > (b) ? (a) : (b))")
        sequence = self.factory.sequence()
        sequence.append(macro)
        output = self.writer.write_str(sequence)
        self.assertIn("#define MAX(a, b) ((a) > (b) ? (a) : (b))", output)

    def test_variadic_macro_with_fixed_params(self):
        """Test variadic macro with fixed parameters."""
        macro = self.factory.variadic_macro("DEBUG", ["level"], "printf(level, __VA_ARGS__)")
        sequence = self.factory.sequence()
        sequence.append(macro)
        output = self.writer.write_str(sequence)
        self.assertIn("#define DEBUG(level, ...) printf(level, __VA_ARGS__)", output)

    def test_variadic_macro_no_fixed_params(self):
        """Test variadic macro without fixed parameters."""
        macro = self.factory.variadic_macro("LOG", [], "printf(__VA_ARGS__)")
        sequence = self.factory.sequence()
        sequence.append(macro)
        output = self.writer.write_str(sequence)
        self.assertIn("#define LOG(...) printf(__VA_ARGS__)", output)

    def test_preprocessor_validation(self):
        """Test preprocessor validation."""
        with self.assertRaises(ValueError):
            self.factory.pragma_directive("")
        with self.assertRaises(ValueError):
            self.factory.function_like_macro("", ["a"], "a")
        with self.assertRaises(ValueError):
            self.factory.function_like_macro("MACRO", [""], "a")
        with self.assertRaises(ValueError):
            self.factory.variadic_macro("MACRO", [""], "a")


class TestC11FeatureIntegration(unittest.TestCase):
    """Test integration of multiple C11 features."""

    def setUp(self):
        self.factory = CFactory()
        self.writer = Writer(StyleOptions())

    def test_complete_c11_program(self):
        """Test a complete program using multiple C11 features."""
        # Include stdint.h for fixed-width integers
        include = self.factory.sysinclude("stdint.h")

        # Include complex.h for complex numbers
        include_complex = self.factory.sysinclude("complex.h")

        # Pragma directive
        pragma = self.factory.pragma_directive("once")

        # Function-like macro
        max_macro = self.factory.function_like_macro("MAX", ["a", "b"], "((a) > (b) ? (a) : (b))")

        # Atomic type (standalone test)
        atomic_type = self.factory.atomic_type("int")

        # Thread-local variable
        thread_local_var = self.factory.variable("tls_var", self.factory.int32_t())
        thread_local_spec = self.factory.thread_local_specifier(thread_local_var)

        # Complex number variable
        complex_var = self.factory.variable("z", self.factory.complex_type("double"))
        complex_decl = self.factory.declaration(complex_var)

        # Pointer-to-pointer variable
        ptr_ptr_var = self.factory.variable("ptr_ptr", self.factory.pointer_to_pointer("char", 2))
        ptr_ptr_decl = self.factory.declaration(ptr_ptr_var)

        # Function with inline specifier
        inline_func = self.factory.function("inline_add", "int", [
            self.factory.variable("a", "int"),
            self.factory.variable("b", "int")
        ])
        inline_spec = self.factory.inline_specifier(inline_func)

        # Create sequence
        sequence = self.factory.sequence()
        sequence.append(include)
        sequence.append(include_complex)
        sequence.append(pragma)
        sequence.append(max_macro)
        sequence.append(atomic_type)
        sequence.append(thread_local_spec)
        sequence.append(complex_decl)
        sequence.append(ptr_ptr_decl)
        sequence.append(inline_spec)

        output = self.writer.write_str(sequence)

        # Verify all features are present
        self.assertIn("#include <stdint.h>", output)
        self.assertIn("#include <complex.h>", output)
        self.assertIn("#pragma once", output)
        self.assertIn("#define MAX(a, b) ((a) > (b) ? (a) : (b))", output)
        self.assertIn("_Atomic(int)", output)
        self.assertIn("_Thread_local", output)
        self.assertIn("double _Complex", output)
        self.assertIn("char**", output)
        self.assertIn("inline", output)

    def test_struct_with_flexible_array_member(self):
        """Test struct with flexible array member."""
        # Create struct members
        size_member = self.factory.struct_member("size", "size_t")
        flex_member = self.factory.flexible_array_member("data", "int")

        # Create struct with flexible array member
        struct = self.factory.struct("flexible_struct")
        struct.append(size_member)
        struct.append(flex_member)
        struct_decl = self.factory.declaration(struct)

        sequence = self.factory.sequence()
        sequence.append(struct_decl)
        output = self.writer.write_str(sequence)

        self.assertIn("struct flexible_struct", output)
        self.assertIn("size_t size", output)
        self.assertIn("int data[]", output)  # Flexible array shows as []

    def test_designated_initializer_in_variable(self):
        """Test designated initializer in variable initialization."""
        # Create array variable with designated initializer
        designated = self.factory.designated_initializer([0], "10")
        array_var = self.factory.variable("arr", "int[5]")
        array_decl = self.factory.declaration(array_var, designated)

        sequence = self.factory.sequence()
        sequence.append(array_decl)
        output = self.writer.write_str(sequence)

        self.assertIn("arr", output)  # Array variable name should be present
        self.assertIn("[0] = 10", output)


if __name__ == '__main__':
    unittest.main()