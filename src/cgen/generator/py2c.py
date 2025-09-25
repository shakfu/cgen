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
from .core import BinaryExpression, UnaryExpression, ComprehensionElement
from .stc_integration import (
    analyze_container_type, stc_type_mapper, stc_declaration_generator,
    stc_operation_mapper, STCContainerElement, STCOperationElement, STCForEachElement, STCSliceElement
)
from .module_system import ModuleResolver, ImportHandler
from .writer import Writer
from ..frontend.type_inference import TypeInferenceEngine
from .style import StyleOptions
from ..common import log


class UnsupportedFeatureError(Exception):
    """Raised when encountering unsupported Python features."""

    pass


class TypeMappingError(Exception):
    """Raised when type annotation cannot be mapped to C type."""

    pass


class FunctionCallConverter:
    """Handles conversion of Python function calls to C function calls."""

    def __init__(self, converter):
        """Initialize with reference to main PythonToCConverter."""
        from ..common import log
        self.log = log.config(self.__class__.__name__)
        self.converter = converter
        # Provide easy access to converter's attributes
        self.defined_structs = converter.defined_structs
        self.container_variables = converter.container_variables
        self.variable_context = converter.variable_context
        self.import_handler = converter.import_handler
        self.c_factory = converter.c_factory
        if hasattr(converter, 'struct_types'):
            self.struct_types = converter.struct_types
        else:
            self.struct_types = {}

    def convert(self, node: ast.Call) -> core.Element:
        """Main entry point for function call conversion."""
        if isinstance(node.func, ast.Name):
            return self._convert_function_by_name(node)
        elif isinstance(node.func, ast.Attribute):
            return self._convert_method_call(node)
        else:
            raise UnsupportedFeatureError("Only simple function calls and method calls supported")

    def _convert_function_by_name(self, node: ast.Call) -> core.Element:
        """Convert function calls by name (e.g., len(), set(), MyClass())."""
        func_name = node.func.id

        # Handle struct constructor calls
        if func_name in self.defined_structs:
            return self._convert_constructor_call(func_name, node.args)

        # Handle built-in functions
        if func_name in ["set", "len", "isinstance"]:
            return self._convert_builtin_call(func_name, node)

        # Handle imported/module functions
        c_func_name, is_stdlib = self.import_handler.resolve_function_call(func_name)
        args = [self.converter._convert_expression(arg) for arg in node.args]
        return self.c_factory.func_call(c_func_name, args)

    def _convert_constructor_call(self, func_name: str, args: List[ast.expr]) -> core.Element:
        """Convert struct constructor calls."""
        converted_args = [self.converter._convert_expression(arg) for arg in args]
        args_str = ', '.join(self.converter._expression_to_string(arg) for arg in converted_args)

        # Check if this is a dataclass or namedtuple
        if func_name in self.struct_types:
            if self.struct_types[func_name] == 'dataclass':
                # Use constructor function for dataclasses
                constructor_name = f"make_{func_name}"
                return core.RawCode(f"{constructor_name}({args_str})")
            else:
                # Use struct literal for namedtuples
                return core.RawCode(f"({func_name}){{{args_str}}}")
        else:
            # Default to constructor function
            constructor_name = f"make_{func_name}"
            return core.RawCode(f"{constructor_name}({args_str})")

    def _convert_builtin_call(self, func_name: str, node: ast.Call) -> core.Element:
        """Convert built-in function calls like len(), set()."""
        if func_name == "set":
            # Handle set() constructor for empty sets
            if len(node.args) == 0:
                # Return a placeholder that will be handled by assignment
                return core.RawCode("{0}")
            else:
                raise UnsupportedFeatureError("set() with arguments not supported yet")

        elif func_name == "len":
            if len(node.args) != 1:
                raise UnsupportedFeatureError("len() requires exactly one argument")

            arg = node.args[0]
            if isinstance(arg, ast.Name) and arg.id in self.container_variables:
                return self._convert_len_for_container(arg.id)
            else:
                # Not a container, treat as regular function call
                args = [self.converter._convert_expression(arg) for arg in node.args]
                return self.c_factory.func_call(func_name, args)

        elif func_name == "isinstance":
            # Handle isinstance(obj, type) - convert to appropriate C type check
            if len(node.args) != 2:
                raise UnsupportedFeatureError("isinstance() requires exactly two arguments")

            # For now, we'll convert isinstance(value, type) to a simple true
            # In real C code, type checking is done at compile time
            # This is a simplified approach since C is statically typed
            self.log.debug(f"Converting isinstance() call - type checking handled at compile time in C")
            return core.RawCode("true")  # C boolean true

    def _convert_len_for_container(self, container_name: str) -> core.Element:
        """Convert len() call for STC containers."""
        container_info = self.container_variables[container_name]
        container_type = container_info['container_type']

        if container_type == "list":
            stc_type = container_info['stc_type']
            operation_code = stc_operation_mapper.map_list_operation(stc_type, "len", variable_name=container_name)
        elif container_type == "dict":
            operation_code = stc_operation_mapper.map_dict_operation(container_name, "len")
        elif container_type == "set":
            operation_code = stc_operation_mapper.map_set_operation(container_name, "len")
        else:
            raise UnsupportedFeatureError(f"len() not supported for {container_type}")

        return STCOperationElement(operation_code)

    def _convert_method_call(self, node: ast.Call) -> core.Element:
        """Convert method calls (e.g., obj.method())."""
        if not isinstance(node.func.value, ast.Name):
            raise UnsupportedFeatureError("Complex method calls not supported")

        obj_name = node.func.value.id
        method_name = node.func.attr

        # Check if this is a container method call
        if obj_name in self.container_variables:
            return self._convert_container_method(obj_name, method_name, node.args)

        # Check if this is a string method call
        elif obj_name in self.variable_context:
            variable = self.variable_context[obj_name]
            if self._is_string_variable(variable):
                return self.converter._convert_string_method(obj_name, method_name, node.args)

        # Handle module function calls (module.function())
        c_func_name, is_stdlib = self.import_handler.resolve_module_function_call(obj_name, method_name)
        args = [self.converter._convert_expression(arg) for arg in node.args]
        return self.c_factory.func_call(c_func_name, args)

    def _convert_container_method(self, obj_name: str, method_name: str, args: List[ast.expr]) -> core.Element:
        """Convert container method calls (list.append, set.add, etc.)."""
        container_info = self.container_variables[obj_name]
        container_type = container_info['container_type']

        if container_type == "list":
            return self._convert_list_method(obj_name, method_name, args)
        elif container_type == "set":
            return self._convert_set_method(obj_name, method_name, args)
        elif container_type == "dict":
            raise UnsupportedFeatureError(f"Dict method {method_name} not implemented yet")
        else:
            raise UnsupportedFeatureError(f"Unsupported container method: {container_type}.{method_name}")

    def _convert_list_method(self, obj_name: str, method_name: str, args: List[ast.expr]) -> core.Element:
        """Convert list method calls."""
        # Get the STC type name for this container variable
        container_info = self.container_variables[obj_name]
        stc_type = container_info['stc_type']

        if method_name == "append":
            if len(args) != 1:
                raise UnsupportedFeatureError("list.append() requires exactly one argument")
            arg_str = self._convert_arg_to_string(args[0])
            operation_code = stc_operation_mapper.map_list_operation(stc_type, "append", arg_str, variable_name=obj_name)
            return STCOperationElement(operation_code)
        else:
            raise UnsupportedFeatureError(f"Unsupported list method: {method_name}")

    def _convert_set_method(self, obj_name: str, method_name: str, args: List[ast.expr]) -> core.Element:
        """Convert set method calls."""
        if method_name in ["add", "remove", "discard"]:
            if len(args) != 1:
                raise UnsupportedFeatureError(f"set.{method_name}() requires exactly one argument")
            arg_str = self._convert_arg_to_string(args[0])
            operation_code = stc_operation_mapper.map_set_operation(obj_name, method_name, arg_str)
            return STCOperationElement(operation_code)
        else:
            raise UnsupportedFeatureError(f"Unsupported set method: {method_name}")

    def _convert_arg_to_string(self, arg: ast.expr) -> str:
        """Convert argument to string representation for STC operations."""
        converted_arg = self.converter._convert_expression(arg)
        if isinstance(converted_arg, core.Element):
            from .writer import Writer
            from .style import StyleOptions
            temp_writer = Writer(StyleOptions())
            return temp_writer.write_str_elem(converted_arg)
        else:
            return str(converted_arg)

    def _is_string_variable(self, variable) -> bool:
        """Check if variable is a string type."""
        return (
            (hasattr(variable.data_type, 'base_type') and variable.data_type.base_type == "char*") or
            (isinstance(variable.data_type, str) and variable.data_type == "char*") or
            str(variable.data_type) == "char*"
        )


