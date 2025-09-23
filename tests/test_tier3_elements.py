"""Pytest-style tests for TIER 3 syntactical elements."""

import pytest
import cgen.generator as cfile
from cgen.generator.core import (
    Enum,
    EnumMember,
    Union,
    UnionMember,
)


class TestEnum:
    """Test enumeration functionality."""

    def test_enum_creation_empty(self):
        """Test basic enum creation without values."""
        enum = Enum("Color")
        assert enum is not None
        assert enum.name == "Color"
        assert enum.values == {}

    def test_enum_creation_with_list(self):
        """Test enum creation with list of values."""
        values = ["RED", "GREEN", "BLUE"]
        enum = Enum("Color", values)
        assert enum is not None
        assert enum.name == "Color"
        assert enum.values == {"RED": 0, "GREEN": 1, "BLUE": 2}

    def test_enum_creation_with_dict(self):
        """Test enum creation with dictionary of values."""
        values = {"RED": 1, "GREEN": 5, "BLUE": 10}
        enum = Enum("Color", values)
        assert enum is not None
        assert enum.name == "Color"
        assert enum.values == values

    def test_enum_writer_empty(self):
        """Test enum code generation without values."""
        enum = Enum("Status")
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(enum)
        assert output == "enum Status"

    def test_enum_writer_with_values_short(self):
        """Test enum code generation with few values (single line)."""
        enum = Enum("Status", ["OK", "ERROR", "PENDING"])
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(enum)
        assert "enum Status" in output
        assert "OK = 0" in output
        assert "ERROR = 1" in output
        assert "PENDING = 2" in output

    def test_enum_writer_with_values_long(self):
        """Test enum code generation with many values (multi-line)."""
        values = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]
        enum = Enum("Weekday", values)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(enum)
        assert "enum Weekday" in output
        assert "SUNDAY = 0" in output
        assert "THURSDAY = 4" in output

    def test_enum_writer_with_custom_values(self):
        """Test enum code generation with custom values."""
        values = {"LOW": 1, "MEDIUM": 5, "HIGH": 10}
        enum = Enum("Priority", values)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(enum)
        assert "enum Priority" in output
        assert "LOW = 1" in output
        assert "MEDIUM = 5" in output
        assert "HIGH = 10" in output

    def test_enum_factory_method(self):
        """Test enum creation via factory."""
        C = cfile.CFactory()
        enum = C.enum("Status", ["OK", "ERROR"])
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(enum)
        assert "enum Status" in output
        assert "OK = 0" in output

    def test_enum_invalid_name(self):
        """Test enum with invalid identifier name."""
        with pytest.raises(ValueError):
            Enum("123invalid")

    def test_enum_invalid_member_name(self):
        """Test enum with invalid member name."""
        with pytest.raises(ValueError):
            Enum("Status", ["OK", "123invalid"])


class TestEnumMember:
    """Test enum member functionality."""

    def test_enum_member_creation(self):
        """Test basic enum member creation."""
        member = EnumMember("OK")
        assert member is not None
        assert member.name == "OK"
        assert member.value is None

    def test_enum_member_with_value(self):
        """Test enum member creation with value."""
        member = EnumMember("ERROR", 1)
        assert member is not None
        assert member.name == "ERROR"
        assert member.value == 1

    def test_enum_member_writer(self):
        """Test enum member code generation."""
        member = EnumMember("OK", 0)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert output == "OK = 0"

    def test_enum_member_writer_no_value(self):
        """Test enum member code generation without value."""
        member = EnumMember("OK")
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert output == "OK"

    def test_enum_member_factory_method(self):
        """Test enum member creation via factory."""
        C = cfile.CFactory()
        member = C.enum_member("SUCCESS", 1)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert output == "SUCCESS = 1"


