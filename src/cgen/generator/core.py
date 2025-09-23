"""Cfile core."""

import re
from typing import Any, Union


def _validate_c_identifier(name: str, context: str = "identifier") -> None:
    """Validate that a string is a valid C identifier."""
    if not isinstance(name, str):
        raise TypeError(f"{context} must be a string, got {type(name)}")
    if not name:
        raise ValueError(f"{context} cannot be empty")
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        raise ValueError(f"'{name}' is not a valid C {context}")


class Element:
    """A code element, for example an expression."""


class Directive(Element):
    """Preprocessor directive."""

    def __init__(self, adjust: int = 0) -> None:
        self.adjust = adjust


class IncludeDirective(Directive):
    """Include directive."""

    def __init__(self, path_to_file: str, system: bool = False, adjust: int = 0) -> None:
        super().__init__(adjust)
        self.path_to_file = path_to_file
        self.system = system


class IfdefDirective(Directive):
    """Ifdef preprocessor directive."""

    def __init__(self, identifier: str, adjust: int = 0) -> None:
        super().__init__(adjust)
        self.identifier = identifier


class IfndefDirective(Directive):
    """Ifndef preprocessor directive."""

    def __init__(self, identifier: str, adjust: int = 0) -> None:
        super().__init__(adjust)
        self.identifier = identifier


class EndifDirective(Directive):
    """Endif preprocessor directive."""


class DefineDirective(Directive):
    """Preprocessor define directive."""

    def __init__(self, left: str, right: str | None = None, adjust: int = 0) -> None:
        super().__init__(adjust)
        self.left = left
        self.right = right


class Extern(Element):
    """Extern declaration."""

    def __init__(self, language: str) -> None:
        self.language = language


class Comment(Element):
    """Comment base.

    adjust: Adds spaces before comment begins to allow right-adjustment
    """

    def __init__(self, text: str | list[str], adjust: int = 1) -> None:
        self.text = text
        self.adjust = adjust


class RawCode(Element):
    """Raw C code element."""

    def __init__(self, code: str) -> None:
        """Initialize raw code element."""
        self.code = code


class BlockComment(Comment):
    """Block Comment.

    width: When > 0, sets the number of asterisks used on first and last line.
           Also puts the text between first and last line.
    line_start: Combine with width > 0. Puts this string at beginning of each line
                inside the comment
    """

    def __init__(
        self,
        text: str | list[str],
        adjust: int = 1,
        width: int = 0,
        line_start: str = "",
    ) -> None:
        super().__init__(text, adjust)
        self.width = width
        self.line_start = line_start


class LineComment(Comment):
    """Line Comment."""


class Whitespace(Element):
    """Whitespace."""

    def __init__(self, width) -> None:
        self.width = width


class Blank(Whitespace):
    """Blank line."""

    def __init__(self) -> None:
        super().__init__(0)


class Line(Element):
    """Adds a newline once all inner parts have been written."""

    def __init__(self, parts: str | Element | list) -> None:
        if isinstance(parts, (str, Element)):
            self.parts = [parts]
        elif isinstance(parts, list):
            self.parts = parts
        else:
            raise TypeError("Invalid type:" + str(type(parts)))


class DataType(Element):
    """Base class for all data types."""

    def __init__(self, name: str | None) -> None:
        self.name = name


class Type(DataType):
    """Data type."""

    def __init__(
        self,
        base_type: Union[str, "Type"],
        const: bool = False,
        pointer: "bool | int" = False,
        volatile: bool = False,
        array: "int | list[int] | None" = None,
    ) -> None:
        super().__init__(None)
        if isinstance(base_type, str):
            if not base_type.strip():
                raise ValueError("type name cannot be empty")
        elif not isinstance(base_type, (Type, DataType)):
            raise TypeError(f"base_type must be str, Type, or DataType, got {type(base_type)}")
        # Handle multi-level pointers
        if isinstance(pointer, bool):
            self.pointer_level = 1 if pointer else 0
        elif isinstance(pointer, int):
            if pointer < 0:
                raise ValueError("pointer level must be non-negative")
            self.pointer_level = pointer
        else:
            # Keep backward compatibility
            self.pointer_level = 1 if pointer else 0

        # Handle multi-dimensional arrays
        if array is not None:
            if isinstance(array, int):
                if array < 0:
                    raise ValueError("array size must be non-negative")
                self.array_dimensions = [array]
            elif isinstance(array, list):
                if not all(isinstance(dim, int) and dim >= 0 for dim in array):
                    raise ValueError("all array dimensions must be non-negative integers")
                self.array_dimensions = array[:]
            else:
                # Keep backward compatibility
                self.array_dimensions = [array] if array is not None else []
        else:
            self.array_dimensions = []

        self.base_type = base_type
        self.const = const
        self.volatile = volatile

        # Keep legacy pointer and array properties for backward compatibility
        self.pointer = self.pointer_level > 0
        self.array = self.array_dimensions[0] if self.array_dimensions else None

    def qualifier(self, name) -> bool:
        """Returns the status of named qualifier."""
        if name == "const":
            return self.const
        if name == "volatile":
            return self.volatile
        else:
            raise KeyError(name)


