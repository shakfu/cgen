"""
STC-Enhanced Python to C Converter

This module extends the basic PythonToCConverter with comprehensive STC
(Smart Template Containers) support, enabling high-performance, memory-safe
container operations in generated C code.
"""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass

from . import core

# Helper function to create raw C code elements
def create_raw_code(code: str) -> core.Statement:
    """Create a statement from raw C code."""
    return core.Statement(code)
from .factory import CFactory
from .py2c import PythonToCConverter, UnsupportedFeatureError, TypeMappingError
from ..ext.stc.containers import STCContainer, STC_CONTAINERS, STCCodeGenerator
from ..ext.stc.translator import STCPythonToCTranslator
from ..ext.stc.memory_manager import STCMemoryManager, MemoryScope


@dataclass
class ContainerUsagePattern:
    """Tracks how a container is used to optimize STC container selection."""
    has_random_access: bool = False
    has_frequent_insertion: bool = False
    has_frequent_deletion: bool = False
    has_sorted_access: bool = False
    has_frequent_lookup: bool = False
    is_key_value: bool = False
    access_count: int = 0
    modification_count: int = 0


# STCMemoryManager is now imported from memory_manager.py


class STCOptimizer:
    """Optimizes container selection based on usage patterns."""

    def __init__(self):
        self.usage_patterns: Dict[str, ContainerUsagePattern] = {}

    def analyze_usage_patterns(self, module: ast.Module) -> Dict[str, ContainerUsagePattern]:
        """Analyze AST to determine container usage patterns."""

        class UsageAnalyzer(ast.NodeVisitor):
            def __init__(self, optimizer):
                self.optimizer = optimizer

            def visit_Subscript(self, node):
                """Track array/dict access patterns."""
                if isinstance(node.value, ast.Name):
                    var_name = node.value.id
                    pattern = self.optimizer._get_or_create_pattern(var_name)
                    pattern.has_random_access = True
                    pattern.access_count += 1
                self.generic_visit(node)

            def visit_Call(self, node):
                """Track method calls on containers."""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        var_name = node.func.value.id
                        method_name = node.func.attr
                        pattern = self.optimizer._get_or_create_pattern(var_name)

                        if method_name in ['append', 'insert', 'add']:
                            pattern.has_frequent_insertion = True
                            pattern.modification_count += 1
                        elif method_name in ['remove', 'pop', 'discard']:
                            pattern.has_frequent_deletion = True
                            pattern.modification_count += 1
                        elif method_name in ['get', 'keys', 'values', 'items']:
                            pattern.has_frequent_lookup = True
                            pattern.is_key_value = True
                            pattern.access_count += 1

                self.generic_visit(node)

        analyzer = UsageAnalyzer(self)
        analyzer.visit(module)
        return self.usage_patterns

    def _get_or_create_pattern(self, var_name: str) -> ContainerUsagePattern:
        """Get or create usage pattern for a variable."""
        if var_name not in self.usage_patterns:
            self.usage_patterns[var_name] = ContainerUsagePattern()
        return self.usage_patterns[var_name]

    def optimize_container_choice(self, python_type: str, var_name: str) -> str:
        """Select optimal STC container based on usage pattern."""
        pattern = self.usage_patterns.get(var_name, ContainerUsagePattern())

        # Analyze the Python type
        if python_type.startswith('List['):
            if pattern.has_frequent_insertion and pattern.has_random_access:
                return 'deque'  # Better for random access + insertion
            else:
                return 'vec'    # Default for lists

        elif python_type.startswith('Dict['):
            if pattern.has_sorted_access:
                return 'smap'   # Sorted map for ordered access
            else:
                return 'hmap'   # Hash map for fast lookup

        elif python_type.startswith('Set['):
            if pattern.has_sorted_access:
                return 'sset'   # Sorted set
            else:
                return 'hset'   # Hash set

        elif python_type == 'str':
            return 'cstr'       # STC string

        # Fallback to basic mapping
        return python_type.lower()


