"""Factory classes."""

from collections import namedtuple
from typing import Any, Union

from . import core

BuiltInTypes = namedtuple("BuiltInTypes", ["char", "short", "int", "long", "float", "double"])

types = BuiltInTypes(
    core.Type("char"),
    core.Type("short"),
    core.Type("int"),
    core.Type("long"),
    core.Type("float"),
    core.Type("double"),
)


class CFactory:
    """Factory for the C programming language."""

    def blank(self) -> core.Blank:
        """Blank line."""
        return core.Blank()

    def line(self, inner: Any) -> core.Line:
        """Like statement but doesn't add ';' before new-line."""
        return core.Line(inner)

    def whitespace(self, width: int) -> core.Whitespace:
        """White space of user-defined length."""
        return core.Whitespace(width)

    def line_comment(self, text: str, adjust: int = 1) -> core.LineComment:
        """New line comment."""
        return core.LineComment(text, adjust)

    def block_comment(
        self,
        text: str | list[str],
        adjust: int = 1,
        width: int = 0,
        line_start: str = "",
    ) -> core.BlockComment:
        """New block comment."""
        return core.BlockComment(text, adjust, width, line_start)

    def sequence(self) -> core.Sequence:
        """New sequence."""
        return core.Sequence()

    def include(self, path_to_file: str, adjust: int = 0) -> core.IncludeDirective:
        """New include directive."""
        return core.IncludeDirective(path_to_file, adjust=adjust)

    def sysinclude(self, path_to_file, adjust: int = 0) -> core.IncludeDirective:
        """New system-level include directive."""
        return core.IncludeDirective(path_to_file, system=True, adjust=adjust)

    def ifdef(self, identifier, adjust: int = 0) -> core.IfdefDirective:
        """New ifdef preprocessor directove."""
        return core.IfdefDirective(identifier, adjust=adjust)

    def ifndef(self, identifier, adjust: int = 0) -> core.IfndefDirective:
        """New ifndef preprocessor directove."""
        return core.IfndefDirective(identifier, adjust=adjust)

    def endif(self, adjust: int = 0) -> core.EndifDirective:
        """New endif preprocessor directove."""
        return core.EndifDirective(adjust=adjust)

    def define(self, left: str, right: str | None = None, adjust: int = 0) -> core.DefineDirective:
        """New define preprocessor directive."""
        return core.DefineDirective(left, right, adjust=adjust)

    def extern(self, language: str) -> core.Extern:
        """New extern declaration."""
        return core.Extern(language)

    def block(self) -> core.Block:
        """New block sequence."""
        return core.Block()

    def function(
        self,
        name: str,
        return_type: str | core.DataType | None = None,
        static: bool = False,
        const: bool = False,  # This is not const of the return type
        extern: bool = False,
        params: core.Variable | list[core.Variable] | None = None,
    ) -> core.Function:
        """New function."""
        return core.Function(name, return_type, static, const, extern, params)

    def type(
        self,
        type_ref: str | core.Type,
        const: bool = False,
        pointer: bool = False,
        volatile: bool = False,
        array: "int | None" = None,
    ) -> core.Type:
        """New type."""
        return core.Type(type_ref, const, pointer, volatile, array)

    def struct_member(
        self,
        name: str,
        data_type: str | core.Type | core.Struct,
        const: bool = False,  # Pointer qualifier only
        pointer: bool = False,
        array: "int | None" = None,
    ) -> core.StructMember:
        """New StructMember."""
        return core.StructMember(name, data_type, const, pointer, array)

    def struct(
        self,
        name: str,
        members: core.StructMember | list[core.StructMember] | None = None,
    ) -> core.Struct:
        """New Struct."""
        return core.Struct(name, members)

    def variable(
        self,
        name: str,
        data_type: str | core.Type | core.Struct,
        const: bool = False,  # Only used as pointer qualifier
        pointer: bool = False,
        extern: bool = False,
        static: bool = False,
        array: "int | None" = None,
    ) -> core.Variable:
        """New variable."""
        return core.Variable(name, data_type, const, pointer, extern, static, array)

    def typedef(
        self,
        name: str,
        base_type: str | core.DataType | core.Declaration,
        const: bool = False,  # Only used as pointer qualifier
        pointer: bool = False,
        volatile: bool = False,
        array: "int | None" = None,
    ) -> core.TypeDef:
        """New typedef."""
        return core.TypeDef(name, base_type, const, pointer, volatile, array)

    def statement(self, expression: Any) -> core.Statement:
        """New statement."""
        return core.Statement(expression)

    def assignment(self, lhs: Any, rhs: Any) -> core.Assignment:
        """New assignment."""
        return core.Assignment(lhs, rhs)

    def str_literal(self, text: str) -> core.StringLiteral:
        """New function call."""
        return core.StringLiteral(text)

    arg_types = int | float | str | core.Element

    def func_call(self, name: str, args: list[arg_types] | arg_types | None = None) -> core.FunctionCall:
        """New function call."""
        if args is None:
            return core.FunctionCall(name, None)
        elif isinstance(args, list):
            return core.FunctionCall(name, args)
        else:
            return core.FunctionCall(name, [args])

    def func_return(self, expression: int | float | str | core.Element) -> core.FunctionReturn:
        """New return expression."""
        return core.FunctionReturn(expression)

    def declaration(
        self,
        element: Union[core.Variable, core.Function, core.DataType],
        init_value: Any | None = None,
    ) -> core.Declaration:
        """New declaration."""
        return core.Declaration(element, init_value)

    def if_statement(self, condition: Any, then_block: Any, else_block: Any = None) -> core.IfStatement:
        """New if statement with optional else clause."""
        return core.IfStatement(condition, then_block, else_block)

    def while_loop(self, condition: Any, body: Any) -> core.WhileLoop:
        """New while loop."""
        return core.WhileLoop(condition, body)

    def for_loop(self, init: Any = None, condition: Any = None, increment: Any = None, body: Any = None) -> core.ForLoop:
        """New for loop."""
        return core.ForLoop(init, condition, increment, body)

    # Additional syntactical elements
    def break_statement(self) -> "core.BreakStatement":
        """New break statement for loop control."""
        return core.BreakStatement()

    def continue_statement(self) -> "core.ContinueStatement":
        """New continue statement for loop control."""
        return core.ContinueStatement()

    def do_while_loop(self, body: Any, condition: Any) -> "core.DoWhileLoop":
        """New do-while loop."""
        return core.DoWhileLoop(body, condition)

    def ternary(self, condition: Any, true_expr: Any, false_expr: Any) -> "core.TernaryOperator":
        """New ternary conditional operator (condition ? true_expr : false_expr)."""
        return core.TernaryOperator(condition, true_expr, false_expr)

    def sizeof(self, operand: Union[str, core.DataType, core.Element]) -> "core.SizeofOperator":
        """New sizeof operator."""
        return core.SizeofOperator(operand)

    def address_of(self, operand: Union[str, core.Element]) -> "core.AddressOfOperator":
        """New address-of operator (&)."""
        return core.AddressOfOperator(operand)

    def dereference(self, operand: Union[str, core.Element]) -> "core.DereferenceOperator":
        """New dereference operator (*)."""
        return core.DereferenceOperator(operand)

    # TIER 3 Language Elements
    def enum(self, name: str, values: "list[str] | dict[str, int] | None" = None) -> "core.Enum":
        """New enumeration type."""
        return core.Enum(name, values)

    def enum_member(self, name: str, value: "int | None" = None) -> "core.EnumMember":
        """New enumeration member."""
        return core.EnumMember(name, value)

    def union(self, name: str, members: "core.UnionMember | list[core.UnionMember] | None" = None) -> "core.Union":
        """New union type."""
        return core.Union(name, members)

    def union_member(
        self,
        name: str,
        data_type: "str | core.Type | core.Struct | core.Union",
        const: bool = False,
        pointer: bool = False,
        array: "int | None" = None
    ) -> "core.UnionMember":
        """New union member."""
        return core.UnionMember(name, data_type, const, pointer, array)

    def multi_pointer_type(
        self,
        base_type: "str | core.Type",
        pointer_level: int,
        const: bool = False,
        volatile: bool = False
    ) -> core.Type:
        """New multi-level pointer type (e.g., int**, char***)."""
        return core.Type(base_type, const, pointer_level, volatile)

    def multi_array_type(
        self,
        base_type: "str | core.Type",
        dimensions: list[int],
        const: bool = False,
        volatile: bool = False
    ) -> core.Type:
        """New multi-dimensional array type (e.g., int[10][20])."""
        return core.Type(base_type, const, False, volatile, dimensions)

    # TIER 4 Language Elements - Advanced C11 Features
    def function_pointer(
        self,
        name: str,
        return_type: "str | core.Type | core.DataType",
        parameters: "list[core.Variable] | None" = None,
        const: bool = False,
        volatile: bool = False
    ) -> "core.FunctionPointer":
        """New function pointer type."""
        return core.FunctionPointer(name, return_type, parameters, const, volatile)

    def variadic_function(
        self,
        name: str,
        return_type: "str | core.Type | core.DataType | None" = None,
        fixed_params: "list[core.Variable] | None" = None,
        static: bool = False,
        extern: bool = False
    ) -> "core.VariadicFunction":
        """New variadic function with variable arguments (...)."""
        return core.VariadicFunction(name, return_type, fixed_params, static, extern)

    def static_assert(self, condition: str, message: str) -> "core.StaticAssert":
        """New static assertion for compile-time checks (_Static_assert)."""
        return core.StaticAssert(condition, message)

    def generic_selection(
        self,
        controlling_expr: str,
        type_associations: "dict[str, str]",
        default_expr: "str | None" = None
    ) -> "core.GenericSelection":
        """New generic selection for type-generic programming (_Generic)."""
        return core.GenericSelection(controlling_expr, type_associations, default_expr)

    def function_pointer_declaration(
        self,
        pointer_name: str,
        return_type: "str | core.Type | core.DataType",
        parameters: "list[core.Variable] | None" = None,
        const: bool = False,
        static: bool = False
    ) -> "core.FunctionPointerDeclaration":
        """New function pointer variable declaration."""
        return core.FunctionPointerDeclaration(pointer_name, return_type, parameters, const, static)

    # Additional Control Flow Elements

    def switch_statement(
        self,
        expression: Union[str, core.Element],
        cases: "list[core.CaseStatement] | None" = None,
        default_case: "core.DefaultCase | None" = None
    ) -> "core.SwitchStatement":
        """New switch statement for multi-way branching."""
        return core.SwitchStatement(expression, cases, default_case)

    def case_statement(
        self,
        value: Union[str, int, core.Element],
        statements: "Any | list[Any] | None" = None
    ) -> "core.CaseStatement":
        """New case statement within a switch."""
        return core.CaseStatement(value, statements)

    def default_case(
        self,
        statements: "Any | list[Any] | None" = None
    ) -> "core.DefaultCase":
        """New default case within a switch statement."""
        return core.DefaultCase(statements)

    def goto_statement(self, label: str) -> "core.GotoStatement":
        """New goto statement for unconditional jumps."""
        return core.GotoStatement(label)

    def label(self, name: str) -> "core.Label":
        """New label for goto statements and code marking."""
        return core.Label(name)

    # Additional Operators

    def bitwise_and(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.BitwiseOperator":
        """New bitwise AND operator (&)."""
        return core.BitwiseOperator(left, "&", right)

    def bitwise_or(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.BitwiseOperator":
        """New bitwise OR operator (|)."""
        return core.BitwiseOperator(left, "|", right)

    def bitwise_xor(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.BitwiseOperator":
        """New bitwise XOR operator (^)."""
        return core.BitwiseOperator(left, "^", right)

    def bitwise_not(self, operand: Union[str, core.Element]) -> "core.BitwiseOperator":
        """New bitwise NOT operator (~)."""
        return core.BitwiseOperator(operand, "~")

    def bitwise_left_shift(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.BitwiseOperator":
        """New bitwise left shift operator (<<)."""
        return core.BitwiseOperator(left, "<<", right)

    def bitwise_right_shift(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.BitwiseOperator":
        """New bitwise right shift operator (>>)."""
        return core.BitwiseOperator(left, ">>", right)

    def logical_and(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.LogicalOperator":
        """New logical AND operator (&&)."""
        return core.LogicalOperator(left, "&&", right)

    def logical_or(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.LogicalOperator":
        """New logical OR operator (||)."""
        return core.LogicalOperator(left, "||", right)

    def logical_not(self, operand: Union[str, core.Element]) -> "core.LogicalOperator":
        """New logical NOT operator (!)."""
        return core.LogicalOperator(operand, "!")

    def pre_increment(self, operand: Union[str, core.Element]) -> "core.IncrementOperator":
        """New prefix increment operator (++var)."""
        return core.IncrementOperator(operand, prefix=True)

    def post_increment(self, operand: Union[str, core.Element]) -> "core.IncrementOperator":
        """New postfix increment operator (var++)."""
        return core.IncrementOperator(operand, prefix=False)

    def pre_decrement(self, operand: Union[str, core.Element]) -> "core.DecrementOperator":
        """New prefix decrement operator (--var)."""
        return core.DecrementOperator(operand, prefix=True)

    def post_decrement(self, operand: Union[str, core.Element]) -> "core.DecrementOperator":
        """New postfix decrement operator (var--)."""
        return core.DecrementOperator(operand, prefix=False)

    def add_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound addition assignment operator (+=)."""
        return core.CompoundAssignmentOperator(left, "+=", right)

    def sub_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound subtraction assignment operator (-=)."""
        return core.CompoundAssignmentOperator(left, "-=", right)

    def mul_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound multiplication assignment operator (*=)."""
        return core.CompoundAssignmentOperator(left, "*=", right)

    def div_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound division assignment operator (/=)."""
        return core.CompoundAssignmentOperator(left, "/=", right)

    def mod_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound modulo assignment operator (%=)."""
        return core.CompoundAssignmentOperator(left, "%=", right)

    def bitwise_and_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound bitwise AND assignment operator (&=)."""
        return core.CompoundAssignmentOperator(left, "&=", right)

    def bitwise_or_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound bitwise OR assignment operator (|=)."""
        return core.CompoundAssignmentOperator(left, "|=", right)

    def bitwise_xor_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound bitwise XOR assignment operator (^=)."""
        return core.CompoundAssignmentOperator(left, "^=", right)

    def left_shift_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound left shift assignment operator (<<=)."""
        return core.CompoundAssignmentOperator(left, "<<=", right)

    def right_shift_assign(self, left: Union[str, core.Element], right: Union[str, core.Element]) -> "core.CompoundAssignmentOperator":
        """New compound right shift assignment operator (>>=)."""
        return core.CompoundAssignmentOperator(left, ">>=", right)