class StructMember(Element):
    """Struct element.

    This is similar to Variable
    but doesn't support type qualifier such as static
    or extern
    """

    def __init__(
        self,
        name: str,
        data_type: DataType | str,
        const: bool = False,  # Pointer qualifier only
        pointer: bool = False,
        array: int | None = None,
    ) -> None:
        _validate_c_identifier(name, "struct member name")
        if array is not None and (not isinstance(array, int) or (array < 0 and array != -1)):
            raise ValueError("array size must be a non-negative integer, -1 (flexible array), or None")
        self.name = name
        self.const = const
        self.pointer = pointer
        self.array = array
        if isinstance(data_type, DataType):
            self.data_type = data_type
        elif isinstance(data_type, str):
            self.data_type = Type(data_type)
        else:
            raise TypeError(f"data_type must be str or DataType, got {type(data_type)}")


class Struct(DataType):
    """A struct definition."""

    def __init__(self, name: str | None, members: StructMember | list[StructMember] | None = None) -> None:
        if name is not None:
            _validate_c_identifier(name, "struct name")
        super().__init__(name)
        self.members: list[StructMember] = []
        if members is not None:
            if isinstance(members, StructMember):
                self.append(members)
            elif isinstance(members, list):
                for member in members:
                    self.append(member)
            else:
                raise TypeError("members must be StructMember, list of StructMembers, or None")

    def append(self, member: StructMember) -> None:
        """Appends new element to the struct definition."""
        if not isinstance(member, StructMember):
            raise TypeError(f'Invalid type, expected "StructMember", got {str(type(member))}')
        self.members.append(member)

    def make_member(
        self,
        name: str,
        data_type: str | Type,
        const: bool = False,  # Pointer qualifier only
        pointer: bool = False,
        array: int | None = None,
    ) -> StructMember:
        """Creates a new StructMember and appends it to the list of elements."""
        member = StructMember(name, data_type, const, pointer, array)
        self.members.append(member)
        return member


class TypeDef(DataType):
    """Type definition (typedef)."""

    def __init__(
        self,
        name: str,
        base_type: Union[str, "DataType", "Declaration"],
        const: bool = False,
        pointer: bool = False,
        volatile: bool = False,
        array: int | None = None,
    ) -> None:
        super().__init__(name)
        self.const = const
        self.volatile = volatile
        self.pointer = pointer
        self.array = array
        self.base_type: DataType | Declaration
        if isinstance(base_type, DataType):
            self.base_type = base_type
        elif isinstance(base_type, str):
            self.base_type = Type(base_type)
        elif isinstance(base_type, Declaration):
            if not isinstance(base_type.element, DataType):
                err_msg = f"base_type: Declaration must declare a type, not {str(type(base_type.element))}"
            self.base_type = base_type
        else:
            err_msg = 'base_type: Invalid type, expected "str" | "DataType" | "Declaration",'
            err_msg += f" got {str(type(base_type))}"
            raise TypeError(err_msg)

    def qualifier(self, name) -> bool:
        """Returns the status of named qualifier."""
        if name == "const":
            return self.const
        if name == "volatile":
            return self.volatile
        else:
            raise KeyError(name)


class Variable(Element):
    """Variable declaration."""

    def __init__(
        self,
        name: str,
        data_type: str | DataType,
        const: bool = False,  # Only used as pointer qualifier
        pointer: bool = False,
        extern: bool = False,
        static: bool = False,
        array: int | None = None,
    ) -> None:
        _validate_c_identifier(name, "variable name")
        if array is not None and (not isinstance(array, int) or array < 0):
            raise ValueError("array size must be a non-negative integer or None")
        self.name = name
        self.const = const
        self.pointer = pointer
        self.extern = extern
        self.static = static
        self.array = array
        if isinstance(data_type, DataType):
            self.data_type = data_type
        elif isinstance(data_type, str):
            self.data_type = Type(data_type)
        else:
            raise TypeError(f"data_type must be str or DataType, got {type(data_type)}")

    def qualifier(self, name) -> bool:
        """Returns the status of named qualifier."""
        if name == "const":
            return self.const  # pointer qualifier, not the same as as type qualifier
        if name == "static":
            return self.static
        if name == "extern":
            return self.extern
        else:
            raise KeyError(name)


