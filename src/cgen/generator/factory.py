"""
CGen Factory - Enhanced C code generation factory for intelligence layer.

Extends the basic cfile factory with intelligence-aware generation methods.
"""

from typing import Any, Union, List, Optional, Dict
from .core import *
from ..intelligence.base import AnalysisResult, OptimizationResult


class CGenFactory:
    """Enhanced C factory with intelligence-aware code generation."""

    def __init__(self):
        """Initialize the CGen factory."""
        pass

    # Basic element creation methods (from cfile)
    def sequence(self) -> Sequence:
        """Creates a new Sequence."""
        return Sequence()

    def block(self) -> Block:
        """Creates a new Block."""
        return Block()

    def statement(self, stmt: str | Element) -> Statement:
        """Creates a new Statement."""
        return Statement(stmt)

    def variable(
        self,
        name: str,
        data_type: Union[str, Type],
        const: bool = False,
        pointer: bool = False,
        array: Optional[int] = None,
        init_value: Any = None,
    ) -> Variable:
        """Creates a new Variable."""
        return Variable(name, data_type, const=const, pointer=pointer, array=array, init_value=init_value)

    def function(
        self,
        name: str,
        return_type: Union[str, Type, None] = None,
        static: bool = False,
        const: bool = False,
        extern: bool = False,
        params: Union[Variable, List[Variable], None] = None,
        body: Optional[Block] = None,
    ) -> Function:
        """Creates a new Function with optional body support."""
        return Function(name, return_type, static=static, const=const, extern=extern, params=params, body=body)

    def func_call(self, name: str, args: List[Any] | None = None) -> FunctionCall:
        """Creates a new FunctionCall."""
        return FunctionCall(name, args)

    def func_return(self, expression: Any = None) -> FunctionReturn:
        """Creates a new FunctionReturn."""
        if expression is None:
            # void return
            return FunctionReturn("")
        return FunctionReturn(expression)

    def type(self, name: str, pointer: bool = False) -> Type:
        """Creates a new Type."""
        return Type(name, pointer=pointer)

    def declaration(self, element: Union[Variable, Function, DataType], init_value: Any = None) -> Declaration:
        """Creates a new Declaration."""
        return Declaration(element, init_value)

    def define(self, identifier: str, value: Optional[str] = None) -> DefineDirective:
        """Creates a new Define (macro)."""
        return DefineDirective(identifier, value)

    def include(self, path: str) -> IncludeDirective:
        """Creates a new Include."""
        return IncludeDirective(path)

    def sysinclude(self, path: str) -> IncludeDirective:
        """Creates a new SysInclude."""
        return IncludeDirective(path, system=True)

    def line_comment(self, text: str) -> LineComment:
        """Creates a new LineComment."""
        return LineComment(text)

    def block_comment(self, text: str) -> BlockComment:
        """Creates a new BlockComment."""
        return BlockComment(text)

    def literal(self, value: Any) -> str:
        """Creates a literal value."""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return f'"{value}"'
        else:
            return str(value)

    def blank(self) -> Blank:
        """Creates a blank line."""
        return Blank()

    def binop(self, left: Any, operator: str, right: Any) -> str:
        """Creates a binary operation expression."""
        return f"{left} {operator} {right}"

    def assign(self, lhs: Any, rhs: Any) -> Assignment:
        """Creates an assignment."""
        return Assignment(lhs, rhs)

    def str_literal(self, text: str) -> str:
        """Creates a string literal."""
        return f'"{text}"'

    def array(self, elements: List[Any]) -> str:
        """Creates an array literal."""
        element_strs = [self.literal(elem) if not isinstance(elem, str) else str(elem) for elem in elements]
        return "{" + ", ".join(element_strs) + "}"

    def subscript(self, array: str, index: Any) -> str:
        """Creates an array subscript expression."""
        return f"{array}[{index}]"

    # CGen Intelligence-aware methods

    def optimized_function(
        self,
        name: str,
        return_type: str | Type,
        params: List[Variable] | None = None,
        optimization_info: Optional[OptimizationResult] = None,
    ) -> Function:
        """Creates a function with optimization annotations."""
        func = self.function(name, return_type, params=params)

        if optimization_info and optimization_info.success:
            # Add optimization comments
            comments = []
            if optimization_info.performance_gain_estimate > 1.0:
                comments.append(f"Optimized function (estimated {optimization_info.performance_gain_estimate:.2f}x speedup)")

            if optimization_info.transformations:
                comments.append("Applied optimizations:")
                for transform in optimization_info.transformations[:3]:
                    comments.append(f"  - {transform}")

            if comments:
                # Add as block comment before function
                return func  # Return function, comments will be added by caller

        return func

    def vectorizable_loop(
        self,
        init: str,
        condition: str,
        increment: str,
        body: Block,
        vector_info: Optional[dict] = None,
    ) -> Sequence:
        """Creates a loop with vectorization annotations."""
        loop_seq = self.sequence()

        if vector_info:
            speedup = vector_info.get('estimated_speedup', 1.0)
            vector_len = vector_info.get('vector_length', 4)
            confidence = vector_info.get('confidence', 0.0)

            loop_seq.append(self.line_comment(
                f"Vectorizable loop: {speedup:.2f}x speedup potential, "
                f"vector length: {vector_len}, confidence: {confidence:.2f}"
            ))

        # For now, create a simple for loop as string statement
        # TODO: Extend with proper for-loop construct
        for_stmt = f"for ({init}; {condition}; {increment})"
        loop_seq.append(self.statement(for_stmt))
        loop_seq.append(body)

        return loop_seq

    def memory_safe_access(
        self,
        array_name: str,
        index: str,
        size: str,
        bounds_check: bool = True,
    ) -> str:
        """Creates a memory-safe array access."""
        if bounds_check:
            # Add bounds checking
            return f"(({index} >= 0 && {index} < {size}) ? {array_name}[{index}] : 0)"
        else:
            return f"{array_name}[{index}]"

    def compile_time_constant(
        self,
        name: str,
        value: str,
        analysis_info: Optional[AnalysisResult] = None,
    ) -> DefineDirective:
        """Creates a compile-time constant with optimization info."""
        define = self.define(name, value)

        # Could add metadata about why this is compile-time optimized
        return define

    def intelligence_header(self, analysis_results: dict) -> Sequence:
        """Creates header comments with intelligence analysis summary."""
        header = self.sequence()

        header.append(self.line_comment("=" * 60))
        header.append(self.line_comment("Generated by CGen Intelligence Layer"))
        header.append(self.line_comment("=" * 60))

        if analysis_results:
            # Count successful analyses
            successful_analyzers = sum(1 for result in analysis_results.values()
                                     if hasattr(result, 'success') and result.success)

            header.append(self.line_comment(f"Analysis Results: {successful_analyzers} successful components"))

            # Add performance estimates
            total_speedup = 1.0
            for name, result in analysis_results.items():
                if hasattr(result, 'performance_gain_estimate'):
                    speedup = result.performance_gain_estimate
                    if speedup > 1.0:
                        total_speedup *= speedup
                        header.append(self.line_comment(f"{name}: {speedup:.2f}x speedup"))

            if total_speedup > 1.0:
                header.append(self.line_comment(f"Combined estimated speedup: {total_speedup:.2f}x"))

        header.append(self.line_comment("=" * 60))
        header.append(self.blank())

        return header