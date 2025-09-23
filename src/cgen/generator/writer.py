"""Cfile writer."""

# pylint: disable=consider-using-with
from enum import Enum
from io import StringIO
from typing import Any, TextIO

from . import core
from . import style as c_style
from .style import BreakBeforeBraces
from ..common import log


class ElementType(Enum):
    """Element types."""

    NONE = 0
    DIRECTIVE = 1
    COMMENT = 2
    TYPE_DECLARATION = 3
    STRUCT_DECLARATION = 4  # Should this be separate from type declaration?
    VARIABLE_DECLARATION = 5
    FUNCTION_DECLARATION = 6
    TYPEDEF = 7
    TYPE_INSTANCE = 8
    STRUCT_INSTANCE = 9
    VARIABLE_USAGE = 10
    FUNCTION_CALL = 11
    STATEMENT = 12
    BLOCK_START = 13
    BLOCK_END = 14


class Formatter:
    """Low-level generator."""

    def __init__(self, indent_width: int, indentation_char: str) -> None:
        self.log = log.config(self.__class__.__name__)
        self.file_path: str | None = None
        self.fh: TextIO | None = None  # pylint: disable=invalid-name
        self.indentation_char: str = indentation_char
        self.white_space_char: str = " "
        self.indent_width = indent_width  # Number of characters (spaces) per indendation
        self.indentation_level: int = 0  # current indentation level
        self.indentation_str: str = ""
        self.line_number: int = 0
        self.column: int = 0

    def _str_open(self):
        self.fh = StringIO()
        self.line_number = 1
        self.indentation_level = 0
        self.indentation_str = ""

    def _open(self, file_path: str):
        self.fh = open(file_path, "w", encoding="utf-8")
        self.file_path = file_path
        self.line_number = 1
        self.indentation_level = 0
        self.indentation_str = ""

    def _close(self):
        self.fh.close()

    def _indent(self):
        self.indentation_level += 1
        self.indentation_str = self.indentation_char * (self.indentation_level * self.indent_width)

    def _dedent(self):
        self.indentation_level -= 1
        if self.indentation_level == 0:
            self.indentation_str = ""
        else:
            self.indentation_str = self.indentation_char * (self.indentation_level * self.indent_width)

    def _start_line(self):
        self.fh.write(self.indentation_str)

    def _write(self, text):
        self.fh.write(text)
        self.column += len(text)

    def _write_line(self, text):
        self.fh.write(text)
        self._eol()

    def _eol(self):
        self.fh.write("\n")
        self.line_number += 1
        self.column = 0


