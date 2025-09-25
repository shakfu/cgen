"""CGen Core - C Code Generation Layer (Layer 3)."""

from .core import (
    AddressOfOperator,
    AlignasSpecifier,
    AlignofOperator,
    # C11 Advanced Features
    AtomicType,
    # Advanced Storage Classes
    AutoSpecifier,
    # Additional Operators
    BitwiseOperator,
    BreakStatement,
    CaseStatement,
    # Complex and Fixed-width Types
    ComplexType,
    CompoundAssignmentOperator,
    ContinueStatement,
    DecrementOperator,
    DefaultCase,
    DereferenceOperator,
    DesignatedInitializer,
    DoWhileLoop,
    # TIER 3 elements
    Enum,
    EnumMember,
    FixedWidthIntegerType,
    FlexibleArrayMember,
    FunctionLikeMacro,
    # TIER 4 elements
    FunctionPointer,
    FunctionPointerDeclaration,
    GenericSelection,
    GotoStatement,
    IncrementOperator,
    # Advanced Constructs
    InlineSpecifier,
    Label,
    LogicalOperator,
    # Complex Pointer Types
    PointerToPointer,
    # Advanced Preprocessor
    PragmaDirective,
    RegisterSpecifier,
    RestrictSpecifier,
    SizeofOperator,
    StaticAssert,
    # Additional Control Flow elements
    SwitchStatement,
    TernaryOperator,
    ThreadLocalSpecifier,
    Union,
    UnionMember,
    VariadicFunction,
    VariadicMacro,
)
from .factory import CFactory
from .py2c import PythonToCConverter, convert_python_file_to_c, convert_python_to_c
from .style import Alignment, BreakBeforeBraces, StyleOptions
from .writer import Writer

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
    # Additional Operators
    "BitwiseOperator",
    "LogicalOperator",
    "IncrementOperator",
    "DecrementOperator",
    "CompoundAssignmentOperator",
    # C11 Advanced Features
    "AtomicType",
    "AlignasSpecifier",
    "AlignofOperator",
    "ThreadLocalSpecifier",
    # Complex and Fixed-width Types
    "ComplexType",
    "FixedWidthIntegerType",
    # Advanced Storage Classes
    "AutoSpecifier",
    "RegisterSpecifier",
    "RestrictSpecifier",
    # Advanced Constructs
    "InlineSpecifier",
    "FlexibleArrayMember",
    "DesignatedInitializer",
    # Complex Pointer Types
    "PointerToPointer",
    # Advanced Preprocessor
    "PragmaDirective",
    "FunctionLikeMacro",
    "VariadicMacro",
]