class PythonToCConverter:
    """Converts type-annotated Python code to C code using cfile."""

    def __init__(self):
        self.log = log.config(self.__class__.__name__)
        self.c_factory = CFactory()
        self.type_mapping = {
            "int": "int",
            "float": "double",
            "bool": "bool",  # Requires stdbool.h
            "str": "char*",
            "None": "void",
        }
        self.current_function: Optional[core.Function] = None
        self.container_variables: Dict[str, Dict[str, Any]] = {}  # Track container variables
        self.variable_context: Dict[str, core.Variable] = {}
        self.defined_structs: Dict[str, core.Struct] = {}  # Track defined struct types

        # Initialize module system
        self.module_resolver = ModuleResolver()
        self.import_handler = ImportHandler(self.module_resolver)

        # Initialize type inference engine
        self.type_inference = TypeInferenceEngine()

    def _infer_element_type(self, expr: ast.expr) -> str:
        """Infer the C type of an expression for container elements."""
        try:
            # Create a simple context from current variables
            context = {}
            for var_name, var_obj in self.variable_context.items():
                # Create a basic TypeInfo (we'd need to import it properly)
                # For now, just use the C type directly
                if hasattr(var_obj, 'data_type') and isinstance(var_obj.data_type, str):
                    context[var_name] = {"c_equivalent": var_obj.data_type}

            # Try to infer the type using the inference engine
            result = self.type_inference.infer_expression_type(expr, context)
            if result.type_info and hasattr(result.type_info, 'c_equivalent'):
                c_type = result.type_info.c_equivalent
                # Map to STC-compatible types
                if c_type == "int":
                    return "int32"
                elif c_type == "double":
                    return "double"
                elif c_type == "char*":
                    return "cstr"
                elif c_type == "bool":
                    return "bool"
                else:
                    return "int32"  # fallback
            else:
                # Fallback based on AST node type
                if isinstance(expr, ast.Constant):
                    if isinstance(expr.value, int):
                        return "int32"
                    elif isinstance(expr.value, float):
                        return "double"
                    elif isinstance(expr.value, str):
                        return "cstr"
                    elif isinstance(expr.value, bool):
                        return "bool"

                return "int32"  # default fallback
        except Exception as e:
            self.log.debug(f"Type inference failed for expression, using default: {e}")
            return "int32"  # safe fallback

    def convert_file(self, python_file_path: str) -> core.Sequence:
        """Convert a Python file to C code sequence."""
        self.log.info(f"Converting Python file: {python_file_path}")
        with open(python_file_path) as f:
            python_code = f.read()
        return self.convert_code(python_code)

    def convert_code(self, python_code: str) -> core.Sequence:
        """Convert Python code string to C code sequence."""
        self.log.debug("Starting Python to C code conversion")
        tree = ast.parse(python_code)
        result = self._convert_module(tree)
        self.log.debug("Python to C code conversion completed")
        return result

    def _convert_module(self, module: ast.Module) -> core.Sequence:
        """Convert Python module to C sequence."""
        sequence = core.Sequence()

        # Clear STC state for fresh conversion
        stc_type_mapper.used_containers.clear()
        stc_type_mapper.container_metadata.clear()

        # First pass - process all statements to discover container types and assert usage
        uses_assert = False
        uses_string_methods = False
        uses_string_comparison = False
        for node in module.body:
            self._discover_container_types(node)
            if self._has_assert_statements(node):
                uses_assert = True
            if self._has_string_method_calls(node):
                uses_string_methods = True
            if self._has_string_comparisons(node):
                uses_string_comparison = True

        # Add standard includes that might be needed
        sequence.append(self.c_factory.sysinclude("stdio.h"))
        sequence.append(self.c_factory.sysinclude("stdbool.h"))

        # Add string.h if string comparisons are used
        if uses_string_comparison:
            sequence.append(self.c_factory.sysinclude("string.h"))

        # Add assert.h if assert statements are used
        if uses_assert:
            sequence.append(self.c_factory.sysinclude("assert.h"))

        # Add string operations header if string methods are used
        if uses_string_methods:
            sequence.append(self.c_factory.include("cgen_string_ops.h"))

        # Add STC includes if we have containers
        stc_includes = stc_declaration_generator.generate_includes()
        if stc_includes:
            for include in stc_includes:
                sequence.append(include)

        sequence.append(self.c_factory.blank())

        # Add STC container declarations
        stc_declarations = stc_declaration_generator.generate_declarations()
        if stc_declarations:
            # Add each declaration as a separate element, similar to includes
            for decl in stc_declarations:
                sequence.append(core.RawCode(decl))
            sequence.append(self.c_factory.blank())

        # Second pass - convert all statements
        for node in module.body:
            # Skip module-level docstrings (string constants at module level)
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                # Convert docstring to C comment instead of invalid string literal
                docstring = node.value.value
                if docstring.strip():
                    # Handle multi-line docstrings by splitting into multiple comment lines
                    lines = docstring.strip().split('\n')
                    for line in lines:
                        if line.strip():  # Only add non-empty lines
                            comment = self.c_factory.line_comment(f" {line.strip()}")
                            sequence.append(comment)
                    # Add blank line after docstring block
                    sequence.append(self.c_factory.blank())
                continue

            c_element = self._convert_statement(node)
            if c_element:
                if isinstance(c_element, list):
                    for elem in c_element:
                        sequence.append(elem)
                else:
                    sequence.append(c_element)

        return sequence

    def _discover_container_types(self, node: ast.AST) -> None:
        """First pass to discover all container types used in the module."""
        if isinstance(node, ast.AnnAssign) and node.annotation:
            # Check for container type annotations
            container_info = analyze_container_type(node.annotation)
            if container_info:
                container_type, element_types = container_info
                # Check if this annotated variable is actually used in operations
                var_name = None
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id

                # For now, assume all annotated containers are used (register_usage=True)
                # This is safer and ensures we include necessary headers
                if container_type == "list" and len(element_types) == 1:
                    stc_type_mapper.get_list_container_name(element_types[0], register_usage=True)
                elif container_type == "dict" and len(element_types) == 2:
                    stc_type_mapper.get_dict_container_name(element_types[0], element_types[1], register_usage=True)
                elif container_type == "set" and len(element_types) == 1:
                    stc_type_mapper.get_set_container_name(element_types[0], register_usage=True)

        elif isinstance(node, ast.FunctionDef):
            # Check function parameters and return types
            if node.returns:
                container_info = analyze_container_type(node.returns)
                if container_info:
                    container_type, element_types = container_info
                    # Return types should be registered as used since they appear in function signatures
                    if container_type == "list" and len(element_types) == 1:
                        stc_type_mapper.get_list_container_name(element_types[0], register_usage=True)
                    elif container_type == "dict" and len(element_types) == 2:
                        stc_type_mapper.get_dict_container_name(element_types[0], element_types[1], register_usage=True)
                    elif container_type == "set" and len(element_types) == 1:
                        stc_type_mapper.get_set_container_name(element_types[0], register_usage=True)

            for arg in node.args.args:
                if arg.annotation:
                    container_info = analyze_container_type(arg.annotation)
                    if container_info:
                        container_type, element_types = container_info
                        if container_type == "list" and len(element_types) == 1:
                            stc_type_mapper.get_list_container_name(element_types[0], register_usage=True)
                        elif container_type == "dict" and len(element_types) == 2:
                            stc_type_mapper.get_dict_container_name(element_types[0], element_types[1], register_usage=True)
                        elif container_type == "set" and len(element_types) == 1:
                            stc_type_mapper.get_set_container_name(element_types[0], register_usage=True)

        # Recursively process child nodes
        for child in ast.iter_child_nodes(node):
            self._discover_container_types(child)

    def _convert_statement(self, node: ast.stmt) -> Union[core.Element, List[core.Element], None]:
        """Convert a Python statement to C element(s)."""
        if isinstance(node, ast.FunctionDef):
            return self._convert_function_def(node)
        elif isinstance(node, ast.AnnAssign):
            return self._convert_annotated_assignment(node)
        elif isinstance(node, ast.Assign):
            return self._convert_assignment(node)
        elif isinstance(node, ast.AugAssign):
            return self._convert_augmented_assignment(node)
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
        elif isinstance(node, ast.Import):
            return self._convert_import(node)
        elif isinstance(node, ast.ImportFrom):
            return self._convert_from_import(node)
        elif isinstance(node, ast.ClassDef):
            return self._convert_class_def(node)
        elif isinstance(node, ast.Assert):
            return self._convert_assert(node)
        elif isinstance(node, ast.Pass):
            # Pass statements can be ignored in C
            return None
        else:
            raise UnsupportedFeatureError(f"Unsupported statement type: {type(node).__name__}")

    def _convert_import(self, node: ast.Import) -> Union[List[core.Element], None]:
        """Convert import statement to C includes."""
        includes = self.import_handler.process_import(node)
        if includes:
            elements = []
            for include in includes:
                elements.append(core.RawCode(include))
            return elements
        return None

    def _convert_from_import(self, node: ast.ImportFrom) -> Union[List[core.Element], None]:
        """Convert from...import statement to C includes."""
        includes = self.import_handler.process_from_import(node)
        if includes:
            elements = []
            for include in includes:
                elements.append(core.RawCode(include))
            return elements
        return None

    def _convert_function_def(self, node: ast.FunctionDef) -> List[core.Element]:
        """Convert Python function definition to C function."""
        # Extract return type (speculative - doesn't create container usage)
        return_type = self._extract_type_annotation(node.returns, register_usage=False) if node.returns else "void"

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

        # Add function parameters to variable context so they can be modified
        for param in params:
            self.variable_context[param.name] = param

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

    def _convert_class_def(self, node: ast.ClassDef) -> List[core.Element]:
        """Convert Python class definition to C struct."""
        # Check if it's a dataclass or namedtuple
        is_dataclass = self._is_dataclass(node)
        is_namedtuple = self._is_namedtuple(node)

        if not (is_dataclass or is_namedtuple):
            raise UnsupportedFeatureError(f"Only dataclass and NamedTuple classes are supported")

        # Create struct
        struct_name = node.name
        struct = core.Struct(struct_name)

        # Register the struct type
        self.defined_structs[struct_name] = struct

        # Track whether this is a dataclass or namedtuple
        if not hasattr(self, 'struct_types'):
            self.struct_types = {}
        self.struct_types[struct_name] = 'dataclass' if is_dataclass else 'namedtuple'

        # Process fields
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                field_name = stmt.target.id
                field_type = self._extract_type_annotation(stmt.annotation, register_usage=False)

                # Convert container types to C equivalents
                c_type = self._map_struct_field_type(field_type)

                # Add to struct
                struct.make_member(field_name, c_type)

        # Create typedef struct declaration (combined form)
        # Generate the struct members as strings
        member_lines = []
        for member in struct.members:
            # Extract type from member.data_type (which is a Type object)
            if hasattr(member.data_type, 'base_type') and isinstance(member.data_type.base_type, str):
                member_type = member.data_type.base_type
            elif hasattr(member.data_type, 'name') and member.data_type.name is not None:
                member_type = member.data_type.name
            else:
                member_type = str(member.data_type)
            member_lines.append(f"    {member_type} {member.name};")

        members_str = "\n".join(member_lines)
        typedef_code = core.RawCode(f"typedef struct {{\n{members_str}\n}} {struct_name};")

        # For dataclasses, also create constructor function
        if is_dataclass:
            constructor_elements = self._create_dataclass_constructor(struct_name, struct.members)
            elements = [typedef_code, self.c_factory.blank(), self.c_factory.blank()]
            elements.extend(constructor_elements)
            elements.append(self.c_factory.blank())
            return elements
        else:
            # For namedtuples, just the typedef struct declaration
            return [typedef_code, self.c_factory.blank(), self.c_factory.blank()]

    def _is_dataclass(self, node: ast.ClassDef) -> bool:
        """Check if class has @dataclass decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                return True
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "dataclass":
                    return True
        return False

    def _is_namedtuple(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from NamedTuple."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "NamedTuple":
                return True
            elif isinstance(base, ast.Attribute):
                if (isinstance(base.value, ast.Name) and
                    base.value.id == "typing" and base.attr == "NamedTuple"):
                    return True
        return False

    def _map_struct_field_type(self, python_type: str) -> str:
        """Map Python type to C struct field type."""
        # For basic types, use direct mapping
        if python_type in self.type_mapping:
            return self.type_mapping[python_type]

        # For container types, need special handling in struct contexts
        # For now, use the STC container types directly
        return python_type

    def _create_dataclass_constructor(self, struct_name: str, members: List[core.StructMember]) -> List[core.Element]:
        """Create constructor function for dataclass."""
        # Create constructor function parameters
        params = []
        for member in members:
            if isinstance(member.data_type, str):
                param_type = member.data_type
            elif hasattr(member.data_type, 'base_type'):
                # For Type objects, use the base_type attribute
                param_type = member.data_type.base_type
            elif hasattr(member.data_type, 'name'):
                # For other DataType objects, use the name attribute
                param_type = member.data_type.name
            else:
                # Fallback - this shouldn't happen with proper Type objects
                param_type = str(member.data_type)

            param = self.c_factory.variable(member.name, param_type)
            params.append(param)

        # Create constructor function
        constructor_name = f"make_{struct_name}"
        constructor = self.c_factory.function(constructor_name, struct_name, params=params)

        # Create function body - return struct literal
        initialization = f"{{{', '.join(member.name for member in members)}}}"
        return_stmt = self.c_factory.statement(f"return ({struct_name}){initialization}")

        # Create function block
        body = self.c_factory.block()
        body.append(return_stmt)

        return [self.c_factory.declaration(constructor), body]

    def _has_assert_statements(self, node: ast.AST) -> bool:
        """Check if a node or its children contain assert statements."""
        for child_node in ast.walk(node):
            if isinstance(child_node, ast.Assert):
                return True
        return False

    def _has_string_method_calls(self, node: ast.AST) -> bool:
        """Check if a node or its children contain string method calls."""
        string_methods = {'upper', 'lower', 'find', 'split', 'strip', 'replace', 'startswith', 'endswith'}
        for child_node in ast.walk(node):
            if isinstance(child_node, ast.Call) and isinstance(child_node.func, ast.Attribute):
                method_name = child_node.func.attr
                if method_name in string_methods:
                    return True
        return False

    def _has_string_comparisons(self, node: ast.AST) -> bool:
        """Check if a node or its children contain string comparisons."""
        for child_node in ast.walk(node):
            if isinstance(child_node, ast.Compare):
                # Check if any comparison involves strings
                if self._is_string_comparison(child_node.left, child_node.comparators[0]):
                    return True
        return False

    def _expression_to_string(self, expr) -> str:
        """Convert an expression (string or Element) to a C string."""
        if isinstance(expr, str):
            return expr
        elif isinstance(expr, core.BinaryExpression):
            left_str = self._expression_to_string(expr.left)
            right_str = self._expression_to_string(expr.right)
            return f"{left_str} {expr.operator} {right_str}"
        elif isinstance(expr, core.UnaryExpression):
            operand_str = self._expression_to_string(expr.operand)
            return f"{expr.operator}{operand_str}"
        elif isinstance(expr, core.FunctionCall):
            # Handle function calls properly
            args_str = ', '.join(self._expression_to_string(arg) for arg in expr.args)
            return f"{expr.name}({args_str})"
        elif hasattr(expr, 'operation_code'):
            # STCOperationElement
            return expr.operation_code
        elif isinstance(expr, core.Element):
            # Use Writer to properly convert Element to string
            temp_writer = Writer(StyleOptions())
            return temp_writer.write_str_elem(expr)
        elif hasattr(expr, '__str__'):
            return str(expr)
        else:
            # Fallback - let the writer handle it later
            return f"/* complex_expr */"

    def _convert_assert(self, node: ast.Assert) -> core.Element:
        """Convert Python assert statement to C assert() call."""
        # Convert the test expression
        test_expr = self._convert_expression(node.test)

        # Handle optional message
        if node.msg:
            msg_expr = self._convert_expression(node.msg)
            # C assert doesn't support messages, but we can use a comment
            # For now, return a RawCode element that will be handled by the writer
            if isinstance(msg_expr, str):
                return core.RawCode(f"assert({self._expression_to_string(test_expr)}); // {msg_expr}")
            else:
                return core.RawCode(f"assert({self._expression_to_string(test_expr)});")
        else:
            return core.RawCode(f"assert({self._expression_to_string(test_expr)});")

    def _extract_type_annotation(self, annotation: ast.expr, register_usage: bool = True) -> str:
        """Extract C type from Python type annotation."""
        if isinstance(annotation, ast.Name):
            python_type = annotation.id
            if python_type in self.type_mapping:
                return self.type_mapping[python_type]
            elif python_type in self.defined_structs:
                # Handle custom struct types
                return python_type
            else:
                raise TypeMappingError(f"Unsupported type: {python_type}")
        elif isinstance(annotation, ast.Constant) and annotation.value is None:
            # Handle -> None
            return "void"
        elif isinstance(annotation, ast.Subscript):
            # Handle generic container types like list[int], dict[str, int], set[int]
            container_info = analyze_container_type(annotation)
            if container_info:
                container_type, element_types = container_info

                if container_type == "list":
                    if len(element_types) == 1:
                        return stc_type_mapper.get_list_container_name(element_types[0], register_usage=register_usage)
                    else:
                        raise TypeMappingError(f"list must have exactly one type parameter")
                elif container_type == "dict":
                    if len(element_types) == 2:
                        return stc_type_mapper.get_dict_container_name(element_types[0], element_types[1], register_usage=register_usage)
                    else:
                        raise TypeMappingError(f"dict must have exactly two type parameters")
                elif container_type == "set":
                    if len(element_types) == 1:
                        return stc_type_mapper.get_set_container_name(element_types[0], register_usage=register_usage)
                    else:
                        raise TypeMappingError(f"set must have exactly one type parameter")
                else:
                    raise TypeMappingError(f"Unsupported container type: {container_type}")
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

        # Check if this is a container type
        container_info = analyze_container_type(node.annotation)
        if container_info:
            container_type, element_types = container_info

            # Track container variable
            self.container_variables[var_name] = {
                'container_type': container_type,
                'element_types': element_types,
                'stc_type': var_type
            }

            # Create variable
            variable = self.c_factory.variable(var_name, var_type)
            self.variable_context[var_name] = variable

            # For containers, handle initialization specially
            if node.value:
                # Check if initializing with empty list/dict/set
                if (isinstance(node.value, ast.List) and len(node.value.elts) == 0) or \
                   (isinstance(node.value, ast.Dict) and len(node.value.keys) == 0) or \
                   (isinstance(node.value, ast.Set) and len(node.value.elts) == 0):
                    # Empty container initialization using STC - create declaration with initialization
                    if container_type == "list":
                        init_value = stc_operation_mapper.map_list_operation(var_type, "init_empty", variable_name=var_name)
                    elif container_type == "dict":
                        init_value = stc_operation_mapper.map_dict_operation(var_name, "init_empty")
                    elif container_type == "set":
                        init_value = stc_operation_mapper.map_set_operation(var_name, "init_empty")
                    else:
                        init_value = "{0}"

                    # Create declaration with initialization: vec_int32 numbers = {0};
                    init_expr = core.RawCode(init_value)
                    declaration = self.c_factory.declaration(variable, init_expr)
                    decl_stmt = self.c_factory.statement(declaration)
                    return [decl_stmt]
                else:
                    # Complex container initialization - convert value expression
                    value_expr = self._convert_expression(node.value)

                    # Check if this is a slice operation
                    if isinstance(value_expr, STCSliceElement):
                        # Handle slice assignment: subset: list[int] = numbers[1:3]
                        value_expr.result_var = var_name  # Set the result variable name
                        decl_stmt = self.c_factory.statement(self.c_factory.declaration(variable))
                        slice_stmt = self.c_factory.statement(value_expr)
                        return [decl_stmt, slice_stmt]
                    # Check if this is a comprehension
                    elif isinstance(value_expr, ComprehensionElement):
                        # Handle comprehension assignment: result: list[int] = [x * 2 for x in range(5)]
                        decl_stmt = self.c_factory.statement(self.c_factory.declaration(variable))

                        # Replace the temporary variable with our actual variable
                        # Remove the temporary variable declaration from the comprehension code
                        comp_code = value_expr.full_code
                        # Remove the temp var declaration line
                        lines = comp_code.split('\n')
                        lines = [line for line in lines if not (value_expr.temp_var in line and ';' in line and not 'init(' in line and not 'push_back(' in line and not 'insert(' in line)]
                        comp_code = '\n'.join(lines)
                        # Replace temp var with actual variable name
                        comp_code = comp_code.replace(value_expr.temp_var, var_name)
                        comp_stmt = self.c_factory.statement(core.RawCode(comp_code))

                        return [decl_stmt, comp_stmt]
                    else:
                        decl_stmt = self.c_factory.statement(self.c_factory.declaration(variable))
                        assign_stmt = self.c_factory.statement(self.c_factory.assignment(variable, value_expr))
                        return [decl_stmt, assign_stmt]
            else:
                # Declaration without initialization - still need to initialize containers
                decl_stmt = self.c_factory.statement(self.c_factory.declaration(variable))
                if container_type == "list":
                    init_code = stc_operation_mapper.map_list_operation(var_type, "init_empty", variable_name=var_name)
                elif container_type == "dict":
                    init_code = stc_operation_mapper.map_dict_operation(var_name, "init_empty")
                elif container_type == "set":
                    init_code = stc_operation_mapper.map_set_operation(var_name, "init_empty")
                else:
                    init_code = f"{var_name} = {{0}}"
                init_stmt = self.c_factory.statement(STCOperationElement(init_code))
                return [decl_stmt, init_stmt]
        else:
            # Regular variable handling
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

        if isinstance(target, ast.Name):
            # Regular variable assignment
            var_name = target.id
            if var_name not in self.variable_context:
                raise TypeMappingError(f"Variable '{var_name}' must be declared with type annotation first")

            variable = self.variable_context[var_name]
            value_expr = self._convert_expression(node.value)

            assignment = self.c_factory.assignment(variable, value_expr)
            return self.c_factory.statement(assignment)

        elif isinstance(target, ast.Subscript):
            # Container element assignment: container[key] = value
            if isinstance(target.value, ast.Name):
                container_name = target.value.id

                # Check if this is a known container variable
                if container_name in self.container_variables:
                    container_info = self.container_variables[container_name]
                    container_type = container_info['container_type']

                    # Convert key and value expressions
                    key_expr = self._convert_expression(target.slice)
                    value_expr = self._convert_expression(node.value)

                    # Convert to strings for STC operations
                    if isinstance(key_expr, core.Element):
                        temp_writer = Writer(StyleOptions())
                        key_str = temp_writer.write_str_elem(key_expr)
                    else:
                        key_str = str(key_expr)

                    if isinstance(value_expr, core.Element):
                        temp_writer = Writer(StyleOptions())
                        value_str = temp_writer.write_str_elem(value_expr)
                    else:
                        value_str = str(value_expr)

                    if container_type == "list":
                        # List element assignment: lst[i] = x
                        stc_type = container_info['stc_type']
                        operation_code = stc_operation_mapper.map_list_operation(stc_type, "set", key_str, value_str, variable_name=container_name)
                        return self.c_factory.statement(STCOperationElement(operation_code))
                    elif container_type == "dict":
                        # Dict element assignment: dict[key] = value
                        operation_code = stc_operation_mapper.map_dict_operation(container_name, "set", key_str, value_str)
                        return self.c_factory.statement(STCOperationElement(operation_code))
                    else:
                        raise UnsupportedFeatureError(f"Subscript assignment not supported for {container_type}")
                else:
                    raise UnsupportedFeatureError(f"Subscript assignment on non-container variable: {container_name}")
            else:
                raise UnsupportedFeatureError("Complex subscript assignment not supported")

        else:
            raise UnsupportedFeatureError("Only simple variable and container element assignments supported")

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
        elif isinstance(node, ast.BoolOp):
            return self._convert_boolean_operation(node)
        elif isinstance(node, ast.UnaryOp):
            return self._convert_unary_operation(node)
        elif isinstance(node, ast.Subscript):
            return self._convert_subscript(node)
        elif isinstance(node, ast.Attribute):
            return self._convert_attribute_access(node)
        elif isinstance(node, ast.ListComp):
            return self._convert_list_comprehension(node)
        elif isinstance(node, ast.DictComp):
            return self._convert_dict_comprehension(node)
        elif isinstance(node, ast.SetComp):
            return self._convert_set_comprehension(node)
        elif isinstance(node, ast.Set):
            return self._convert_set_literal(node)
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

    def _convert_binary_operation(self, node: ast.BinOp) -> core.Element:
        """Convert binary operation to C syntax."""
        left = self._convert_expression(node.left)
        right = self._convert_expression(node.right)

        op_map = {
            # Arithmetic operators
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "/",  # Floor division maps to regular division in C
            ast.Mod: "%",
            # Bitwise operators
            ast.BitOr: "|",
            ast.BitXor: "^",
            ast.BitAnd: "&",
            ast.LShift: "<<",
            ast.RShift: ">>",
        }

        if type(node.op) in op_map:
            op_str = op_map[type(node.op)]
            # Create a BinaryExpression element that can handle nested expressions
            return BinaryExpression(left, op_str, right)
        else:
            raise UnsupportedFeatureError(f"Unsupported binary operator: {type(node.op).__name__}")

    def _convert_comparison(self, node: ast.Compare) -> core.Element:
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

            # Check if this is a string comparison
            if self._is_string_comparison(node.left, node.comparators[0]):
                return self._convert_string_comparison(left, right, node.ops[0])

            return BinaryExpression(left, op_str, right)
        elif isinstance(node.ops[0], ast.In):
            # Handle membership testing: element in container
            return self._convert_membership_test(node.left, node.comparators[0], False)
        elif isinstance(node.ops[0], ast.NotIn):
            # Handle negative membership testing: element not in container
            return self._convert_membership_test(node.left, node.comparators[0], True)
        else:
            raise UnsupportedFeatureError(f"Unsupported comparison operator: {type(node.ops[0]).__name__}")

    def _is_string_comparison(self, left_node: ast.expr, right_node: ast.expr) -> bool:
        """Check if this is a comparison between strings."""
        # Check if either side is a string literal
        left_is_string = isinstance(left_node, ast.Str) or isinstance(left_node, ast.Constant) and isinstance(left_node.value, str)
        right_is_string = isinstance(right_node, ast.Str) or isinstance(right_node, ast.Constant) and isinstance(right_node.value, str)

        # For now, handle cases where at least one side is a string literal
        # TODO: Could be enhanced to detect string variables through type inference
        return left_is_string or right_is_string

    def _convert_string_comparison(self, left_expr, right_expr, op_node) -> core.Element:
        """Convert string comparison to use strcmp()."""
        from .writer import Writer
        from .style import StyleOptions

        # Get string representations of the expressions
        temp_writer = Writer(StyleOptions())
        if isinstance(left_expr, core.Element):
            left_str = temp_writer.write_str_elem(left_expr)
        else:
            left_str = str(left_expr)

        if isinstance(right_expr, core.Element):
            right_str = temp_writer.write_str_elem(right_expr)
        else:
            right_str = str(right_expr)

        # Generate appropriate strcmp comparison based on operator
        if isinstance(op_node, ast.Eq):
            comparison = f"strcmp({left_str}, {right_str}) == 0"
        elif isinstance(op_node, ast.NotEq):
            comparison = f"strcmp({left_str}, {right_str}) != 0"
        elif isinstance(op_node, ast.Lt):
            comparison = f"strcmp({left_str}, {right_str}) < 0"
        elif isinstance(op_node, ast.LtE):
            comparison = f"strcmp({left_str}, {right_str}) <= 0"
        elif isinstance(op_node, ast.Gt):
            comparison = f"strcmp({left_str}, {right_str}) > 0"
        elif isinstance(op_node, ast.GtE):
            comparison = f"strcmp({left_str}, {right_str}) >= 0"
        else:
            # Fallback to regular comparison
            op_map = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}
            op_str = op_map.get(type(op_node), "==")
            return BinaryExpression(left_expr, op_str, right_expr)

        return core.RawCode(comparison)

    def _convert_membership_test(self, element_node: ast.expr, container_node: ast.expr, negate: bool) -> core.Element:
        """Convert membership test (element in container) to C syntax."""
        if isinstance(container_node, ast.Name):
            container_name = container_node.id

            # Check if this is a known container variable
            if container_name in self.container_variables:
                container_info = self.container_variables[container_name]
                container_type = container_info['container_type']

                # Convert the element expression
                element_expr = self._convert_expression(element_node)

                # Convert to string for STC operation
                if isinstance(element_expr, core.Element):
                    temp_writer = Writer(StyleOptions())
                    element_str = temp_writer.write_str_elem(element_expr)
                else:
                    element_str = str(element_expr)

                if container_type == "set":
                    # Set membership: element in set -> set_contains(&set, element)
                    operation_code = stc_operation_mapper.map_set_operation(container_name, "contains", element_str)
                    contains_expr = STCOperationElement(operation_code)

                    if negate:
                        # not in: !set_contains(&set, element)
                        return UnaryExpression("!", contains_expr)
                    else:
                        # in: set_contains(&set, element)
                        return contains_expr
                else:
                    raise UnsupportedFeatureError(f"Membership testing not supported for {container_type} (only sets)")
            elif container_name in self.variable_context:
                # Check if this is a string variable
                variable = self.variable_context[container_name]
                # Check if this is a string type (char* or equivalent)
                is_string = (
                    (hasattr(variable.data_type, 'base_type') and variable.data_type.base_type == "char*") or
                    (isinstance(variable.data_type, str) and variable.data_type == "char*") or
                    str(variable.data_type) == "char*"
                )
                if is_string:
                    # Convert the element expression
                    element_expr = self._convert_expression(element_node)

                    # Convert to string for C operation
                    if isinstance(element_expr, core.Element):
                        temp_writer = Writer(StyleOptions())
                        element_str = temp_writer.write_str_elem(element_expr)
                    else:
                        element_str = str(element_expr)

                    # String membership: "substring" in string -> strstr(string, substring) != NULL
                    strstr_expr = f"strstr({container_name}, {element_str})"
                    contains_expr = BinaryExpression(strstr_expr, "!=", "NULL")

                    if negate:
                        # not in: strstr(string, substring) == NULL
                        return BinaryExpression(strstr_expr, "==", "NULL")
                    else:
                        # in: strstr(string, substring) != NULL
                        return contains_expr
                else:
                    raise UnsupportedFeatureError(f"Membership test on non-container/non-string variable: {container_name} (type: {variable.data_type})")
            else:
                raise UnsupportedFeatureError(f"Membership test on non-container variable: {container_name}")
        else:
            raise UnsupportedFeatureError("Complex membership test expressions not supported")

    def _convert_boolean_operation(self, node: ast.BoolOp) -> core.Element:
        """Convert boolean operation (and, or) to C syntax."""
        # Convert all operands
        operands = [self._convert_expression(operand) for operand in node.values]

        # Map Python boolean operators to C
        op_map = {
            ast.And: "&&",
            ast.Or: "||",
        }

        if type(node.op) in op_map:
            op_str = op_map[type(node.op)]
            # For multiple operands, create a chain of binary expressions
            if len(operands) == 2:
                return BinaryExpression(operands[0], op_str, operands[1])
            elif len(operands) > 2:
                # Create a left-associative chain: ((a && b) && c) && d
                result = BinaryExpression(operands[0], op_str, operands[1])
                for operand in operands[2:]:
                    result = BinaryExpression(result, op_str, operand)
                return result
            else:
                raise UnsupportedFeatureError("Boolean operation must have at least 2 operands")
        else:
            raise UnsupportedFeatureError(f"Unsupported boolean operator: {type(node.op).__name__}")

    def _convert_unary_operation(self, node: ast.UnaryOp) -> core.Element:
        """Convert unary operation to C syntax."""
        operand = self._convert_expression(node.operand)

        op_map = {
            ast.UAdd: "+",      # Unary plus
            ast.USub: "-",      # Unary minus
            ast.Not: "!",       # Logical NOT
            ast.Invert: "~",    # Bitwise NOT
        }

        if type(node.op) in op_map:
            op_str = op_map[type(node.op)]
            return UnaryExpression(op_str, operand)
        else:
            raise UnsupportedFeatureError(f"Unsupported unary operator: {type(node.op).__name__}")

    def _convert_subscript(self, node: ast.Subscript) -> core.Element:
        """Convert subscript operation (container[key]) or slice operation (container[start:end]) to C syntax."""
        # Check if this is a container subscript operation
        if isinstance(node.value, ast.Name):
            container_name = node.value.id

            # Check if this is a known container variable
            if container_name in self.container_variables:
                container_info = self.container_variables[container_name]
                container_type = container_info['container_type']

                # Check if this is a slice operation
                if isinstance(node.slice, ast.Slice):
                    # Handle slice operations: container[start:end]
                    if container_type != "list":
                        raise UnsupportedFeatureError(f"Slicing not supported for {container_type}")

                    # Extract start and end expressions
                    start_expr = "0"  # Default start
                    if node.slice.lower is not None:
                        start_elem = self._convert_expression(node.slice.lower)
                        temp_writer = Writer(StyleOptions())
                        start_expr = temp_writer.write_str_elem(start_elem) if isinstance(start_elem, core.Element) else str(start_elem)

                    end_expr = f"{container_name}_size(&{container_name})"  # Default end (full size)
                    if node.slice.upper is not None:
                        end_elem = self._convert_expression(node.slice.upper)
                        temp_writer = Writer(StyleOptions())
                        end_expr = temp_writer.write_str_elem(end_elem) if isinstance(end_elem, core.Element) else str(end_elem)

                    # Return a slice element that can be handled by assignment context
                    stc_type = container_info['stc_type']
                    return STCSliceElement(container_name, stc_type, start_expr, end_expr, "")

                else:
                    # Handle single element access: container[key]
                    key_expr = self._convert_expression(node.slice)

                    # Convert to string for STC operation
                    if isinstance(key_expr, core.Element):
                        temp_writer = Writer(StyleOptions())
                        key_str = temp_writer.write_str_elem(key_expr)
                    else:
                        key_str = str(key_expr)

                    if container_type == "list":
                        # List indexing: lst[i] -> *lst_at(&lst, i)
                        stc_type = container_info['stc_type']
                        operation_code = stc_operation_mapper.map_list_operation(stc_type, "get", key_str, variable_name=container_name)
                        return STCOperationElement(operation_code)
                    elif container_type == "dict":
                        # Dict access: dict[key] -> *dict_at(&dict, key)
                        operation_code = stc_operation_mapper.map_dict_operation(container_name, "get", key_str)
                        return STCOperationElement(operation_code)
                    else:
                        raise UnsupportedFeatureError(f"Subscript operation not supported for {container_type}")
            else:
                raise UnsupportedFeatureError(f"Subscript on non-container variable: {container_name}")
        else:
            raise UnsupportedFeatureError("Complex subscript expressions not supported")

    def _convert_attribute_access(self, node: ast.Attribute) -> str:
        """Convert attribute access to C struct field access."""
        if isinstance(node.value, ast.Name):
            object_name = node.value.id
            field_name = node.attr
            return f"{object_name}.{field_name}"
        else:
            raise UnsupportedFeatureError("Complex attribute access not supported")

    def _convert_function_call(self, node: ast.Call) -> core.Element:
        """Convert function call to C function call."""
        converter = FunctionCallConverter(self)
        return converter.convert(node)

    def _convert_string_method(self, obj_name: str, method_name: str, args: List[ast.expr]) -> core.Element:
        """Convert string method calls to C equivalents."""
        if method_name == "upper":
            # str.upper() -> custom upper function (requires implementation)
            if len(args) != 0:
                raise UnsupportedFeatureError("str.upper() takes no arguments")
            # For now, we'll create a function call that needs to be implemented
            return f"cgen_str_upper({obj_name})"

        elif method_name == "lower":
            # str.lower() -> custom lower function (requires implementation)
            if len(args) != 0:
                raise UnsupportedFeatureError("str.lower() takes no arguments")
            return f"cgen_str_lower({obj_name})"

        elif method_name == "find":
            # str.find(substring) -> custom find function that returns index or -1
            if len(args) != 1:
                raise UnsupportedFeatureError("str.find() requires exactly one argument")
            arg_expr = self._convert_expression(args[0])
            if isinstance(arg_expr, core.Element):
                temp_writer = Writer(StyleOptions())
                arg_str = temp_writer.write_str_elem(arg_expr)
            else:
                arg_str = str(arg_expr)
            return f"cgen_str_find({obj_name}, {arg_str})"

        elif method_name == "split":
            # str.split() -> split on whitespace, str.split(separator) -> split on separator
            if len(args) == 0:
                # Split on whitespace
                return f"cgen_str_split({obj_name}, NULL)"
            elif len(args) == 1:
                # Split on specific separator
                arg_expr = self._convert_expression(args[0])
                if isinstance(arg_expr, core.Element):
                    temp_writer = Writer(StyleOptions())
                    arg_str = temp_writer.write_str_elem(arg_expr)
                else:
                    arg_str = str(arg_expr)
                return f"cgen_str_split({obj_name}, {arg_str})"
            else:
                raise UnsupportedFeatureError("str.split() takes at most one argument")

        elif method_name == "strip":
            # str.strip() -> strip whitespace, str.strip(chars) -> strip specific characters
            if len(args) == 0:
                # Strip whitespace
                return f"cgen_str_strip({obj_name}, NULL)"
            elif len(args) == 1:
                # Strip specific characters
                arg_expr = self._convert_expression(args[0])
                if isinstance(arg_expr, core.Element):
                    temp_writer = Writer(StyleOptions())
                    arg_str = temp_writer.write_str_elem(arg_expr)
                else:
                    arg_str = str(arg_expr)
                return f"cgen_str_strip({obj_name}, {arg_str})"
            else:
                raise UnsupportedFeatureError("str.strip() takes at most one argument")

        elif method_name == "replace":
            # str.replace(old, new) -> replace all occurrences of old with new
            if len(args) != 2:
                raise UnsupportedFeatureError("str.replace() requires exactly two arguments")
            old_expr = self._convert_expression(args[0])
            new_expr = self._convert_expression(args[1])

            if isinstance(old_expr, core.Element):
                temp_writer = Writer(StyleOptions())
                old_str = temp_writer.write_str_elem(old_expr)
            else:
                old_str = str(old_expr)

            if isinstance(new_expr, core.Element):
                temp_writer = Writer(StyleOptions())
                new_str = temp_writer.write_str_elem(new_expr)
            else:
                new_str = str(new_expr)

            return f"cgen_str_replace({obj_name}, {old_str}, {new_str})"

        elif method_name == "join":
            # str.join(iterable) -> join elements of iterable with str as separator
            if len(args) != 1:
                raise UnsupportedFeatureError("str.join() requires exactly one argument")
            arg_expr = self._convert_expression(args[0])
            if isinstance(arg_expr, core.Element):
                temp_writer = Writer(StyleOptions())
                arg_str = temp_writer.write_str_elem(arg_expr)
            else:
                arg_str = str(arg_expr)
            return f"cgen_str_join({obj_name}, {arg_str})"

        else:
            raise UnsupportedFeatureError(f"Unsupported string method: {method_name}")

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
            # Convert expressions to proper C elements
            if isinstance(start, core.Element):
                init_expr = BinaryExpression(loop_var, "=", start)
                init = f"int {loop_var} = "  # Partial - will be completed by writer
            else:
                init = f"int {loop_var} = {start}"

            # Create condition as BinaryExpression
            if isinstance(end, core.Element):
                condition_expr = BinaryExpression(loop_var, "<", end)
            else:
                condition_expr = BinaryExpression(loop_var, "<", end)

            # For now, use a simpler approach and convert complex expressions to strings
            from .writer import Writer
            from .style import StyleOptions
            temp_writer = Writer(StyleOptions())

            def expr_to_str(expr):
                if isinstance(expr, core.Element):
                    return temp_writer.write_str_elem(expr)
                else:
                    return str(expr)

            start_str = expr_to_str(start)
            end_str = expr_to_str(end)
            step_str = expr_to_str(step)

            init = f"int {loop_var} = {start_str}"
            condition = f"{loop_var} < {end_str}"
            if step_str == "1":
                increment = f"{loop_var}++"
            else:
                increment = f"{loop_var} += {step_str}"

            # Convert body
            body_statements = []
            for stmt in node.body:
                body_statements.append(self._convert_statement(stmt))

            body_block = self.c_factory.block()
            for stmt in body_statements:
                body_block.append(stmt)

            return self.c_factory.for_loop(init, condition, increment, body_block)

        # Handle container iteration: for item in container
        elif (isinstance(node.iter, ast.Name) and
              node.iter.id in self.container_variables):

            container_name = node.iter.id
            container_info = self.container_variables[container_name]
            container_type = container_info['container_type']

            # Extract loop variable
            if isinstance(node.target, ast.Name):
                loop_var = node.target.id
            else:
                raise UnsupportedFeatureError("Only simple loop variables supported in container iteration")

            # Get the STC container type for the foreach macro
            stc_container_type = container_info['stc_type']

            # Convert body statements
            body_statements = []
            for stmt in node.body:
                body_statements.append(self._convert_statement(stmt))

            body_block = self.c_factory.block()
            for stmt in body_statements:
                body_block.append(stmt)

            # Generate STC foreach loop using raw C code
            # c_foreach (item, container_type, container_var)
            foreach_code = f"c_foreach ({loop_var}, {stc_container_type}, {container_name})"

            # Create a special foreach element that combines the foreach with the body
            return STCForEachElement(foreach_code, body_block)

        else:
            raise UnsupportedFeatureError("Only range-based and container iteration for loops are currently supported")

    def _convert_augmented_assignment(self, node: ast.AugAssign) -> core.Statement:
        """Convert augmented assignment (+=, -=, etc.) to C syntax."""
        if not isinstance(node.target, ast.Name):
            raise UnsupportedFeatureError("Only simple variable augmented assignments supported")

        var_name = node.target.id
        if var_name not in self.variable_context:
            raise TypeMappingError(f"Variable '{var_name}' must be declared before augmented assignment")

        variable = self.variable_context[var_name]
        value_expr = self._convert_expression(node.value)

        # Map Python augmented assignment operators to C
        op_map = {
            ast.Add: "+=",
            ast.Sub: "-=",
            ast.Mult: "*=",
            ast.Div: "/=",
            ast.FloorDiv: "/=",  # Floor division maps to regular division in C
            ast.Mod: "%=",
            ast.BitOr: "|=",
            ast.BitXor: "^=",
            ast.BitAnd: "&=",
            ast.LShift: "<<=",
            ast.RShift: ">>=",
        }

        if type(node.op) in op_map:
            op_str = op_map[type(node.op)]
            value_str = self._expression_to_string(value_expr)
            assignment = f"{var_name} {op_str} {value_str}"
            return self.c_factory.statement(assignment)
        else:
            raise UnsupportedFeatureError(f"Unsupported augmented assignment operator: {type(node.op).__name__}")

    def _convert_list_comprehension(self, node: ast.ListComp) -> core.Element:
        """Convert list comprehension to C loop with STC list operations.

        [expr for target in iter if condition] becomes:
        vec_type result;
        vec_type_init(&result);
        for (...) {
            if (condition) {
                vec_type_push_back(&result, expr);
            }
        }
        """
        # Generate unique temporary variable name for the result
        temp_var = self._generate_temp_var_name("comp_result")

        # Infer result element type from the expression
        result_element_type = self._infer_element_type(node.elt)
        result_container_type = f"vec_{result_element_type}"

        # Create initialization code
        init_code = f"{result_container_type} {temp_var};\n"
        init_code += f"{result_container_type}_init(&{temp_var});"

        # Process the single generator (comprehensions can have multiple, but we'll start simple)
        if len(node.generators) != 1:
            raise UnsupportedFeatureError("Multiple generators in list comprehensions not yet supported")

        generator = node.generators[0]

        # Extract loop variable and iterable
        if not isinstance(generator.target, ast.Name):
            raise UnsupportedFeatureError("Only simple loop variables supported in comprehensions")

        loop_var = generator.target.id

        # Handle range-based iteration (most common case)
        if (isinstance(generator.iter, ast.Call) and
            isinstance(generator.iter.func, ast.Name) and
            generator.iter.func.id == "range"):

            # Generate range-based for loop
            range_args = generator.iter.args
            if len(range_args) == 1:
                start = "0"
                end = self._expression_to_string(self._convert_expression(range_args[0]))
                step = "1"
            elif len(range_args) == 2:
                start = self._expression_to_string(self._convert_expression(range_args[0]))
                end = self._expression_to_string(self._convert_expression(range_args[1]))
                step = "1"
            elif len(range_args) == 3:
                start = self._expression_to_string(self._convert_expression(range_args[0]))
                end = self._expression_to_string(self._convert_expression(range_args[1]))
                step = self._expression_to_string(self._convert_expression(range_args[2]))
            else:
                raise UnsupportedFeatureError("Invalid range() arguments in comprehension")

            loop_code = f"for (int {loop_var} = {start}; {loop_var} < {end}; {loop_var} += {step}) {{\n"
        else:
            # Handle container iteration (lists, etc.)
            if isinstance(generator.iter, ast.Name):
                container_name = generator.iter.id
                if container_name in self.container_variables:
                    container_info = self.container_variables[container_name]
                    if container_info['container_type'] == 'list':
                        # Generate container iteration loop
                        loop_code = f"for (size_t i = 0; i < {container_name}_size(&{container_name}); i++) {{\n"
                        loop_code += f"    {result_element_type} {loop_var} = *{container_name}_at(&{container_name}, i);\n"
                    else:
                        raise UnsupportedFeatureError(f"Comprehension over {container_info['container_type']} not yet supported")
                else:
                    raise UnsupportedFeatureError(f"Unknown container in comprehension: {container_name}")
            else:
                raise UnsupportedFeatureError("Complex iterables in comprehensions not yet supported")

        # Handle conditions (if any)
        condition_code = ""
        if generator.ifs:
            if len(generator.ifs) > 1:
                raise UnsupportedFeatureError("Multiple conditions in comprehensions not yet supported")

            condition = generator.ifs[0]
            condition_expr = self._expression_to_string(self._convert_expression(condition))
            condition_code = f"    if ({condition_expr}) {{\n        "
            close_condition = "    }\n"
        else:
            condition_code = "    "
            close_condition = ""

        # Convert the expression
        expr = self._convert_expression(node.elt)
        expr_str = self._expression_to_string(expr)

        # Generate append operation
        append_code = f"{result_container_type}_push_back(&{temp_var}, {expr_str});\n"

        # Combine all parts
        full_code = init_code + "\n" + loop_code + condition_code + append_code + close_condition + "}"

        # Return as a complex element that represents the temporary variable
        return ComprehensionElement(temp_var, full_code, result_container_type)

    def _convert_dict_comprehension(self, node: ast.DictComp) -> core.Element:
        """Convert dictionary comprehension to C loop with STC hashmap operations.

        {key_expr: value_expr for target in iter if condition} becomes:
        hmap_key_value result;
        hmap_key_value_init(&result);
        for (...) {
            if (condition) {
                hmap_key_value_insert(&result, key_expr, value_expr);
            }
        }
        """
        # Generate unique temporary variable name
        temp_var = self._generate_temp_var_name("dict_comp_result")

        # Infer key and value types from expressions
        key_type = self._infer_element_type(node.key)
        value_type = self._infer_element_type(node.value)
        result_container_type = f"hmap_{key_type}_{value_type}"

        # Create initialization code
        init_code = f"{result_container_type} {temp_var};\n"
        init_code += f"{result_container_type}_init(&{temp_var});"

        # Process the single generator (similar to list comprehension)
        if len(node.generators) != 1:
            raise UnsupportedFeatureError("Multiple generators in dict comprehensions not yet supported")

        generator = node.generators[0]

        # Extract loop variable and iterable
        if not isinstance(generator.target, ast.Name):
            raise UnsupportedFeatureError("Only simple loop variables supported in dict comprehensions")

        loop_var = generator.target.id

        # Handle range-based iteration
        if (isinstance(generator.iter, ast.Call) and
            isinstance(generator.iter.func, ast.Name) and
            generator.iter.func.id == "range"):

            range_args = generator.iter.args
            if len(range_args) == 1:
                start = "0"
                end = self._expression_to_string(self._convert_expression(range_args[0]))
                step = "1"
            elif len(range_args) == 2:
                start = self._expression_to_string(self._convert_expression(range_args[0]))
                end = self._expression_to_string(self._convert_expression(range_args[1]))
                step = "1"
            else:
                raise UnsupportedFeatureError("Complex range() in dict comprehensions not yet supported")

            loop_code = f"    for (int {loop_var} = {start}; {loop_var} < {end}; {loop_var} += {step}) {{\n"
        else:
            raise UnsupportedFeatureError("Non-range iterables in dict comprehensions not yet supported")

        # Handle conditions
        condition_code = ""
        if generator.ifs:
            if len(generator.ifs) > 1:
                raise UnsupportedFeatureError("Multiple conditions in dict comprehensions not yet supported")

            condition = generator.ifs[0]
            condition_expr = self._expression_to_string(self._convert_expression(condition))
            condition_code = f"    if ({condition_expr}) {{\n        "
            close_condition = "    }\n"
        else:
            condition_code = "    "
            close_condition = ""

        # Convert key and value expressions
        key_expr = self._convert_expression(node.key)
        # Use Writer to properly convert key expression to C code
        if isinstance(key_expr, core.Element):
            temp_writer = Writer(StyleOptions())
            key_str = temp_writer.write_str_elem(key_expr)
        else:
            key_str = self._expression_to_string(key_expr)

        value_expr = self._convert_expression(node.value)
        value_str = self._expression_to_string(value_expr)

        # Generate insert operation
        insert_code = f"{result_container_type}_insert(&{temp_var}, {key_str}, {value_str});\n"

        # Combine all parts
        full_code = init_code + "\n" + loop_code + condition_code + insert_code + close_condition + "}\n"

        return ComprehensionElement(temp_var, full_code, result_container_type)

    def _convert_set_comprehension(self, node: ast.SetComp) -> core.Element:
        """Convert set comprehension to C loop with STC hset operations.

        {expr for target in iter if condition} becomes:
        hset_type result;
        hset_type_init(&result);
        for (...) {
            if (condition) {
                hset_type_insert(&result, expr);
            }
        }
        """
        # Generate unique temporary variable name
        temp_var = self._generate_temp_var_name("set_comp_result")

        # Infer element type from the expression
        element_type = self._infer_element_type(node.elt)
        result_container_type = f"hset_{element_type}"

        # Create initialization code
        init_code = f"{result_container_type} {temp_var};\n"
        init_code += f"{result_container_type}_init(&{temp_var});"

        # Process the single generator (similar to list comprehension)
        if len(node.generators) != 1:
            raise UnsupportedFeatureError("Multiple generators in set comprehensions not yet supported")

        generator = node.generators[0]

        # Extract loop variable and iterable
        if not isinstance(generator.target, ast.Name):
            raise UnsupportedFeatureError("Only simple loop variables supported in set comprehensions")

        loop_var = generator.target.id

        # Handle range-based iteration
        if (isinstance(generator.iter, ast.Call) and
            isinstance(generator.iter.func, ast.Name) and
            generator.iter.func.id == "range"):

            range_args = generator.iter.args
            if len(range_args) == 1:
                start = "0"
                end = self._expression_to_string(self._convert_expression(range_args[0]))
                step = "1"
            elif len(range_args) == 2:
                start = self._expression_to_string(self._convert_expression(range_args[0]))
                end = self._expression_to_string(self._convert_expression(range_args[1]))
                step = "1"
            else:
                raise UnsupportedFeatureError("Complex range() in set comprehensions not yet supported")

            loop_code = f"for (int {loop_var} = {start}; {loop_var} < {end}; {loop_var} += {step}) {{\n"
        else:
            raise UnsupportedFeatureError("Non-range iterables in set comprehensions not yet supported")

        # Handle conditions
        condition_code = ""
        close_condition = ""
        if generator.ifs:
            if len(generator.ifs) > 1:
                raise UnsupportedFeatureError("Multiple conditions in set comprehensions not yet supported")

            condition = generator.ifs[0]
            condition_expr = self._expression_to_string(self._convert_expression(condition))
            condition_code = f"    if ({condition_expr}) {{\n        "
            close_condition = "    }\n"
        else:
            condition_code = "    "
            close_condition = ""

        # Convert the set element expression
        expr = self._convert_expression(node.elt)
        expr_str = self._expression_to_string(expr)

        # Generate insert operation (no semicolon - will be added by statement handler)
        insert_code = f"{result_container_type}_insert(&{temp_var}, {expr_str})"

        # Combine all parts
        full_code = init_code + "\n" + loop_code + condition_code + insert_code + close_condition + "}"

        return ComprehensionElement(temp_var, full_code, result_container_type)

    def _generate_temp_var_name(self, base: str) -> str:
        """Generate a unique temporary variable name."""
        if not hasattr(self, '_temp_var_counter'):
            self._temp_var_counter = 0
        self._temp_var_counter += 1
        return f"{base}_{self._temp_var_counter}"

    def _convert_set_literal(self, node: ast.Set) -> core.Element:
        """Convert set literal to STC hset operations.

        {1, 2, 3} becomes:
        hset_int32 temp_set;
        hset_int32_init(&temp_set);
        hset_int32_insert(&temp_set, 1);
        hset_int32_insert(&temp_set, 2);
        hset_int32_insert(&temp_set, 3);
        """
        # Generate unique temporary variable name
        temp_var = self._generate_temp_var_name("set_literal")

        # Infer element type from the first element (if available) or context
        if node.elts:
            element_type = self._infer_element_type(node.elts[0])
        else:
            element_type = "int32"  # fallback for empty set literal
        result_container_type = f"hset_{element_type}"

        # Create initialization code (each line needs semicolon except the last)
        init_code = f"{result_container_type} {temp_var};\n"
        init_code += f"{result_container_type}_init(&{temp_var});"

        # Add elements to set (all but last insert need semicolons)
        insert_code = ""
        for i, element in enumerate(node.elts):
            element_expr = self._convert_expression(element)
            element_str = self._expression_to_string(element_expr)
            if i < len(node.elts) - 1:  # All but the last element get semicolons
                insert_code += f"\n{result_container_type}_insert(&{temp_var}, {element_str});"
            else:  # Last element doesn't get semicolon - will be added by statement handler
                insert_code += f"\n{result_container_type}_insert(&{temp_var}, {element_str})"

        # Combine all parts
        full_code = init_code + insert_code

        return ComprehensionElement(temp_var, full_code, result_container_type)

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