class Writer(Formatter):
    """High level generator."""

    def __init__(self, style: c_style.StyleOptions) -> None:
        super().__init__(style.indent_width, style.indent_char)
        self.log = log.config(self.__class__.__name__)
        self.style = style
        self.switcher_all = {
            "Type": self._write_base_type,
            "TypeDef": self._write_typedef_usage,
            "Struct": self._write_struct_usage,
            "Variable": self._write_variable_usage,
            "Function": self._write_function_usage,
            "Declaration": self._write_declaration,
            "Assignment": self._write_assignment,
            "StringLiteral": self._write_string_literal,
            "FunctionReturn": self._write_func_return,
            "FunctionCall": self._write_func_call,
            "BinaryExpression": self._write_binary_expression,
            "UnaryExpression": self._write_unary_expression,
            "STCContainerElement": self._write_stc_container,
            "STCOperationElement": self._write_stc_operation,
            "STCForEachElement": self._write_stc_foreach,
            "STCSliceElement": self._write_stc_slice,
            "Blank": self._write_blank,
            "Whitespace": self._write_whitespace,
            "LineComment": self._write_line_comment,
            "BlockComment": self._write_block_comment,
            "Block": self._write_block,
            "Statement": self._write_statement,
            "Line": self._write_line_element,
            "IncludeDirective": self._write_include_directive,
            "DefineDirective": self._write_define_directive,
            "IfdefDirective": self._write_ifdef_directive,
            "IfndefDirective": self._write_ifndef_directive,
            "EndifDirective": self._write_endif_directive,
            "Extern": self._write_extern,
            "IfStatement": self._write_if_statement,
            "WhileLoop": self._write_while_loop,
            "ForLoop": self._write_for_loop,
            # TIER 2 elements
            "BreakStatement": self._write_break_statement,
            "ContinueStatement": self._write_continue_statement,
            "DoWhileLoop": self._write_do_while_loop,
            "TernaryOperator": self._write_ternary_operator,
            "SizeofOperator": self._write_sizeof_operator,
            "AddressOfOperator": self._write_address_of_operator,
            "DereferenceOperator": self._write_dereference_operator,
            # TIER 3 elements
            "Enum": self._write_enum,
            "EnumMember": self._write_enum_member,
            "Union": self._write_union,
            "UnionMember": self._write_union_member,
            # TIER 4 elements
            "FunctionPointer": self._write_function_pointer,
            "VariadicFunction": self._write_variadic_function,
            "StaticAssert": self._write_static_assert,
            "GenericSelection": self._write_generic_selection,
            "FunctionPointerDeclaration": self._write_function_pointer_declaration,
            # Additional Control Flow elements
            "SwitchStatement": self._write_switch_statement,
            "CaseStatement": self._write_case_statement,
            "DefaultCase": self._write_default_case,
            "GotoStatement": self._write_goto_statement,
            "Label": self._write_label,
            # Additional Operators
            "BitwiseOperator": self._write_bitwise_operator,
            "LogicalOperator": self._write_logical_operator,
            "IncrementOperator": self._write_increment_operator,
            "DecrementOperator": self._write_decrement_operator,
            "CompoundAssignmentOperator": self._write_compound_assignment_operator,
            # C11 Advanced Features
            "AtomicType": self._write_atomic_type,
            "AlignasSpecifier": self._write_alignas_specifier,
            "AlignofOperator": self._write_alignof_operator,
            "ThreadLocalSpecifier": self._write_thread_local_specifier,
            # Complex and Fixed-width Types
            "ComplexType": self._write_complex_type,
            "FixedWidthIntegerType": self._write_fixed_width_integer_type,
            # Advanced Storage Classes
            "AutoSpecifier": self._write_auto_specifier,
            "RegisterSpecifier": self._write_register_specifier,
            "RestrictSpecifier": self._write_restrict_specifier,
            # Advanced Constructs
            "InlineSpecifier": self._write_inline_specifier,
            "FlexibleArrayMember": self._write_flexible_array_member,
            "DesignatedInitializer": self._write_designated_initializer,
            # Complex Pointer Types
            "PointerToPointer": self._write_pointer_to_pointer,
            # Advanced Preprocessor
            "PragmaDirective": self._write_pragma_directive,
            "FunctionLikeMacro": self._write_function_like_macro,
            "VariadicMacro": self._write_variadic_macro,

            # Raw code and STC integration
            "RawCode": self._write_raw_code,
            "STCContainerElement": self._write_stc_container,
            "STCOperationElement": self._write_stc_operation,
            "STCForEachElement": self._write_stc_foreach,
            "STCSliceElement": self._write_stc_slice,
        }
        self.last_element = ElementType.NONE

        # Writer methods for additional syntactical elements are defined below

    def write_file(self, sequence: core.Sequence, file_path: str):
        """Writes the sequence to file using pre-selected format style."""
        self._open(file_path)
        self._write_sequence(sequence)
        self._close()

    def write_str(self, sequence: core.Sequence) -> str:
        """Writes the sequence to string using pre-selected format style."""
        assert isinstance(sequence, core.Sequence)
        self._str_open()
        self._write_sequence(sequence)
        assert isinstance(self.fh, StringIO)
        return self.fh.getvalue()

    def write_str_elem(self, elem: Any, trim_end: bool = True) -> str:
        """Writes single item to string using pre-selected format style."""
        self._str_open()
        self._write_element(elem)
        assert isinstance(self.fh, StringIO)
        value = self.fh.getvalue()
        return value.removesuffix("\n") if trim_end else value

    def _write_element(self, elem: Any) -> None:
        class_name = elem.__class__.__name__
        write_method = self.switcher_all.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for element {class_name}")

    def _write_sequence(self, sequence: core.Sequence) -> None:
        """Writes a sequence."""
        for elem in sequence.elements:
            if isinstance(elem, list):
                tmp = core.Line(elem)
                self._start_line()
                self._write_line_element(tmp)
            elif isinstance(elem, core.Function):
                self._start_line()
                self._write_function_usage(elem)
            elif isinstance(elem, core.Statement):
                self._start_line()
                self._write_statement(elem)
                self._eol()
            elif isinstance(elem, core.LineComment):
                self._start_line()
                self._write_line_comment(elem)
                self._eol()
            elif isinstance(elem, core.Block):
                self._start_line()
                self._write_block(elem)
            elif isinstance(elem, core.Line):
                self._start_line()
                self._write_line_element(elem)
            else:
                self._start_line()
                class_name = elem.__class__.__name__
                write_method = self.switcher_all.get(class_name, None)
                if write_method is not None:
                    write_method(elem)
                else:
                    raise NotImplementedError(f"Found no writer for element {class_name}")
                if isinstance(elem, core.Directive):
                    self._eol()

    def _write_line_element(self, elem: core.Line) -> None:
        for i, part in enumerate(elem.parts):
            if i > 0:
                if isinstance(part, core.Comment):
                    self._write(" " * part.adjust)
                else:
                    self._write(" ")
            self._write_line_part(part)
        self._eol()

    def _write_line_part(self, elem: str | core.Element) -> None:
        if isinstance(elem, core.Element):
            class_name = elem.__class__.__name__
            write_method = self.switcher_all.get(class_name, None)
            if write_method is not None:
                write_method(elem)
            else:
                raise NotImplementedError(f"Found no writer for element {class_name}")
        elif isinstance(elem, str):
            self._write(elem)
        else:
            raise NotImplementedError(str(type(elem)))

    def _write_blank(self, white_space: core.Blank) -> None:  # pylint: disable=unused-argument
        """Writes blank line."""
        self._write_line("")

    def _write_whitespace(self, white_space: core.Whitespace) -> None:
        """Writes whitespace."""
        self._write(self.white_space_char * white_space.width)

    def _write_line_comment(self, elem: core.LineComment) -> None:
        """Writes line comment."""
        if isinstance(elem.text, str):
            self._write("//" + elem.text)
        else:
            raise NotImplementedError("list of strings not yet supported")
        self.last_element = ElementType.COMMENT

    def _write_block_comment(self, elem: core.BlockComment) -> None:
        """Writes block comment."""
        if isinstance(elem.text, str):
            lines = elem.text.splitlines()
        elif isinstance(elem.text, list):
            lines = elem.text
        else:
            raise TypeError("Unsupported type", str(type(elem.text)))
        if elem.width == 0:
            self._format_block_comment(lines, False, 1, "")
        else:
            self._format_block_comment(lines, True, elem.width, elem.line_start)
        self.last_element = ElementType.COMMENT

    def _format_block_comment(self, lines: list[str], wrap_text: bool, width: int, line_start: str) -> None:
        self._write(f"/{'*' * width}")
        if wrap_text:
            self._eol()
            for line in lines:
                self._write_line(line_start + line)
            self._write_line(f"{'*' * (width + 1)}/")
        else:
            for line in lines[:-1]:
                self._write_line(line_start + line)
            self._write(lines[-1] + f"{'*' * width}/")

    def _write_declaration(self, elem: core.Declaration) -> None:
        """Declares type, typedef, variable or function."""
        if isinstance(elem.element, core.Type):
            self._write_type_declaration(elem.element)
        elif isinstance(elem.element, core.TypeDef):
            self._write_typedef_declaration(elem.element)
        elif isinstance(elem.element, core.Struct):
            self._write_struct_declaration(elem.element)
        elif isinstance(elem.element, core.Variable):
            self._write_variable_declaration(elem.element)
        elif isinstance(elem.element, core.Function):
            self._write_function_declaration(elem.element)
        elif elem.element.__class__.__name__ == "FunctionPointer":
            self._write_function_pointer(elem.element)
        elif elem.element.__class__.__name__ == "VariadicFunction":
            self._write_variadic_function(elem.element)
        else:
            raise NotImplementedError(str(type(elem.element)))
        if elem.init_value is not None:
            self._write(" = ")
            self._write_initializer(elem.init_value)

    def _write_initializer(self, value: Any) -> None:
        """Writes initializer."""
        if isinstance(value, list):
            self._write("{")
            for i, member in enumerate(value):
                if i > 0:
                    self._write(", ")
                self._write_initializer_member(member)
            self._write("}")
        else:
            self._write_initializer_member(value)

    def _write_initializer_member(self, value: Any) -> None:
        """Writes initializer member."""
        if isinstance(value, int):
            self._write(str(value))
        elif isinstance(value, str):
            self._write(f'"{value}"')
        elif isinstance(value, core.DesignatedInitializer):
            self._write_element(value)
        else:
            raise NotImplementedError(str(type(value)))

    def _write_base_type(self, elem: core.Type) -> None:
        """Writes name of type."""
        self._write(elem.base_type)

    def _write_type_declaration(self, elem: core.Type) -> None:
        """Writes type declaration."""
        self._write(self._format_type(elem))
        self.last_element = ElementType.TYPE_DECLARATION

    def _format_type(self, elem: core.Type) -> str:
        parts = []
        handled = {"const": False, "volatile": False, "type": False}
        for qualifier in self.style.type_qualifier_order:
            assert qualifier in handled
            handled[qualifier] = True
            if qualifier == "type":
                parts.append(self._format_type_part(elem))
            else:
                if elem.qualifier(qualifier):
                    parts.append(qualifier)
        for key, value in handled.items():
            if value is False and elem.qualifier(key):
                raise RuntimeError(f"Used qualifier '{key}' not part of selected qualifier_order list")
        return " ".join(parts)

    def _format_type_part(self, elem: core.Type) -> str:
        """Writes type name and pointer."""
        result = ""
        if isinstance(elem.base_type, str):
            result += elem.base_type
        elif isinstance(elem.base_type, (core.Enum, core.Union)):
            # Handle enum/union base types
            result += elem.base_type.__class__.__name__.lower() + " " + elem.base_type.name
        elif isinstance(elem.base_type, core.Struct):
            # Handle struct base types
            result += "struct " + elem.base_type.name
        elif isinstance(elem.base_type, core.Type):
            result += self._format_type(elem.base_type)
        else:
            # For other types, convert to string
            result += str(elem.base_type)

        # Handle pointers (both single and multi-level)
        if hasattr(elem, 'pointer_level') and elem.pointer_level > 0:
            pointer_str = "*" * elem.pointer_level
            if self.style.pointer_alignment == c_style.Alignment.LEFT:
                result += pointer_str
            elif self.style.pointer_alignment == c_style.Alignment.RIGHT:
                result += " " + pointer_str
            else:  # MIDDLE - only add trailing space for multi-level pointers
                if elem.pointer_level > 1:
                    result += " " + pointer_str + " "
                else:
                    result += " " + pointer_str
        elif elem.pointer:
            # Backward compatibility for single-level pointers
            if self.style.pointer_alignment == c_style.Alignment.LEFT:
                result += "*"
            elif self.style.pointer_alignment == c_style.Alignment.RIGHT:
                result += " *"
            elif self.style.pointer_alignment == c_style.Alignment.MIDDLE:
                result += " *"
        return result

    def _format_pointer_spacing(self, has_pointer: bool, is_const: bool, data_type: Any) -> str:
        """Format pointer spacing according to style options."""
        result = ""
        if has_pointer:
            if is_const:
                if self.style.space_around_pointer_qualifiers == c_style.SpaceLocation.DEFAULT:
                    if self.style.pointer_alignment == c_style.Alignment.LEFT:
                        result += "* const "
                    elif self.style.pointer_alignment == c_style.Alignment.RIGHT:
                        result += "*const "
                    elif self.style.pointer_alignment == c_style.Alignment.MIDDLE:
                        result += " * const "
                    else:
                        raise ValueError(self.style.pointer_alignment)
                else:
                    raise NotImplementedError("Only default space location supported for pointer qualifiers")
            else:
                if self.style.pointer_alignment == c_style.Alignment.LEFT:
                    result += "* "
                elif self.style.pointer_alignment == c_style.Alignment.RIGHT:
                    if isinstance(data_type, core.Type) and data_type.pointer:
                        result += "*"
                    else:
                        result += " *"
                elif self.style.pointer_alignment == c_style.Alignment.MIDDLE:
                    result += " * "
                else:
                    raise ValueError(self.style.pointer_alignment)
        elif isinstance(data_type, core.Type):
            if not (data_type.pointer and self.style.pointer_alignment == c_style.Alignment.RIGHT):
                result += " "
        else:
            result += " "
        return result

    def _write_variable_usage(self, elem: core.Variable) -> None:
        """Writes variable usage."""
        self._write(elem.name)
        self.last_element = ElementType.VARIABLE_USAGE

    def _write_variable_declaration(self, elem: core.Variable) -> None:
        """Writes variable declaration."""
        if elem.static:
            self._write("static ")
        if elem.extern:
            self._write("extern ")
        if isinstance(elem.data_type, core.PointerToPointer):
            # Write pointer-to-pointer type (check before Type since PointerToPointer inherits from Type)
            self._write_element(elem.data_type)
            # For pointer-to-pointer, skip the regular pointer formatting
            result = " " + elem.name
            result += self._format_array_dimensions(elem)
            self._write(result)
            self.last_element = ElementType.VARIABLE_DECLARATION
            return
        elif isinstance(elem.data_type, core.Type):
            self._write_type_declaration(elem.data_type)
        elif isinstance(elem.data_type, core.Struct):
            self._write_struct_usage(elem.data_type)
        elif isinstance(elem.data_type, core.Declaration):
            self._write_declaration(elem.data_type)
        elif isinstance(elem.data_type, core.TypeDef):
            self._write_typedef_usage(elem.data_type)
        elif isinstance(elem.data_type, (core.Enum, core.Union)):
            # Write enum/union usage (just the name)
            self._write(elem.data_type.__class__.__name__.lower() + " " + elem.data_type.name)
        else:
            raise NotImplementedError(str(type(elem.data_type)))

        result = self._format_pointer_spacing(elem.pointer, elem.const, elem.data_type)
        result += elem.name
        result += self._format_array_dimensions(elem)
        self._write(result)
        self.last_element = ElementType.VARIABLE_DECLARATION

    def _write_typedef_usage(self, elem: core.TypeDef):
        """Writes typedef usage."""
        if not elem.name:
            raise ValueError("Typedef without name detected")
        self._write(elem.name)

    def _write_typedef_declaration(self, elem: core.TypeDef):
        """Writes typedef declaration."""
        self._write("typedef ")

        if elem.const and not elem.pointer:
            self._write("const ")
        if isinstance(elem.base_type, core.Type):
            self._write_type_declaration(elem.base_type)
        elif isinstance(elem.base_type, core.Struct):
            self._write_struct_usage(elem.base_type)
        elif isinstance(elem.base_type, core.Declaration):
            self._write_declaration(elem.base_type)
        else:
            raise NotImplementedError(str(type(elem.base_type)))

        result = self._format_pointer_spacing(elem.pointer, elem.const, elem.base_type)
        assert elem.name is not None
        result += elem.name
        result += self._format_array_dimensions(elem)
        self._write(result)
        self.last_element = ElementType.TYPEDEF

    def _write_function_usage(self, elem: core.Function) -> None:
        """Writes function usage (name of the function)."""
        if not elem.name:
            raise ValueError("Function with no name detected")
        self._write(elem.name)

    def _write_function_declaration(self, elem: core.Function) -> None:
        """Writes function declaration."""
        if elem.extern:
            self._write("extern ")
        if elem.static:
            self._write("static ")
        if isinstance(elem.return_type, core.Type):
            self._write_type_declaration(elem.return_type)
        elif isinstance(elem.return_type, core.Struct):
            self._write_struct_usage(elem.return_type)
        else:
            raise NotImplementedError(str(type(elem.return_type)))
        self._write(f" {elem.name}(")
        if len(elem.params):
            for i, param in enumerate(elem.params):
                if i:
                    self._write(", ")
                self._write_variable_declaration(param)
        else:
            self._write("void")
        self._write(")")
        self.last_element = ElementType.FUNCTION_DECLARATION

    def _write_block(self, elem: core.Block) -> None:
        """Writes a block sequence."""
        self._write_starting_brace()
        if len(elem.elements):
            self._indent()
            self._write_sequence(elem)
            self._dedent()
            self._write_ending_brace()
        else:
            if self.style.short_functions_on_single_line in (
                c_style.ShortFunction.EMPTY,
                c_style.ShortFunction.INLINE,
            ):
                self._write("}")
                self._eol()
            else:
                self._write_ending_brace()

    def _write_starting_brace(self) -> None:
        handled = False
        if self.last_element == ElementType.FUNCTION_DECLARATION:
            handled = True
            if self.style.brace_wrapping.after_function:
                self._eol()
                self._start_line()
                self._write("{")
                self._eol()
            else:
                self._write(" {")
                self._eol()
        if not handled:
            self._write("{")
            self._eol()

    def _write_ending_brace(self) -> None:
        self._start_line()
        self._write("}")
        self._eol()

    def _write_statement(self, elem: core.Statement) -> None:
        assert len(elem.parts) != 0
        if len(elem.parts) > 1:
            for i, part in enumerate(elem.parts):
                if i:
                    self._write(" ")
                self._write_expression(part)
        else:
            self._write_expression(elem.parts[0])
        self._write(";")
        self.last_element = ElementType.STATEMENT

    def _write_expression(self, elem: Any) -> None:
        if isinstance(elem, str):
            self._write(elem)
        else:
            self._write_element(elem)

    def _write_assignment(self, elem: core.Assignment) -> None:
        self._write_expression(elem.lhs)
        self._write(" = ")
        self._write_expression(elem.rhs)

    def _write_string_literal(self, elem: core.StringLiteral) -> None:
        self._write(f'"{elem.text}"')

    def _write_func_return(self, elem: core.FunctionReturn) -> None:
        self._write("return ")
        self._write_expression(elem.expression)

    def _write_func_call(self, elem: core.FunctionCall) -> None:
        self._write(f"{elem.name}(")
        for i, arg in enumerate(elem.args):
            if i:
                self._write(", ")
            self._write_expression(arg)
        self._write(")")

    def _write_binary_expression(self, elem: core.BinaryExpression) -> None:
        # Add parentheses for complex nested expressions to ensure proper precedence
        needs_parens = isinstance(elem.left, core.Element) or isinstance(elem.right, core.Element)
        if needs_parens and elem.operator in ["&&", "||"]:
            self._write("(")

        self._write_expression(elem.left)
        self._write(f" {elem.operator} ")
        self._write_expression(elem.right)

        if needs_parens and elem.operator in ["&&", "||"]:
            self._write(")")

    def _write_unary_expression(self, elem: core.UnaryExpression) -> None:
        self._write(elem.operator)
        self._write_expression(elem.operand)

    def _write_stc_container(self, elem) -> None:
        """Write STC container declaration."""
        # elem should be STCContainerElement
        self._write(f"{elem.container_type} {elem.name}")

    def _write_stc_operation(self, elem) -> None:
        """Write STC operation call."""
        # elem should be STCOperationElement
        self._write(elem.operation_code)

    def _write_stc_foreach(self, elem) -> None:
        """Write STC foreach loop."""
        # elem should be STCForEachElement
        self._write(elem.foreach_code)
        self._write(" {")
        self._eol()
        self._indent()

        # Write the body block
        self._write_element(elem.body_block)

        self._dedent()
        self._write("}")
        self._eol()
        self.last_element = ElementType.STATEMENT

    def _write_stc_slice(self, elem) -> None:
        """Write STC slice operation."""
        # elem should be STCSliceElement
        # Generate code to slice a container into a new container
        #
        # Example generated C code:
        # result = {0};  // Initialize empty container
        # for (size_t i = start; i < end && i < container_size(&container); ++i) {
        #     result_push(&result, *container_at(&container, i));
        # }

        # Initialize the result container
        self._write(f"{elem.result_var} = {{0}}")
        self._eol()

        # Generate the slicing loop
        self._write(f"for (size_t i = {elem.start_expr}; i < {elem.end_expr} && i < {elem.container_name}_size(&{elem.container_name}); ++i) {{")
        self._eol()
        self._indent()

        # Push each element from source to result
        self._write(f"{elem.result_var}_push(&{elem.result_var}, *{elem.container_name}_at(&{elem.container_name}, i))")
        self._eol()

        self._dedent()
        self._write("}")
        self._eol()
        self.last_element = ElementType.STATEMENT

    def _write_struct_usage(self, elem: core.Struct) -> None:
        """Writes struct usage."""
        if not elem.name:
            raise ValueError("struct doesn't have a name. Did you mean to use a declaration?")
        self._write(f"struct {elem.name}")

    def _write_struct_declaration(self, elem: core.Struct) -> None:
        """Writes struct declaration."""
        self._write(f"struct {elem.name}")
        if self.style.brace_wrapping.after_struct:
            self._eol()
            self._start_line()
            self._write("{")
            self._eol()
        else:
            self._write(" {")
            self._eol()
        if len(elem.members):
            self._indent()
        for member in elem.members:
            self._start_line()
            self._write_struct_member(member)
            self._write(";")
            self._eol()
        if len(elem.members):
            self._dedent()
        self._start_line()
        self._write("}")
        self.last_element = ElementType.STRUCT_DECLARATION

    def _write_struct_member(self, elem: core.StructMember) -> None:
        """Writes struct member."""
        if isinstance(elem.data_type, core.Type):
            self._write_type_declaration(elem.data_type)
        elif isinstance(elem.data_type, core.Struct):
            self._write_struct_usage(elem.data_type)
        elif isinstance(elem.data_type, (core.Enum, core.Union)):
            # Write enum/union usage (just the name)
            self._write(elem.data_type.__class__.__name__.lower() + " " + elem.data_type.name)
        else:
            raise NotImplementedError(str(type(elem.data_type)))

        result = self._format_pointer_spacing(elem.pointer, elem.const, elem.data_type)
        result += elem.name
        result += self._format_array_dimensions(elem)
        self._write(result)

    # Preprocessor directives

    def _write_include_directive(self, elem: core.IncludeDirective) -> None:
        if elem.system:
            self._write(f"#include <{elem.path_to_file}>")
        else:
            self._write(f'#include "{elem.path_to_file}"')
        self.last_element = ElementType.DIRECTIVE

    def _write_define_directive(self, elem: core.DefineDirective) -> None:
        if elem.right is not None:
            self._write(f"#{' ' * elem.adjust}define {elem.left} {elem.right}")
        else:
            self._write(f"#{' ' * elem.adjust}define {elem.left}")
        self.last_element = ElementType.DIRECTIVE

    def _write_ifdef_directive(self, elem: core.IfdefDirective) -> None:
        self._write(f"#{' ' * elem.adjust}ifdef {elem.identifier}")
        self.last_element = ElementType.DIRECTIVE

    def _write_ifndef_directive(self, elem: core.IfndefDirective) -> None:
        self._write(f"#{' ' * elem.adjust}ifndef {elem.identifier}")
        self.last_element = ElementType.DIRECTIVE

    def _write_endif_directive(self, elem: core.EndifDirective) -> None:
        self._write(f"#{' ' * elem.adjust}endif")
        self.last_element = ElementType.DIRECTIVE

    def _write_extern(self, elem: core.Extern) -> None:
        self._write(f'extern "{elem.language}"')
        self.last_element = ElementType.DIRECTIVE

    def _write_if_statement(self, elem: core.IfStatement) -> None:
        """Write if statement with optional else clause."""
        # Write if condition
        self._write("if (")
        if isinstance(elem.condition, str):
            self._write(elem.condition)
        else:
            self._write_element(elem.condition)
        self._write(")")

        # Handle brace style
        if self.style.break_before_braces == BreakBeforeBraces.ATTACH:
            self._write(" ")
        else:
            self._eol()

        # Write then block
        if isinstance(elem.then_block, core.Block):
            self._write_block(elem.then_block)
        else:
            self._write("{")
            self._eol()
            self._indent()
            self._write_element(elem.then_block)
            self._dedent()
            self._write_line("}")

        # Write else block if present
        if elem.else_block is not None:
            self._write(" else")
            if self.style.break_before_braces == BreakBeforeBraces.ATTACH:
                self._write(" ")
            else:
                self._eol()

            if isinstance(elem.else_block, core.Block):
                self._write_block(elem.else_block)
            else:
                self._write("{")
                self._eol()
                self._indent()
                self._write_element(elem.else_block)
                self._dedent()
                self._write_line("}")

        self.last_element = ElementType.STATEMENT

    def _write_while_loop(self, elem: core.WhileLoop) -> None:
        """Write while loop."""
        # Write while condition
        self._write("while (")
        if isinstance(elem.condition, str):
            self._write(elem.condition)
        else:
            self._write_element(elem.condition)
        self._write(")")

        # Handle brace style
        if self.style.break_before_braces == BreakBeforeBraces.ATTACH:
            self._write(" ")
        else:
            self._eol()

        # Write body
        if isinstance(elem.body, core.Block):
            self._write_block(elem.body)
        else:
            self._write("{")
            self._eol()
            self._indent()
            self._write_element(elem.body)
            self._dedent()
            self._write_line("}")

        self.last_element = ElementType.STATEMENT

    def _write_for_loop(self, elem: core.ForLoop) -> None:
        """Write for loop."""
        # Write for header
        self._write("for (")

        # Write initialization
        if elem.init is not None:
            if isinstance(elem.init, str):
                self._write(elem.init)
            else:
                self._write_element(elem.init)
        self._write("; ")

        # Write condition
        if elem.condition is not None:
            if isinstance(elem.condition, str):
                self._write(elem.condition)
            else:
                self._write_element(elem.condition)
        self._write("; ")

        # Write increment
        if elem.increment is not None:
            if isinstance(elem.increment, str):
                self._write(elem.increment)
            else:
                self._write_element(elem.increment)

        self._write(")")

        # Handle brace style
        if self.style.break_before_braces == BreakBeforeBraces.ATTACH:
            self._write(" ")
        else:
            self._eol()

        # Write body
        if isinstance(elem.body, core.Block):
            self._write_block(elem.body)
        else:
            self._write("{")
            self._eol()
            self._indent()
            self._write_element(elem.body)
            self._dedent()
            self._write_line("}")

        self.last_element = ElementType.STATEMENT


    def _add_tier2_writers(self):
        """Add TIER 2 writer methods to this Writer instance."""
        pass  # Methods are defined below

    # TIER 2 syntactical elements writers
    def _write_break_statement(self, elem) -> None:
        """Write break statement."""
        self._write("break")
        self.last_element = ElementType.STATEMENT

    def _write_continue_statement(self, elem) -> None:
        """Write continue statement."""
        self._write("continue")
        self.last_element = ElementType.STATEMENT

    def _write_do_while_loop(self, elem) -> None:
        """Write do-while loop."""
        self._write("do")

        # Handle brace style
        if self.style.break_before_braces == BreakBeforeBraces.ATTACH:
            self._write(" ")
        else:
            self._eol()

        # Write body
        if isinstance(elem.body, core.Block):
            self._write_block(elem.body)
        else:
            self._write("{")
            self._eol()
            self._indent()
            self._write_element(elem.body)
            self._dedent()
            self._write_line("}")

        # Write while condition
        self._write(" while (")
        if isinstance(elem.condition, str):
            self._write(elem.condition)
        else:
            self._write_element(elem.condition)
        self._write(")")

        self.last_element = ElementType.STATEMENT

    def _write_ternary_operator(self, elem) -> None:
        """Write ternary conditional operator."""
        # Write condition
        if isinstance(elem.condition, str):
            self._write(elem.condition)
        else:
            self._write_element(elem.condition)

        self._write(" ? ")

        # Write true expression
        if isinstance(elem.true_expr, str):
            self._write(elem.true_expr)
        else:
            self._write_element(elem.true_expr)

        self._write(" : ")

        # Write false expression
        if isinstance(elem.false_expr, str):
            self._write(elem.false_expr)
        else:
            self._write_element(elem.false_expr)

        self.last_element = ElementType.STATEMENT

    def _write_sizeof_operator(self, elem) -> None:
        """Write sizeof operator."""
        self._write("sizeof(")

        if isinstance(elem.operand, str):
            self._write(elem.operand)
        else:
            self._write_element(elem.operand)

        self._write(")")
        self.last_element = ElementType.STATEMENT

    def _write_address_of_operator(self, elem) -> None:
        """Write address-of operator."""
        self._write("&")

        if isinstance(elem.operand, str):
            self._write(elem.operand)
        else:
            self._write_element(elem.operand)

        self.last_element = ElementType.STATEMENT

    def _write_dereference_operator(self, elem) -> None:
        """Write dereference operator."""
        self._write("*")

        if isinstance(elem.operand, str):
            self._write(elem.operand)
        else:
            self._write_element(elem.operand)

        self.last_element = ElementType.STATEMENT

    def _format_array_dimensions(self, elem) -> str:
        """Format array dimensions for multi-dimensional arrays."""
        # Check for flexible array member
        if hasattr(elem, 'is_flexible') and elem.is_flexible:
            return "[]"

        # First check if the element itself has array dimensions
        if hasattr(elem, 'array_dimensions') and elem.array_dimensions:
            return "".join(f"[{dim}]" for dim in elem.array_dimensions)
        elif hasattr(elem, 'array') and elem.array is not None:
            if elem.array == -1:  # Flexible array marker
                return "[]"
            return f"[{elem.array}]"

        # If not, check if the data_type has array dimensions (for variables with array types)
        if hasattr(elem, 'data_type'):
            if hasattr(elem.data_type, 'array_dimensions') and elem.data_type.array_dimensions:
                return "".join(f"[{dim}]" for dim in elem.data_type.array_dimensions)
            elif hasattr(elem.data_type, 'array') and elem.data_type.array is not None:
                if elem.data_type.array == -1:  # Flexible array marker
                    return "[]"
                return f"[{elem.data_type.array}]"

        return ""

    # TIER 3 syntactical elements writers
    def _write_enum(self, elem) -> None:
        """Write enum declaration."""
        self._write("enum ")
        self._write(elem.name)

        if elem.values:
            self._write(" {")
            if isinstance(elem.values, dict):
                enum_items = []
                for name, value in elem.values.items():
                    if value is not None:
                        enum_items.append(f"{name} = {value}")
                    else:
                        enum_items.append(name)

                if len(enum_items) > 3:  # Multi-line for readability
                    self._eol()
                    self._indent()
                    for i, item in enumerate(enum_items):
                        self._write(item)
                        if i < len(enum_items) - 1:
                            self._write(",")
                            self._eol()
                    self._dedent()
                    self._eol()
                    self._write("}")
                else:  # Single line for short enums
                    self._write(" ")
                    self._write(", ".join(enum_items))
                    self._write(" }")
            else:
                # Handle list format (shouldn't happen with current implementation)
                self._write(" ")
                self._write(", ".join(str(v) for v in elem.values))
                self._write(" }")

        self.last_element = ElementType.TYPE_DECLARATION

    def _write_enum_member(self, elem) -> None:
        """Write enum member."""
        self._write(elem.name)
        if elem.value is not None:
            self._write(f" = {elem.value}")
        self.last_element = ElementType.STATEMENT

    def _write_union(self, elem) -> None:
        """Write union declaration."""
        self._write("union ")
        self._write(elem.name)

        if elem.members:
            self._write(" {")
            self._eol()
            self._indent()

            for member in elem.members:
                self._write_element(member)
                self._write(";")
                self._eol()

            self._dedent()
            self._write("}")

        self.last_element = ElementType.TYPE_DECLARATION

    def _write_union_member(self, elem) -> None:
        """Write union member."""
        # Write type with qualifiers and pointers
        if hasattr(elem, 'const') and elem.const:
            self._write("const ")

        if isinstance(elem.data_type, str):
            self._write(elem.data_type)
        else:
            self._write_element(elem.data_type)

        # Handle pointer
        if hasattr(elem, 'pointer') and elem.pointer:
            if self.style.pointer_alignment == c_style.Alignment.LEFT:
                self._write("* ")
            elif self.style.pointer_alignment == c_style.Alignment.RIGHT:
                self._write(" *")
            else:  # MIDDLE
                self._write(" * ")
        else:
            self._write(" ")

        # Write member name
        self._write(elem.name)

        # Handle array
        array_str = self._format_array_dimensions(elem)
        if array_str:
            self._write(array_str)

        self.last_element = ElementType.STATEMENT

    # TIER 4: Advanced C11 Features writers
    def _write_function_pointer(self, elem) -> None:
        """Write function pointer type."""
        # Add qualifiers
        if elem.const:
            self._write("const ")
        if elem.volatile:
            self._write("volatile ")

        # Write return type
        if isinstance(elem.return_type, str):
            self._write(elem.return_type)
        else:
            self._write_element(elem.return_type)

        # Write function pointer syntax: (*name)
        self._write(" (*")
        self._write(elem.name)
        self._write(")")

        # Write parameters
        self._write("(")
        if elem.parameters:
            for i, param in enumerate(elem.parameters):
                if i > 0:
                    self._write(", ")
                if isinstance(param, str):
                    self._write(param)
                else:
                    self._write_variable_declaration(param)
        else:
            self._write("void")
        self._write(")")

        self.last_element = ElementType.TYPE_DECLARATION

    def _write_variadic_function(self, elem) -> None:
        """Write variadic function declaration."""
        # Write storage class
        if elem.static:
            self._write("static ")
        if elem.extern:
            self._write("extern ")

        # Write return type
        if elem.return_type:
            if isinstance(elem.return_type, str):
                self._write(elem.return_type)
            else:
                self._write_element(elem.return_type)
            self._write(" ")
        else:
            self._write("void ")

        # Write function name
        self._write(elem.name)

        # Write parameters
        self._write("(")
        if elem.fixed_params:
            for i, param in enumerate(elem.fixed_params):
                if i > 0:
                    self._write(", ")
                if isinstance(param, str):
                    self._write(param)
                else:
                    self._write_variable_declaration(param)
            self._write(", ...")
        else:
            self._write("...")
        self._write(")")

        self.last_element = ElementType.FUNCTION_DECLARATION

    def _write_static_assert(self, elem) -> None:
        """Write static assertion."""
        self._write("_Static_assert(")
        self._write(elem.condition)
        self._write(", ")
        self._write(f'"{elem.message}"')
        self._write(")")

        self.last_element = ElementType.STATEMENT

    def _write_generic_selection(self, elem) -> None:
        """Write generic selection."""
        self._write("_Generic(")
        self._write(elem.controlling_expr)

        # Write type associations
        for type_name, expr in elem.type_associations.items():
            self._write(", ")
            self._write(type_name)
            self._write(": ")
            self._write(expr)

        # Write default case if present
        if elem.default_expr:
            self._write(", default: ")
            self._write(elem.default_expr)

        self._write(")")

        self.last_element = ElementType.STATEMENT

    def _write_function_pointer_declaration(self, elem) -> None:
        """Write function pointer variable declaration."""
        # Write storage class
        if elem.static:
            self._write("static ")
        if elem.const:
            self._write("const ")

        # Write return type
        if isinstance(elem.return_type, str):
            self._write(elem.return_type)
        else:
            self._write_element(elem.return_type)

        # Write function pointer syntax: (*pointer_name)
        self._write(" (*")
        self._write(elem.pointer_name)
        self._write(")")

        # Write parameters
        self._write("(")
        if elem.parameters:
            for i, param in enumerate(elem.parameters):
                if i > 0:
                    self._write(", ")
                if isinstance(param, str):
                    self._write(param)
                else:
                    self._write_variable_declaration(param)
        else:
            self._write("void")
        self._write(")")

        self.last_element = ElementType.VARIABLE_DECLARATION

    # Additional Control Flow Writers

    def _write_switch_statement(self, elem) -> None:
        """Write switch statement."""
        self._write("switch (")
        if isinstance(elem.expression, (str, int, float)):
            self._write(str(elem.expression))
        else:
            self._write_element(elem.expression)
        self._write(")")

        # Handle brace style
        if self.style.break_before_braces == BreakBeforeBraces.ATTACH:
            self._write(" {")
        else:
            self._eol()
            self._write("{")

        self._eol()
        self._indent()

        # Write cases
        for case in elem.cases:
            self._write_element(case)

        # Write default case if present
        if elem.default_case:
            self._write_element(elem.default_case)

        self._dedent()
        self._write("}")

        self.last_element = ElementType.STATEMENT

    def _write_case_statement(self, elem) -> None:
        """Write case statement."""
        self._write("case ")
        if isinstance(elem.value, (str, int, float)):
            self._write(str(elem.value))
        else:
            self._write_element(elem.value)
        self._write(":")
        self._eol()

        # Write case statements with indentation
        if elem.statements:
            self._indent()
            for statement in elem.statements:
                if isinstance(statement, str):
                    self._write_line(statement)
                else:
                    self._write_element(statement)
                    if not hasattr(statement, '__class__') or statement.__class__.__name__ not in ['Block']:
                        self._write(";")
                    self._eol()
            self._dedent()

        self.last_element = ElementType.STATEMENT

    def _write_default_case(self, elem) -> None:
        """Write default case."""
        self._write("default:")
        self._eol()

        # Write default statements with indentation
        if elem.statements:
            self._indent()
            for statement in elem.statements:
                if isinstance(statement, str):
                    self._write_line(statement)
                else:
                    self._write_element(statement)
                    if not hasattr(statement, '__class__') or statement.__class__.__name__ not in ['Block']:
                        self._write(";")
                    self._eol()
            self._dedent()

        self.last_element = ElementType.STATEMENT

    def _write_goto_statement(self, elem) -> None:
        """Write goto statement."""
        self._write("goto ")
        self._write(elem.label)

        self.last_element = ElementType.STATEMENT

    def _write_label(self, elem) -> None:
        """Write label."""
        self._write(elem.name)
        self._write(":")

        self.last_element = ElementType.STATEMENT

    # Additional Operator Writers

    def _write_bitwise_operator(self, elem) -> None:
        """Write bitwise operator."""
        if elem.operator == "~":
            # Unary bitwise NOT
            self._write("~")
            if isinstance(elem.left, (str, int, float)):
                self._write(str(elem.left))
            else:
                self._write_element(elem.left)
        else:
            # Binary bitwise operators
            if isinstance(elem.left, (str, int, float)):
                self._write(str(elem.left))
            else:
                self._write_element(elem.left)

            self._write(f" {elem.operator} ")

            if isinstance(elem.right, (str, int, float)):
                self._write(str(elem.right))
            else:
                self._write_element(elem.right)

        self.last_element = ElementType.STATEMENT

    def _write_logical_operator(self, elem) -> None:
        """Write logical operator."""
        if elem.operator == "!":
            # Unary logical NOT
            self._write("!")
            if isinstance(elem.left, (str, int, float)):
                self._write(str(elem.left))
            else:
                self._write_element(elem.left)
        else:
            # Binary logical operators
            if isinstance(elem.left, (str, int, float)):
                self._write(str(elem.left))
            else:
                self._write_element(elem.left)

            self._write(f" {elem.operator} ")

            if isinstance(elem.right, (str, int, float)):
                self._write(str(elem.right))
            else:
                self._write_element(elem.right)

        self.last_element = ElementType.STATEMENT

    def _write_increment_operator(self, elem) -> None:
        """Write increment operator."""
        if elem.prefix:
            # Prefix increment: ++var
            self._write("++")
            if isinstance(elem.operand, (str, int, float)):
                self._write(str(elem.operand))
            else:
                self._write_element(elem.operand)
        else:
            # Postfix increment: var++
            if isinstance(elem.operand, (str, int, float)):
                self._write(str(elem.operand))
            else:
                self._write_element(elem.operand)
            self._write("++")

        self.last_element = ElementType.STATEMENT

    def _write_decrement_operator(self, elem) -> None:
        """Write decrement operator."""
        if elem.prefix:
            # Prefix decrement: --var
            self._write("--")
            if isinstance(elem.operand, (str, int, float)):
                self._write(str(elem.operand))
            else:
                self._write_element(elem.operand)
        else:
            # Postfix decrement: var--
            if isinstance(elem.operand, (str, int, float)):
                self._write(str(elem.operand))
            else:
                self._write_element(elem.operand)
            self._write("--")

        self.last_element = ElementType.STATEMENT

    def _write_compound_assignment_operator(self, elem) -> None:
        """Write compound assignment operator."""
        if isinstance(elem.left, (str, int, float)):
            self._write(str(elem.left))
        else:
            self._write_element(elem.left)

        self._write(f" {elem.operator} ")

        if isinstance(elem.right, (str, int, float)):
            self._write(str(elem.right))
        else:
            self._write_element(elem.right)

        self.last_element = ElementType.STATEMENT

    # C11 Advanced Features Writer Methods

    def _write_atomic_type(self, elem) -> None:
        """Write C11 atomic type (_Atomic)."""
        self._write("_Atomic(")
        if isinstance(elem.base_type, str):
            self._write(elem.base_type)
        else:
            self._write_element(elem.base_type)
        self._write(")")
        self.last_element = ElementType.TYPE_DECLARATION

    def _write_alignas_specifier(self, elem) -> None:
        """Write C11 alignment specifier (_Alignas)."""
        self._write("_Alignas(")
        if isinstance(elem.alignment, int):
            self._write(str(elem.alignment))
        else:
            self._write(elem.alignment)
        self._write(")")
        self.last_element = ElementType.TYPE_DECLARATION

    def _write_alignof_operator(self, elem) -> None:
        """Write C11 alignment query operator (_Alignof)."""
        self._write("_Alignof(")
        if isinstance(elem.type_or_expr, str):
            self._write(elem.type_or_expr)
        else:
            self._write_element(elem.type_or_expr)
        self._write(")")
        self.last_element = ElementType.STATEMENT

    def _write_thread_local_specifier(self, elem) -> None:
        """Write C11 thread-local storage specifier (_Thread_local)."""
        self._write("_Thread_local ")
        if isinstance(elem.variable, str):
            self._write(elem.variable)
        else:
            self._write_element(elem.variable)
        self.last_element = ElementType.STATEMENT

    def _write_complex_type(self, elem) -> None:
        """Write C11 complex number type (_Complex)."""
        self._write(elem.base_type)
        self.last_element = ElementType.TYPE_DECLARATION

    def _write_fixed_width_integer_type(self, elem) -> None:
        """Write C11 fixed-width integer type."""
        self._write(elem.base_type)
        self.last_element = ElementType.TYPE_DECLARATION

    def _write_auto_specifier(self, elem) -> None:
        """Write C11 auto storage class specifier."""
        self._write("auto ")
        if isinstance(elem.variable, str):
            self._write(elem.variable)
        else:
            self._write_element(elem.variable)
        self.last_element = ElementType.STATEMENT

    def _write_register_specifier(self, elem) -> None:
        """Write register storage class specifier."""
        self._write("register ")
        if isinstance(elem.variable, str):
            self._write(elem.variable)
        else:
            self._write_element(elem.variable)
        self.last_element = ElementType.STATEMENT

    def _write_restrict_specifier(self, elem) -> None:
        """Write C99/C11 restrict type qualifier."""
        if isinstance(elem.pointer_variable, str):
            self._write(f"restrict {elem.pointer_variable}")
        else:
            self._write("restrict ")
            self._write_element(elem.pointer_variable)
        self.last_element = ElementType.STATEMENT

    def _write_inline_specifier(self, elem) -> None:
        """Write inline function specifier."""
        self._write("inline ")
        if isinstance(elem.function, str):
            self._write(elem.function)
        else:
            self._write_element(elem.function)
        self.last_element = ElementType.STATEMENT

    def _write_flexible_array_member(self, elem) -> None:
        """Write C99/C11 flexible array member."""
        if isinstance(elem.element_type, str):
            self._write(elem.element_type)
        else:
            self._write_element(elem.element_type)
        self._write(f" {elem.name}[]")
        self.last_element = ElementType.STATEMENT

    def _write_designated_initializer(self, elem) -> None:
        """Write C99/C11 designated initializer."""
        # Write designators
        for i, designator in enumerate(elem.designators):
            if isinstance(designator, int):
                self._write(f"[{designator}]")
            else:
                self._write(f".{designator}")

        self._write(" = ")

        # Write value
        if isinstance(elem.value, str):
            self._write(elem.value)
        else:
            self._write_element(elem.value)

        self.last_element = ElementType.STATEMENT

    def _write_pointer_to_pointer(self, elem) -> None:
        """Write multi-level pointer type."""
        if isinstance(elem.base_type, str):
            self._write(elem.base_type)
        else:
            self._write_element(elem.base_type)
        self._write(elem.pointer_levels)
        self.last_element = ElementType.TYPE_DECLARATION

    def _write_pragma_directive(self, elem) -> None:
        """Write pragma preprocessor directive."""
        self._write(f"#pragma {elem.pragma_text}")
        self.last_element = ElementType.DIRECTIVE

    def _write_function_like_macro(self, elem) -> None:
        """Write function-like macro with parameters."""
        self._write(f"#define {elem.name}(")

        # Write parameters
        for i, param in enumerate(elem.parameters):
            if i > 0:
                self._write(", ")
            self._write(param)

        self._write(f") {elem.replacement}")
        self.last_element = ElementType.DIRECTIVE

    def _write_variadic_macro(self, elem) -> None:
        """Write variadic macro with ... parameter."""
        self._write(f"#define {elem.name}(")

        # Write fixed parameters
        for i, param in enumerate(elem.fixed_params):
            if i > 0:
                self._write(", ")
            self._write(param)

        # Add variadic parameter
        if elem.fixed_params:
            self._write(", ...")
        else:
            self._write("...")

        self._write(f") {elem.replacement}")
        self.last_element = ElementType.DIRECTIVE

    def _write_raw_code(self, elem) -> None:
        """Write raw C code."""
        self._write(elem.code)
        self.last_element = ElementType.STATEMENT

    def _write_stc_container(self, elem) -> None:
        """Write STC container element."""
        self._write(f"{elem.container_type} {elem.name}")
        self.last_element = ElementType.DECLARATION

    def _write_stc_operation(self, elem) -> None:
        """Write STC operation element."""
        self._write(elem.operation_code)
        self.last_element = ElementType.STATEMENT

