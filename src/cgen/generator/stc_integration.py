"""STC (Smart Template Containers) Integration for CGen.

This module provides integration between Python container types (list, dict, set)
and STC library containers (vec, hmap, hset) for efficient C code generation.
"""

import ast
from typing import Dict, List, Optional, Set, Tuple

from . import core


class STCTypeMapper:
    """Maps Python container types to STC container types."""

    def __init__(self):
        from ..common import log

        self.log = log.config(self.__class__.__name__)
        self.type_mappings = {
            # Basic type mappings for STC
            "int": "int32_t",
            "float": "double",
            "bool": "bool",
            "str": "cstr",
        }

        # Track which STC containers we've seen (for declarations)
        self.used_containers: Set[str] = set()

        # Track container metadata: container_name -> (container_type, element_types)
        self.container_metadata: Dict[str, Tuple[str, List[str]]] = {}

    def python_type_to_stc(self, python_type: str) -> str:
        """Convert Python type to STC equivalent."""
        return self.type_mappings.get(python_type, python_type)

    def get_list_container_name(self, element_type: str, register_usage: bool = True) -> str:
        """Generate STC vec container name for list[element_type]."""
        stc_type = self.python_type_to_stc(element_type)
        container_name = f"vec_{stc_type.replace('_t', '')}"
        if register_usage:
            # Debug logging to track where containers are registered
            from ..common import log

            logger = log.config("STCTypeMapper.get_list")
            logger.debug(f"Registering list container: {container_name} for element_type: {element_type}")
            self.used_containers.add(container_name)
            self.container_metadata[container_name] = ("list", [element_type])
        return container_name

    def get_dict_container_name(self, key_type: str, value_type: str, register_usage: bool = True) -> str:
        """Generate STC hmap container name for dict[key_type, value_type]."""
        stc_key = self.python_type_to_stc(key_type)
        stc_value = self.python_type_to_stc(value_type)
        container_name = f"hmap_{stc_key}_{stc_value}".replace("_t", "")
        if register_usage:
            self.used_containers.add(container_name)
            self.container_metadata[container_name] = ("dict", [key_type, value_type])
        return container_name

    def get_set_container_name(self, element_type: str, register_usage: bool = True) -> str:
        """Generate STC hset container name for set[element_type]."""
        stc_type = self.python_type_to_stc(element_type)
        container_name = f"hset_{stc_type.replace('_t', '')}"
        if register_usage:
            # Debug logging to track where containers are registered
            from ..common import log

            logger = log.config("STCTypeMapper.get_set")
            logger.debug(f"Registering set container: {container_name} for element_type: {element_type}")
            self.used_containers.add(container_name)
            self.container_metadata[container_name] = ("set", [element_type])
        return container_name

    def register_container_usage(self, container_name: str) -> None:
        """Register that a container is actually used in generated code."""
        # Debug logging to track where containers are registered
        from ..common import log

        logger = log.config("STCTypeMapper.register")
        logger.debug(f"Registering container usage: {container_name}")
        self.used_containers.add(container_name)


class STCDeclarationGenerator:
    """Generates STC container declarations."""

    def __init__(self, type_mapper: STCTypeMapper):
        from ..common import log

        self.log = log.config(self.__class__.__name__)
        self.type_mapper = type_mapper

    def generate_includes(self) -> List[core.Element]:
        """Generate necessary STC include statements."""
        includes = []

        # Only include stc/types.h if we actually have containers
        if self.type_mapper.used_containers:
            includes.append(core.IncludeDirective("stc/types.h", system=False))

        # Note: specific container headers are included after declarations using #define T
        return includes

    def generate_declarations(self) -> List[str]:
        """Generate STC container declarations and implementations."""
        declarations = []

        # Group containers by type for better organization
        vec_containers = []
        hmap_containers = []
        hset_containers = []

        for container in self.type_mapper.used_containers:
            if container in self.type_mapper.container_metadata:
                container_type, element_types = self.type_mapper.container_metadata[container]
                if container_type == "list":
                    element_type = element_types[0]
                    stc_type = self.type_mapper.python_type_to_stc(element_type)
                    vec_containers.append((container, stc_type))
                elif container_type == "dict":
                    key_type, value_type = element_types
                    stc_key = self.type_mapper.python_type_to_stc(key_type)
                    stc_value = self.type_mapper.python_type_to_stc(value_type)
                    hmap_containers.append((container, stc_key, stc_value))
                elif container_type == "set":
                    element_type = element_types[0]
                    stc_type = self.type_mapper.python_type_to_stc(element_type)
                    hset_containers.append((container, stc_type))

        # Generate declare statements for all containers
        for container, stc_type in vec_containers:
            declarations.append(f"declare_vec({container}, {stc_type});")

        for container, stc_key, stc_value in hmap_containers:
            declarations.append(f"declare_hmap({container}, {stc_key}, {stc_value});")

        for container, stc_type in hset_containers:
            declarations.append(f"declare_hset({container}, {stc_type});")

        # Add blank line before template instantiations
        if declarations:
            declarations.append("")

        # Generate template instantiations using #define T + #include pattern
        for container, stc_type in vec_containers:
            declarations.append(f"#define T {container}, {stc_type}, (c_declared)")
            declarations.append('#include "stc/vec.h"')
            declarations.append("")  # Blank line after each instantiation

        for container, stc_key, stc_value in hmap_containers:
            declarations.append(f"#define T {container}, {stc_key}, {stc_value}, (c_declared)")
            declarations.append('#include "stc/hmap.h"')
            declarations.append("")

        for container, stc_type in hset_containers:
            declarations.append(f"#define T {container}, {stc_type}, (c_declared)")
            declarations.append('#include "stc/hset.h"')
            declarations.append("")

        return declarations


