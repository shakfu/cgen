"""
STC Container Type Mappings and Code Generation

This module provides mappings between Python container types and STC containers,
along with code generation utilities for translating Python operations to STC.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class STCContainer:
    """Represents an STC container type mapping."""
    stc_name: str           # STC container name (e.g., "vec")
    header_file: str        # Header to include (e.g., "stc/vec.h")
    python_equivalent: str  # Python type (e.g., "list")
    description: str        # Human-readable description
    requires_key_type: bool = False  # Whether container needs key type
    requires_value_type: bool = True # Whether container needs value type

# Core STC container mappings
STC_CONTAINERS = {
    # Sequence containers
    'list': STCContainer(
        stc_name='vec',
        header_file='stc/vec.h',
        python_equivalent='list',
        description='Dynamic array with push/pop operations',
        requires_value_type=True
    ),
    'deque': STCContainer(
        stc_name='deque',
        header_file='stc/deque.h',
        python_equivalent='collections.deque',
        description='Double-ended queue with efficient insertion/deletion',
        requires_value_type=True
    ),

    # Associative containers
    'dict': STCContainer(
        stc_name='hmap',
        header_file='stc/hmap.h',
        python_equivalent='dict',
        description='Unordered key-value mapping (hash map)',
        requires_key_type=True,
        requires_value_type=True
    ),
    'set': STCContainer(
        stc_name='hset',
        header_file='stc/hset.h',
        python_equivalent='set',
        description='Unordered unique element collection (hash set)',
        requires_key_type=True,
        requires_value_type=False
    ),

    # Sorted containers
    'sorted_dict': STCContainer(
        stc_name='smap',
        header_file='stc/smap.h',
        python_equivalent='dict',  # Sorted behavior
        description='Sorted key-value mapping (tree map)',
        requires_key_type=True,
        requires_value_type=True
    ),
    'sorted_set': STCContainer(
        stc_name='sset',
        header_file='stc/sset.h',
        python_equivalent='set',   # Sorted behavior
        description='Sorted unique element collection (tree set)',
        requires_key_type=True,
        requires_value_type=False
    ),

    # String container
    'str': STCContainer(
        stc_name='cstr',
        header_file='stc/cstr.h',
        python_equivalent='str',
        description='String with short string optimization and UTF-8 support',
        requires_value_type=False
    ),

    # Stack and queue
    'stack': STCContainer(
        stc_name='stack',
        header_file='stc/stack.h',
        python_equivalent='list',  # Used as stack
        description='Stack (LIFO) container',
        requires_value_type=True
    ),
    'queue': STCContainer(
        stc_name='queue',
        header_file='stc/queue.h',
        python_equivalent='collections.deque',  # Used as queue
        description='Queue (FIFO) container',
        requires_value_type=True
    ),

    # Priority queue
    'priority_queue': STCContainer(
        stc_name='pqueue',
        header_file='stc/pqueue.h',
        python_equivalent='heapq',
        description='Priority queue (heap)',
        requires_value_type=True
    )
}

# Python type to C type mappings for STC
PYTHON_TO_C_TYPES = {
    'int': 'int',
    'float': 'double',
    'str': 'cstr',
    'bool': 'bool',
    'bytes': 'uint8_t*',
    # Add more as needed
}

class STCCodeGenerator:
    """Generates STC container code from Python type annotations."""

    def __init__(self):
        self.generated_types = set()

    def get_c_type(self, python_type: str) -> str:
        """Convert Python type to C type suitable for STC containers."""
        return PYTHON_TO_C_TYPES.get(python_type, python_type)

    def generate_container_type_def(self, container_name: str, python_type_hint: str) -> Tuple[str, str]:
        """
        Generate STC container type definition.

        Args:
            container_name: Variable name for the container
            python_type_hint: Python type hint (e.g., 'List[int]', 'Dict[str, int]')

        Returns:
            Tuple of (type_definition, include_statement)
        """
        # Parse Python type hint
        if python_type_hint.startswith('List['):
            # List[int] -> vec
            inner_type = python_type_hint[5:-1]  # Extract 'int' from 'List[int]'
            c_type = self.get_c_type(inner_type)
            container = STC_CONTAINERS['list']

            type_name = f"{container_name.capitalize()}Vec"
            type_def = f"#define T {type_name}, {c_type}"
            include = f"#include <{container.header_file}>"

            return type_def, include

        elif python_type_hint.startswith('Dict['):
            # Dict[str, int] -> hmap
            # Extract key and value types
            inner = python_type_hint[5:-1]  # Extract 'str, int' from 'Dict[str, int]'
            key_type, value_type = [t.strip() for t in inner.split(',')]

            key_c_type = self.get_c_type(key_type)
            value_c_type = self.get_c_type(value_type)
            container = STC_CONTAINERS['dict']

            type_name = f"{container_name.capitalize()}Map"
            type_def = f"#define T {type_name}, {key_c_type}, {value_c_type}"
            include = f"#include <{container.header_file}>"

            return type_def, include

        elif python_type_hint.startswith('Set['):
            # Set[int] -> hset
            inner_type = python_type_hint[4:-1]  # Extract 'int' from 'Set[int]'
            c_type = self.get_c_type(inner_type)
            container = STC_CONTAINERS['set']

            type_name = f"{container_name.capitalize()}Set"
            type_def = f"#define T {type_name}, {c_type}"
            include = f"#include <{container.header_file}>"

            return type_def, include

        elif python_type_hint == 'str':
            # String type
            container = STC_CONTAINERS['str']
            include = f"#include <{container.header_file}>"
            return "", include  # cstr doesn't need type definition

        else:
            # Fallback for unsupported types
            return f"// Unsupported type: {python_type_hint}", ""

    def generate_operation_translation(self, operation: str, container_type: str, args: List[str]) -> str:
        """
        Translate Python container operations to STC operations.

        Args:
            operation: Python operation (e.g., 'append', 'get', 'pop')
            container_type: STC container type name
            args: Operation arguments

        Returns:
            STC function call
        """
        # Map Python operations to STC operations
        operation_mappings = {
            # List operations
            'append': 'push',
            'pop': 'pop',
            'insert': 'insert',
            'remove': 'erase',
            'clear': 'clear',
            'copy': 'clone',

            # Dict operations
            'get': 'get',
            'put': 'insert',
            'del': 'erase',
            'keys': 'keys',
            'values': 'values',
            'items': 'items',

            # Set operations
            'add': 'insert',
            'discard': 'erase',
            'union': 'union',
            'intersection': 'intersection',

            # Common operations
            'len': 'size',
            'empty': 'empty',
        }

        stc_operation = operation_mappings.get(operation, operation)

        if args:
            args_str = ', '.join(args)
            return f"{container_type}_{stc_operation}({args_str})"
        else:
            return f"{container_type}_{stc_operation}()"

    def generate_initialization(self, container_name: str, container_type: str) -> str:
        """Generate STC container initialization code."""
        return f"{container_type} {container_name} = {{0}};"

    def generate_cleanup(self, container_name: str, container_type: str) -> str:
        """Generate STC container cleanup code."""
        return f"{container_type}_drop(&{container_name});"

    def generate_iteration(self, container_name: str, container_type: str,
                         iterator_var: str = "it") -> str:
        """Generate STC container iteration code."""
        return f"for (c_each({iterator_var}, {container_type}, {container_name}))"

def get_stc_container_for_python_type(python_type: str) -> Optional[STCContainer]:
    """Get the appropriate STC container for a Python type."""
    # Simple mappings
    direct_mappings = {
        'list': 'list',
        'dict': 'dict',
        'set': 'set',
        'str': 'str',
        'deque': 'deque'
    }

    for py_type, stc_key in direct_mappings.items():
        if python_type.startswith(py_type) or python_type == py_type:
            return STC_CONTAINERS.get(stc_key)

    return None

__all__ = [
    'STCContainer',
    'STC_CONTAINERS',
    'PYTHON_TO_C_TYPES',
    'STCCodeGenerator',
    'get_stc_container_for_python_type'
]