#!/usr/bin/env python3
"""
Smart Pointers and Memory Allocators Demo

This demo showcases the advanced memory management capabilities of CGen
including smart pointers, custom allocators, and memory safety analysis.

Features Demonstrated:
- Smart pointer types (unique_ptr, shared_ptr, weak_ptr)
- Custom allocators (arena, pool, stack allocators)
- Memory safety analysis and cycle detection
- Performance optimization recommendations
- Integration with STC containers
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from cgen.ext.stc.smart_pointers import (
    SmartPointerManager, SmartPointerType, SMART_POINTER_SPECS
)
from cgen.ext.stc.allocators import (
    MemoryAllocatorManager, AllocatorType, ALLOCATOR_SPECS
)
from cgen.ext.stc.enhanced_memory_manager import (
    EnhancedMemoryManager, ResourceType
)
from cgen.ext.stc.enhanced_translator import EnhancedSTCTranslator


def demo_smart_pointers():
    """Demonstrate smart pointer functionality."""
    print("🧠 SMART POINTERS DEMONSTRATION")
    print("=" * 60)

    manager = SmartPointerManager()

    print("\n1. Smart Pointer Types and Specifications:")
    for pointer_type, spec in SMART_POINTER_SPECS.items():
        print(f"   • {pointer_type.value}: {spec.description}")
        print(f"     Header: {spec.header_file}")
        print(f"     Thread-safe: {spec.thread_safe}")
        print()

    print("2. Smart Pointer Registration and Type Generation:")

    # Register different types of smart pointers
    unique_alloc = manager.register_smart_pointer(
        "unique_data", SmartPointerType.UNIQUE, "DataNode", 10
    )
    print(f"   ✓ Registered unique_ptr: {unique_alloc.name}")

    shared_alloc = manager.register_smart_pointer(
        "shared_tree", SmartPointerType.SHARED, "TreeNode", 15
    )
    print(f"   ✓ Registered shared_ptr: {shared_alloc.name}")

    weak_alloc = manager.register_smart_pointer(
        "weak_ref", SmartPointerType.WEAK, "TreeNode", 20
    )
    print(f"   ✓ Registered weak_ptr: {weak_alloc.name}")

    # Generate type definitions
    print("\n3. Generated C Type Definitions:")
    for name, allocation in manager.allocations.items():
        type_def, include = manager.generate_smart_pointer_type_def(allocation)
        print(f"   {name}:")
        print(f"     Include: {include}")
        print(f"     Type def: {type_def}")
        print()

    print("4. Smart Pointer Operations:")

    # Generate operations
    operations = [
        ("reset", ["NULL"]),
        ("get", []),
        ("operator bool", []),
    ]

    for op_name, args in operations:
        op_code = manager.generate_smart_pointer_operation(op_name, "unique_data", args)
        print(f"   {op_name}: {op_code}")

    print("\n5. Factory Functions:")

    # Generate factory functions
    make_unique = manager.generate_make_smart_pointer(
        SmartPointerType.UNIQUE, "DataNode", ["42", "\"test\""]
    )
    print(f"   make_unique: {make_unique}")

    make_shared = manager.generate_make_smart_pointer(
        SmartPointerType.SHARED, "TreeNode", ["data", "left", "right"]
    )
    print(f"   make_shared: {make_shared}")

    print("\n6. Reference Cycle Detection:")

    # Create a reference cycle for demonstration
    manager.register_smart_pointer("nodeA", SmartPointerType.SHARED, "Node")
    manager.register_smart_pointer("nodeB", SmartPointerType.SHARED, "Node")
    manager.register_smart_pointer("nodeC", SmartPointerType.SHARED, "Node")

    # Create cycle: A -> B -> C -> A
    manager.reference_graph["nodeA"] = {"nodeB"}
    manager.reference_graph["nodeB"] = {"nodeC"}
    manager.reference_graph["nodeC"] = {"nodeA"}

    cycles = manager.detect_reference_cycles()
    if cycles:
        print(f"   ⚠️  Detected {len(cycles)} reference cycle(s):")
        for i, cycle in enumerate(cycles):
            print(f"     Cycle {i + 1}: {' → '.join(cycle)}")
    else:
        print("   ✓ No reference cycles detected")

    print("\n7. Cleanup Code Generation:")
    for name in ["unique_data", "shared_tree", "weak_ref"]:
        cleanup = manager.generate_cleanup_code(name)
        print(f"   {name}: {cleanup}")

    print("\n" + "=" * 60)


def demo_memory_allocators():
    """Demonstrate memory allocator functionality."""
    print("\n🏗️  MEMORY ALLOCATORS DEMONSTRATION")
    print("=" * 60)

    manager = MemoryAllocatorManager()

    print("\n1. Allocator Types and Specifications:")
    for allocator_type, spec in ALLOCATOR_SPECS.items():
        print(f"   • {allocator_type.value}: {spec.description}")
        print(f"     Header: {spec.header_file}")
        print(f"     Thread-safe: {spec.thread_safe}")
        print(f"     Container-suitable: {spec.suitable_for_containers}")
        print()

    print("2. Allocator Registration and Setup:")

    # Register different types of allocators
    arena = manager.register_allocator(
        "fast_arena", AllocatorType.ARENA, block_size=4096
    )
    print(f"   ✓ Registered arena allocator: {arena.name} (block_size: {arena.block_size})")

    pool = manager.register_allocator(
        "node_pool", AllocatorType.POOL, block_size=64, pool_size=1000
    )
    print(f"   ✓ Registered pool allocator: {pool.name} (block: {pool.block_size}, pool: {pool.pool_size})")

    stack = manager.register_allocator(
        "temp_stack", AllocatorType.STACK, block_size=2048
    )
    print(f"   ✓ Registered stack allocator: {stack.name} (block_size: {stack.block_size})")

    free_list = manager.register_allocator(
        "general_heap", AllocatorType.FREE_LIST, alignment=16
    )
    print(f"   ✓ Registered free-list allocator: {free_list.name} (alignment: {free_list.alignment})")

    print("\n3. Generated Allocator Setup Code:")
    for name, instance in manager.allocators.items():
        init_code, include = manager.generate_allocator_setup(instance)
        print(f"   {name}:")
        print(f"     Include: {include}")
        print(f"     Init: {init_code}")
        print()

    print("4. Container-Allocator Binding:")

    # Bind containers to allocators
    bindings = [
        ("vector_data", "fast_arena"),
        ("node_list", "node_pool"),
        ("temp_buffer", "temp_stack"),
        ("general_data", "general_heap")
    ]

    for container, allocator in bindings:
        manager.bind_container_to_allocator(container, allocator)
        print(f"   ✓ Bound {container} to {allocator}")

        # Generate container with allocator
        type_def, include = manager.generate_container_with_allocator(
            container, "Vec", "int"
        )
        if type_def:
            print(f"     Type def: {type_def}")

    print("\n5. Allocation Tracking and Statistics:")

    # Track some allocations
    allocations = [
        ("var1", "fast_arena", 1024, "DataStruct"),
        ("var2", "node_pool", 64, "TreeNode"),
        ("var3", "temp_stack", 256, "TempData"),
        ("var4", "general_heap", 512, "Buffer")
    ]

    for var_name, allocator_name, size, element_type in allocations:
        manager.track_allocation(var_name, allocator_name, size, element_type)
        print(f"   ✓ Tracked allocation: {var_name} ({size} bytes) in {allocator_name}")

    print("\n6. Allocation Pattern Analysis:")
    analysis = manager.analyze_allocation_patterns()

    print(f"   Total allocations: {analysis['total_allocations']}")
    print(f"   Total memory: {analysis['total_memory']} bytes")

    for allocator_name, allocator_data in analysis['allocators'].items():
        print(f"\n   {allocator_name}:")
        print(f"     Type: {allocator_data['type']}")
        print(f"     Allocations: {allocator_data['allocation_count']}")
        print(f"     Total size: {allocator_data['total_size']} bytes")
        print(f"     Average size: {allocator_data['average_size']:.1f} bytes")
        print(f"     Fragmentation risk: {allocator_data['fragmentation_risk']}")

    print("\n7. Optimization Recommendations:")
    for recommendation in analysis['recommendations']:
        print(f"   💡 {recommendation}")

    print("\n" + "=" * 60)


def demo_enhanced_memory_manager():
    """Demonstrate enhanced memory manager integration."""
    print("\n🔧 ENHANCED MEMORY MANAGER DEMONSTRATION")
    print("=" * 60)

    manager = EnhancedMemoryManager()

    print("\n1. Unified Resource Management:")

    # Register various types of resources
    arena_alloc = manager.register_allocator("arena", AllocatorType.ARENA, block_size=4096)
    print(f"   ✓ Registered arena allocator: {arena_alloc.name}")

    container_res = manager.register_container_with_allocator(
        "data_vector", "Vec", "int", allocator_name="arena"
    )
    print(f"   ✓ Registered container with allocator: {container_res.name}")

    smart_ptr_res = manager.register_smart_pointer(
        "smart_data", SmartPointerType.SHARED, "DataNode"
    )
    print(f"   ✓ Registered smart pointer: {smart_ptr_res.name}")

    print(f"\n   Total resources managed: {len(manager.resources)}")

    print("\n2. Resource Dependency Tracking:")

    # Create more resources for dependency demo
    manager.register_smart_pointer("parent", SmartPointerType.SHARED, "TreeNode")
    manager.register_smart_pointer("child1", SmartPointerType.SHARED, "TreeNode")
    manager.register_smart_pointer("child2", SmartPointerType.SHARED, "TreeNode")

    # Create dependencies
    manager.track_resource_dependency("parent", "child1")
    manager.track_resource_dependency("parent", "child2")

    print("   ✓ Created parent-child dependencies")

    # Create a potential cycle
    manager.register_smart_pointer("nodeX", SmartPointerType.SHARED, "Node")
    manager.register_smart_pointer("nodeY", SmartPointerType.SHARED, "Node")
    manager.track_resource_dependency("nodeX", "nodeY")
    manager.track_resource_dependency("nodeY", "nodeX")

    print("   ⚠️  Created potential cycle: nodeX ↔ nodeY")

    print("\n3. Memory Safety Analysis:")

    issues = manager.detect_memory_issues()
    print(f"   Detected {len(issues)} potential memory issues:")

    for issue in issues:
        severity_icon = "🔴" if issue.severity == "error" else "🟡" if issue.severity == "warning" else "ℹ️"
        print(f"   {severity_icon} {issue.error_type}: {issue.message}")

    print("\n4. Initialization Code Generation:")

    includes, init_code = manager.generate_initialization_code()

    print("   Generated includes:")
    for include in includes:
        print(f"     {include}")

    print("\n   Generated initialization code:")
    for code in init_code:
        print(f"     {code}")

    print("\n5. Cleanup Code Generation:")

    cleanup_code = manager.generate_cleanup_code()
    print("   Generated cleanup code:")
    for cleanup in cleanup_code:
        print(f"     {cleanup}")

    print("\n6. Performance Analysis:")

    analysis = manager.analyze_performance()

    print("   Performance Metrics:")
    metrics = analysis['metrics']
    for metric, value in metrics.items():
        print(f"     {metric}: {value}")

    print("\n   Smart Pointer Analysis:")
    sp_analysis = analysis['smart_pointer_analysis']
    for key, value in sp_analysis.items():
        print(f"     {key}: {value}")

    print("\n   Optimization Recommendations:")
    for recommendation in analysis['optimization_recommendations']:
        print(f"     💡 {recommendation}")

    print("\n7. Move Semantics:")

    # Demonstrate move semantics
    manager.register_smart_pointer("source_ptr", SmartPointerType.UNIQUE, "Resource")
    manager.register_smart_pointer("dest_ptr", SmartPointerType.UNIQUE, "Resource")

    move_code = manager.generate_move_semantics("source_ptr", "dest_ptr")
    if move_code:
        print("   Generated move semantics:")
        for code in move_code:
            print(f"     {code}")

        # Check if source is marked as moved
        source_resource = manager.resources["source_ptr"]
        print(f"   Source moved: {source_resource.is_moved}")

    print("\n" + "=" * 60)


def demo_integration_scenarios():
    """Demonstrate real-world integration scenarios."""
    print("\n🌟 INTEGRATION SCENARIOS DEMONSTRATION")
    print("=" * 60)

    manager = EnhancedMemoryManager()

    print("\n1. Game Engine Memory Management Scenario:")

    # Game engine allocators
    manager.register_allocator("frame_arena", AllocatorType.ARENA, block_size=1024*1024)  # 1MB frames
    manager.register_allocator("entity_pool", AllocatorType.POOL, block_size=128, pool_size=10000)  # Entities
    manager.register_allocator("audio_stack", AllocatorType.STACK, block_size=64*1024)  # Audio buffers

    print("   ✓ Registered game engine allocators")

    # Game objects with smart pointers
    manager.register_smart_pointer("player", SmartPointerType.UNIQUE, "Player")
    manager.register_smart_pointer("camera", SmartPointerType.SHARED, "Camera")
    manager.register_smart_pointer("scene_graph", SmartPointerType.SHARED, "SceneNode")

    print("   ✓ Registered game objects with smart pointers")

    # Containers with custom allocators
    manager.register_container_with_allocator("entities", "Vec", "Entity", "entity_pool")
    manager.register_container_with_allocator("frame_data", "Vec", "RenderCommand", "frame_arena")
    manager.register_container_with_allocator("audio_buffers", "Vec", "AudioSample", "audio_stack")

    print("   ✓ Registered game containers with appropriate allocators")

    print("\n2. Database Connection Pool Scenario:")

    # Database allocators
    manager.register_allocator("connection_pool", AllocatorType.POOL, block_size=256, pool_size=100)
    manager.register_allocator("query_arena", AllocatorType.ARENA, block_size=4096)

    # Database objects
    manager.register_smart_pointer("db_connection", SmartPointerType.SHARED, "DBConnection")
    manager.register_container_with_allocator("connection_pool_vec", "Vec", "DBConnection", "connection_pool")
    manager.register_container_with_allocator("query_cache", "Map", "QueryResult", "query_arena")

    print("   ✓ Set up database connection pool with optimized allocators")

    print("\n3. Scientific Computing Scenario:")

    # Scientific computing allocators
    manager.register_allocator("matrix_arena", AllocatorType.ARENA, block_size=8*1024*1024)  # 8MB matrices
    manager.register_allocator("vector_pool", AllocatorType.POOL, block_size=1024, pool_size=1000)

    # Scientific objects
    manager.register_container_with_allocator("matrix_data", "Vec", "double", "matrix_arena")
    manager.register_container_with_allocator("vector_cache", "Vec", "Vector3D", "vector_pool")

    print("   ✓ Set up scientific computing memory management")

    print("\n4. Complete Performance Analysis:")

    analysis = manager.analyze_performance()

    print(f"   Total resources: {analysis['metrics']['total_allocations']}")
    print(f"   Smart pointers: {analysis['metrics']['smart_pointer_usage']}")
    print(f"   Custom allocators: {analysis['metrics']['custom_allocator_usage']}")

    allocator_analysis = analysis['allocator_analysis']
    print(f"   Total memory managed: {allocator_analysis['total_memory']} bytes")

    print("\n   Allocator efficiency:")
    for allocator_name, data in allocator_analysis['allocators'].items():
        if data['allocation_count'] > 0:
            print(f"     {allocator_name}: {data['allocation_count']} allocations, "
                  f"{data['total_size']} bytes, "
                  f"fragmentation: {data['fragmentation_risk']}")

    print("\n5. Memory Safety Report:")

    issues = manager.detect_memory_issues()
    if issues:
        print(f"   Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"     {issue.severity.upper()}: {issue.message}")
    else:
        print("   ✅ No memory safety issues detected!")

    print("\n6. Generated System Code:")

    includes, init_code = manager.generate_initialization_code()

    print(f"   Generated {len(includes)} includes and {len(init_code)} initialization statements")
    print("   Sample generated code:")
    for i, code in enumerate(init_code[:3]):  # Show first 3
        print(f"     {i+1}. {code}")
    if len(init_code) > 3:
        print(f"     ... and {len(init_code) - 3} more")

    cleanup_code = manager.generate_cleanup_code()
    print(f"\n   Generated {len(cleanup_code)} cleanup statements")

    print("\n" + "=" * 60)


def main():
    """Run all smart pointer and allocator demonstrations."""
    print("🚀 CGen Smart Pointers and Memory Allocators Demo")
    print("=" * 70)
    print("Showcasing advanced memory management capabilities:")
    print("• C++ style smart pointers with RAII semantics")
    print("• High-performance custom memory allocators")
    print("• Automatic memory safety analysis")
    print("• Reference cycle detection and prevention")
    print("• Performance optimization recommendations")
    print("• Integration with STC containers")
    print("=" * 70)

    try:
        # Run all demonstrations
        demo_smart_pointers()
        demo_memory_allocators()
        demo_enhanced_memory_manager()
        demo_integration_scenarios()

        # Summary
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("✅ Smart Pointer Features:")
        print("   • unique_ptr, shared_ptr, weak_ptr, scoped_ptr")
        print("   • Reference cycle detection")
        print("   • Automatic cleanup generation")
        print("   • Move semantics support")
        print()
        print("✅ Memory Allocator Features:")
        print("   • Arena, Pool, Stack, Free-list allocators")
        print("   • Container-allocator binding")
        print("   • Allocation pattern analysis")
        print("   • Performance optimization recommendations")
        print()
        print("✅ Enhanced Memory Management:")
        print("   • Unified resource tracking")
        print("   • Dependency graph analysis")
        print("   • Memory safety guarantees")
        print("   • Real-world scenario optimization")
        print()
        print("🔥 Ready for production C code generation with advanced memory management!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error in demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)