class STCOperationMapper:
    """Maps Python container operations to STC operations."""

    def __init__(self, type_mapper: STCTypeMapper):
        from ..common import log

        self.log = log.config(self.__class__.__name__)
        self.type_mapper = type_mapper

    def map_list_operation(self, stc_type: str, operation: str, *args, variable_name: str = None) -> str:
        """Map Python list operation to STC vec operation."""
        # Use variable_name if provided, otherwise use stc_type
        var_name = variable_name or stc_type

        # Register that this container is actually used
        self.type_mapper.register_container_usage(var_name)

        if operation == "append":
            return f"{stc_type}_push(&{var_name}, {args[0]})"
        elif operation == "len":
            return f"{stc_type}_size(&{var_name})"
        elif operation == "get":  # lst[i]
            return f"*{stc_type}_at(&{var_name}, {args[0]})"
        elif operation == "set":  # lst[i] = x
            return f"*{stc_type}_at(&{var_name}, {args[0]}) = {args[1]}"
        elif operation == "init_empty":
            # For STC containers, return the initialization value that will be used in declaration
            return "{0}"
        elif operation == "slice":  # lst[start:end]
            # For slicing, we need special handling - this should be handled differently
            # as it returns a new container rather than a single operation
            raise ValueError("Slice operation should be handled by STCSliceElement, not as a simple operation")
        else:
            raise ValueError(f"Unsupported list operation: {operation}")

    def map_dict_operation(self, container_name: str, operation: str, *args) -> str:
        """Map Python dict operation to STC hmap operation."""
        # Register that this container is actually used
        self.type_mapper.register_container_usage(container_name)

        if operation == "get":  # dict[key]
            return f"*{container_name}_at(&{container_name}, {args[0]})"
        elif operation == "set":  # dict[key] = value
            return f"{container_name}_insert(&{container_name}, {args[0]}, {args[1]})"
        elif operation == "len":
            return f"{container_name}_size(&{container_name})"
        elif operation == "init_empty":
            return f"{container_name} = {{0}}"
        else:
            raise ValueError(f"Unsupported dict operation: {operation}")

    def map_set_operation(self, container_name: str, operation: str, *args) -> str:
        """Map Python set operation to STC hset operation."""
        # Register that this container is actually used
        self.type_mapper.register_container_usage(container_name)

        if operation == "add":  # set.add(element)
            return f"{container_name}_insert(&{container_name}, {args[0]})"
        elif operation == "len":
            return f"{container_name}_size(&{container_name})"
        elif operation == "contains":  # element in set
            return f"{container_name}_contains(&{container_name}, {args[0]})"
        elif operation == "remove":  # set.remove(element)
            return f"{container_name}_erase(&{container_name}, {args[0]})"
        elif operation == "discard":  # set.discard(element) - no error if not found
            return f"{container_name}_erase(&{container_name}, {args[0]})"  # STC erase is safe
        elif operation == "init_empty":
            return f"{container_name} = {{0}}"
        else:
            raise ValueError(f"Unsupported set operation: {operation}")


class STCContainerElement(core.Element):
    """Represents an STC container in the generated C code."""

    def __init__(self, container_type: str, name: str, element_type: str):
        self.container_type = container_type  # e.g., 'vec_i32'
        self.name = name
        self.element_type = element_type


class STCOperationElement(core.Element):
    """Represents an STC container operation in the generated C code."""

    def __init__(self, operation_code: str):
        self.operation_code = operation_code


class STCForEachElement(core.Element):
    """Represents an STC foreach loop in the generated C code."""

    def __init__(self, foreach_code: str, body_block):
        self.foreach_code = foreach_code  # e.g., "c_foreach (item, vec_int32, numbers)"
        self.body_block = body_block


class STCSliceElement(core.Element):
    """Represents an STC container slice operation in the generated C code."""

    def __init__(self, container_name: str, container_type: str, start_expr: str, end_expr: str, result_var: str):
        self.container_name = container_name
        self.container_type = container_type  # e.g., 'vec_int32'
        self.start_expr = start_expr  # start index expression
        self.end_expr = end_expr  # end index expression
        self.result_var = result_var  # variable name for the result


def analyze_container_type(type_annotation) -> Optional[Tuple[str, List[str]]]:
    """Analyze a type annotation to extract container type and element types.

    Returns:
        Tuple of (container_type, element_types) or None if not a container

    Examples:
        list[int] -> ('list', ['int'])
        dict[str, int] -> ('dict', ['str', 'int'])
        set[str] -> ('set', ['str'])
    """
    if not isinstance(type_annotation, ast.Subscript):
        return None

    # Extract container name (e.g., 'list', 'dict', 'set')
    if isinstance(type_annotation.value, ast.Name):
        container_name = type_annotation.value.id
    else:
        return None

    # Extract element types
    element_types = []
    slice_value = type_annotation.slice

    if isinstance(slice_value, ast.Tuple):
        # Multiple types (e.g., dict[str, int])
        for elt in slice_value.elts:
            if isinstance(elt, ast.Name):
                element_types.append(elt.id)
            else:
                return None  # Complex types not supported yet
    elif isinstance(slice_value, ast.Name):
        # Single type (e.g., list[int])
        element_types.append(slice_value.id)
    else:
        return None  # Complex types not supported yet

    return (container_name, element_types)


# Global instances for use across the module
stc_type_mapper = STCTypeMapper()
stc_declaration_generator = STCDeclarationGenerator(stc_type_mapper)
stc_operation_mapper = STCOperationMapper(stc_type_mapper)