class Function(Element):
    """Function declaration."""

    def __init__(
        self,
        name: str,
        return_type: str | DataType | None = None,
        static: bool = False,
        const: bool = False,  # const function (as seen in C++)
        extern: bool = False,
        params: Variable | list[Variable] | None = None,
    ) -> None:
        _validate_c_identifier(name, "function name")
        self.name = name
        self.static = static
        self.const = const
        self.extern = extern
        if isinstance(return_type, DataType):
            self.return_type = return_type
        elif isinstance(return_type, str):
            self.return_type = Type(return_type)
        elif return_type is None:  # None is a synomym for void
            self.return_type = Type("void")
        else:
            raise TypeError(f"return_type must be str, DataType, or None, got {type(return_type)}")
        self.params: list[Variable] = []
        if params is not None:
            if isinstance(params, Variable):
                self.append(params)
            elif isinstance(params, list):
                for param in params:
                    self.append(param)
            else:
                raise TypeError("params must be Variable, list of Variables, or None")

    def append(self, param: Variable) -> "Function":
        """Adds new function parameter."""
        if not isinstance(param, (Variable)):
            raise TypeError("Expected Variable or FunctionPtr object")
        self.params.append(param)
        return self

    def make_param(
        self,
        name: str,
        data_type: str | Type,
        const: bool = False,
        pointer: bool = False,
        array: int | None = None,
    ) -> "Function":
        """Creates new Variable from arguments and adds as parameter."""
        param = Variable(name, data_type, const=const, pointer=pointer, array=array)
        return self.append(param)


class Declaration(Element):
    """A declaration element.

    Valid sub-elements:
    - Variable
    - DataType (including struct)
    - Function
    """

    def __init__(
        self,
        element: Union[Variable, Function, DataType],
        init_value: Any | None = None,
    ) -> None:
        if isinstance(element, (Variable, Function, DataType)):
            self.element = element
            self.init_value = None
        else:
            raise TypeError(f"element: Invalid type '{str(type(element))}'")
        if init_value is not None:
            if not isinstance(element, Variable):
                raise ValueError("init_value only allowed for Variable declarations")
            self.init_value = init_value


class FunctionCall(Element):
    """Function call expression."""

    def __init__(self, name: str, args: list[int | float | str | Element] | None = None) -> None:
        self.name = name
        self.args: list[str | Element] = []
        if args is not None:
            for arg in args:
                self.append(arg)

    def append(self, arg: int | float | str | Element) -> "FunctionCall":
        """Appends argument to function call, can be chained."""
        if isinstance(arg, (int, float)):
            self.args.append(str(arg))
        elif isinstance(arg, (str, Element)):
            self.args.append(arg)
        else:
            raise NotImplementedError(str(type(arg)))
        return self


class BinaryExpression(Element):
    """Binary expression (e.g., a + b, func() * 2)."""

    def __init__(self, left: str | Element, operator: str, right: str | Element) -> None:
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpression(Element):
    """Unary expression (e.g., -x, !flag)."""

    def __init__(self, operator: str, operand: str | Element) -> None:
        self.operator = operator
        self.operand = operand


class FunctionReturn(Element):
    """Function return expression."""

    def __init__(self, expression: int | float | bool | str | Element) -> None:
        self.expression: str | Element
        if isinstance(expression, bool):
            self.expression = "true" if expression else "false"
        elif isinstance(expression, (int, float)):
            self.expression = str(expression)
        elif isinstance(expression, (str, Element)):
            self.expression = expression
        else:
            raise NotImplementedError(str(type(expression)))


class Assignment(Element):
    """Assignment has a left-hand-side and right-hand-side expressions."""

    def __init__(self, lhs: Any, rhs: Any) -> None:
        self.lhs = self._check_and_convert(lhs)
        self.rhs = self._check_and_convert(rhs)

    def _check_and_convert(self, elem: Any):
        if isinstance(elem, bool):
            return "true" if elem else "false"
        elif isinstance(elem, (int, float, str)):
            return str(elem)
        elif isinstance(elem, Element):
            return elem
        else:
            raise NotImplementedError(str(type(elem)))


