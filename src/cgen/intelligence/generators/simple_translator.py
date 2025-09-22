"""
Simple Python-to-C AST Translator

A simplified version that generates basic C code using direct string generation
rather than complex CFactory methods that may not exist.
"""

import ast
from typing import Dict, List, Optional


class SimplePythonToCTranslator:
    """Simple translator that generates C code as strings."""

    def __init__(self):
        self.variables = {}  # variable_name -> c_type
        self.functions = {}  # function_name -> return_type
        self.indent_level = 0

    def translate_module(self, module_node: ast.Module) -> str:
        """Translate a complete Python module to C code."""
        lines = []

        # Add includes
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("#include <math.h>")
        lines.append("")

        # Add global constants and variables first
        for node in module_node.body:
            if isinstance(node, ast.Assign):
                const_code = self._translate_global_constant(node)
                if const_code:
                    lines.extend(const_code)
            elif isinstance(node, ast.AnnAssign):
                const_code = self._translate_global_ann_constant(node)
                if const_code:
                    lines.extend(const_code)

        if any(isinstance(node, (ast.Assign, ast.AnnAssign)) for node in module_node.body):
            lines.append("")

        # Process function definitions
        for node in module_node.body:
            if isinstance(node, ast.FunctionDef):
                func_code = self._translate_function(node)
                if func_code:
                    lines.extend(func_code)
                    lines.append("")

        return "\n".join(lines)

    def _translate_function(self, func_node: ast.FunctionDef) -> List[str]:
        """Translate a Python function to C function."""
        lines = []

        func_name = func_node.name

        # Handle parameters
        params = []
        for arg in func_node.args.args:
            param_type = self._infer_parameter_type(arg, func_node)
            param_name = arg.arg
            self.variables[param_name] = param_type
            params.append(f"{param_type} {param_name}")

        # Infer return type
        return_type = self._infer_return_type(func_node)
        self.functions[func_name] = return_type

        # Build function signature
        params_str = ", ".join(params) if params else "void"
        lines.append(f"{return_type} {func_name}({params_str}) {{")

        # Translate function body (skip docstrings)
        self.indent_level = 1
        for i, stmt in enumerate(func_node.body):
            # Skip docstring (first statement that's a string constant)
            if (i == 0 and isinstance(stmt, ast.Expr) and
                isinstance(stmt.value, ast.Constant) and
                isinstance(stmt.value.value, str)):
                continue

            stmt_lines = self._translate_statement(stmt)
            if stmt_lines:
                if isinstance(stmt_lines, list):
                    lines.extend(stmt_lines)
                else:
                    lines.append(stmt_lines)

        # Add default return for main function if no return was found
        has_return = any(isinstance(stmt, ast.Return) for stmt in func_node.body)
        if func_name == "main" and return_type == "int" and not has_return:
            lines.append(self._indent("return 0;"))

        lines.append("}")
        self.indent_level = 0

        return lines

    def _translate_statement(self, stmt: ast.stmt) -> List[str]:
        """Translate a Python statement to C statement(s)."""
        if isinstance(stmt, ast.Return):
            return self._translate_return(stmt)
        elif isinstance(stmt, ast.Assign):
            return self._translate_assignment(stmt)
        elif isinstance(stmt, ast.AnnAssign):
            return self._translate_ann_assignment(stmt)
        elif isinstance(stmt, ast.AugAssign):
            return self._translate_aug_assignment(stmt)
        elif isinstance(stmt, ast.If):
            return self._translate_if(stmt)
        elif isinstance(stmt, ast.While):
            return self._translate_while(stmt)
        elif isinstance(stmt, ast.For):
            return self._translate_for(stmt)
        elif isinstance(stmt, ast.Expr):
            return self._translate_expression_statement(stmt)
        else:
            return [self._indent(f"/* Unsupported statement: {type(stmt).__name__} */")]

    def _translate_return(self, return_node: ast.Return) -> List[str]:
        """Translate return statement."""
        if return_node.value:
            expr = self._translate_expression(return_node.value)
            return [self._indent(f"return {expr};")]
        else:
            return [self._indent("return;")]

    def _translate_assignment(self, assign_node: ast.Assign) -> List[str]:
        """Translate assignment statement."""
        lines = []
        value_expr = self._translate_expression(assign_node.value)

        for target in assign_node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                var_type = self._infer_variable_type(assign_node.value)

                if var_name not in self.variables:
                    # Variable declaration with initialization
                    self.variables[var_name] = var_type

                    # Special handling for array initialization
                    if isinstance(assign_node.value, ast.List):
                        array_size = len(assign_node.value.elts)
                        element_type = "int"  # Default element type
                        lines.append(self._indent(f"{element_type} {var_name}[{array_size}] = {value_expr};"))
                    else:
                        lines.append(self._indent(f"{var_type} {var_name} = {value_expr};"))
                else:
                    # Simple assignment
                    lines.append(self._indent(f"{var_name} = {value_expr};"))

        return lines

    def _translate_ann_assignment(self, ann_assign_node: ast.AnnAssign) -> List[str]:
        """Translate annotated assignment (var: type = value)."""
        lines = []

        if isinstance(ann_assign_node.target, ast.Name):
            var_name = ann_assign_node.target.id
            var_type = self._annotation_to_c_type(ann_assign_node.annotation)

            if ann_assign_node.value:
                value_expr = self._translate_expression(ann_assign_node.value)
                lines.append(self._indent(f"{var_type} {var_name} = {value_expr};"))
            else:
                lines.append(self._indent(f"{var_type} {var_name};"))

            self.variables[var_name] = var_type

        return lines

    def _translate_aug_assignment(self, aug_assign_node: ast.AugAssign) -> List[str]:
        """Translate augmented assignment (+=, -=, etc.)."""
        target_expr = self._translate_expression(aug_assign_node.target)
        value_expr = self._translate_expression(aug_assign_node.value)

        op_map = {
            ast.Add: '+=',
            ast.Sub: '-=',
            ast.Mult: '*=',
            ast.Div: '/=',
            ast.Mod: '%=',
        }

        op = op_map.get(type(aug_assign_node.op), '+=')
        return [self._indent(f"{target_expr} {op} {value_expr};")]

    def _translate_if(self, if_node: ast.If) -> List[str]:
        """Translate if statement."""
        lines = []
        condition = self._translate_expression(if_node.test)
        lines.append(self._indent(f"if ({condition}) {{"))

        # Translate body
        self.indent_level += 1
        for stmt in if_node.body:
            stmt_lines = self._translate_statement(stmt)
            if stmt_lines:
                if isinstance(stmt_lines, list):
                    lines.extend(stmt_lines)
                else:
                    lines.append(stmt_lines)
        self.indent_level -= 1

        if if_node.orelse:
            lines.append(self._indent("} else {"))
            self.indent_level += 1
            for stmt in if_node.orelse:
                stmt_lines = self._translate_statement(stmt)
                if stmt_lines:
                    if isinstance(stmt_lines, list):
                        lines.extend(stmt_lines)
                    else:
                        lines.append(stmt_lines)
            self.indent_level -= 1

        lines.append(self._indent("}"))
        return lines

    def _translate_while(self, while_node: ast.While) -> List[str]:
        """Translate while loop."""
        lines = []
        condition = self._translate_expression(while_node.test)
        lines.append(self._indent(f"while ({condition}) {{"))

        # Translate body
        self.indent_level += 1
        for stmt in while_node.body:
            stmt_lines = self._translate_statement(stmt)
            if stmt_lines:
                if isinstance(stmt_lines, list):
                    lines.extend(stmt_lines)
                else:
                    lines.append(stmt_lines)
        self.indent_level -= 1

        lines.append(self._indent("}"))
        return lines

    def _translate_for(self, for_node: ast.For) -> List[str]:
        """Translate for loop (convert to while loop for range)."""
        lines = []

        # Handle range() loops
        if (isinstance(for_node.iter, ast.Call) and
            isinstance(for_node.iter.func, ast.Name) and
            for_node.iter.func.id == 'range'):

            loop_var = for_node.target.id
            range_args = for_node.iter.args

            if len(range_args) == 1:
                # range(n) -> for(i=0; i<n; i++)
                start = "0"
                end = self._translate_expression(range_args[0])
            elif len(range_args) == 2:
                # range(start, end)
                start = self._translate_expression(range_args[0])
                end = self._translate_expression(range_args[1])
            else:
                # Default fallback
                start = "0"
                end = "10"

            # Check if loop variable is already declared
            if loop_var not in self.variables:
                self.variables[loop_var] = "int"
                lines.append(self._indent(f"int {loop_var} = {start};"))
            else:
                lines.append(self._indent(f"{loop_var} = {start};"))

            lines.append(self._indent(f"while ({loop_var} < {end}) {{"))

            # Translate body
            self.indent_level += 1
            for stmt in for_node.body:
                stmt_lines = self._translate_statement(stmt)
                if stmt_lines:
                    if isinstance(stmt_lines, list):
                        lines.extend(stmt_lines)
                    else:
                        lines.append(stmt_lines)

            # Add increment
            lines.append(self._indent(f"{loop_var} = {loop_var} + 1;"))
            self.indent_level -= 1

            lines.append(self._indent("}"))

        else:
            lines.append(self._indent("/* Complex for loop not supported */"))

        return lines

    def _translate_expression_statement(self, expr_stmt: ast.Expr) -> List[str]:
        """Translate expression statement."""
        expr = self._translate_expression(expr_stmt.value)
        return [self._indent(f"{expr};")]

    def _translate_expression(self, expr: ast.expr) -> str:
        """Translate a Python expression to C expression."""
        if isinstance(expr, ast.Constant):
            return self._translate_constant(expr)
        elif isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.BinOp):
            return self._translate_binary_op(expr)
        elif isinstance(expr, ast.UnaryOp):
            return self._translate_unary_op(expr)
        elif isinstance(expr, ast.Compare):
            return self._translate_compare(expr)
        elif isinstance(expr, ast.Call):
            return self._translate_call(expr)
        elif isinstance(expr, ast.Subscript):
            return self._translate_subscript(expr)
        elif isinstance(expr, ast.List):
            return self._translate_list(expr)
        elif isinstance(expr, ast.BoolOp):
            return self._translate_bool_op(expr)
        else:
            return f"/* Unsupported expr: {type(expr).__name__} */"

    def _translate_constant(self, const: ast.Constant) -> str:
        """Translate constant values."""
        if isinstance(const.value, bool):
            return "1" if const.value else "0"
        elif isinstance(const.value, int):
            return str(const.value)
        elif isinstance(const.value, float):
            return f"{const.value:.6f}"
        elif isinstance(const.value, str):
            return f'"{const.value}"'
        else:
            return str(const.value)

    def _translate_binary_op(self, binop: ast.BinOp) -> str:
        """Translate binary operations."""
        left = self._translate_expression(binop.left)
        right = self._translate_expression(binop.right)

        if isinstance(binop.op, ast.Pow):
            return f"pow({left}, {right})"

        op_map = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.FloorDiv: '/',
        }

        op = op_map.get(type(binop.op), '+')
        return f"({left} {op} {right})"

    def _translate_unary_op(self, unaryop: ast.UnaryOp) -> str:
        """Translate unary operations."""
        operand = self._translate_expression(unaryop.operand)

        if isinstance(unaryop.op, ast.UAdd):
            return operand
        elif isinstance(unaryop.op, ast.USub):
            return f"(-{operand})"
        elif isinstance(unaryop.op, ast.Not):
            return f"(!{operand})"
        else:
            return operand

    def _translate_compare(self, compare: ast.Compare) -> str:
        """Translate comparison operations."""
        left = self._translate_expression(compare.left)

        if len(compare.ops) == 1 and len(compare.comparators) == 1:
            op = compare.ops[0]
            right = self._translate_expression(compare.comparators[0])

            op_map = {
                ast.Eq: '==',
                ast.NotEq: '!=',
                ast.Lt: '<',
                ast.LtE: '<=',
                ast.Gt: '>',
                ast.GtE: '>=',
            }

            c_op = op_map.get(type(op), '==')
            return f"{left} {c_op} {right}"

        # For complex comparisons, create compound conditions
        conditions = []
        current_left = left

        for op, comparator in zip(compare.ops, compare.comparators):
            right = self._translate_expression(comparator)
            op_map = {
                ast.Eq: '==',
                ast.NotEq: '!=',
                ast.Lt: '<',
                ast.LtE: '<=',
                ast.Gt: '>',
                ast.GtE: '>=',
            }

            c_op = op_map.get(type(op), '==')
            conditions.append(f"({current_left} {c_op} {right})")
            current_left = right

        return " && ".join(conditions)

    def _translate_bool_op(self, boolop: ast.BoolOp) -> str:
        """Translate boolean operations (and, or)."""
        values = [self._translate_expression(val) for val in boolop.values]

        if isinstance(boolop.op, ast.And):
            op = ' && '
        elif isinstance(boolop.op, ast.Or):
            op = ' || '
        else:
            op = ' && '

        return f"({op.join(values)})"

    def _translate_call(self, call: ast.Call) -> str:
        """Translate function calls."""
        if isinstance(call.func, ast.Name):
            func_name = call.func.id

            # Handle built-in functions
            if func_name == 'print':
                return self._translate_print_call(call)
            elif func_name == 'abs':
                if call.args:
                    arg = self._translate_expression(call.args[0])
                    return f"abs({arg})"
                return "0"
            elif func_name == 'pow':
                if len(call.args) >= 2:
                    base = self._translate_expression(call.args[0])
                    exp = self._translate_expression(call.args[1])
                    return f"pow({base}, {exp})"
                return "1"
            elif func_name in ['sin', 'cos', 'tan', 'sqrt', 'log', 'exp']:
                if call.args:
                    arg = self._translate_expression(call.args[0])
                    return f"{func_name}({arg})"
                return "0"

            # Regular function call
            args = [self._translate_expression(arg) for arg in call.args]
            args_str = ", ".join(args)
            return f"{func_name}({args_str})"

        return "/* Unsupported call */"

    def _translate_print_call(self, call: ast.Call) -> str:
        """Translate print() function to printf()."""
        if not call.args:
            return 'printf("\\n")'

        # Simple print implementation
        args = []
        format_parts = []

        for arg in call.args:
            args.append(self._translate_expression(arg))

            # Infer format specifier (simplified)
            if isinstance(arg, ast.Constant):
                if isinstance(arg.value, int):
                    format_parts.append("%d")
                elif isinstance(arg.value, float):
                    format_parts.append("%.6f")
                elif isinstance(arg.value, str):
                    format_parts.append("%s")
                else:
                    format_parts.append("%s")
            else:
                format_parts.append("%d")  # Default

        format_str = " ".join(format_parts) + "\\n"
        all_args = [f'"{format_str}"'] + args
        return f"printf({', '.join(all_args)})"

    def _translate_subscript(self, subscript: ast.Subscript) -> str:
        """Translate array/list subscript access."""
        array = self._translate_expression(subscript.value)
        index = self._translate_expression(subscript.slice)
        return f"{array}[{index}]"

    def _translate_list(self, list_node: ast.List) -> str:
        """Translate list literal to C array initializer."""
        if not list_node.elts:
            return "{}"

        elements = [self._translate_expression(elt) for elt in list_node.elts]
        return "{" + ", ".join(elements) + "}"

    def _translate_global_constant(self, assign_node: ast.Assign) -> List[str]:
        """Translate global constant assignment."""
        lines = []

        for target in assign_node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id

                # Check if it's a constant (ALL_CAPS naming convention)
                if var_name.isupper():
                    value_expr = self._translate_expression(assign_node.value)
                    var_type = self._infer_variable_type(assign_node.value)
                    lines.append(f"#define {var_name} {value_expr}")
                    self.variables[var_name] = var_type

        return lines

    def _translate_global_ann_constant(self, ann_assign_node: ast.AnnAssign) -> List[str]:
        """Translate global annotated constant assignment."""
        lines = []

        if isinstance(ann_assign_node.target, ast.Name):
            var_name = ann_assign_node.target.id

            # Check if it's a constant (ALL_CAPS naming convention)
            if var_name.isupper() and ann_assign_node.value:
                value_expr = self._translate_expression(ann_assign_node.value)
                lines.append(f"#define {var_name} {value_expr}")
                self.variables[var_name] = "int"  # Constants are treated as ints

        return lines

    def _infer_parameter_type(self, arg: ast.arg, func_node: ast.FunctionDef) -> str:
        """Infer parameter type from annotations or usage."""
        if arg.annotation:
            return self._annotation_to_c_type(arg.annotation)
        return "int"

    def _infer_return_type(self, func_node: ast.FunctionDef) -> str:
        """Infer return type from annotations or return statements."""
        if func_node.returns:
            return self._annotation_to_c_type(func_node.returns)

        # Special case for main function
        if func_node.name == "main":
            return "int"

        # Look for return statements
        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.Return) and stmt.value:
                return self._infer_expression_type(stmt.value)

        return "void"

    def _infer_variable_type(self, expr: ast.expr) -> str:
        """Infer variable type from expression."""
        return self._infer_expression_type(expr)

    def _infer_expression_type(self, expr: ast.expr) -> str:
        """Infer type of expression."""
        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, bool):
                return "int"
            elif isinstance(expr.value, int):
                return "int"
            elif isinstance(expr.value, float):
                return "double"
            elif isinstance(expr.value, str):
                return "char*"
        elif isinstance(expr, ast.BinOp):
            left_type = self._infer_expression_type(expr.left)
            right_type = self._infer_expression_type(expr.right)
            if left_type == "double" or right_type == "double":
                return "double"
            else:
                return "int"
        elif isinstance(expr, ast.Name):
            return self.variables.get(expr.id, "int")

        return "int"

    def _annotation_to_c_type(self, annotation: ast.expr) -> str:
        """Convert Python type annotation to C type."""
        if isinstance(annotation, ast.Name):
            type_map = {
                'int': 'int',
                'float': 'double',
                'str': 'char*',
                'bool': 'int',
            }
            return type_map.get(annotation.id, 'int')
        elif isinstance(annotation, ast.Constant):
            if annotation.value is None:
                return "void"  # None return type
            return "void"
        elif isinstance(annotation, ast.Subscript):
            # Handle List[type], Tuple[type], etc.
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'List':
                    # For now, return int* for List[int], double* for List[float], etc.
                    element_type = self._annotation_to_c_type(annotation.slice)
                    return f"{element_type}*"
                elif annotation.value.id == 'Tuple':
                    # Simplified tuple handling
                    return "void*"
        elif hasattr(annotation, 'id') and annotation.id == 'list':
            # Handle bare 'list' type
            return "int*"

        return "int"

    def _indent(self, line: str) -> str:
        """Add indentation to a line."""
        return "    " * self.indent_level + line