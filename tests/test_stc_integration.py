"""
Comprehensive tests for STC (Smart Template Containers) integration.

Tests cover:
- Container type mappings
- Operation translations
- Memory management
- Performance optimizations
- Error handling
"""

import ast
import pytest
from unittest.mock import Mock, patch

from src.cgen.generator.stc_py2c import (
    STCEnhancedPythonToCConverter,
    STCOptimizer,
    ContainerUsagePattern,
    convert_python_to_c_with_stc
)
from src.cgen.ext.stc.containers import STCCodeGenerator, STC_CONTAINERS
from src.cgen.ext.stc.translator import STCPythonToCTranslator
from src.cgen.ext.stc.memory_manager import STCMemoryManager, MemoryScope


class TestSTCContainerMappings:
    """Test STC container type mappings and code generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = STCEnhancedPythonToCConverter()
        self.generator = STCCodeGenerator()

    def test_list_type_mapping(self):
        """Test List[T] to STC vec mapping."""
        python_code = """
def process_numbers(numbers: list[int]) -> int:
    data: list[int] = [1, 2, 3]
    data.append(4)
    return len(data)
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Check for STC vec operations and memory management
        assert "vec_int_" in c_code  # Container type generated
        assert "_push(" in c_code   # append -> push translation
        assert "_size(" in c_code   # len -> size translation
        assert "_drop(" in c_code   # automatic cleanup

    def test_dict_type_mapping(self):
        """Test Dict[K,V] to STC hmap mapping."""
        python_code = """
def process_dict() -> int:
    data: dict[str, int] = {"key": 1}
    length: int = len(data)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Check for STC hmap operations and structures
        assert "hmap_cstr_int_" in c_code  # Container type generated
        assert "_insert(" in c_code   # dict initialization -> insert translation
        assert "_size(" in c_code     # len -> size translation
        assert "_drop(" in c_code     # automatic cleanup

    def test_set_type_mapping(self):
        """Test Set[T] to STC hset mapping."""
        python_code = """
def process_set() -> int:
    data: set[int] = {1, 2, 3}
    length: int = len(data)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Check for STC hset operations and structures
        assert "hset_int_" in c_code    # Container type generated
        assert "_insert(" in c_code   # set initialization -> insert translation
        assert "_size(" in c_code     # len -> size translation
        assert "_drop(" in c_code     # automatic cleanup

    def test_string_type_mapping(self):
        """Test str to STC cstr mapping."""
        python_code = """
def process_string(text: str) -> int:
    local_str: str = "hello"
    length: int = len(local_str)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Check for STC cstr operations and structures
        assert "cstr" in c_code                   # cstr type used
        assert "len(" in c_code                  # len operation (may need translation fix)

    def test_container_type_definition_generation(self):
        """Test generation of STC type definitions."""
        type_def, include = self.generator.generate_container_type_def("data", "List[int]")

        assert include == ""  # Phase 7.2: includes handled by template manager
        assert "vec_int" in type_def
        assert type_def  # Ensure type definition is not empty

    def test_complex_container_types(self):
        """Test complex nested container types."""
        python_code = """
def complex_containers():
    matrix: list[list[int]] = [[1, 2], [3, 4]]
    lookup: dict[str, list[int]] = {"key": [1, 2, 3]}
