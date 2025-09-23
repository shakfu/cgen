# STC Library Integration Design

## Overview

This document outlines the strategy for integrating STC (Smart Template Containers) library with CGen to support Python list/dict/set operations in generated C code.

## STC Library Features

STC provides:
- **vec**: Dynamic arrays (like Python lists)
- **hmap**: Hash maps (like Python dicts)
- **hset**: Hash sets (like Python sets)
- **Automatic memory management**: RAII-style constructors/destructors
- **Template-based**: Type-safe generic containers

## Python to STC Mapping

| Python Type | STC Container | Example Declaration |
|-------------|---------------|-------------------|
| `list[int]` | `vec_i32` | `declare_vec(vec_i32, int32_t)` |
| `list[str]` | `vec_str` | `declare_vec(vec_str, cstr)` |
| `dict[str, int]` | `hmap_str_i32` | `declare_hmap(hmap_str_i32, cstr, int32_t)` |
| `set[int]` | `hset_i32` | `declare_hset(hset_i32, int32_t)` |

## Implementation Strategy

### Phase 1: Basic List Support
1. **Type Analysis**: Detect `list[T]` type annotations
2. **STC Declaration Generation**: Generate appropriate `declare_vec` statements
3. **Operation Mapping**: Map Python list operations to STC vec operations
4. **Memory Management**: Automatic cleanup via STC's destructors

### Phase 2: List Operations Mapping

| Python Operation | STC Equivalent | Notes |
|-----------------|----------------|-------|
| `lst = []` | `vec_i32 lst = {0};` | Empty initialization |
| `lst.append(x)` | `vec_i32_push(&lst, x);` | Add element |
| `len(lst)` | `vec_i32_size(&lst)` | Get size |
| `lst[i]` | `*vec_i32_at(&lst, i)` | Element access |
| `lst[i] = x` | `*vec_i32_at(&lst, i) = x;` | Element assignment |
| `for x in lst:` | `c_foreach (x, vec_i32, lst)` | Iteration |

### Phase 3: Advanced Features
- Range operations (`lst[1:3]`)
- List comprehensions (where possible)
- Nested containers (`list[list[int]]`)

## Code Generation Strategy

### 1. Type Declaration Phase
```c
// Generated at top of file based on detected types
#include <stc/vec.h>
declare_vec(vec_i32, int32_t);
```

### 2. Variable Declaration
```python
# Python
numbers: list[int] = []
```
```c
// Generated C
vec_i32 numbers = {0};  // Initialize empty
```

### 3. Function Parameter/Return Types
```python
# Python
def process_list(items: list[int]) -> list[int]:
    result: list[int] = []
    # ...
```
```c
// Generated C
vec_i32 process_list(vec_i32* items) {
    vec_i32 result = {0};
    // ...
    return result;
}
```

### 4. Cleanup Integration
STC containers automatically clean up via destructors, but for explicit control:
```c
// At function end or scope exit
vec_i32_drop(&container_name);
```

## Implementation Files

### New Modules to Create:
1. **`src/cgen/generator/stc_integration.py`**: STC-specific code generation
2. **`src/cgen/frontend/type_analyzer.py`**: Enhanced type analysis for containers
3. **`src/cgen/generator/stc_templates.py`**: STC template generation

### Existing Modules to Modify:
1. **`src/cgen/generator/py2c.py`**: Add container type support
2. **`src/cgen/generator/core.py`**: Add STC-specific elements
3. **`src/cgen/generator/writer.py`**: Add STC writers

## Testing Strategy

### Unit Tests:
- Type detection and mapping
- STC declaration generation
- Operation mapping accuracy
- Memory management verification

### Integration Tests:
- End-to-end Python list → STC vec conversion
- Complex nested operations
- Performance verification vs manual C

## Benefits

1. **Automatic Memory Management**: STC handles malloc/free automatically
2. **Type Safety**: Template-based approach provides compile-time safety
3. **Performance**: Optimized C containers with minimal overhead
4. **Familiar API**: Python-like operations map naturally to STC
5. **Self-Contained**: Generated code includes necessary STC headers

## Limitations

1. **Compile-Time Types**: Container element types must be known at compile time
2. **No Dynamic Typing**: Cannot mix types in same container
3. **Limited Python Features**: Some advanced list features may not map directly
4. **Build Complexity**: Requires STC library in build environment

## Next Steps

1. Implement basic `list[int]` support
2. Add STC header generation
3. Test with simple list operations
4. Expand to other basic types
5. Add dict/set support in future phases