class Statement(Element):
    """A statement can contain one or more expressions."""

    def __init__(self, expression: Any) -> None:
        parts = []
        if isinstance(expression, (list, tuple)):
            for part in expression:
                parts.append(self._check_and_convert(part))
        else:
            parts.append(self._check_and_convert(expression))
        self.parts = tuple(parts)

    def _check_and_convert(self, elem: Any):
        if isinstance(elem, bool):
            return "true" if elem else "false"
        elif isinstance(elem, (int, float, str)):
            return str(elem)
        elif isinstance(elem, Element):
            return elem
        else:
            raise NotImplementedError(str(type(elem)))


class StringLiteral(Element):
    """String literal."""

    def __init__(self, text: str) -> None:
        self.text = text


class Sequence:
    """A sequence of statements, comments or whitespace."""

    def __init__(self) -> None:
        self.elements: list[Union[Comment, Statement, Sequence]] = []

    def __len__(self) -> int:
        return len(self.elements)

    def append(self, elem: Any) -> "Sequence":
        """Appends one element to this sequence."""
        self.elements.append(elem)
        return self

    def extend(self, seq) -> "Sequence":
        """Extends this sequence with items from another sequence."""
        if isinstance(seq, Sequence):
            self.elements.extend(seq.elements)
        else:
            raise TypeError("seq must be of type Sequence")
        return self


class Block(Sequence):
    """A sequence wrapped in braces."""


class IfStatement(Element):
    """If statement with optional else clause."""

    def __init__(self, condition: Any, then_block: Any, else_block: Any = None) -> None:
        self.condition = self._convert_condition(condition)
        self.then_block = self._convert_block(then_block)
        self.else_block = self._convert_block(else_block) if else_block is not None else None

    def _convert_condition(self, condition: Any) -> Union[str, Element]:
        """Convert condition to appropriate type."""
        if isinstance(condition, (str, Element)):
            return condition
        elif isinstance(condition, bool):
            return "true" if condition else "false"
        elif isinstance(condition, (int, float)):
            return str(condition)
        else:
            raise NotImplementedError(f"Unsupported condition type: {type(condition)}")

    def _convert_block(self, block: Any) -> Union[Block, Statement, Sequence]:
        """Convert block to appropriate type."""
        if block is None:
            return Block()
        elif isinstance(block, (Block, Statement, Sequence)):
            return block
        elif isinstance(block, list):
            seq = Sequence()
            for item in block:
                seq.append(item)
            return seq
        else:
            # Treat as single statement
            return Statement(block)


class WhileLoop(Element):
    """While loop construct."""

    def __init__(self, condition: Any, body: Any) -> None:
        self.condition = self._convert_condition(condition)
        self.body = self._convert_body(body)

    def _convert_condition(self, condition: Any) -> Union[str, Element]:
        """Convert condition to appropriate type."""
        if isinstance(condition, (str, Element)):
            return condition
        elif isinstance(condition, bool):
            return "true" if condition else "false"
        elif isinstance(condition, (int, float)):
            return str(condition)
        else:
            raise NotImplementedError(f"Unsupported condition type: {type(condition)}")

    def _convert_body(self, body: Any) -> Union[Block, Statement, Sequence]:
        """Convert body to appropriate type."""
        if body is None:
            return Block()
        elif isinstance(body, (Block, Statement, Sequence)):
            return body
        elif isinstance(body, list):
            seq = Sequence()
            for item in body:
                seq.append(item)
            return seq
        else:
            # Treat as single statement
            return Statement(body)


class ForLoop(Element):
    """For loop construct."""

    def __init__(self, init: Any = None, condition: Any = None, increment: Any = None, body: Any = None) -> None:
        self.init = self._convert_statement(init) if init is not None else None
        self.condition = self._convert_condition(condition) if condition is not None else None
        self.increment = self._convert_statement(increment) if increment is not None else None
        self.body = self._convert_body(body)

    def _convert_condition(self, condition: Any) -> Union[str, Element]:
        """Convert condition to appropriate type."""
        if isinstance(condition, (str, Element)):
            return condition
        elif isinstance(condition, bool):
            return "true" if condition else "false"
        elif isinstance(condition, (int, float)):
            return str(condition)
        else:
            raise NotImplementedError(f"Unsupported condition type: {type(condition)}")

    def _convert_statement(self, stmt: Any) -> Union[str, Element, Statement]:
        """Convert statement to appropriate type."""
        if isinstance(stmt, (str, Element, Statement)):
            return stmt
        elif isinstance(stmt, (int, float, bool)):
            return str(stmt)
        else:
            raise NotImplementedError(f"Unsupported statement type: {type(stmt)}")

    def _convert_body(self, body: Any) -> Union[Block, Statement, Sequence]:
        """Convert body to appropriate type."""
        if body is None:
            return Block()
        elif isinstance(body, (Block, Statement, Sequence)):
            return body
        elif isinstance(body, list):
            seq = Sequence()
            for item in body:
                seq.append(item)
            return seq
        else:
            # Treat as single statement
            return Statement(body)