class STCEnhancedPythonToCConverter(PythonToCConverter):
    """Enhanced Python-to-C converter with comprehensive STC support."""

    def __init__(self):
        super().__init__()

        # STC integration components
        self.stc_translator = STCPythonToCTranslator()
        self.stc_generator = STCCodeGenerator()
        self.memory_manager = STCMemoryManager()
        self.optimizer = STCOptimizer()

        # Enhanced type mapping with STC containers
        self.stc_type_mapping = {
            # Basic types (enhanced)
            'int': 'int',
            'float': 'double',
            'bool': 'bool',
            'str': 'cstr',      # Use STC string instead of char*
            'None': 'void',

            # Container type patterns (will be dynamically resolved)
            'list': 'vec',
            'dict': 'hmap',
            'set': 'hset',
            'deque': 'deque',
            'queue': 'queue',
            'stack': 'stack'
        }

        # Track generated STC types to avoid duplicates
        self.generated_stc_types: Set[str] = set()
        self.stc_includes: Set[str] = set()

    def convert_code(self, python_code: str) -> core.Sequence:
        """Convert Python code with STC container support."""
        tree = ast.parse(python_code)

        # Analyze usage patterns for optimization
        self.optimizer.analyze_usage_patterns(tree)

        # Analyze variable types for STC container detection
        type_info = self.stc_translator.analyze_variable_types(tree)

        return self._convert_module_with_stc(tree, type_info)

    def _convert_module_with_stc(self, module: ast.Module, type_info: Dict[str, str]) -> core.Sequence:
        """Convert module with STC container support."""
        sequence = core.Sequence()

        # Add standard includes
        sequence.append(self.c_factory.sysinclude("stdio.h"))
        sequence.append(self.c_factory.sysinclude("stdlib.h"))
        sequence.append(self.c_factory.sysinclude("stdbool.h"))

        # Generate and add STC includes
        stc_includes, stc_type_defs = self._generate_stc_setup(type_info)
        for include in stc_includes:
            sequence.append(create_raw_code(include))

        sequence.append(self.c_factory.blank())

        # Add STC type definitions
        for type_def in stc_type_defs:
            sequence.append(create_raw_code(type_def))

        if stc_type_defs:
            sequence.append(self.c_factory.blank())

        # Convert module body
        for node in module.body:
            c_element = self._convert_statement(node)
            if c_element:
                if isinstance(c_element, list):
                    for elem in c_element:
                        sequence.append(elem)
                else:
                    sequence.append(c_element)

        return sequence

    def _generate_stc_setup(self, type_info: Dict[str, str]) -> Tuple[List[str], List[str]]:
        """Generate STC includes and type definitions."""
        includes = []
        type_defs = []

        for var_name, python_type in type_info.items():
            container = self._get_stc_container_for_type(python_type)
            if container:
                # Generate optimized container choice
                optimized_container = self.optimizer.optimize_container_choice(python_type, var_name)

                # Generate type definition and include
                type_def, include = self._generate_container_type_def(
                    var_name, python_type, optimized_container
                )

                if include and include not in includes:
                    includes.append(include)

                if type_def and type_def not in type_defs:
                    type_defs.append(type_def)

                # Register with memory manager and STC translator
                container_type_name = self._get_container_type_name(var_name, python_type)
                self.memory_manager.register_container(
                    var_name, container_type_name, MemoryScope.BLOCK
                )
                # Also register with STC translator for operation translation
                self.stc_translator.container_variables[var_name] = container_type_name

        return includes, type_defs

    def _generate_container_type_def(self, var_name: str, python_type: str,
                                   stc_container: str) -> Tuple[str, str]:
        """Generate STC container type definition."""
        if python_type.startswith(('List[', 'list[')):
            # Extract element type: List[int] or list[int] -> int
            start_pos = 5 if python_type.startswith('List[') else 5
            element_type = python_type[start_pos:-1]
            c_element_type = self._map_python_type_to_c(element_type)

            container_type_name = f"{var_name.capitalize()}Vec"
            type_def = f"#define T {container_type_name}, {c_element_type}"
            include = "#include <stc/vec.h>"

            return type_def, include

        elif python_type.startswith(('Dict[', 'dict[')):
            # Extract key and value types: Dict[str, int] or dict[str, int] -> str, int
            start_pos = 5 if python_type.startswith('Dict[') else 5
            inner = python_type[start_pos:-1]
            key_type, value_type = [t.strip() for t in inner.split(',')]

            c_key_type = self._map_python_type_to_c(key_type)
            c_value_type = self._map_python_type_to_c(value_type)

            container_type_name = f"{var_name.capitalize()}Map"

            if stc_container == 'smap':
                type_def = f"#define T {container_type_name}, {c_key_type}, {c_value_type}"
                include = "#include <stc/smap.h>"
            else:  # hmap
                type_def = f"#define T {container_type_name}, {c_key_type}, {c_value_type}"
                include = "#include <stc/hmap.h>"

            return type_def, include

        elif python_type.startswith(('Set[', 'set[')):
            # Extract element type: Set[int] or set[int] -> int
            start_pos = 4 if python_type.startswith('Set[') else 4
            element_type = python_type[start_pos:-1]
            c_element_type = self._map_python_type_to_c(element_type)

            container_type_name = f"{var_name.capitalize()}Set"

            if stc_container == 'sset':
                type_def = f"#define T {container_type_name}, {c_element_type}"
                include = "#include <stc/sset.h>"
            else:  # hset
                type_def = f"#define T {container_type_name}, {c_element_type}"
                include = "#include <stc/hset.h>"

            return type_def, include

        elif python_type == 'str':
            # String doesn't need type definition
            return "", "#include <stc/cstr.h>"

        return "", ""

    def _get_container_type_name(self, var_name: str, python_type: str) -> str:
        """Get the C container type name for a variable."""
        if python_type.startswith(('List[', 'list[')):
            return f"{var_name.capitalize()}Vec"
        elif python_type.startswith(('Dict[', 'dict[')):
            return f"{var_name.capitalize()}Map"
        elif python_type.startswith(('Set[', 'set[')):
            return f"{var_name.capitalize()}Set"
        elif python_type == 'str':
            return "cstr"
        return var_name

    def _map_python_type_to_c(self, python_type: str) -> str:
        """Map Python type to C type for STC containers."""
        mapping = {
            'int': 'int',
            'float': 'double',
            'str': 'cstr',
            'bool': 'bool'
        }
        return mapping.get(python_type, python_type)

    def _get_stc_container_for_type(self, python_type: str) -> Optional[STCContainer]:
        """Get STC container for Python type."""
        # Handle both List[T] and list[T] formats
        if any(python_type.startswith(prefix) for prefix in ['List[', 'list[', 'Dict[', 'dict[', 'Set[', 'set[']):
            if python_type.startswith(('List[', 'list[')):
                return STC_CONTAINERS.get('list')
            elif python_type.startswith(('Dict[', 'dict[')):
                return STC_CONTAINERS.get('dict')
            elif python_type.startswith(('Set[', 'set[')):
                return STC_CONTAINERS.get('set')
        elif python_type in ['list', 'dict', 'set', 'str']:
            return STC_CONTAINERS.get(python_type)
        return None

    def _extract_type_annotation(self, annotation: ast.expr) -> str:
        """Enhanced type annotation extraction with STC support."""
        if isinstance(annotation, ast.Name):
            python_type = annotation.id
            if python_type in self.stc_type_mapping:
                return self.stc_type_mapping[python_type]
            return super()._extract_type_annotation(annotation)

        elif isinstance(annotation, ast.Subscript):
            # Handle List[T], Dict[K,V], Set[T] with STC containers
            full_type = ast.unparse(annotation)

            if full_type.startswith(('List[', 'list[')):
                # For return types, we'll return the container pointer
                return "void*"  # STC container returned by pointer

            elif full_type.startswith(('Dict[', 'dict[')):
                return "void*"  # STC map returned by pointer

            elif full_type.startswith(('Set[', 'set[')):
                return "void*"  # STC set returned by pointer

            else:
                # Try parent implementation for other generic types
                try:
                    return super()._extract_type_annotation(annotation)
                except:
                    # If parent fails, return generic pointer for container types
                    return "void*"

        return super()._extract_type_annotation(annotation)

    def _convert_annotated_assignment(self, node: ast.AnnAssign) -> Union[core.Statement, List[core.Statement]]:
        """Enhanced annotated assignment with STC container support."""
        if not isinstance(node.target, ast.Name):
            raise UnsupportedFeatureError("Only simple variable assignments supported")

        var_name = node.target.id
        python_type = ast.unparse(node.annotation) if node.annotation else 'int'

        # Check if this is an STC container type
        if self._is_stc_container_type(python_type):
            return self._convert_stc_container_assignment(node, var_name, python_type)
        else:
            return super()._convert_annotated_assignment(node)

    def _is_stc_container_type(self, python_type: str) -> bool:
        """Check if type should use STC containers."""
        return (python_type.startswith(('List[', 'Dict[', 'Set[', 'list[', 'dict[', 'set[')) or
                python_type in ['list', 'dict', 'set', 'str', 'List', 'Dict', 'Set'])

    def _convert_stc_container_assignment(self, node: ast.AnnAssign, var_name: str,
                                        python_type: str) -> List[core.Statement]:
        """Convert STC container assignment with memory management."""
        statements = []

        # Generate container type name
        container_type = self._get_container_type_name(var_name, python_type)

        # Register with memory manager and STC translator
        self.memory_manager.register_container(
            var_name, container_type, MemoryScope.BLOCK, getattr(node, 'lineno', 0)
        )
        self.stc_translator.container_variables[var_name] = container_type

        # Generate memory-safe initialization
        init_code = self.memory_manager.generate_memory_safe_initialization(
            var_name, container_type
        )
        for line in init_code:
            statements.append(create_raw_code(line))

        # Handle initialization value if present
        if node.value:
            init_statements = self._convert_stc_container_initialization(
                var_name, container_type, node.value
            )
            statements.extend(init_statements)

        return statements

    def _convert_stc_container_initialization(self, var_name: str, container_type: str,
                                           value_node: ast.expr) -> List[core.Statement]:
        """Convert STC container initialization from Python value."""
        statements = []

        if isinstance(value_node, ast.List):
            # Initialize from list literal: [1, 2, 3]
            for element in value_node.elts:
                element_code = self._convert_expression(element)
                push_stmt = f"{container_type}_push(&{var_name}, {element_code});"
                statements.append(create_raw_code(push_stmt))

        elif isinstance(value_node, ast.Dict):
            # Initialize from dict literal: {"key": value}
            for key, value in zip(value_node.keys, value_node.values):
                key_code = self._convert_expression(key)
                value_code = self._convert_expression(value)
                insert_stmt = f"{container_type}_insert(&{var_name}, {key_code}, {value_code});"
                statements.append(create_raw_code(insert_stmt))

        elif isinstance(value_node, ast.Set):
            # Initialize from set literal: {1, 2, 3}
            for element in value_node.elts:
                element_code = self._convert_expression(element)
                insert_stmt = f"{container_type}_insert(&{var_name}, {element_code});"
                statements.append(create_raw_code(insert_stmt))

        return statements

    def _convert_function_def(self, node: ast.FunctionDef) -> List[core.Element]:
        """Enhanced function definition with comprehensive STC memory management."""
        # Enter function scope for memory management
        self.memory_manager.enter_function(node.name)

        # Extract return type and register parameters
        return_type = self._extract_type_annotation(node.returns) if node.returns else "void"

        # Register container parameters with memory manager
        for arg in node.args.args:
            if arg.annotation:
                param_type = ast.unparse(arg.annotation) if arg.annotation else 'int'
                if self._is_stc_container_type(param_type):
                    container_type = self._get_container_type_name(arg.arg, param_type)
                    self.memory_manager.register_parameter(arg.arg, container_type)
                    self.stc_translator.container_variables[arg.arg] = container_type

        # Convert function normally
        result = super()._convert_function_def(node)

        # Generate comprehensive cleanup and error handling
        cleanup_code, error_handling = self.memory_manager.exit_function()

        if result and len(result) >= 2 and hasattr(result[1], 'append'):
            # Add error handling label
            if error_handling:
                for error_line in error_handling:
                    result[1].append(create_raw_code(error_line))

            # Add cleanup before function end
            if cleanup_code:
                result[1].append(create_raw_code("// Automatic STC container cleanup"))
                for cleanup in cleanup_code:
                    result[1].append(create_raw_code(cleanup))

        return result

    def _convert_expression_statement(self, node: ast.Expr) -> core.Statement:
        """Enhanced expression statement with memory safety checks."""
        if isinstance(node.value, ast.Call):
            # Check for STC container operations that might fail
            if isinstance(node.value.func, ast.Attribute):
                if isinstance(node.value.func.value, ast.Name):
                    obj_name = node.value.func.value.id
                    if obj_name in self.memory_manager.allocations:
                        # Generate exception-safe wrapper
                        operation_code = self._convert_expression(node.value)
                        safe_code = self.memory_manager.generate_exception_safe_wrapper(
                            str(operation_code), obj_name
                        )
                        if len(safe_code) > 1:
                            # Return multi-line safe code
                            return create_raw_code('\n'.join(safe_code))

        return super()._convert_expression_statement(node)

    def _convert_return(self, node: ast.Return) -> core.Statement:
        """Enhanced return statement with memory transfer tracking."""
        if node.value and isinstance(node.value, ast.Name):
            var_name = node.value.id
            # Check if returning a container - mark as moved
            transfer_code = self.memory_manager.register_return_value(var_name)
            if transfer_code:
                # Add comment about memory transfer
                return create_raw_code(f"{transfer_code}\n    return {var_name};")

        return super()._convert_return(node)

    def _convert_expression(self, node: ast.expr) -> Union[str, core.Element]:
        """Enhanced expression conversion with STC container support."""
        if isinstance(node, ast.List):
            # Handle list literals: [1, 2, 3]
            elements = [self._convert_expression(elem) for elem in node.elts]
            return "{" + ", ".join(str(e) for e in elements) + "}"

        elif isinstance(node, ast.Dict):
            # Handle dict literals: {"key": value}
            pairs = []
            for key, value in zip(node.keys, node.values):
                key_code = self._convert_expression(key)
                value_code = self._convert_expression(value)
                pairs.append(f"{{{key_code}, {value_code}}}")
            return "{" + ", ".join(pairs) + "}"

        elif isinstance(node, ast.Set):
            # Handle set literals: {1, 2, 3}
            elements = [self._convert_expression(elem) for elem in node.elts]
            return "{" + ", ".join(str(e) for e in elements) + "}"

        elif isinstance(node, ast.Subscript):
            # Handle container subscript access
            if isinstance(node.value, ast.Name):
                container_name = node.value.id

                # Check if this is an STC container
                if (hasattr(self, 'stc_translator') and
                    self.stc_translator and
                    container_name in self.stc_translator.container_variables):

                    container_type = self.stc_translator.container_variables[container_name]
                    key = self._convert_expression(node.slice)

                    # Generate appropriate STC operation
                    if container_type.endswith('Vec'):
                        # List indexing: list[i] -> *vec_at(&list, i)
                        return f"*{container_type}_at(&{container_name}, {key})"
                    elif container_type.endswith('Map'):
                        # Dict lookup: dict[key] -> *hmap_get(&dict, key)
                        return f"*{container_type}_get(&{container_name}, {key})"
                    elif container_type.endswith('Set'):
                        # Set membership check: set[key] -> hset_contains(&set, key)
                        return f"{container_type}_contains(&{container_name}, {key})"
                    elif container_type == 'cstr':
                        # String indexing: str[i] -> cstr_at(&str, i)
                        return f"cstr_at(&{container_name}, {key})"

            # Fall back to parent implementation
            return super()._convert_expression(node)

        else:
            # Fall back to parent implementation
            return super()._convert_expression(node)

    def _convert_for(self, node: ast.For) -> Union[core.Element, List[core.Element]]:
        """Enhanced for loop conversion with STC container iteration support."""
        # Check if this is iteration over an STC container
        if isinstance(node.iter, ast.Name):
            container_name = node.iter.id

            # Check if this is a known STC container
            if (hasattr(self, 'stc_translator') and
                self.stc_translator and
                container_name in self.stc_translator.container_variables):

                container_type = self.stc_translator.container_variables[container_name]

                if isinstance(node.target, ast.Name):
                    loop_var = node.target.id
                    iterator_var = "it"

                    # Generate STC iteration
                    iteration_code = f"for (c_each({iterator_var}, {container_type}, {container_name}))"

                    # Create the for loop structure
                    statements = []

                    # Add the for loop start as raw code
                    statements.append(create_raw_code(f"{iteration_code} {{"))

                    # Generate code to access iterator value
                    if container_type.endswith('Vec') or container_type.endswith('Set'):
                        value_access = f"*{iterator_var}.ref"
                    elif container_type.endswith('Map'):
                        value_access = f"{iterator_var}.ref->first"  # For key iteration
                    else:
                        value_access = f"*{iterator_var}.ref"

                    # Add variable assignment
                    statements.append(create_raw_code(f"    int {loop_var} = {value_access};"))

                    # Convert loop body
                    for stmt in node.body:
                        body_stmt = self._convert_statement(stmt)
                        if isinstance(body_stmt, list):
                            for s in body_stmt:
                                statements.append(s)
                        else:
                            statements.append(body_stmt)

                    # Close the loop
                    statements.append(create_raw_code("}"))

                    return statements

        # Fall back to parent implementation for range-based loops
        return super()._convert_for(node)

    def _convert_assignment(self, node: ast.Assign) -> Union[core.Statement, List[core.Statement]]:
        """Enhanced assignment conversion with STC container subscript support."""
        if len(node.targets) != 1:
            return super()._convert_assignment(node)

        target = node.targets[0]

        # Check if this is a subscript assignment (container[key] = value)
        if isinstance(target, ast.Subscript):
            if isinstance(target.value, ast.Name):
                container_name = target.value.id

                # Check if this is an STC container
                if (hasattr(self, 'stc_translator') and
                    self.stc_translator and
                    container_name in self.stc_translator.container_variables):

                    container_type = self.stc_translator.container_variables[container_name]
                    key = self._convert_expression(target.slice)
                    value = self._convert_expression(node.value)

                    # Generate appropriate STC operation
                    if container_type.endswith('Vec'):
                        # List assignment: list[i] = value -> *vec_at_mut(&list, i) = value
                        operation = f"*{container_type}_at_mut(&{container_name}, {key}) = {value}"
                    elif container_type.endswith('Map'):
                        # Dict assignment: dict[key] = value -> hmap_insert(&dict, key, value)
                        operation = f"{container_type}_insert(&{container_name}, {key}, {value})"
                    elif container_type == 'cstr':
                        # String character assignment: str[i] = char -> cstr_set_at(&str, i, char)
                        operation = f"cstr_set_at(&{container_name}, {key}, {value})"
                    else:
                        return super()._convert_assignment(node)

                    return create_raw_code(operation)

        # Fall back to parent implementation
        return super()._convert_assignment(node)

    def _convert_comparison(self, node: ast.Compare) -> str:
        """Enhanced comparison conversion with STC container membership support."""
        # Check for membership tests (x in container)
        if (len(node.ops) == 1 and
            isinstance(node.ops[0], ast.In) and
            len(node.comparators) == 1):

            left_expr = self._convert_expression(node.left)
            right = node.comparators[0]

            # Check if right side is an STC container
            if (isinstance(right, ast.Name) and
                hasattr(self, 'stc_translator') and
                self.stc_translator and
                right.id in self.stc_translator.container_variables):

                container_type = self.stc_translator.container_variables[right.id]
                container_name = right.id

                if container_type.endswith(('Set', 'Map')):
                    return f"{container_type}_contains(&{container_name}, {left_expr})"
                elif container_type.endswith('Vec'):
                    # For vectors, we need to search
                    return f"({container_type}_find(&{container_name}, {left_expr}).ref != {container_type}_end(&{container_name}).ref)"
                elif container_type == 'cstr':
                    return f"(cstr_find(&{container_name}, {left_expr}) != cstr_npos)"

        # Fall back to parent implementation
        return super()._convert_comparison(node)

    def _convert_function_call(self, node: ast.Call) -> core.Element:
        """Enhanced function call conversion with STC container support."""
        # Check if this is a container method call first
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id
                method_name = node.func.attr

                # Check if this is an STC container operation
                stc_operation = self.stc_translator.translate_container_operation(node)
                if stc_operation:
                    return create_raw_code(stc_operation)

                # Fall back to treating as regular function call
                func_name = f"{obj_name}_{method_name}"
                args = [self._convert_expression(arg) for arg in node.args]
                return self.c_factory.func_call(func_name, args)

        # Handle builtin functions that might work with containers
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

            # Check for STC builtin translations
            stc_builtin = self.stc_translator.translate_builtin_functions(node)
            if stc_builtin:
                return create_raw_code(stc_builtin)

            # Special handling for len() function
            if func_name == 'len' and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, ast.Name) and arg.id in self.stc_translator.container_variables:
                    container_type = self.stc_translator.container_variables[arg.id]
                    return create_raw_code(f"{container_type}_size(&{arg.id})")

        # Fall back to parent implementation
        return super()._convert_function_call(node)

    def analyze_memory_safety(self, python_code: str) -> Dict[str, any]:
        """
        Analyze Python code for memory safety issues.

        Returns:
            Dictionary containing memory safety analysis results
        """
        tree = ast.parse(python_code)
        memory_errors = self.memory_manager.analyze_memory_safety(tree)

        return {
            "memory_errors": [
                {
                    "type": error.error_type,
                    "message": error.message,
                    "line": error.line_number,
                    "severity": error.severity
                }
                for error in memory_errors
            ],
            "cleanup_summary": self.memory_manager.generate_cleanup_summary()
        }


# Convenience functions
def convert_python_to_c_with_stc(python_code: str) -> str:
    """Convert Python code to C with STC container support."""
    converter = STCEnhancedPythonToCConverter()
    c_sequence = converter.convert_code(python_code)

    from ..core.style import StyleOptions
    from ..core.writer import Writer

    writer = Writer(StyleOptions())
    return writer.write_str(c_sequence)


def convert_python_file_to_c_with_stc(input_file: str, output_file: str) -> None:
    """Convert Python file to C with STC container support."""
    converter = STCEnhancedPythonToCConverter()
    c_sequence = converter.convert_file(input_file)

    from ..core.style import StyleOptions
    from ..core.writer import Writer

    writer = Writer(StyleOptions())
    writer.write_file(c_sequence, output_file)