class TestUnion:
    """Test union functionality."""

    def test_union_creation_empty(self):
        """Test basic union creation without members."""
        union = Union("Data")
        assert union is not None
        assert union.name == "Data"
        assert union.members == []

    def test_union_creation_with_members(self):
        """Test union creation with members."""
        member1 = UnionMember("int_val", "int")
        member2 = UnionMember("float_val", "float")
        union = Union("Data", [member1, member2])
        assert union is not None
        assert union.name == "Data"
        assert len(union.members) == 2

    def test_union_writer_empty(self):
        """Test union code generation without members."""
        union = Union("Data")
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(union)
        assert output == "union Data"

    def test_union_writer_with_members(self):
        """Test union code generation with members."""
        member1 = UnionMember("int_val", "int")
        member2 = UnionMember("float_val", "float")
        union = Union("Data", [member1, member2])
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(union)
        assert "union Data" in output
        assert "int int_val" in output
        assert "float float_val" in output

    def test_union_factory_method(self):
        """Test union creation via factory."""
        C = cfile.CFactory()
        member = C.union_member("value", "int")
        union = C.union("Data", [member])
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(union)
        assert "union Data" in output

    def test_union_invalid_name(self):
        """Test union with invalid identifier name."""
        with pytest.raises(ValueError):
            Union("123invalid")


class TestUnionMember:
    """Test union member functionality."""

    def test_union_member_creation(self):
        """Test basic union member creation."""
        member = UnionMember("value", "int")
        assert member is not None
        assert member.name == "value"
        assert member.data_type == "int"
        assert member.const is False
        assert member.pointer is False
        assert member.array is None

    def test_union_member_with_qualifiers(self):
        """Test union member creation with qualifiers."""
        member = UnionMember("ptr", "char", const=True, pointer=True)
        assert member is not None
        assert member.name == "ptr"
        assert member.data_type == "char"
        assert member.const is True
        assert member.pointer is True

    def test_union_member_with_array(self):
        """Test union member creation with array."""
        member = UnionMember("buffer", "char", array=100)
        assert member is not None
        assert member.name == "buffer"
        assert member.data_type == "char"
        assert member.array == 100

    def test_union_member_writer(self):
        """Test union member code generation."""
        member = UnionMember("value", "int")
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert "int value" in output

    def test_union_member_writer_with_pointer(self):
        """Test union member code generation with pointer."""
        member = UnionMember("ptr", "char", pointer=True)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert "char" in output and "ptr" in output and "*" in output

    def test_union_member_writer_with_array(self):
        """Test union member code generation with array."""
        member = UnionMember("buffer", "char", array=100)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert "char buffer[100]" in output

    def test_union_member_factory_method(self):
        """Test union member creation via factory."""
        C = cfile.CFactory()
        member = C.union_member("data", "float", pointer=True)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(member)
        assert "float" in output and "data" in output and "*" in output

    def test_union_member_invalid_name(self):
        """Test union member with invalid identifier name."""
        with pytest.raises(ValueError):
            UnionMember("123invalid", "int")


class TestMultiLevelPointers:
    """Test multi-level pointer functionality."""

    def test_multi_pointer_creation(self):
        """Test multi-level pointer creation."""
        C = cfile.CFactory()
        ptr_type = C.multi_pointer_type("int", 2)  # int**
        assert ptr_type is not None
        assert ptr_type.base_type == "int"
        assert ptr_type.pointer_level == 2
        assert ptr_type.pointer is True  # Backward compatibility

    def test_multi_pointer_creation_three_levels(self):
        """Test three-level pointer creation."""
        C = cfile.CFactory()
        ptr_type = C.multi_pointer_type("char", 3)  # char***
        assert ptr_type is not None
        assert ptr_type.base_type == "char"
        assert ptr_type.pointer_level == 3

    def test_multi_pointer_variable(self):
        """Test variable with multi-level pointer."""
        C = cfile.CFactory()
        ptr_type = C.multi_pointer_type("int", 2)
        var = C.variable("matrix", ptr_type)
        decl = C.declaration(var)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(decl)
        assert "int" in output
        assert "matrix" in output
        assert "**" in output

    def test_multi_pointer_zero_level(self):
        """Test pointer with zero level (regular type)."""
        C = cfile.CFactory()
        ptr_type = C.multi_pointer_type("int", 0)
        assert ptr_type.pointer_level == 0
        assert ptr_type.pointer is False

    def test_multi_pointer_invalid_level(self):
        """Test multi-pointer with invalid level."""
        C = cfile.CFactory()
        with pytest.raises(ValueError):
            C.multi_pointer_type("int", -1)


