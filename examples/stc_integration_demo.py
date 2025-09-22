#!/usr/bin/env python3
"""
STC Integration Demonstration

This script demonstrates the comprehensive STC (Smart Template Containers)
integration in CGen, showing how Python container operations are translated
to high-performance, memory-safe C code using STC containers.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from cgen.core.stc_py2c import STCEnhancedPythonToCConverter, convert_python_to_c_with_stc


def demonstrate_list_operations():
    """Demonstrate Python list to STC vec translation."""
    print("=" * 70)
    print("DEMONSTRATION 1: List Operations (Python → STC vec)")
    print("=" * 70)

    python_code = '''
def process_numbers(input_data: list[int]) -> list[int]:
    """Process a list of numbers with various operations."""
    result: list[int] = []

    # Basic operations
    for num in input_data:
        if num > 0:
            result.append(num * 2)

    # Advanced operations
    result.sort()
    result.reverse()

    # Insert and remove
    result.insert(0, -1)
    if len(result) > 1:
        result.pop()

    return result
'''

    print("Python Source Code:")
    print(python_code)
    print("\n" + "→" * 50 + " CONVERTS TO " + "→" * 50 + "\n")

    c_code = convert_python_to_c_with_stc(python_code)
    print("Generated C Code with STC:")
    print(c_code)
    print("\n")


def demonstrate_dict_operations():
    """Demonstrate Python dict to STC hmap translation."""
    print("=" * 70)
    print("DEMONSTRATION 2: Dictionary Operations (Python → STC hmap)")
    print("=" * 70)

    python_code = '''
def word_frequency(text: str) -> dict[str, int]:
    """Count word frequencies using dictionary operations."""
    counts: dict[str, int] = {}

    # Split text into words (simplified)
    words = ["hello", "world", "hello", "python"]

    for word in words:
        if word in counts:
            counts[word] = counts[word] + 1
        else:
            counts[word] = 1

    # Dictionary methods
    total_words = len(counts)

    return counts
'''

    print("Python Source Code:")
    print(python_code)
    print("\n" + "→" * 50 + " CONVERTS TO " + "→" * 50 + "\n")

    c_code = convert_python_to_c_with_stc(python_code)
    print("Generated C Code with STC:")
    print(c_code)
    print("\n")


def demonstrate_set_operations():
    """Demonstrate Python set to STC hset translation."""
    print("=" * 70)
    print("DEMONSTRATION 3: Set Operations (Python → STC hset)")
    print("=" * 70)

    python_code = '''
def unique_elements(data1: set[int], data2: set[int]) -> set[int]:
    """Perform set operations on collections."""
    result: set[int] = set()

    # Add elements
    result.add(1)
    result.add(2)
    result.add(3)

    # Set operations
    union_set = data1.union(data2)
    intersection_set = data1.intersection(data2)

    # Membership testing
    if 1 in result:
        result.discard(1)

    return result
'''

    print("Python Source Code:")
    print(python_code)
    print("\n" + "→" * 50 + " CONVERTS TO " + "→" * 50 + "\n")

    c_code = convert_python_to_c_with_stc(python_code)
    print("Generated C Code with STC:")
    print(c_code)
    print("\n")


def demonstrate_memory_management():
    """Demonstrate automatic memory management."""
    print("=" * 70)
    print("DEMONSTRATION 4: Automatic Memory Management")
    print("=" * 70)

    python_code = '''
def memory_safe_processing(size: int) -> int:
    """Demonstrate automatic memory management."""
    # Multiple containers with automatic cleanup
    buffer: list[int] = []
    cache: dict[int, str] = {}
    processed: set[int] = set()

    for i in range(size):
        buffer.append(i)
        cache[i] = f"item_{i}"
        processed.add(i)

    # Potential early return (cleanup still guaranteed)
    if size > 100:
        return -1

    result = len(buffer) + len(cache) + len(processed)
    return result  # All containers automatically cleaned up
'''

    print("Python Source Code:")
    print(python_code)
    print("\n" + "→" * 50 + " CONVERTS TO " + "→" * 50 + "\n")

    converter = STCEnhancedPythonToCConverter()
    c_sequence = converter.convert_code(python_code)
    c_code = str(c_sequence)

    print("Generated C Code with Automatic Cleanup:")
    print(c_code)

    # Demonstrate memory safety analysis
    print("\n" + "─" * 70)
    print("MEMORY SAFETY ANALYSIS:")
    print("─" * 70)

    analysis = converter.analyze_memory_safety(python_code)
    print(f"Memory Errors: {len(analysis['memory_errors'])}")
    print(f"Total Allocations: {analysis['cleanup_summary']['total_allocations']}")
    print(f"Require Cleanup: {analysis['cleanup_summary']['requires_cleanup']}")
    print(f"Container Types: {analysis['cleanup_summary']['allocations_by_type']}")

    if analysis['memory_errors']:
        print("\nDetected Issues:")
        for error in analysis['memory_errors']:
            print(f"  {error['severity'].upper()}: {error['message']} (line {error['line']})")
    else:
        print("\n✅ No memory safety issues detected!")

    print("\n")


def demonstrate_performance_optimization():
    """Demonstrate performance-based container selection."""
    print("=" * 70)
    print("DEMONSTRATION 5: Performance Optimization")
    print("=" * 70)

    python_code = '''
def performance_critical_operations():
    """Operations that benefit from performance optimization."""
    # Frequent random access + insertion → optimized to deque
    buffer: list[int] = []

    # Simulate frequent insertion and random access
    for i in range(1000):
        buffer.append(i)
        if i % 2 == 0:
            buffer[i // 2] = i * 2  # Random access
        if i % 10 == 0:
            buffer.insert(0, -i)   # Front insertion

    # Sorted operations → could optimize to sorted containers
    lookup: dict[str, int] = {}
    for i in range(100):
        key = f"key_{i:03d}"  # Keys in sorted order
        lookup[key] = i

    return len(buffer) + len(lookup)
'''

    print("Python Source Code:")
    print(python_code)
    print("\n" + "→" * 50 + " OPTIMIZED TO " + "→" * 50 + "\n")

    converter = STCEnhancedPythonToCConverter()

    # Show usage pattern analysis
    import ast
    tree = ast.parse(python_code)
    patterns = converter.optimizer.analyze_usage_patterns(tree)

    print("USAGE PATTERN ANALYSIS:")
    for var_name, pattern in patterns.items():
        print(f"  {var_name}:")
        print(f"    Random Access: {pattern.has_random_access}")
        print(f"    Frequent Insertion: {pattern.has_frequent_insertion}")
        print(f"    Frequent Lookup: {pattern.has_frequent_lookup}")
        print(f"    Access Count: {pattern.access_count}")
        print(f"    Modification Count: {pattern.modification_count}")

        # Show optimization choice
        if var_name in ["buffer", "lookup"]:
            choice = converter.optimizer.optimize_container_choice(
                "List[int]" if var_name == "buffer" else "Dict[str, int]",
                var_name
            )
            print(f"    Optimized Container: {choice}")
        print()

    c_code = convert_python_to_c_with_stc(python_code)
    print("Generated Optimized C Code:")
    print(c_code)
    print("\n")


def demonstrate_error_handling():
    """Demonstrate error handling and exception safety."""
    print("=" * 70)
    print("DEMONSTRATION 6: Error Handling & Exception Safety")
    print("=" * 70)

    python_code = '''
def error_prone_operations(data: list[int]) -> bool:
    """Operations that might fail and need proper cleanup."""
    temp_buffer: list[int] = []
    cache: dict[int, str] = {}

    try:
        # Operations that might fail
        for i, value in enumerate(data):
            temp_buffer.append(value * 2)
            cache[i] = f"processed_{value}"

            # Potential early exit on error
            if value < 0:
                return False  # Cleanup must happen here

        # More operations
        temp_buffer.sort()

    except Exception:
        # Exception handling with cleanup
        return False

    return len(temp_buffer) > 0
'''

    print("Python Source Code:")
    print(python_code)
    print("\n" + "→" * 50 + " SAFE TRANSLATION " + "→" * 50 + "\n")

    converter = STCEnhancedPythonToCConverter()
    c_sequence = converter.convert_code(python_code)
    c_code = str(c_sequence)

    print("Generated C Code with Exception Safety:")
    print(c_code)
    print("\n")


def main():
    """Run all STC integration demonstrations."""
    print("🚀 CGen Phase 6: STC Integration Demonstration")
    print("=" * 70)
    print("Showcasing advanced Python-to-C translation with:")
    print("• High-performance STC containers")
    print("• Automatic memory management")
    print("• Performance optimization")
    print("• Memory safety analysis")
    print("• Exception safety")
    print("=" * 70)
    print()

    try:
        # Run all demonstrations
        demonstrate_list_operations()
        demonstrate_dict_operations()
        demonstrate_set_operations()
        demonstrate_memory_management()
        demonstrate_performance_optimization()
        demonstrate_error_handling()

        # Summary
        print("=" * 70)
        print("🎉 STC INTEGRATION SUMMARY")
        print("=" * 70)
        print("✅ Container Type Mappings:")
        print("   • Python list[T] → STC vec<T>")
        print("   • Python dict[K,V] → STC hmap<K,V>")
        print("   • Python set[T] → STC hset<T>")
        print("   • Python str → STC cstr")
        print()
        print("✅ Operation Translations:")
        print("   • append() → vec_push()")
        print("   • dict[key] → hmap_get()")
        print("   • set.add() → hset_insert()")
        print("   • len() → container_size()")
        print("   • in operator → container_contains()")
        print()
        print("✅ Memory Management:")
        print("   • Automatic cleanup generation")
        print("   • Exception-safe operations")
        print("   • Memory leak prevention")
        print("   • RAII-style resource management")
        print()
        print("✅ Performance Optimization:")
        print("   • Usage pattern analysis")
        print("   • Optimal container selection")
        print("   • Access pattern optimization")
        print()
        print("🏆 Phase 6 STC Integration: COMPLETE!")
        print("Ready for production use with high-performance C code generation")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error in STC integration demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)