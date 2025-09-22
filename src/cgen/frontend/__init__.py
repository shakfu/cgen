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
    AnalysisResult,
    ASTAnalyzer,
    FunctionInfo,
    NodeType,
    StaticComplexity,
    TypeInfo,
    VariableInfo,
    analyze_python_code,
    analyze_python_file,
)

# Static Constraint Checking
from .constraint_checker import (
    ConstraintCategory,
    ConstraintReport,
    ConstraintSeverity,
    ConstraintViolation,
    StaticConstraintChecker,
)

# Static IR
from .static_ir import (
    IRBuilder,
    IRDataType,
    IRExpression,
    IRFunction,
    IRModule,
    IRStatement,
    IRType,
    IRVariable,
    build_ir_from_code,
)

# Python Subset Validation
from .subset_validator import FeatureRule, FeatureStatus, StaticPythonSubsetValidator, SubsetTier, ValidationResult

# Type Inference System
from .type_inference import InferenceMethod, InferenceResult, TypeConstraint, TypeInferenceEngine

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
