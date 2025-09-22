"""Python to C converter module.

This module provides functionality to convert type-annotated Python code
to C code using the cfile library. It supports a subset of Python features
that can be reasonably mapped to C constructs.

Supported Features:
- Type-annotated function definitions
- Basic data types (int, float, bool, str)
- Variable declarations with type annotations
- Basic arithmetic and comparison operations
- Control structures (if/else, while, for with range)
- Function calls
- Return statements

Limitations:
- No dynamic typing
- No Python-specific features (list comprehensions, generators, etc.)
- Limited standard library support
- Arrays must be explicitly sized or passed with size parameters
"""

import ast
from typing import Any, Dict, List, Optional, Union

from . import core
from .factory import CFactory


class UnsupportedFeatureError(Exception):
    """Raised when encountering unsupported Python features."""

    pass


class TypeMappingError(Exception):
    """Raised when type annotation cannot be mapped to C type."""

    pass


class PythonToCConverter:
    """Converts type-annotated Python code to C code using cfile."""

    def __init__(self):
        self.c_factory = CFactory()
        self.type_mapping = {
            "int": "int",
            "float": "double",
            "bool": "bool",  # Requires stdbool.h
            "str": "char*",
            "None": "void",
        }
        self.current_function: Optional[core.Function] = None
        self.variable_context: Dict[str, core.Variable] = {}

    def convert_file(self, python_file_path: str) -> core.Sequence:
        """Convert a Python file to C code sequence."""
        with open(python_file_path) as f:
            python_code = f.read()
        return self.convert_code(python_code)

    def convert_code(self, python_code: str) -> core.Sequence:
        """Convert Python code string to C code sequence."""
        tree = ast.parse(python_code)
        return self._convert_module(tree)

    def _convert_module(self, module: ast.Module) -> core.Sequence:
        """Convert Python module to C sequence."""
        sequence = core.Sequence()

        # Add standard includes that might be needed
        sequence.append(self.c_factory.sysinclude("stdio.h"))
        sequence.append(self.c_factory.sysinclude("stdbool.h"))
        sequence.append(self.c_factory.blank())

        for node in module.body:
            c_element = self._convert_statement(node)
            if c_element:
                if isinstance(c_element, list):
                    for elem in c_element:
                        sequence.append(elem)
                else:
                    sequence.append(c_element)

        return sequence

    def _convert_statement(self, node: ast.stmt) -> Union[core.Element, List[core.Element], None]:
        """Convert a Python statement to C element(s)."""
        if isinstance(node, ast.FunctionDef):
            return self._convert_function_def(node)
        elif isinstance(node, ast.AnnAssign):
            return self._convert_annotated_assignment(node)
        elif isinstance(node, ast.Assign):
            return self._convert_assignment(node)
        elif isinstance(node, ast.Return):
            return self._convert_return(node)
        elif isinstance(node, ast.If):
            return self._convert_if(node)
        elif isinstance(node, ast.While):
            return self._convert_while(node)
        elif isinstance(node, ast.For):
            return self._convert_for(node)
        elif isinstance(node, ast.Expr):
            # Expression statements (like function calls)
            return self._convert_expression_statement(node)
        elif isinstance(node, ast.Pass):
            # Pass statements can be ignored in C
            return None
        else:
            raise UnsupportedFeatureError(f"Unsupported statement type: {type(node).__name__}")

    def _convert_function_def(self, node: ast.FunctionDef) -> List[core.Element]:
        """Convert Python function definition to C function."""
        # Extract return type
        return_type = self._extract_type_annotation(node.returns) if node.returns else "void"

        # Create function parameters
        params = []
        for arg in node.args.args:
            if not arg.annotation:
                raise TypeMappingError(f"Parameter '{arg.arg}' must have type annotation")
            param_type = self._extract_type_annotation(arg.annotation)
            param = self.c_factory.variable(arg.arg, param_type)
            params.append(param)

        # Create function
        function = self.c_factory.function(node.name, return_type, params=params)
        self.current_function = function

        # Create function body
        body_statements = []
        for stmt in node.body:
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                # Skip docstrings
                continue
            c_stmt = self._convert_statement(stmt)
            if c_stmt:
                if isinstance(c_stmt, list):
                    body_statements.extend(c_stmt)
                else:
                    body_statements.append(c_stmt)

        # Create function block
        function_block = self.c_factory.block()
        for stmt in body_statements:
            function_block.append(stmt)

        self.current_function = None
        self.variable_context.clear()

        return [self.c_factory.declaration(function), function_block, self.c_factory.blank()]

    def _extract_type_annotation(self, annotation: ast.expr) -> str:
        """Extract C type from Python type annotation."""
        if isinstance(annotation, ast.Name):
            python_type = annotation.id
            if python_type in self.type_mapping:
                return self.type_mapping[python_type]
            else:
                raise TypeMappingError(f"Unsupported type: {python_type}")
        elif isinstance(annotation, ast.Constant) and annotation.value is None:
            # Handle -> None
            return "void"
        elif isinstance(annotation, ast.Subscript):
            # Handle generic types like list[int]
            if isinstance(annotation.value, ast.Name) and annotation.value.id == "list":
                element_type = self._extract_type_annotation(annotation.slice)
                return f"{element_type}*"  # Convert list[T] to T*
            else:
                raise TypeMappingError(f"Unsupported generic type: {ast.unparse(annotation)}")
        else:
            raise TypeMappingError(f"Unsupported annotation: {ast.unparse(annotation)}")

    def _convert_annotated_assignment(self, node: ast.AnnAssign) -> core.Statement:
        """Convert annotated assignment (var: type = value)."""
        if not isinstance(node.target, ast.Name):
            raise UnsupportedFeatureError("Only simple variable assignments supported")

        var_name = node.target.id
        var_type = self._extract_type_annotation(node.annotation)

        # Create variable
        variable = self.c_factory.variable(var_name, var_type)
        self.variable_context[var_name] = variable

        # Convert value expression
        if node.value:
            value_expr = self._convert_expression(node.value)
            # Create declaration and assignment as separate statements
            decl_stmt = self.c_factory.statement(self.c_factory.declaration(variable))
            assign_stmt = self.c_factory.statement(self.c_factory.assignment(variable, value_expr))
            return [decl_stmt, assign_stmt]
        else:
            return self.c_factory.statement(self.c_factory.declaration(variable))

    def _convert_assignment(self, node: ast.Assign) -> core.Statement:
        """Convert regular assignment (var = value)."""
        if len(node.targets) != 1:
            raise UnsupportedFeatureError("Multiple assignment targets not supported")

        target = node.targets[0]
        if not isinstance(target, ast.Name):
            raise UnsupportedFeatureError("Only simple variable assignments supported")

        var_name = target.id
        if var_name not in self.variable_context:
            raise TypeMappingError(f"Variable '{var_name}' must be declared with type annotation first")

        variable = self.variable_context[var_name]
        value_expr = self._convert_expression(node.value)
        assignment = self.c_factory.assignment(variable, value_expr)

        return self.c_factory.statement(assignment)

    def _convert_return(self, node: ast.Return) -> core.Statement:
        """Convert return statement."""
        if node.value:
            return_expr = self._convert_expression(node.value)
            return self.c_factory.statement(self.c_factory.func_return(return_expr))
        else:
            return self.c_factory.statement("return")

    def _convert_expression(self, node: ast.expr) -> Union[str, core.Element]:
        """Convert Python expression to C expression."""
        if isinstance(node, ast.Constant):
            return self._convert_constant(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return self._convert_binary_operation(node)
        elif isinstance(node, ast.Call):
            return self._convert_function_call(node)
        elif isinstance(node, ast.Compare):
            return self._convert_comparison(node)
        else:
            raise UnsupportedFeatureError(f"Unsupported expression: {type(node).__name__}")

    def _convert_constant(self, value: Any) -> str:
        """Convert Python constant to C constant."""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        else:
            raise UnsupportedFeatureError(f"Unsupported constant type: {type(value)}")

    def _convert_binary_operation(self, node: ast.BinOp) -> str:
        """Convert binary operation to C syntax."""
        left = self._convert_expression(node.left)
        right = self._convert_expression(node.right)

        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
        }

        if type(node.op) in op_map:
            op_str = op_map[type(node.op)]
            return f"{left} {op_str} {right}"  # Remove the parentheses for now
        else:
            raise UnsupportedFeatureError(f"Unsupported binary operator: {type(node.op).__name__}")

    def _convert_comparison(self, node: ast.Compare) -> str:
        """Convert comparison to C syntax."""
        # Simple implementation: handle single comparison operations
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise UnsupportedFeatureError("Complex comparisons with multiple operators not supported")

        left = self._convert_expression(node.left)
        right = self._convert_expression(node.comparators[0])

        op_map = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
        }

        if type(node.ops[0]) in op_map:
            op_str = op_map[type(node.ops[0])]
            return f"{left} {op_str} {right}"
        else:
            raise UnsupportedFeatureError(f"Unsupported comparison operator: {type(node.ops[0]).__name__}")

    def _convert_function_call(self, node: ast.Call) -> core.Element:
        """Convert function call to C function call."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            args = [self._convert_expression(arg) for arg in node.args]
            return self.c_factory.func_call(func_name, args)
        else:
            raise UnsupportedFeatureError("Only simple function calls supported")

    def _convert_if(self, node: ast.If) -> core.Element:
        """Convert if statement to C if statement."""
        # Convert condition
        condition = self._convert_expression(node.test)

        # Convert then block (if body)
        then_statements = []
        for stmt in node.body:
            then_statements.append(self._convert_statement(stmt))

        then_block = self.c_factory.block()
        for stmt in then_statements:
            then_block.append(stmt)

        # Convert else block if present
        else_block = None
        if node.orelse:
            else_statements = []
            for stmt in node.orelse:
                else_statements.append(self._convert_statement(stmt))

            else_block = self.c_factory.block()
            for stmt in else_statements:
                else_block.append(stmt)

        return self.c_factory.if_statement(condition, then_block, else_block)

    def _convert_while(self, node: ast.While) -> core.Element:
        """Convert while loop to C while loop."""
        # Convert condition
        condition = self._convert_expression(node.test)

        # Convert body
        body_statements = []
        for stmt in node.body:
            body_statements.append(self._convert_statement(stmt))

        body_block = self.c_factory.block()
        for stmt in body_statements:
            body_block.append(stmt)

        return self.c_factory.while_loop(condition, body_block)

    def _convert_for(self, node: ast.For) -> core.Element:
        """Convert for loop to C for loop."""
        # Handle range-based for loops: for i in range(start, end, step)
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == "range"):

            # Extract loop variable
            if isinstance(node.target, ast.Name):
                loop_var = node.target.id
            else:
                raise UnsupportedFeatureError("Only simple loop variables supported in for loops")

            # Parse range arguments
            range_args = node.iter.args
            if len(range_args) == 1:
                # range(n) -> for(i=0; i<n; i++)
                start = "0"
                end = self._convert_expression(range_args[0])
                step = "1"
            elif len(range_args) == 2:
                # range(start, end) -> for(i=start; i<end; i++)
                start = self._convert_expression(range_args[0])
                end = self._convert_expression(range_args[1])
                step = "1"
            elif len(range_args) == 3:
                # range(start, end, step) -> for(i=start; i<end; i+=step)
                start = self._convert_expression(range_args[0])
                end = self._convert_expression(range_args[1])
                step = self._convert_expression(range_args[2])
            else:
                raise UnsupportedFeatureError("Invalid range() arguments in for loop")

            # Build for loop components
            init = f"int {loop_var} = {start}"
            condition = f"{loop_var} < {end}"
            if str(step) == "1":
                increment = f"{loop_var}++"
            else:
                increment = f"{loop_var} += {step}"

            # Convert body
            body_statements = []
            for stmt in node.body:
                body_statements.append(self._convert_statement(stmt))

            body_block = self.c_factory.block()
            for stmt in body_statements:
                body_block.append(stmt)

            return self.c_factory.for_loop(init, condition, increment, body_block)

        else:
            raise UnsupportedFeatureError("Only range-based for loops are currently supported")

    def _convert_expression_statement(self, node: ast.Expr) -> core.Statement:
        """Convert expression statement (like standalone function call)."""
        expr = self._convert_expression(node.value)
        return self.c_factory.statement(expr)


def convert_python_to_c(python_code: str) -> str:
    """Convenience function to convert Python code to C code string."""
    converter = PythonToCConverter()
    c_sequence = converter.convert_code(python_code)

    from .style import StyleOptions
    from .writer import Writer

    writer = Writer(StyleOptions())
    return writer.write_str(c_sequence)


def convert_python_file_to_c(input_file: str, output_file: str) -> None:
    """Convert Python file to C file."""
    converter = PythonToCConverter()
    c_sequence = converter.convert_file(input_file)

    from .style import StyleOptions
    from .writer import Writer

    writer = Writer(StyleOptions())
    writer.write_file(c_sequence, output_file)