class BreakStatement(Element):
    """Break statement for loop control."""

    def __init__(self) -> None:
        pass


class ContinueStatement(Element):
    """Continue statement for loop control."""

    def __init__(self) -> None:
        pass


class DoWhileLoop(Element):
    """Do-while loop construct."""

    def __init__(self, body: Any, condition: Any) -> None:
        self.body = self._convert_body(body)
        self.condition = self._convert_condition(condition)

    def _convert_condition(self, condition: Any) -> Union[str, Element]:
        """Convert condition to appropriate type."""
        if isinstance(condition, (str, Element)):
            return condition
        elif isinstance(condition, bool):
            return "true" if condition else "false"
        elif isinstance(condition, (int, float)):
            return str(condition)
        else:
            raise NotImplementedError(f"Unsupported condition type: {type(condition)}")

    def _convert_body(self, body: Any) -> Union[Block, Statement, Sequence]:
        """Convert body to appropriate type."""
        if body is None:
            return Block()
        elif isinstance(body, (Block, Statement, Sequence)):
            return body
        elif isinstance(body, list):
            seq = Sequence()
            for item in body:
                seq.append(item)
            return seq
        else:
            # Treat as single statement
            return Statement(body)


class TernaryOperator(Element):
    """Ternary conditional operator (condition ? true_expr : false_expr)."""

    def __init__(self, condition: Any, true_expr: Any, false_expr: Any) -> None:
        self.condition = self._convert_expression(condition)
        self.true_expr = self._convert_expression(true_expr)
        self.false_expr = self._convert_expression(false_expr)

    def _convert_expression(self, expr: Any) -> Union[str, Element]:
        """Convert expression to appropriate type."""
        if isinstance(expr, (str, Element)):
            return expr
        elif isinstance(expr, (int, float, bool)):
            return str(expr)
        else:
            raise NotImplementedError(f"Unsupported expression type: {type(expr)}")


class SizeofOperator(Element):
    """Sizeof operator for getting size of types or expressions."""

    def __init__(self, operand: Union[str, DataType, Element]) -> None:
        self.operand = operand
        self.is_type = isinstance(operand, (str, DataType))


class AddressOfOperator(Element):
    """Address-of operator (&) for getting address of variables."""

    def __init__(self, operand: Union[str, Element]) -> None:
        # Validate that string operands are not empty
        if isinstance(operand, str):
            if not operand.strip():
                raise ValueError("address-of operand cannot be empty")
            # Only validate simple identifiers, allow complex expressions like array[0]
            if operand.isidentifier():
                _validate_c_identifier(operand, "address-of operand")
        self.operand = operand


class DereferenceOperator(Element):
    """Dereference operator (*) for accessing value at pointer address."""

    def __init__(self, operand: Union[str, Element]) -> None:
        self.operand = operand


class Enum(DataType):
    """Enumeration type for creating named constants."""

    def __init__(self, name: str, values: "list[str] | dict[str, int] | None" = None) -> None:
        _validate_c_identifier(name, "enum name")
        self.name = name
        self.values = values or []

        # Convert list to dict with auto-incrementing values
        if isinstance(self.values, list):
            self.values = {value: i for i, value in enumerate(self.values)}

        # Validate enum constant names
        if isinstance(self.values, dict):
            for enum_name in self.values.keys():
                _validate_c_identifier(enum_name, "enum constant name")


class EnumMember(Element):
    """Member of an enumeration."""

    def __init__(self, name: str, value: "int | None" = None) -> None:
        _validate_c_identifier(name, "enum member name")
        self.name = name
        self.value = value


class Union(DataType):
    """Union type for memory-efficient data structures."""

    def __init__(self, name: str, members: "UnionMember | list[UnionMember] | None" = None) -> None:
        _validate_c_identifier(name, "union name")
        self.name = name
        if members is None:
            self.members = []
        elif isinstance(members, list):
            self.members = members
        else:
            self.members = [members]


class UnionMember(Element):
    """Member of a union."""

    def __init__(
        self,
        name: str,
        data_type: "str | Type | Struct | Union",
        const: bool = False,
        pointer: bool = False,
        array: "int | None" = None
    ) -> None:
        _validate_c_identifier(name, "union member name")
        self.name = name
        self.data_type = data_type
        self.const = const
        self.pointer = pointer
        self.array = array


