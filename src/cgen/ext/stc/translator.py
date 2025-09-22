"""
STC-Enhanced Python-to-C Translator

This module extends the SimplePythonToCTranslator with STC container support,
enabling translation of Python container operations to high-performance STC
container operations in generated C code.
"""

import ast
from typing import Dict, List, Set, Optional, Tuple
from .containers import STCCodeGenerator, get_stc_container_for_python_type

class STCPythonToCTranslator:
    """Enhanced Python-to-C translator with STC container support."""

    def __init__(self):
        self.stc_generator = STCCodeGenerator()
        self.container_variables: Dict[str, str] = {}  # var_name -> container_type
        self.required_includes: Set[str] = set()
        self.type_definitions: List[str] = []

    def analyze_variable_types(self, node: ast.AST) -> Dict[str, str]:
        """
        Analyze AST to identify variable types and their STC container mappings.

        Returns:
            Dictionary mapping variable names to their Python types
        """
        type_info = {}

        class TypeAnalyzer(ast.NodeVisitor):
            def visit_AnnAssign(self, node):
                """Handle type-annotated assignments: var: List[int] = []"""
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    if isinstance(node.annotation, ast.Name):
                        type_info[var_name] = node.annotation.id
                    elif isinstance(node.annotation, ast.Subscript):
                        # Handle List[int], Dict[str, int], etc.
                        type_info[var_name] = ast.unparse(node.annotation)

            def visit_Assign(self, node):
                """Handle regular assignments with type inference"""
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # Try to infer type from assignment value
                        if isinstance(node.value, ast.List):
                            type_info[var_name] = "list"
                        elif isinstance(node.value, ast.Dict):
                            type_info[var_name] = "dict"
                        elif isinstance(node.value, ast.Set):
                            type_info[var_name] = "set"
                        elif isinstance(node.value, ast.Str):
                            type_info[var_name] = "str"
                        elif isinstance(node.value, ast.Call):
                            # Handle list(), dict(), set() constructor calls
                            if isinstance(node.value.func, ast.Name):
                                func_name = node.value.func.id
                                if func_name in ['list', 'dict', 'set', 'deque']:
                                    type_info[var_name] = func_name

        analyzer = TypeAnalyzer()
        analyzer.visit(node)
        return type_info

    def generate_stc_includes_and_types(self, type_info: Dict[str, str]) -> Tuple[List[str], List[str]]:
        """
        Generate STC include statements and type definitions.

        Args:
            type_info: Variable name to Python type mapping

        Returns:
            Tuple of (include_statements, type_definitions)
        """
        includes = []
        type_defs = []

        for var_name, python_type in type_info.items():
            container = get_stc_container_for_python_type(python_type)
            if container:
                # Generate type definition and include
                type_def, include = self.stc_generator.generate_container_type_def(
                    var_name, python_type
                )

                if include and include not in includes:
                    includes.append(include)

                if type_def and type_def not in type_defs:
                    type_defs.append(type_def)

                # Store container type for later use
                if python_type.startswith('List['):
                    self.container_variables[var_name] = f"{var_name.capitalize()}Vec"
                elif python_type.startswith('Dict['):
                    self.container_variables[var_name] = f"{var_name.capitalize()}Map"
                elif python_type.startswith('Set['):
                    self.container_variables[var_name] = f"{var_name.capitalize()}Set"
                elif python_type == 'list':
                    self.container_variables[var_name] = f"{var_name.capitalize()}Vec"
                elif python_type == 'dict':
                    self.container_variables[var_name] = f"{var_name.capitalize()}Map"
                elif python_type == 'set':
                    self.container_variables[var_name] = f"{var_name.capitalize()}Set"

        return includes, type_defs

    def translate_container_operation(self, call_node: ast.Call) -> Optional[str]:
        """
        Translate Python container method calls to STC operations.

        Args:
            call_node: AST Call node representing a method call

        Returns:
            STC operation string or None if not a container operation
        """
        if not isinstance(call_node.func, ast.Attribute):
            return None

        # Get the object and method name
        if isinstance(call_node.func.value, ast.Name):
            obj_name = call_node.func.value.id
            method_name = call_node.func.attr

            # Check if this is a known container variable
            if obj_name in self.container_variables:
                container_type = self.container_variables[obj_name]

                # Translate common operations
                if method_name == 'append':
                    if call_node.args:
                        arg = ast.unparse(call_node.args[0])
                        return f"{container_type}_push(&{obj_name}, {arg})"

                elif method_name == 'pop':
                    if call_node.args:
                        # pop(index) - more complex, may need bounds checking
                        index = ast.unparse(call_node.args[0])
                        return f"{container_type}_erase_at(&{obj_name}, {index})"
                    else:
                        # pop() - remove last element
                        return f"{container_type}_pop(&{obj_name})"

                elif method_name == 'insert':
                    if len(call_node.args) >= 2:
                        index = ast.unparse(call_node.args[0])
                        value = ast.unparse(call_node.args[1])
                        return f"{container_type}_insert_at(&{obj_name}, {index}, {value})"

                elif method_name == 'remove':
                    if call_node.args:
                        value = ast.unparse(call_node.args[0])
                        return f"{container_type}_erase_val(&{obj_name}, {value})"

                elif method_name == 'clear':
                    return f"{container_type}_clear(&{obj_name})"

                elif method_name == 'copy':
                    return f"{container_type}_clone({obj_name})"

                # Dict-specific operations
                elif method_name == 'get':
                    if call_node.args:
                        key = ast.unparse(call_node.args[0])
                        default = ast.unparse(call_node.args[1]) if len(call_node.args) > 1 else "NULL"
                        return f"{container_type}_get(&{obj_name}, {key})"

                elif method_name == 'keys':
                    return f"{container_type}_keys({obj_name})"

                elif method_name == 'values':
                    return f"{container_type}_values({obj_name})"

                # Set-specific operations
                elif method_name == 'add':
                    if call_node.args:
                        value = ast.unparse(call_node.args[0])
                        return f"{container_type}_insert(&{obj_name}, {value})"

                elif method_name == 'discard':
                    if call_node.args:
                        value = ast.unparse(call_node.args[0])
                        return f"{container_type}_erase(&{obj_name}, {value})"

        return None

    def translate_container_initialization(self, assign_node: ast.Assign) -> Optional[str]:
        """
        Translate container initialization to STC initialization.

        Args:
            assign_node: AST Assignment node

        Returns:
            STC initialization string or None
        """
        if len(assign_node.targets) == 1 and isinstance(assign_node.targets[0], ast.Name):
            var_name = assign_node.targets[0].id

            if var_name in self.container_variables:
                container_type = self.container_variables[var_name]
                return self.stc_generator.generate_initialization(var_name, container_type)

        return None

    def generate_cleanup_code(self) -> List[str]:
        """Generate cleanup code for all STC containers."""
        cleanup_lines = []
        for var_name, container_type in self.container_variables.items():
            cleanup_lines.append(self.stc_generator.generate_cleanup(var_name, container_type))
        return cleanup_lines

    def translate_len_builtin(self, call_node: ast.Call) -> Optional[str]:
        """Translate len() builtin for STC containers."""
        if (isinstance(call_node.func, ast.Name) and
            call_node.func.id == 'len' and
            len(call_node.args) == 1):

            arg = call_node.args[0]
            if isinstance(arg, ast.Name) and arg.id in self.container_variables:
                container_type = self.container_variables[arg.id]
                return f"{container_type}_size(&{arg.id})"

        return None

    def generate_iteration_code(self, for_node: ast.For) -> Optional[str]:
        """
        Generate STC iteration code for for loops.

        Args:
            for_node: AST For node

        Returns:
            STC iteration string or None
        """
        if (isinstance(for_node.iter, ast.Name) and
            for_node.iter.id in self.container_variables):

            container_name = for_node.iter.id
            container_type = self.container_variables[container_name]

            if isinstance(for_node.target, ast.Name):
                iterator_var = "it"  # Standard STC iterator name
                target_var = for_node.target.id

                iteration_code = self.stc_generator.generate_iteration(
                    container_name, container_type, iterator_var
                )

                # Generate code to access the iterator value
                if container_type.endswith('Vec') or container_type.endswith('Set'):
                    value_access = f"*{iterator_var}.ref"
                elif container_type.endswith('Map'):
                    value_access = f"{iterator_var}.ref->second"  # For key-value pairs
                else:
                    value_access = f"*{iterator_var}.ref"

                return f"{iteration_code} {{\n    {target_var} = {value_access};"

        return None

__all__ = ['STCPythonToCTranslator']