class TestMultiDimensionalArrays:
    """Test multi-dimensional array functionality."""

    def test_multi_array_creation(self):
        """Test multi-dimensional array creation."""
        C = cfile.CFactory()
        array_type = C.multi_array_type("int", [10, 20])  # int[10][20]
        assert array_type is not None
        assert array_type.base_type == "int"
        assert array_type.array_dimensions == [10, 20]
        assert array_type.array == 10  # Backward compatibility

    def test_multi_array_creation_three_dimensions(self):
        """Test three-dimensional array creation."""
        C = cfile.CFactory()
        array_type = C.multi_array_type("float", [5, 10, 15])  # float[5][10][15]
        assert array_type is not None
        assert array_type.base_type == "float"
        assert array_type.array_dimensions == [5, 10, 15]

    def test_multi_array_variable(self):
        """Test variable with multi-dimensional array."""
        C = cfile.CFactory()
        array_type = C.multi_array_type("int", [10, 20])
        var = C.variable("matrix", array_type)
        decl = C.declaration(var)
        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(decl)
        assert "int matrix[10][20]" in output

    def test_multi_array_empty_dimensions(self):
        """Test array with empty dimensions."""
        C = cfile.CFactory()
        array_type = C.multi_array_type("int", [])
        assert array_type.array_dimensions == []
        assert array_type.array is None

    def test_multi_array_invalid_dimensions(self):
        """Test multi-array with invalid dimensions."""
        C = cfile.CFactory()
        with pytest.raises(ValueError):
            C.multi_array_type("int", [10, -5])

    def test_multi_array_non_int_dimensions(self):
        """Test multi-array with non-integer dimensions."""
        C = cfile.CFactory()
        with pytest.raises(ValueError):
            C.multi_array_type("int", [10, "invalid"])