# TIER 4: Advanced C11 Features

class FunctionPointer(DataType):
    """Function pointer type for advanced programming patterns."""

    def __init__(
        self,
        name: str,
        return_type: "str | Type | DataType",
        parameters: "list[Variable] | None" = None,
        const: bool = False,
        volatile: bool = False
    ) -> None:
        _validate_c_identifier(name, "function pointer name")
        self.name = name
        self.return_type = return_type
        self.parameters = parameters or []
        self.const = const
        self.volatile = volatile


class VariadicFunction(DataType):
    """Variadic function with variable arguments (...)."""

    def __init__(
        self,
        name: str,
        return_type: "str | Type | DataType | None" = None,
        fixed_params: "list[Variable] | None" = None,
        static: bool = False,
        extern: bool = False
    ) -> None:
        _validate_c_identifier(name, "function name")
        self.name = name
        self.return_type = return_type
        self.fixed_params = fixed_params or []
        self.static = static
        self.extern = extern


class StaticAssert(Element):
    """Static assertion for compile-time checks (_Static_assert)."""

    def __init__(self, condition: str, message: str) -> None:
        if not condition.strip():
            raise ValueError("static assertion condition cannot be empty")
        if not message.strip():
            raise ValueError("static assertion message cannot be empty")
        self.condition = condition
        self.message = message


class GenericSelection(Element):
    """Generic selection for type-generic programming (_Generic)."""

    def __init__(
        self,
        controlling_expr: str,
        type_associations: "dict[str, str]",
        default_expr: "str | None" = None
    ) -> None:
        if not controlling_expr.strip():
            raise ValueError("controlling expression cannot be empty")
        if not type_associations:
            raise ValueError("type associations cannot be empty")

        self.controlling_expr = controlling_expr
        self.type_associations = type_associations
        self.default_expr = default_expr


class FunctionPointerDeclaration(Element):
    """Declaration of a function pointer variable."""

    def __init__(
        self,
        pointer_name: str,
        return_type: "str | Type | DataType",
        parameters: "list[Variable] | None" = None,
        const: bool = False,
        static: bool = False
    ) -> None:
        _validate_c_identifier(pointer_name, "function pointer variable name")
        self.pointer_name = pointer_name
        self.return_type = return_type
        self.parameters = parameters or []
        self.const = const
        self.static = static


# Additional Control Flow Elements

class SwitchStatement(Element):
    """Switch statement for multi-way branching."""

    def __init__(self, expression: Any, cases: "list[CaseStatement] | None" = None, default_case: "DefaultCase | None" = None) -> None:
        if isinstance(expression, str):
            if not expression.strip():
                raise ValueError("switch expression cannot be empty")
        self.expression = expression
        self.cases = cases or []
        self.default_case = default_case

    def add_case(self, case: "CaseStatement") -> None:
        """Add a case to the switch statement."""
        self.cases.append(case)

    def set_default(self, default_case: "DefaultCase") -> None:
        """Set the default case for the switch statement."""
        self.default_case = default_case


class CaseStatement(Element):
    """Case statement within a switch."""

    def __init__(self, value: Any, statements: "Any | list[Any] | None" = None) -> None:
        if isinstance(value, str):
            if not value.strip():
                raise ValueError("case value cannot be empty")
        self.value = value
        self.statements = statements or []
        if not isinstance(self.statements, list):
            self.statements = [self.statements]

    def add_statement(self, statement: Any) -> None:
        """Add a statement to this case."""
        self.statements.append(statement)


class DefaultCase(Element):
    """Default case within a switch statement."""

    def __init__(self, statements: "Any | list[Any] | None" = None) -> None:
        self.statements = statements or []
        if not isinstance(self.statements, list):
            self.statements = [self.statements]

    def add_statement(self, statement: Any) -> None:
        """Add a statement to the default case."""
        self.statements.append(statement)


class GotoStatement(Element):
    """Goto statement for unconditional jumps."""

    def __init__(self, label: str) -> None:
        _validate_c_identifier(label, "goto label")
        self.label = label


class Label(Element):
    """Label for goto statements and general code marking."""

    def __init__(self, name: str) -> None:
        _validate_c_identifier(name, "label name")
        self.name = name


# Additional Operators

