"""
Comprehensive tests for smart pointers and memory allocators.

Tests cover:
- Smart pointer operations and memory safety
- Custom allocator functionality
- Integration with STC containers
- Memory leak detection
- Reference cycle detection
- Performance optimization
"""

import pytest
from unittest.mock import Mock, patch

from src.cgen.ext.stc.smart_pointers import (
    SmartPointerManager, SmartPointerType, SmartPointerAllocation, SMART_POINTER_SPECS
)
from src.cgen.ext.stc.allocators import (
    MemoryAllocatorManager, AllocatorType, AllocatorInstance, ALLOCATOR_SPECS
)
from src.cgen.ext.stc.enhanced_memory_manager import (
    EnhancedMemoryManager, ResourceType, ResourceAllocation
)
from src.cgen.ext.stc.enhanced_translator import EnhancedSTCTranslator


class TestSmartPointerManager:
    """Test smart pointer management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SmartPointerManager()

    def test_unique_ptr_registration(self):
        """Test unique_ptr registration and tracking."""
        allocation = self.manager.register_smart_pointer(
            "ptr", SmartPointerType.UNIQUE, "int", 10
        )

        assert allocation.name == "ptr"
        assert allocation.pointer_type == SmartPointerType.UNIQUE
        assert allocation.element_type == "int"
        assert allocation.line_number == 10
        assert "ptr" in self.manager.allocations

    def test_shared_ptr_registration(self):
        """Test shared_ptr registration and reference counting."""
        allocation = self.manager.register_smart_pointer(
            "shared", SmartPointerType.SHARED, "string", 15
        )

        assert allocation.pointer_type == SmartPointerType.SHARED
        assert "shared" in self.manager.shared_references
        assert self.manager.shared_references["shared"] == 1

    def test_weak_ptr_registration(self):
        """Test weak_ptr registration."""
        allocation = self.manager.register_smart_pointer(
            "weak", SmartPointerType.WEAK, "int", 20
        )

        assert allocation.pointer_type == SmartPointerType.WEAK
        assert "weak" in self.manager.allocations

    def test_smart_pointer_type_definition_generation(self):
        """Test generation of smart pointer type definitions."""
        allocation = self.manager.register_smart_pointer(
            "test_ptr", SmartPointerType.UNIQUE, "double"
        )

        type_def, include = self.manager.generate_smart_pointer_type_def(allocation)

        assert include == "#include <stc/unique_ptr.h>"
        assert "unique_ptr_double" in type_def
        assert "double" in type_def

    def test_smart_pointer_operations(self):
        """Test smart pointer operation generation."""
        self.manager.register_smart_pointer(
            "ptr", SmartPointerType.UNIQUE, "int"
        )

        # Test reset operation
        reset_op = self.manager.generate_smart_pointer_operation("reset", "ptr", ["NULL"])
        assert "reset" in reset_op
        assert "ptr" in reset_op

        # Test get operation
        get_op = self.manager.generate_smart_pointer_operation("get", "ptr")
        assert "get" in get_op

    def test_make_smart_pointer_generation(self):
        """Test make_unique and make_shared generation."""
        # Test make_unique
        make_unique = self.manager.generate_make_smart_pointer(
            SmartPointerType.UNIQUE, "int", ["42"]
        )
        assert "make_unique_int(42)" == make_unique

        # Test make_shared
        make_shared = self.manager.generate_make_smart_pointer(
            SmartPointerType.SHARED, "string", ["\"hello\""]
        )
        assert "make_shared_string(\"hello\")" == make_shared

    def test_reference_cycle_detection(self):
        """Test detection of reference cycles in smart pointers."""
        # Create a cycle: A -> B -> C -> A
        self.manager.register_smart_pointer("ptrA", SmartPointerType.SHARED, "NodeA")
        self.manager.register_smart_pointer("ptrB", SmartPointerType.SHARED, "NodeB")
        self.manager.register_smart_pointer("ptrC", SmartPointerType.SHARED, "NodeC")

        # Create cycle in reference graph
        self.manager.reference_graph["ptrA"] = {"ptrB"}
        self.manager.reference_graph["ptrB"] = {"ptrC"}
        self.manager.reference_graph["ptrC"] = {"ptrA"}

        cycles = self.manager.detect_reference_cycles()
        assert len(cycles) > 0
        # Should detect the cycle A -> B -> C -> A

    def test_assignment_tracking(self):
        """Test smart pointer assignment tracking."""
        self.manager.register_smart_pointer("src", SmartPointerType.SHARED, "int")
        self.manager.register_smart_pointer("dst", SmartPointerType.SHARED, "int")

        self.manager.track_assignment("dst", "src")

        assert "src" in self.manager.reference_graph["dst"]
        assert self.manager.shared_references["src"] == 2  # Original + assignment

    def test_cleanup_code_generation(self):
        """Test cleanup code generation for smart pointers."""
        self.manager.register_smart_pointer("ptr", SmartPointerType.UNIQUE, "int")

        cleanup = self.manager.generate_cleanup_code("ptr")
        assert len(cleanup) > 0
        assert "reset" in cleanup[0] or "drop" in cleanup[0]

    def test_move_semantics(self):
        """Test move semantics for unique_ptr."""
        self.manager.register_smart_pointer("src", SmartPointerType.UNIQUE, "int")
        self.manager.register_smart_pointer("dst", SmartPointerType.UNIQUE, "int")

        move_code = self.manager.generate_move_semantics("src", "dst")
        assert len(move_code) > 0
        assert "move" in move_code[0]

    def test_custom_deleter_support(self):
        """Test smart pointers with custom deleters."""
        allocation = self.manager.register_smart_pointer(
            "ptr", SmartPointerType.UNIQUE, "FILE",
            custom_deleter="fclose_deleter"
        )

        assert allocation.custom_deleter == "fclose_deleter"

        type_def, include = self.manager.generate_smart_pointer_type_def(allocation)
        assert "fclose_deleter" in type_def


class TestMemoryAllocatorManager:
    """Test memory allocator management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = MemoryAllocatorManager()

    def test_arena_allocator_registration(self):
        """Test arena allocator registration."""
        instance = self.manager.register_allocator(
            "arena", AllocatorType.ARENA, block_size=4096
        )

        assert instance.name == "arena"
        assert instance.allocator_type == AllocatorType.ARENA
        assert instance.block_size == 4096
        assert "arena" in self.manager.allocators

    def test_pool_allocator_registration(self):
        """Test pool allocator registration."""
        instance = self.manager.register_allocator(
            "pool", AllocatorType.POOL, block_size=64, pool_size=1000
        )

        assert instance.allocator_type == AllocatorType.POOL
        assert instance.block_size == 64
        assert instance.pool_size == 1000

    def test_allocator_setup_generation(self):
        """Test allocator setup code generation."""
        instance = self.manager.register_allocator(
            "test_arena", AllocatorType.ARENA, block_size=2048
        )

        init_code, include = self.manager.generate_allocator_setup(instance)

        assert include == "#include <stc/arena_alloc.h>"
        assert "arena_alloc_test_arena" in init_code
        assert "2048" in init_code

    def test_container_allocator_binding(self):
        """Test binding containers to allocators."""
        self.manager.register_allocator("custom", AllocatorType.POOL)
        self.manager.bind_container_to_allocator("my_vector", "custom")

        assert self.manager.container_allocators["my_vector"] == "custom"

    def test_allocation_tracking(self):
        """Test allocation tracking and statistics."""
        self.manager.register_allocator("tracker", AllocatorType.ARENA)

        self.manager.track_allocation("var1", "tracker", 100, "int")
        self.manager.track_allocation("var2", "tracker", 200, "double")

        allocations = self.manager.allocations["tracker"]
        assert len(allocations) == 2

        stats = self.manager.allocation_stats["tracker"]
        assert stats["total_allocations"] == 2
        assert stats["total_size"] == 300

    def test_allocation_code_generation(self):
        """Test allocation code generation."""
        self.manager.register_allocator("arena", AllocatorType.ARENA)

        alloc_code = self.manager.generate_allocation_code(
            "arena", "ptr", "sizeof(int) * 10", "int"
        )

        assert "arena_alloc_arena_alloc" in alloc_code
        assert "sizeof(int) * 10" in alloc_code

    def test_deallocation_code_generation(self):
        """Test deallocation code generation."""
        self.manager.register_allocator("pool", AllocatorType.POOL)

        dealloc_code = self.manager.generate_deallocation_code("pool", "ptr")

        assert "pool_alloc_pool_free" in dealloc_code
        assert "ptr" in dealloc_code

    def test_allocator_cleanup(self):
        """Test allocator cleanup code generation."""
        self.manager.register_allocator("arena", AllocatorType.ARENA)

        cleanup = self.manager.generate_allocator_cleanup("arena")
        assert len(cleanup) > 0
        assert any("clear" in line for line in cleanup)
        assert any("drop" in line for line in cleanup)

    def test_allocation_pattern_analysis(self):
        """Test allocation pattern analysis."""
        self.manager.register_allocator("analyzer", AllocatorType.FREE_LIST)

        # Add some test allocations
        for i in range(5):
            self.manager.track_allocation(f"var{i}", "analyzer", i * 10, "int")

        analysis = self.manager.analyze_allocation_patterns()

        assert "allocators" in analysis
        assert "analyzer" in analysis["allocators"]
        assert analysis["allocators"]["analyzer"]["allocation_count"] == 5

    def test_optimization_recommendations(self):
        """Test generation of optimization recommendations."""
        # Create allocator with many small allocations
        self.manager.register_allocator("inefficient", AllocatorType.SYSTEM)

        for i in range(60):  # Many allocations
            self.manager.track_allocation(f"small{i}", "inefficient", 32, "int")

        analysis = self.manager.analyze_allocation_patterns()
        recommendations = analysis["recommendations"]

        assert len(recommendations) > 0
        assert any("custom allocator" in rec for rec in recommendations)


