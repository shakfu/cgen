# STC Integration Architecture Design

## Overview

This document outlines the architecture for integrating STC (Smart Template Containers) with the CGen Python-to-C translation system, enabling high-performance, memory-safe container operations in generated C code.

## Current State Analysis

### Existing Components
1. **Basic Python-to-C Converter** (`src/cgen/core/py2c.py`)
   - Supports basic types: int, float, bool, str, None
   - Limited container support (list[T] → T*)
   - No advanced container operations

2. **STC Framework** (`src/cgen/ext/stc/`)
   - Container mappings defined in `containers.py`
   - Basic translator in `translator.py`
   - Enhanced translator in `stc_enhanced_translator.py`
   - Supports: vec, hmap, hset, cstr, deque, stack, queue, pqueue

3. **Integration Gaps**
   - Basic py2c converter doesn't use STC
   - STC translator is separate from main conversion pipeline
   - No unified architecture for container type inference
   - Missing memory management integration

## STC Integration Architecture

### 1. Core Integration Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    CGen Intelligence Layer                  │
├─────────────────────────────────────────────────────────────┤
│  AST Analysis → Type Inference → STC Container Selection    │
│       ↓              ↓                     ↓               │
│  Static Analysis → Container Ops → Memory Safety Analysis   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Enhanced Py2C Converter                   │
├─────────────────────────────────────────────────────────────┤
│  • STC-aware type mapping                                   │
│  • Container operation translation                          │
│  • Automatic memory management                              │
│  • Performance optimization                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     C Code Generation                       │
├─────────────────────────────────────────────────────────────┤
│  • STC includes and type definitions                        │
│  • Container declarations                                    │
│  • Operation translations                                    │
│  • Cleanup code                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Enhanced Type System

#### Container Type Mappings
```python
ENHANCED_TYPE_MAPPINGS = {
    # Basic types (unchanged)
    'int': 'int',
    'float': 'double',
    'bool': 'bool',
    'str': 'cstr',  # Enhanced: Use STC cstr instead of char*

    # Container types with STC
    'List[int]': 'IntVec',
    'List[float]': 'DoubleVec',
    'List[str]': 'CstrVec',
    'Dict[str, int]': 'StrIntMap',
    'Dict[int, str]': 'IntStrMap',
    'Set[int]': 'IntSet',
    'Set[str]': 'CstrSet',

    # Advanced containers
    'collections.deque': 'Deque',
    'queue.Queue': 'Queue',
    'heapq': 'PriorityQueue'
}
```

#### Type Inference Enhancement
```python
class STCTypeInference:
    def infer_container_usage(self, ast_node):
        """Analyze AST to determine optimal STC containers."""
        # Analyze access patterns
        # Determine if sorted containers needed
        # Check for concurrent access requirements
        # Optimize for performance characteristics
```

### 3. Container Operation Translation

#### Python → STC Operation Mappings
```python
OPERATION_MAPPINGS = {
    # List operations
    'list.append(x)': 'vec_push(&container, x)',
    'list.pop()': 'vec_pop(&container)',
    'list.insert(i, x)': 'vec_insert_at(&container, i, x)',
    'list.remove(x)': 'vec_erase_val(&container, x)',
    'len(list)': 'vec_size(&container)',

    # Dict operations
    'dict[key]': 'hmap_get(&container, key)',
    'dict[key] = value': 'hmap_insert(&container, key, value)',
    'del dict[key]': 'hmap_erase(&container, key)',
    'key in dict': 'hmap_contains(&container, key)',

    # Set operations
    'set.add(x)': 'hset_insert(&container, x)',
    'set.remove(x)': 'hset_erase(&container, x)',
    'x in set': 'hset_contains(&container, x)',

    # String operations
    'str + str': 'cstr_cat(&str1, str2)',
    'str[i]': 'cstr_at(&str, i)',
    'len(str)': 'cstr_size(&str)'
}
```

### 4. Memory Management Integration

