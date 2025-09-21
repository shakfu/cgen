"""CGen Frontend - Static Python Analysis Layer (Layer 1).

This module handles the analysis and parsing of static Python code.
It identifies statically analyzable constructs and prepares them for
the intelligence layer.

Key components:
- AST parsing and analysis
- Type inference and validation
- Static constraint checking
- Python subset validation
- Static IR generation
"""

# AST Analysis Framework
from .ast_analyzer import (
    ASTAnalyzer,
    AnalysisResult,
    FunctionInfo,
    VariableInfo,
    TypeInfo,
    StaticComplexity,
    NodeType,
    analyze_python_code,
    analyze_python_file
)

# Type Inference System
from .type_inference import (
    TypeInferenceEngine,
    InferenceResult,
    InferenceMethod,
    TypeConstraint
)

# Static Constraint Checking
from .constraint_checker import (
    StaticConstraintChecker,
    ConstraintReport,
    ConstraintViolation,
    ConstraintSeverity,
    ConstraintCategory
)

# Python Subset Validation
from .subset_validator import (
    StaticPythonSubsetValidator,
    ValidationResult,
    FeatureRule,
    SubsetTier,
    FeatureStatus
)

# Static IR
from .static_ir import (
    IRModule,
    IRFunction,
    IRVariable,
    IRStatement,
    IRExpression,
    IRType,
    IRDataType,
    IRBuilder,
    build_ir_from_code
)

__all__ = [
    # AST Analysis
    "ASTAnalyzer",
    "AnalysisResult",
    "FunctionInfo",
    "VariableInfo",
    "TypeInfo",
    "StaticComplexity",
    "NodeType",
    "analyze_python_code",
    "analyze_python_file",

    # Type Inference
    "TypeInferenceEngine",
    "InferenceResult",
    "InferenceMethod",
    "TypeConstraint",

    # Constraint Checking
    "StaticConstraintChecker",
    "ConstraintReport",
    "ConstraintViolation",
    "ConstraintSeverity",
    "ConstraintCategory",

    # Subset Validation
    "StaticPythonSubsetValidator",
    "ValidationResult",
    "FeatureRule",
    "SubsetTier",
    "FeatureStatus",

    # Static IR
    "IRModule",
    "IRFunction",
    "IRVariable",
    "IRStatement",
    "IRExpression",
    "IRType",
    "IRDataType",
    "IRBuilder",
    "build_ir_from_code",
]