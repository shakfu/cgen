"""Simple C Code Emitter for Basic Functions.

This module provides a simplified C code emitter based on patterns from
mini_py2c_module_fixed.py, optimized for functions that don't require
complex STC container operations.
"""

import ast
from typing import Dict, List, Optional

from ..common import log
from . import core


class SimpleEmitter:
    """Simple C code emitter for basic functions without STC overhead."""

    def __init__(self):
        self.log = log.config(self.__class__.__name__)
        self.var_order: List[str] = []

    def can_use_simple_emission(self, func_node: ast.FunctionDef, type_context: Dict[str, str]) -> bool:
        """Determine if a function can use simple emission (only very basic integer/float arithmetic)."""
        # Only allow very basic types for simple emission
        allowed_types = {"int", "float", "bool", "void"}

        # Check parameter and variable types - must be basic types only
        for param_type in type_context.values():
            if param_type not in allowed_types:
                return False

        # Check for any complex operations that require the full py2c converter
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Any function calls indicate need for complex emission
                return False

            elif isinstance(node, (ast.List, ast.Dict, ast.Set)):
                # Literal containers
                return False

            elif isinstance(node, ast.Subscript):
                # Container indexing or string slicing
                return False

            elif isinstance(node, ast.ListComp) or isinstance(node, ast.DictComp) or isinstance(node, ast.SetComp):
                # Comprehensions
                return False

            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                # String literals require string handling
                return False

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # Import statements require complex handling
                return False

        # Validation: functions and parameters must have annotations, locals can be inferred
        # Check that function has return annotation or defaults to void for functions without returns
        # This allows functions without return annotations to be treated as void functions

        # Check that all parameters have annotations
        for arg in func_node.args.args:
            if arg.annotation is None and arg.arg not in type_context:
                return False

        self.log.debug(f"Function {func_node.name} can use simple emission")
        return True

    def emit_function(self, func_node: ast.FunctionDef, type_context: Dict[str, str]) -> str:
        """Emit clean C code for a simple function."""
        self.var_order = []

        # Extract function signature
        func_name = func_node.name
        params = []
        for arg in func_node.args.args:
            param_type = type_context.get(arg.arg, "int")
            params.append(f"{self._map_type_to_c(param_type)} {arg.arg}")

        # Determine return type
        return_type = type_context.get("__return__", "void")
        c_return_type = self._map_type_to_c(return_type)

        # Track local variables
        for node in ast.walk(func_node):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                if isinstance(node.target if isinstance(node, ast.AnnAssign) else node.targets[0], ast.Name):
                    var_name = (node.target if isinstance(node, ast.AnnAssign) else node.targets[0]).id
                    if var_name not in [arg.arg for arg in func_node.args.args]:
                        self._remember_var(var_name)

        # Generate function signature
        param_str = ", ".join(params) if params else "void"
        lines = [f"{c_return_type} {func_name}({param_str}) " + "{"]

        # Generate local variable declarations
        for var_name in self.var_order:
            var_type = type_context.get(var_name, "int")
            c_type = self._map_type_to_c(var_type)
            lines.append(f"    {c_type} {var_name};")

        # Generate function body
        self._emit_block(func_node.body, lines, indent=1, type_context=type_context)

        lines.append("}")
        return "\n".join(lines)

    def _emit_block(self, stmts: List[ast.stmt], lines: List[str], indent: int, type_context: Dict[str, str]):
        """Emit a block of statements."""
        ind = "    " * indent

        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0]
                if isinstance(target, ast.Name):
                    lines.append(f"{ind}{target.id} = {self._emit_expr(stmt.value, type_context)};")

            elif isinstance(stmt, ast.AnnAssign):
                if isinstance(stmt.target, ast.Name) and stmt.value is not None:
                    lines.append(f"{ind}{stmt.target.id} = {self._emit_expr(stmt.value, type_context)};")

            elif isinstance(stmt, ast.Return):
                if stmt.value:
                    lines.append(f"{ind}return {self._emit_expr(stmt.value, type_context)};")
                else:
                    lines.append(f"{ind}return;")

            elif isinstance(stmt, ast.If):
                condition = self._emit_expr(stmt.test, type_context)
                lines.append(f"{ind}if ({condition}) " + "{")
                self._emit_block(stmt.body, lines, indent + 1, type_context)
                lines.append(f"{ind}" + "}")

                if stmt.orelse:
                    lines.append(f"{ind}else " + "{")
                    self._emit_block(stmt.orelse, lines, indent + 1, type_context)
                    lines.append(f"{ind}" + "}")

            elif isinstance(stmt, ast.While):
                condition = self._emit_expr(stmt.test, type_context)
                lines.append(f"{ind}while ({condition}) " + "{")
                self._emit_block(stmt.body, lines, indent + 1, type_context)
                lines.append(f"{ind}" + "}")

            elif isinstance(stmt, ast.For):
                if (isinstance(stmt.target, ast.Name) and
                    isinstance(stmt.iter, ast.Call) and
                    isinstance(stmt.iter.func, ast.Name) and
                    stmt.iter.func.id == "range"):

                    iter_var = stmt.target.id
                    start, stop, step = self._emit_range_parts(stmt.iter, type_context)
                    condition = f"(({step}) > 0 ? {iter_var} < {stop} : {iter_var} > {stop})"
                    lines.append(f"{ind}for ({iter_var} = {start}; {condition}; {iter_var} += ({step})) " + "{")
                    self._emit_block(stmt.body, lines, indent + 1, type_context)
                    lines.append(f"{ind}" + "}")

            elif isinstance(stmt, ast.Assert):
                if stmt.test:
                    test_expr = self._emit_expr(stmt.test, type_context)
                    if stmt.msg:
                        msg_expr = self._emit_expr(stmt.msg, type_context)
                        lines.append(f"{ind}assert({test_expr} && {msg_expr});")
                    else:
                        lines.append(f"{ind}assert({test_expr});")

            elif isinstance(stmt, ast.Pass):
                lines.append(f"{ind}/* pass */")

            elif isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                    # Skip docstrings
                    continue
                lines.append(f"{ind}{self._emit_expr(stmt.value, type_context)};")

            else:
                lines.append(f"{ind}/* unsupported stmt: {type(stmt).__name__} */")

    def _emit_expr(self, expr: ast.expr, type_context: Dict[str, str]) -> str:
        """Emit expression as C code."""
        if isinstance(expr, ast.Name):
            return expr.id

        elif isinstance(expr, ast.Constant):
            if isinstance(expr.value, bool):
                return "true" if expr.value else "false"
            elif isinstance(expr.value, int):
                return str(expr.value)
            elif isinstance(expr.value, float):
                return repr(float(expr.value))
            elif isinstance(expr.value, str):
                return f'"{expr.value}"'

        elif isinstance(expr, ast.BinOp):
            op_map = {
                ast.Add: "+", ast.Sub: "-", ast.Mult: "*",
                ast.Div: "/", ast.FloorDiv: "/", ast.Mod: "%"
            }
            op_symbol = op_map.get(type(expr.op), "?")
            left = self._emit_expr(expr.left, type_context)
            right = self._emit_expr(expr.right, type_context)
            # Only add parentheses for complex expressions or when operator precedence matters
            if isinstance(expr.left, ast.BinOp) or isinstance(expr.right, ast.BinOp):
                return f"({left} {op_symbol} {right})"
            else:
                return f"{left} {op_symbol} {right}"

        elif isinstance(expr, ast.UnaryOp):
            if isinstance(expr.op, ast.UAdd):
                return f"+{self._emit_expr(expr.operand, type_context)}"
            elif isinstance(expr.op, ast.USub):
                return f"-{self._emit_expr(expr.operand, type_context)}"
            elif isinstance(expr.op, ast.Not):
                return f"!{self._emit_expr(expr.operand, type_context)}"

        elif isinstance(expr, ast.Compare):
            if len(expr.ops) == 1 and len(expr.comparators) == 1:
                op_map = {
                    ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">",
                    ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="
                }
                op_symbol = op_map.get(type(expr.ops[0]), "?")
                left = self._emit_expr(expr.left, type_context)
                right = self._emit_expr(expr.comparators[0], type_context)
                return f"{left} {op_symbol} {right}"

        elif isinstance(expr, ast.IfExp):
            test = self._emit_expr(expr.test, type_context)
            body = self._emit_expr(expr.body, type_context)
            orelse = self._emit_expr(expr.orelse, type_context)
            return f"({test} ? {body} : {orelse})"

        elif isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                func_name = expr.func.id
                args = [self._emit_expr(arg, type_context) for arg in expr.args]
                return f"{func_name}({', '.join(args)})"

        return "/* unknown expr */"

    def _emit_range_parts(self, range_call: ast.Call, type_context: Dict[str, str]) -> tuple:
        """Extract start, stop, step from range() call."""
        args = range_call.args
        if len(args) == 1:
            return "0", self._emit_expr(args[0], type_context), "1"
        elif len(args) == 2:
            return (self._emit_expr(args[0], type_context),
                    self._emit_expr(args[1], type_context), "1")
        elif len(args) == 3:
            return (self._emit_expr(args[0], type_context),
                    self._emit_expr(args[1], type_context),
                    self._emit_expr(args[2], type_context))
        return "0", "0", "1"

    def _map_type_to_c(self, python_type: str) -> str:
        """Map Python/inferred types to C types."""
        type_map = {
            "int": "int",
            "float": "double",
            "bool": "int",
            "str": "char*",
            "void": "void",
            "unknown": "int",  # Default fallback
        }
        return type_map.get(python_type, "int")

    def _remember_var(self, var_name: str):
        """Track variable declaration order."""
        if var_name not in self.var_order:
            self.var_order.append(var_name)