"""CGen Core - C Code Generation Layer (Layer 3)."""

from .factory import CFactory
from .py2c import PythonToCConverter, convert_python_file_to_c, convert_python_to_c
from .style import Alignment, BreakBeforeBraces, StyleOptions
from .writer import Writer
from .core import (
    BreakStatement,
    ContinueStatement,
    DoWhileLoop,
    TernaryOperator,
    SizeofOperator,
    AddressOfOperator,
    DereferenceOperator,
    # TIER 3 elements
    Enum,
    EnumMember,
    Union,
    UnionMember,
    # TIER 4 elements
    FunctionPointer,
    VariadicFunction,
    StaticAssert,
    GenericSelection,
    FunctionPointerDeclaration,
    # Additional Control Flow elements
    SwitchStatement,
    CaseStatement,
    DefaultCase,
    GotoStatement,
    Label,
)

__all__ = [
    "CFactory",
    "Writer",
    "StyleOptions",
    "BreakBeforeBraces",
    "Alignment",
    "PythonToCConverter",
    "convert_python_to_c",
    "convert_python_file_to_c",
    # TIER 2 elements
    "BreakStatement",
    "ContinueStatement",
    "DoWhileLoop",
    "TernaryOperator",
    "SizeofOperator",
    "AddressOfOperator",
    "DereferenceOperator",
    # TIER 3 elements
    "Enum",
    "EnumMember",
    "Union",
    "UnionMember",
    # TIER 4 elements
    "FunctionPointer",
    "VariadicFunction",
    "StaticAssert",
    "GenericSelection",
    "FunctionPointerDeclaration",
    # Additional Control Flow elements
    "SwitchStatement",
    "CaseStatement",
    "DefaultCase",
    "GotoStatement",
    "Label",
]