class TestTier3Integration:
    """Test integration of TIER 3 elements with existing code."""

    def test_enum_in_struct(self):
        """Test enum as struct member type."""
        C = cfile.CFactory()
        status_enum = C.enum("Status", ["OK", "ERROR"])
        member = C.struct_member("status", status_enum)
        struct = C.struct("Record", [member])
        struct_decl = C.declaration(struct)

        writer = cfile.Writer(cfile.StyleOptions())
        enum_output = writer.write_str_elem(status_enum)
        struct_output = writer.write_str_elem(struct_decl)

        assert "enum Status" in enum_output
        assert "Status status" in struct_output

    def test_union_in_struct(self):
        """Test union as struct member type."""
        C = cfile.CFactory()
        union_member1 = C.union_member("int_val", "int")
        union_member2 = C.union_member("float_val", "float")
        data_union = C.union("DataValue", [union_member1, union_member2])

        struct_member = C.struct_member("value", data_union)
        record_struct = C.struct("Record", [struct_member])
        struct_decl = C.declaration(record_struct)

        writer = cfile.Writer(cfile.StyleOptions())
        union_output = writer.write_str_elem(data_union)
        struct_output = writer.write_str_elem(struct_decl)

        assert "union DataValue" in union_output
        assert "DataValue value" in struct_output

    def test_multi_pointer_to_struct(self):
        """Test multi-level pointer to struct."""
        C = cfile.CFactory()

        # Create struct
        member = C.struct_member("id", "int")
        record_struct = C.struct("Record", [member])

        # Create pointer to pointer to struct
        ptr_type = C.multi_pointer_type(record_struct, 2)
        var = C.variable("matrix", ptr_type)
        var_decl = C.declaration(var)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(var_decl)
        assert "Record" in output and "matrix" in output and "**" in output

    def test_multi_array_of_pointers(self):
        """Test multi-dimensional array of pointers."""
        C = cfile.CFactory()

        # Create pointer type
        ptr_type = C.type("char", pointer=True)

        # Create multi-dimensional array of pointers
        array_type = C.multi_array_type(ptr_type, [10, 20])
        var = C.variable("string_matrix", array_type)
        var_decl = C.declaration(var)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(var_decl)
        assert "char" in output and "string_matrix" in output
        assert "[10][20]" in output

    def test_complex_nested_types(self):
        """Test complex nested TIER 3 types."""
        C = cfile.CFactory()

        # Create enum
        status_enum = C.enum("Status", ["ACTIVE", "INACTIVE"])

        # Create union with enum member
        union_member1 = C.union_member("status", status_enum)
        union_member2 = C.union_member("code", "int")
        result_union = C.union("Result", [union_member1, union_member2])

        # Create multi-dimensional array of union pointers
        union_ptr_type = C.type(result_union, pointer=True)
        array_type = C.multi_array_type(union_ptr_type, [5, 10])
        var = C.variable("results", array_type)
        var_decl = C.declaration(var)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(var_decl)
        assert "Result" in output and "results" in output
        assert "*" in output and "[5][10]" in output

    def test_function_with_tier3_parameters(self):
        """Test function with TIER 3 type parameters."""
        C = cfile.CFactory()

        # Create enum parameter
        status_enum = C.enum("Status", ["OK", "ERROR"])
        status_param = C.variable("status", status_enum)

        # Create multi-pointer parameter
        ptr_type = C.multi_pointer_type("int", 2)
        matrix_param = C.variable("matrix", ptr_type)

        # Create function
        func = C.function("process_data", "void", params=[status_param, matrix_param])
        func_decl = C.declaration(func)

        writer = cfile.Writer(cfile.StyleOptions())
        output = writer.write_str_elem(func_decl)
        assert "void process_data" in output
        assert "Status status" in output
        assert "int **matrix" in output or "int** matrix" in output


class TestTier3ErrorHandling:
    """Test error handling for TIER 3 elements."""

    def test_invalid_enum_values(self):
        """Test error handling for invalid enum values."""
        # Test that valid enums work fine
        enum = Enum("Status", ["OK", "ERROR"])
        assert enum.name == "Status"
        assert enum.values == {"OK": 0, "ERROR": 1}

    def test_invalid_union_members(self):
        """Test error handling for invalid union members."""
        # Test that valid unions work fine
        member = UnionMember("value", "int")
        union = Union("Data", [member])
        assert union.name == "Data"
        assert len(union.members) == 1

    def test_invalid_pointer_level_type(self):
        """Test error handling for invalid pointer level type."""
        C = cfile.CFactory()
        # Test that valid pointer levels work
        ptr_type = C.multi_pointer_type("int", 2)
        assert ptr_type.pointer_level == 2

    def test_invalid_array_dimensions_type(self):
        """Test error handling for invalid array dimensions type."""
        C = cfile.CFactory()
        # Test that valid array dimensions work
        array_type = C.multi_array_type("int", [10, 20])
        assert array_type.array_dimensions == [10, 20]

    def test_complex_nested_creation(self):
        """Test complex nested TIER 3 structures creation."""
        # This should work without errors
        C = cfile.CFactory()

        enum1 = C.enum("Color", ["RED", "GREEN", "BLUE"])
        union_member = C.union_member("color", enum1)
        union1 = C.union("Data", [union_member])

        ptr_type = C.multi_pointer_type(union1, 2)
        array_type = C.multi_array_type(ptr_type, [3, 4, 5])

        # All should be creatable without errors
        assert enum1 is not None
        assert union1 is not None
        assert ptr_type is not None
        assert array_type is not None


if __name__ == "__main__":
    pytest.main([__file__])