class BitwiseOperator(Element):
    """Bitwise operators (&, |, ^, ~, <<, >>)."""

    def __init__(self, left: "Union[str, Element]", operator: str, right: "Union[str, Element, None]" = None) -> None:
        valid_operators = ["&", "|", "^", "~", "<<", ">>"]
        if operator not in valid_operators:
            raise ValueError(f"Invalid bitwise operator '{operator}'. Valid operators: {valid_operators}")

        self.left = left
        self.operator = operator
        self.right = right

        # Validate unary operators (only ~ for bitwise NOT)
        if operator == "~":
            if right is not None:
                raise ValueError("Bitwise NOT (~) is a unary operator and should not have a right operand")
        else:
            if right is None:
                raise ValueError(f"Bitwise operator '{operator}' requires a right operand")


class LogicalOperator(Element):
    """Logical operators (&&, ||, !)."""

    def __init__(self, left: "Union[str, Element]", operator: str, right: "Union[str, Element, None]" = None) -> None:
        valid_operators = ["&&", "||", "!"]
        if operator not in valid_operators:
            raise ValueError(f"Invalid logical operator '{operator}'. Valid operators: {valid_operators}")

        self.left = left
        self.operator = operator
        self.right = right

        # Validate unary operators (only ! for logical NOT)
        if operator == "!":
            if right is not None:
                raise ValueError("Logical NOT (!) is a unary operator and should not have a right operand")
        else:
            if right is None:
                raise ValueError(f"Logical operator '{operator}' requires a right operand")


class IncrementOperator(Element):
    """Increment operators (++var, var++)."""

    def __init__(self, operand: "Union[str, Element]", prefix: bool = True) -> None:
        if isinstance(operand, str):
            if not operand.strip():
                raise ValueError("increment operand cannot be empty")

        self.operand = operand
        self.prefix = prefix  # True for ++var, False for var++


class DecrementOperator(Element):
    """Decrement operators (--var, var--)."""

    def __init__(self, operand: "Union[str, Element]", prefix: bool = True) -> None:
        if isinstance(operand, str):
            if not operand.strip():
                raise ValueError("decrement operand cannot be empty")

        self.operand = operand
        self.prefix = prefix  # True for --var, False for var--


class CompoundAssignmentOperator(Element):
    """Compound assignment operators (+=, -=, *=, /=, %=, &=, |=, ^=, <<=, >>=)."""

    def __init__(self, left: "Union[str, Element]", operator: str, right: "Union[str, Element]") -> None:
        valid_operators = ["+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="]
        if operator not in valid_operators:
            raise ValueError(f"Invalid compound assignment operator '{operator}'. Valid operators: {valid_operators}")

        if isinstance(left, str) and not left.strip():
            raise ValueError("compound assignment left operand cannot be empty")
        if isinstance(right, str) and not right.strip():
            raise ValueError("compound assignment right operand cannot be empty")

        self.left = left
        self.operator = operator
        self.right = right


# C11 Advanced Features

class AtomicType(Element):
    """C11 atomic type (_Atomic)."""

    def __init__(self, base_type: "str | Type | DataType") -> None:
        if isinstance(base_type, str):
            if not base_type.strip():
                raise ValueError("atomic base type cannot be empty")
        self.base_type = base_type


class AlignasSpecifier(Element):
    """C11 alignment specifier (_Alignas)."""

    def __init__(self, alignment: "str | int") -> None:
        if isinstance(alignment, str):
            if not alignment.strip():
                raise ValueError("alignment specifier cannot be empty")
        elif isinstance(alignment, int):
            if alignment <= 0:
                raise ValueError("alignment must be positive")
        else:
            raise TypeError("alignment must be string or positive integer")
        self.alignment = alignment


class AlignofOperator(Element):
    """C11 alignment query operator (_Alignof)."""

    def __init__(self, type_or_expr: "str | Type | DataType") -> None:
        if isinstance(type_or_expr, str):
            if not type_or_expr.strip():
                raise ValueError("alignof operand cannot be empty")
        self.type_or_expr = type_or_expr


class ThreadLocalSpecifier(Element):
    """C11 thread-local storage specifier (_Thread_local)."""

    def __init__(self, variable: "Variable | str") -> None:
        if isinstance(variable, str):
            _validate_c_identifier(variable, "thread-local variable")
        self.variable = variable


# Complex and Fixed-width Types

class ComplexType(Type):
    """C11 complex number types (_Complex)."""

    def __init__(self, base_type: str = "double") -> None:
        valid_base_types = ["float", "double", "long double"]
        if base_type not in valid_base_types:
            raise ValueError(f"Invalid complex base type '{base_type}'. Valid types: {valid_base_types}")
        super().__init__(f"{base_type} _Complex")