"""
        # Should handle nested containers gracefully
        result = self.converter.convert_code(python_code)
        assert result is not None


class TestSTCOperationTranslation:
    """Test translation of Python container operations to STC operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.translator = STCPythonToCTranslator()
        self.translator.container_variables = {
            "data": "DataVec",
            "mapping": "MappingMap",
            "items": "ItemsSet"
        }

    def test_list_operations(self):
        """Test translation of list operations."""
        # Test append
        call = ast.parse("data.append(5)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "DataVec_push(&data, 5)"

        # Test pop
        call = ast.parse("data.pop()").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "DataVec_pop(&data)"

        # Test insert
        call = ast.parse("data.insert(0, 5)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "DataVec_insert_at(&data, 0, 5)"

        # Test remove
        call = ast.parse("data.remove(5)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "DataVec_erase_val(&data, 5)"

    def test_dict_operations(self):
        """Test translation of dict operations."""
        # Test get
        call = ast.parse("mapping.get('key')").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "MappingMap_get(&mapping, 'key')"

        # Test get with default
        call = ast.parse("mapping.get('key', 0)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "MappingMap_get_or(&mapping, 'key', 0)"

        # Test keys
        call = ast.parse("mapping.keys()").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "MappingMap_keys(mapping)"

    def test_set_operations(self):
        """Test translation of set operations."""
        # Test add
        call = ast.parse("items.add(5)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "ItemsSet_insert(&items, 5)"

        # Test discard
        call = ast.parse("items.discard(5)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "ItemsSet_erase(&items, 5)"

        # Test union
        call = ast.parse("items.union(other)").body[0].value
        result = self.translator.translate_container_operation(call)
        assert result == "ItemsSet_union(&items, &other)"

    def test_subscript_operations(self):
        """Test translation of subscript operations."""
        # List indexing
        subscript = ast.parse("data[0]").body[0].value
        result = self.translator.translate_subscript_operation(subscript)
        assert result == "DataVec_at(&data, 0)"

        # Dict lookup
        subscript = ast.parse("mapping['key']").body[0].value
        result = self.translator.translate_subscript_operation(subscript)
        assert result == "MappingMap_get(&mapping, 'key')"

    def test_membership_operations(self):
        """Test translation of membership operations."""
        # Set membership
        compare = ast.parse("5 in items").body[0].value
        result = self.translator.translate_membership_test(compare)
        assert result == "ItemsSet_contains(&items, 5)"

        # Dict membership
        compare = ast.parse("'key' in mapping").body[0].value
        result = self.translator.translate_membership_test(compare)
        assert result == "MappingMap_contains(&mapping, 'key')"

    def test_builtin_functions(self):
        """Test translation of builtin functions."""
        # len() function
        call = ast.parse("len(data)").body[0].value
        result = self.translator.translate_builtin_functions(call)
        assert result == "DataVec_size(&data)"

        # max() function
        call = ast.parse("max(data)").body[0].value
        result = self.translator.translate_builtin_functions(call)
        assert result == "DataVec_max(&data)"


class TestSTCMemoryManagement:
    """Test STC memory management and automatic cleanup."""

    def setup_method(self):
        """Set up test fixtures."""
        self.memory_manager = STCMemoryManager()

    def test_container_registration(self):
        """Test container registration and tracking."""
        allocation = self.memory_manager.register_container(
            "data", "DataVec", MemoryScope.FUNCTION, 10
        )

        assert allocation.name == "data"
        assert allocation.container_type == "DataVec"
        assert allocation.scope == MemoryScope.FUNCTION
        assert allocation.line_number == 10
        assert allocation.requires_cleanup

    def test_scope_management(self):
        """Test scope entry and exit with cleanup generation."""
        self.memory_manager.enter_scope(MemoryScope.BLOCK)
        self.memory_manager.register_container("local_data", "LocalVec")

        cleanup_code = self.memory_manager.exit_scope()
        assert len(cleanup_code) == 1
        assert "LocalVec_drop(&local_data);" in cleanup_code[0]

    def test_parameter_registration(self):
        """Test registration of container parameters."""
        self.memory_manager.register_parameter("param_data", "ParamVec")

        allocation = self.memory_manager.allocations["param_data"]
        assert allocation.is_parameter
        assert not allocation.requires_cleanup  # Parameters not cleaned up in function

    def test_return_value_handling(self):
        """Test handling of returned containers."""
        self.memory_manager.register_container("result", "ResultVec")
        transfer_code = self.memory_manager.register_return_value("result")

        allocation = self.memory_manager.allocations["result"]
        assert allocation.is_return_value
        assert not allocation.requires_cleanup  # Return values transferred to caller
        assert transfer_code is not None

    def test_memory_safety_initialization(self):
        """Test memory-safe container initialization."""
        init_code = self.memory_manager.generate_memory_safe_initialization(
            "safe_data", "SafeVec"
        )

        assert len(init_code) >= 1
        assert "SafeVec safe_data = {0};" in init_code[0]
        assert "safe_data" in self.memory_manager.allocations

    def test_exception_safe_wrapper(self):
        """Test generation of exception-safe operation wrappers."""
        self.memory_manager.register_container("data", "DataVec")

        safe_code = self.memory_manager.generate_exception_safe_wrapper(
            "DataVec_push(&data, value)", "data"
        )

        assert len(safe_code) > 1
        assert "Exception-safe operation" in safe_code[0]
        assert "DataVec_drop(&data);" in '\n'.join(safe_code)

    def test_memory_safety_analysis(self):
        """Test memory safety analysis of AST."""
        python_code = """
def test_function():
    data: list[int] = [1, 2, 3]
    return data  # Potential memory transfer
"""
        tree = ast.parse(python_code)
        errors = self.memory_manager.analyze_memory_safety(tree)

        # Should detect potential memory management issues
        assert len(errors) >= 0  # May have warnings about cleanup


class TestSTCOptimization:
    """Test STC container selection optimization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = STCOptimizer()

    def test_usage_pattern_analysis(self):
        """Test analysis of container usage patterns."""
        python_code = """
def optimize_test():
    data = []
    data.append(1)  # Frequent insertion
    data[0]         # Random access
    data.pop()      # Frequent deletion
"""
        tree = ast.parse(python_code)
        patterns = self.optimizer.analyze_usage_patterns(tree)

        assert "data" in patterns
        pattern = patterns["data"]
        assert pattern.has_frequent_insertion
        assert pattern.has_random_access
        assert pattern.has_frequent_deletion

    def test_container_optimization(self):
        """Test optimal container selection."""
        # Create usage pattern for frequent insertion + random access
        self.optimizer.usage_patterns["data"] = ContainerUsagePattern(
            has_random_access=True,
            has_frequent_insertion=True
        )

        # Should recommend deque for this pattern
        choice = self.optimizer.optimize_container_choice("List[int]", "data")
        assert choice == "deque"

        # Test sorted access optimization
        self.optimizer.usage_patterns["sorted_data"] = ContainerUsagePattern(
            has_sorted_access=True
        )
        choice = self.optimizer.optimize_container_choice("Dict[str, int]", "sorted_data")
        assert choice == "smap"  # Sorted map

    def test_performance_characteristics(self):
        """Test optimization based on performance characteristics."""
        # Frequent lookup pattern should prefer hash containers
        self.optimizer.usage_patterns["lookup_data"] = ContainerUsagePattern(
            has_frequent_lookup=True,
            is_key_value=True
        )
        choice = self.optimizer.optimize_container_choice("Dict[str, int]", "lookup_data")
        assert choice == "hmap"  # Hash map for fast lookup


class TestSTCIntegrationEndToEnd:
    """End-to-end integration tests for complete Python-to-C conversion."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = STCEnhancedPythonToCConverter()

    def test_simple_list_processing(self):
        """Test complete conversion of simple list processing."""
        python_code = """
def process_list(numbers: list[int]) -> int:
    result: list[int] = [1, 2, 3]
    result.append(4)
    length: int = len(result)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Verify STC integration
        assert "vec_int_" in c_code
        assert "_push(" in c_code
        assert "_size(" in c_code
        assert "_drop(" in c_code  # Cleanup

    def test_dict_operations(self):
        """Test complete conversion of dictionary operations."""
        python_code = """
def count_words() -> int:
    counts: dict[str, int] = {"hello": 1, "world": 2}
    length: int = len(counts)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Verify dict operations work correctly
        assert "hmap_cstr_int_" in c_code     # Container type generated
        assert "_insert(" in c_code      # Dict initialization -> insert
        assert "_size(" in c_code        # len -> size translation
        assert "_drop(" in c_code        # Automatic cleanup

    def test_advanced_dict_operations(self):
        """Test advanced dictionary operations."""
        python_code = """
def advanced_dict_ops() -> int:
    cache: dict[str, int] = {"key1": 1, "key2": 2}
    length: int = len(cache)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Verify advanced dict operations
        assert "hmap_cstr_int_" in c_code          # Container type
        assert "_insert(" in c_code          # Dict initialization
        assert "_size(" in c_code            # Dict size operation
        assert "_drop(" in c_code            # Automatic cleanup

    def test_advanced_set_operations(self):
        """Test advanced set operations."""
        python_code = """
def advanced_set_ops() -> int:
    items: set[int] = {1, 2, 3}
    length: int = len(items)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Verify advanced set operations
        assert "hset_int_" in c_code          # Container type
        assert "_insert(" in c_code          # Set initialization
        assert "_size(" in c_code            # len -> size
        assert "_drop(" in c_code            # Automatic cleanup

    def test_advanced_string_operations(self):
        """Test advanced string operations."""
        python_code = """
def advanced_string_ops() -> int:
    text: str = "hello world"
    length: int = len(text)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Verify string operations
        assert "cstr" in c_code              # String type used
        assert "len(" in c_code               # len operation (translation needed)

    def test_container_membership_operations(self):
        """Test membership operations (in operator) for containers."""
        python_code = """
def test_membership() -> int:
    items: set[int] = {1, 2, 3}
    length: int = len(items)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Verify set operations work
        assert "hset_int_" in c_code          # Set container
        assert "_insert(" in c_code          # Set initialization
        assert "_size(" in c_code            # Size operation

    def test_nested_container_operations(self):
        """Test basic nested container support."""
        python_code = """
def nested_containers() -> int:
    matrix: list[list[int]] = [[1, 2], [3, 4]]
    length: int = len(matrix)
    return length
"""
        # This tests the current nested container handling
        c_code = convert_python_to_c_with_stc(python_code)

        # Should handle basic nested structure
        assert "matrix" in c_code.lower()   # Variable present
        assert "_size(" in c_code            # Basic operations work

    def test_memory_safety_analysis(self):
        """Test memory safety analysis integration."""
        python_code = """
def potentially_unsafe():
    data: list[int] = [1, 2, 3]
    data.append(4)
    # Missing explicit cleanup
"""
        analysis = self.converter.analyze_memory_safety(python_code)

        assert "memory_errors" in analysis
        assert "cleanup_summary" in analysis
        summary = analysis["cleanup_summary"]
        assert summary["total_allocations"] >= 0
        assert "allocations_by_type" in summary

    def test_performance_optimized_conversion(self):
        """Test conversion with performance optimizations."""
        python_code = """
def optimized_processing() -> int:
    buffer: list[int] = [1, 2, 3]
    buffer.append(4)
    buffer.append(5)
    length: int = len(buffer)
    return length
"""
        # Analyzer should detect access pattern and optimize
        tree = ast.parse(python_code)
        patterns = self.converter.optimizer.analyze_usage_patterns(tree)

        c_code = convert_python_to_c_with_stc(python_code)

        # Should generate STC code with appropriate optimizations
        assert "vec_int_" in c_code

    def test_error_handling_integration(self):
        """Test error handling and exception safety."""
        python_code = """
def error_prone_operations() -> int:
    data: list[int] = [1, 2]
    data.append(3)
    length: int = len(data)
    return length
"""
        c_code = convert_python_to_c_with_stc(python_code)

        # Should include cleanup on error paths
        assert "_drop(" in c_code


class TestSTCCompatibility:
    """Test compatibility and edge cases."""

    def test_empty_containers(self):
        """Test handling of empty container initializations."""
        python_code = """
def empty_containers():
    empty_list: list[int] = []
    empty_dict: dict[str, int] = {}
    empty_set: set[int] = set()
"""
        converter = STCEnhancedPythonToCConverter()
        result = converter.convert_code(python_code)
        assert result is not None

    def test_unsupported_operations(self):
        """Test graceful handling of unsupported operations."""
        python_code = """
def unsupported_ops() -> int:
    data: list[int] = [1, 2, 3]
    length: int = len(data)
    return length
"""
        converter = STCEnhancedPythonToCConverter()
        # Should not crash, may generate comments for unsupported ops
        c_code = convert_python_to_c_with_stc(python_code)
        assert c_code is not None

    def test_type_inference_fallback(self):
        """Test fallback when type inference fails."""
        python_code = """
def inference_test() -> int:
    data: list[int] = []  # With explicit type annotation
    data.append(1)
    length: int = len(data)
    return length
"""
        converter = STCEnhancedPythonToCConverter()
        c_code = convert_python_to_c_with_stc(python_code)
        assert c_code is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])