#### Automatic Resource Management
```python
class STCMemoryManager:
    def __init__(self):
        self.container_vars = {}  # Track all STC containers
        self.scope_stack = []     # Track variable scopes

    def generate_cleanup_code(self, scope_exit):
        """Generate automatic cleanup for containers going out of scope."""
        cleanup_code = []
        for var_name, container_type in self.get_scope_containers(scope_exit):
            cleanup_code.append(f"{container_type}_drop(&{var_name});")
        return cleanup_code

    def generate_error_handling(self):
        """Generate error handling for container operations."""
        # Check allocation failures
        # Handle container operation errors
        # Ensure cleanup on early returns
```

### 5. Performance Optimization Layer

#### Container Selection Optimization
```python
class STCOptimizer:
    def optimize_container_choice(self, usage_pattern):
        """Select optimal STC container based on usage."""
        if usage_pattern.has_random_access and usage_pattern.has_frequent_insertion:
            return 'deque'  # Better for random access + insertion
        elif usage_pattern.sorted_access_required:
            return 'smap' if usage_pattern.is_key_value else 'sset'
        elif usage_pattern.has_frequent_lookup:
            return 'hmap' if usage_pattern.is_key_value else 'hset'
        else:
            return 'vec'  # Default for sequential access
```

### 6. Integration Points

#### Enhanced PythonToCConverter
```python
class STCEnhancedPythonToCConverter(PythonToCConverter):
    def __init__(self):
        super().__init__()
        self.stc_translator = STCPythonToCTranslator()
        self.memory_manager = STCMemoryManager()
        self.optimizer = STCOptimizer()

        # Enhanced type mapping with STC support
        self.type_mapping.update(ENHANCED_TYPE_MAPPINGS)

    def _convert_module(self, module):
        # 1. Analyze container usage patterns
        usage_analysis = self.optimizer.analyze_usage_patterns(module)

        # 2. Generate STC includes and type definitions
        stc_includes, type_defs = self.stc_translator.generate_stc_includes_and_types(
            usage_analysis.type_info
        )

        # 3. Generate enhanced C code with STC support
        return self._generate_stc_enhanced_code(module, stc_includes, type_defs)
```

### 7. Code Generation Pipeline

#### 1. AST Analysis Phase
- Identify container types and usage patterns
- Analyze access patterns (sequential, random, sorted)
- Determine optimal STC container types
- Check for memory safety requirements

#### 2. Type Definition Phase
- Generate STC type definitions
- Create container-specific typedefs
- Add necessary include statements
- Set up error handling macros

#### 3. Translation Phase
- Convert Python operations to STC operations
- Handle edge cases and error conditions
- Generate bounds checking where needed
- Optimize common operation patterns

#### 4. Memory Management Phase
- Track container lifecycles
- Generate automatic cleanup code
- Handle exception/error cleanup
- Ensure memory safety guarantees

### 8. Testing Strategy

#### Unit Tests
- Container operation translation accuracy
- Memory management correctness
- Type inference correctness
- Performance optimization effectiveness

#### Integration Tests
- End-to-end Python to C conversion
- Complex container usage scenarios
- Memory leak detection
- Performance benchmarking

#### Validation Tests
- Generated C code compilation
- Runtime correctness verification
- Memory safety validation
- Performance regression testing

## Implementation Plan

### Phase 1: Core Integration
1. Enhance PythonToCConverter with STC support
2. Implement container type inference
3. Add basic operation translation
4. Create memory management framework

### Phase 2: Advanced Features
1. Implement performance optimization
2. Add error handling and bounds checking
3. Support complex container patterns
4. Add automatic cleanup generation

### Phase 3: Production Readiness
1. Comprehensive testing suite
2. Performance benchmarking
3. Documentation and examples
4. CI/CD integration

## Success Metrics

1. **Correctness**: 100% compatibility with Python container semantics
2. **Performance**: 2-5x performance improvement over naive C translations
3. **Memory Safety**: Zero memory leaks in generated code
4. **Coverage**: Support for 90%+ of common Python container operations
5. **Maintainability**: Clean, extensible architecture for future enhancements

## Conclusion

This architecture provides a comprehensive integration of STC containers into the CGen Python-to-C translation pipeline, enabling high-performance, memory-safe container operations while maintaining Python's ease of use and safety guarantees.