class FixedWidthIntegerType(Type):
    """C11 fixed-width integer types (int8_t, uint32_t, etc.)."""

    def __init__(self, width: int, signed: bool = True) -> None:
        valid_widths = [8, 16, 32, 64]
        if width not in valid_widths:
            raise ValueError(f"Invalid integer width {width}. Valid widths: {valid_widths}")

        prefix = "int" if signed else "uint"
        type_name = f"{prefix}{width}_t"
        super().__init__(type_name)
        self.width = width
        self.signed = signed


# Advanced Storage Classes

class AutoSpecifier(Element):
    """C11 auto storage class specifier."""

    def __init__(self, variable: "Variable | str") -> None:
        if isinstance(variable, str):
            _validate_c_identifier(variable, "auto variable")
        self.variable = variable


class RegisterSpecifier(Element):
    """Register storage class specifier."""

    def __init__(self, variable: "Variable | str") -> None:
        if isinstance(variable, str):
            _validate_c_identifier(variable, "register variable")
        self.variable = variable


class RestrictSpecifier(Element):
    """C99/C11 restrict type qualifier."""

    def __init__(self, pointer_variable: "Variable | str") -> None:
        if isinstance(pointer_variable, str):
            _validate_c_identifier(pointer_variable, "restrict pointer")
        self.pointer_variable = pointer_variable


# Advanced Constructs

class InlineSpecifier(Element):
    """Inline function specifier."""

    def __init__(self, function: "Function | str") -> None:
        if isinstance(function, str):
            _validate_c_identifier(function, "inline function")
        self.function = function


class FlexibleArrayMember(StructMember):
    """C99/C11 flexible array member (struct member with empty array)."""

    def __init__(self, name: str, element_type: "str | Type | DataType") -> None:
        # Initialize as a struct member with a special array marker
        super().__init__(name, element_type, array=-1)  # Use -1 to indicate flexible array
        self.element_type = element_type
        self.is_flexible = True  # Marker for writer


class DesignatedInitializer(Element):
    """C99/C11 designated initializer for arrays and structs."""

    def __init__(self, designators: "list[str | int]", value: "str | Element") -> None:
        if not designators:
            raise ValueError("designated initializer must have at least one designator")

        for designator in designators:
            if isinstance(designator, str):
                if not designator.strip():
                    raise ValueError("string designator cannot be empty")
            elif not isinstance(designator, int):
                raise TypeError("designator must be string or integer")

        if isinstance(value, str) and not value.strip():
            raise ValueError("designated initializer value cannot be empty")

        self.designators = designators
        self.value = value


# Complex Pointer Types

class PointerToPointer(Type):
    """Multi-level pointer type (e.g., int**, char***)."""

    def __init__(self, base_type: "str | Type | DataType", levels: int = 2) -> None:
        if levels < 2:
            raise ValueError("pointer-to-pointer must have at least 2 levels")
        if levels > 5:  # Reasonable limit
            raise ValueError("pointer levels should not exceed 5 for readability")

        if isinstance(base_type, str):
            if not base_type.strip():
                raise ValueError("pointer base type cannot be empty")

        super().__init__(base_type)
        self.levels = levels
        self.pointer_levels = "*" * levels


# Advanced Preprocessor

class PragmaDirective(Directive):
    """Pragma preprocessor directive."""

    def __init__(self, pragma_text: str, adjust: int = 0) -> None:
        super().__init__(adjust)
        if not pragma_text.strip():
            raise ValueError("pragma text cannot be empty")
        self.pragma_text = pragma_text


class FunctionLikeMacro(Directive):
    """Function-like macro with parameters."""

    def __init__(self, name: str, parameters: "list[str]", replacement: str, adjust: int = 0) -> None:
        super().__init__(adjust)
        _validate_c_identifier(name, "macro name")

        for param in parameters:
            _validate_c_identifier(param, "macro parameter")

        if not replacement.strip():
            raise ValueError("macro replacement cannot be empty")

        self.name = name
        self.parameters = parameters
        self.replacement = replacement


class VariadicMacro(Directive):
    """Variadic macro with ... parameter."""

    def __init__(self, name: str, fixed_params: "list[str]", replacement: str, adjust: int = 0) -> None:
        super().__init__(adjust)
        _validate_c_identifier(name, "variadic macro name")

        for param in fixed_params:
            _validate_c_identifier(param, "macro parameter")

        if not replacement.strip():
            raise ValueError("variadic macro replacement cannot be empty")

        self.name = name
        self.fixed_params = fixed_params
        self.replacement = replacement