class TestEnhancedMemoryManager:
    """Test enhanced memory management integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = EnhancedMemoryManager()

    def test_container_with_allocator_registration(self):
        """Test container registration with custom allocator."""
        # Register allocator first
        self.manager.register_allocator("fast_arena", AllocatorType.ARENA, block_size=4096)

        # Register container with allocator
        resource = self.manager.register_container_with_allocator(
            "data", "Vec", "int", allocator_name="fast_arena"
        )

        assert resource.name == "data"
        assert resource.resource_type == ResourceType.CONTAINER
        assert resource.allocator == "fast_arena"
        assert "data" in self.manager.resources

    def test_smart_pointer_registration(self):
        """Test smart pointer registration in enhanced manager."""
        resource = self.manager.register_smart_pointer(
            "smart", SmartPointerType.SHARED, "string"
        )

        assert resource.resource_type == ResourceType.SMART_POINTER
        assert "shared_ptr<string>" in resource.data_type

    def test_dependency_tracking(self):
        """Test resource dependency tracking."""
        self.manager.register_smart_pointer("ptr1", SmartPointerType.SHARED, "Node")
        self.manager.register_smart_pointer("ptr2", SmartPointerType.SHARED, "Node")

        self.manager.track_resource_dependency("ptr1", "ptr2")

        assert "ptr2" in self.manager.resources["ptr1"].dependencies
        assert "ptr2" in self.manager.dependency_graph["ptr1"]

    def test_cycle_detection(self):
        """Test dependency cycle detection."""
        # Create resources
        self.manager.register_smart_pointer("a", SmartPointerType.SHARED, "Node")
        self.manager.register_smart_pointer("b", SmartPointerType.SHARED, "Node")
        self.manager.register_smart_pointer("c", SmartPointerType.SHARED, "Node")

        # Create cycle: a -> b -> c -> a
        self.manager.track_resource_dependency("a", "b")
        self.manager.track_resource_dependency("b", "c")
        self.manager.track_resource_dependency("c", "a")

        cycles = self.manager._detect_dependency_cycles()
        assert len(cycles) > 0

    def test_memory_issue_detection(self):
        """Test comprehensive memory issue detection."""
        # Create some resources with potential issues
        self.manager.register_container_with_allocator("leak_prone", "Vec", "int")
        self.manager.register_smart_pointer("cycle1", SmartPointerType.SHARED, "Node")
        self.manager.register_smart_pointer("cycle2", SmartPointerType.SHARED, "Node")

        # Create cycle
        self.manager.track_resource_dependency("cycle1", "cycle2")
        self.manager.track_resource_dependency("cycle2", "cycle1")

        issues = self.manager.detect_memory_issues()
        assert len(issues) > 0

    def test_initialization_code_generation(self):
        """Test initialization code generation."""
        self.manager.register_allocator("arena", AllocatorType.ARENA)
        self.manager.register_smart_pointer("ptr", SmartPointerType.UNIQUE, "int")

        includes, init_code = self.manager.generate_initialization_code()

        assert len(includes) > 0
        assert len(init_code) > 0
        assert any("arena" in include for include in includes)
        assert any("unique_ptr" in include for include in includes)

    def test_cleanup_code_generation(self):
        """Test cleanup code generation."""
        self.manager.register_container_with_allocator("vec", "Vec", "int")
        self.manager.register_smart_pointer("ptr", SmartPointerType.UNIQUE, "double")

        cleanup_code = self.manager.generate_cleanup_code()
        assert len(cleanup_code) > 0

    def test_move_semantics_generation(self):
        """Test move semantics code generation."""
        self.manager.register_smart_pointer("src", SmartPointerType.UNIQUE, "int")
        self.manager.register_smart_pointer("dst", SmartPointerType.UNIQUE, "int")

        move_code = self.manager.generate_move_semantics("src", "dst")
        assert len(move_code) > 0
        assert self.manager.resources["src"].is_moved

    def test_performance_analysis(self):
        """Test performance analysis and recommendations."""
        # Create various resources
        self.manager.register_allocator("arena", AllocatorType.ARENA)
        self.manager.register_smart_pointer("ptr1", SmartPointerType.SHARED, "int")
        self.manager.register_smart_pointer("ptr2", SmartPointerType.UNIQUE, "double")
        self.manager.register_container_with_allocator("vec", "Vec", "int", "arena")

        analysis = self.manager.analyze_performance()

        assert "metrics" in analysis
        assert "allocator_analysis" in analysis
        assert "smart_pointer_analysis" in analysis
        assert "optimization_recommendations" in analysis

    def test_scope_management(self):
        """Test scope entry and exit."""
        # Enter scope
        self.manager.enter_scope()

        # Register resource in scope
        self.manager.register_smart_pointer("scoped", SmartPointerType.UNIQUE, "int")

        # Exit scope
        cleanup = self.manager.exit_scope()
        assert len(cleanup) > 0


class TestEnhancedSTCTranslator:
    """Test enhanced STC translator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.translator = EnhancedSTCTranslator()

    def test_smart_pointer_syntax_recognition(self):
        """Test recognition of smart pointer syntax."""
        # Test smart pointer syntax mapping
        assert self.translator.smart_pointer_syntax["unique_ptr"] == SmartPointerType.UNIQUE
        assert self.translator.smart_pointer_syntax["shared_ptr"] == SmartPointerType.SHARED

    def test_allocator_syntax_recognition(self):
        """Test recognition of allocator syntax."""
        # Test allocator syntax mapping
        assert self.translator.allocator_syntax["arena_alloc"] == AllocatorType.ARENA
        assert self.translator.allocator_syntax["pool_alloc"] == AllocatorType.POOL

    def test_type_extraction(self):
        """Test element type extraction from annotations."""
        # Test smart pointer type extraction
        element_type = self.translator._extract_element_type_from_annotation("unique_ptr[int]")
        assert element_type == "int"

        # Test container type extraction
        container_type = self.translator._extract_container_type_from_annotation("list[string]")
        assert container_type == "list"

    def test_enhanced_type_definition_generation(self):
        """Test enhanced type definition generation."""
        # Mock some type info
        type_info = {
            "smart": "unique_ptr[int]",
            "container": "list[double]",
            "allocator": "arena_alloc"
        }

        # Register the types
        self.translator.smart_pointer_variables["smart"] = SmartPointerType.UNIQUE
        self.translator.allocator_variables["allocator"] = AllocatorType.ARENA

        includes, type_defs = self.translator.generate_enhanced_type_definitions(type_info)

        assert len(includes) > 0
        assert len(type_defs) > 0

    def test_memory_safety_analysis(self):
        """Test comprehensive memory safety analysis."""
        # Create mock AST
        import ast
        code = """
def test_function():
    ptr: unique_ptr[int] = make_unique_int(42)
    data: list[int] = [1, 2, 3]
"""
        tree = ast.parse(code)

        analysis = self.translator.analyze_memory_safety(tree)

        assert "memory_errors" in analysis
        assert "performance_analysis" in analysis
        assert "cleanup_summary" in analysis


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = EnhancedMemoryManager()

    def test_smart_pointer_with_custom_allocator(self):
        """Test smart pointer using custom allocator."""
        # Register custom allocator
        self.manager.register_allocator("custom", AllocatorType.POOL, block_size=64)

        # Register smart pointer with custom allocator
        resource = self.manager.register_smart_pointer(
            "ptr", SmartPointerType.UNIQUE, "MyClass", allocator_name="custom"
        )

        assert resource.allocator == "custom"

        # Generate initialization code
        includes, init_code = self.manager.generate_initialization_code()
        assert len(includes) > 0
        assert len(init_code) > 0

    def test_container_with_smart_pointer_elements(self):
        """Test container holding smart pointers."""
        # Register arena allocator for container
        self.manager.register_allocator("arena", AllocatorType.ARENA)

        # Register container with smart pointer elements
        resource = self.manager.register_container_with_allocator(
            "ptr_vec", "Vec", "unique_ptr[Node]", "arena"
        )

        assert "unique_ptr[Node]" in resource.data_type
        assert resource.allocator == "arena"

    def test_complex_dependency_graph(self):
        """Test complex resource dependency management."""
        # Create multiple allocators
        self.manager.register_allocator("arena1", AllocatorType.ARENA)
        self.manager.register_allocator("pool1", AllocatorType.POOL)

        # Create resources with dependencies
        self.manager.register_smart_pointer("root", SmartPointerType.SHARED, "TreeNode")
        self.manager.register_smart_pointer("left", SmartPointerType.SHARED, "TreeNode")
        self.manager.register_smart_pointer("right", SmartPointerType.SHARED, "TreeNode")

        # Create tree structure
        self.manager.track_resource_dependency("root", "left")
        self.manager.track_resource_dependency("root", "right")

        # Generate cleanup in proper order
        cleanup = self.manager.generate_cleanup_code()
        assert len(cleanup) > 0

    def test_performance_optimization_scenario(self):
        """Test performance optimization recommendations."""
        # Create scenario with suboptimal allocator usage
        for i in range(100):  # Many small allocations
            self.manager.register_container_with_allocator(
                f"small_vec_{i}", "Vec", "int"  # No custom allocator
            )

        analysis = self.manager.analyze_performance()
        recommendations = analysis["optimization_recommendations"]

        # Should recommend custom allocators
        assert len(recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])