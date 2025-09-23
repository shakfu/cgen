/**
 * CGen Runtime Library - Memory Management Utilities
 *
 * Provides safe memory management utilities for generated C code.
 * These functions handle error checking and automatic cleanup.
 */

#ifndef CGEN_MEMORY_OPS_H
#define CGEN_MEMORY_OPS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cgen_error_handling.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Safe memory allocation with error handling
 */
void* cgen_malloc(size_t size);

/**
 * Safe memory reallocation with error handling
 */
void* cgen_realloc(void* ptr, size_t new_size);

/**
 * Safe memory allocation for arrays with overflow checking
 */
void* cgen_calloc(size_t count, size_t size);

/**
 * Safe memory deallocation (sets pointer to NULL)
 */
void cgen_free(void** ptr);

/**
 * Safe memory copy with bounds checking
 */
cgen_error_t cgen_memcpy_safe(void* dest, size_t dest_size,
                             const void* src, size_t src_size);

/**
 * Safe memory move with bounds checking
 */
cgen_error_t cgen_memmove_safe(void* dest, size_t dest_size,
                              const void* src, size_t src_size);

/**
 * Safe memory set with bounds checking
 */
cgen_error_t cgen_memset_safe(void* dest, int value, size_t count, size_t dest_size);

/**
 * Memory pool for efficient allocation/deallocation
 */
typedef struct cgen_memory_pool cgen_memory_pool_t;

/**
 * Create a new memory pool
 */
cgen_memory_pool_t* cgen_memory_pool_new(size_t initial_size);

/**
 * Allocate from memory pool
 */
void* cgen_memory_pool_alloc(cgen_memory_pool_t* pool, size_t size);

/**
 * Reset memory pool (deallocates all at once)
 */
void cgen_memory_pool_reset(cgen_memory_pool_t* pool);

/**
 * Free memory pool
 */
void cgen_memory_pool_free(cgen_memory_pool_t* pool);

/**
 * Automatic memory management with scope-based cleanup
 */
typedef struct cgen_scope_allocator cgen_scope_allocator_t;

/**
 * Create a new scope allocator
 */
cgen_scope_allocator_t* cgen_scope_new(void);

/**
 * Allocate memory that will be automatically freed when scope ends
 */
void* cgen_scope_alloc(cgen_scope_allocator_t* scope, size_t size);

/**
 * Register existing pointer for automatic cleanup
 */
cgen_error_t cgen_scope_register(cgen_scope_allocator_t* scope, void* ptr);

/**
 * Free all allocations in scope
 */
void cgen_scope_free(cgen_scope_allocator_t* scope);

/**
 * Memory debugging and leak detection
 */
typedef struct cgen_memory_stats {
    size_t total_allocated;
    size_t total_freed;
    size_t current_allocated;
    size_t peak_allocated;
    size_t allocation_count;
    size_t free_count;
} cgen_memory_stats_t;

/**
 * Enable memory tracking
 */
void cgen_memory_tracking_enable(void);

/**
 * Disable memory tracking
 */
void cgen_memory_tracking_disable(void);

/**
 * Get current memory statistics
 */
cgen_memory_stats_t cgen_get_memory_stats(void);

/**
 * Print memory statistics
 */
void cgen_print_memory_stats(void);

/**
 * Check for memory leaks
 */
int cgen_check_memory_leaks(void);

/**
 * Reference counting utilities
 */
typedef struct cgen_refcounted {
    int refcount;
    void (*destructor)(void* data);
    char data[];
} cgen_refcounted_t;

/**
 * Create reference counted object
 */
cgen_refcounted_t* cgen_refcounted_new(size_t data_size, void (*destructor)(void*));

/**
 * Increment reference count
 */
cgen_refcounted_t* cgen_refcounted_retain(cgen_refcounted_t* obj);

/**
 * Decrement reference count (frees if reaches 0)
 */
void cgen_refcounted_release(cgen_refcounted_t* obj);

/**
 * Get reference count
 */
int cgen_refcounted_count(cgen_refcounted_t* obj);

/**
 * Get data pointer from reference counted object
 */
void* cgen_refcounted_data(cgen_refcounted_t* obj);

/**
 * Buffer management for string operations
 */
typedef struct cgen_buffer {
    char* data;
    size_t size;
    size_t capacity;
} cgen_buffer_t;

/**
 * Create a new dynamic buffer
 */
cgen_buffer_t* cgen_buffer_new(size_t initial_capacity);

/**
 * Append data to buffer
 */
cgen_error_t cgen_buffer_append(cgen_buffer_t* buffer, const char* data, size_t len);

/**
 * Append string to buffer
 */
cgen_error_t cgen_buffer_append_str(cgen_buffer_t* buffer, const char* str);

/**
 * Append formatted string to buffer
 */
cgen_error_t cgen_buffer_append_fmt(cgen_buffer_t* buffer, const char* format, ...);

/**
 * Get buffer data as C string
 */
const char* cgen_buffer_cstr(cgen_buffer_t* buffer);

/**
 * Get buffer size
 */
size_t cgen_buffer_size(cgen_buffer_t* buffer);

/**
 * Clear buffer (reset size to 0)
 */
void cgen_buffer_clear(cgen_buffer_t* buffer);

/**
 * Free buffer
 */
void cgen_buffer_free(cgen_buffer_t* buffer);

/**
 * RAII-style cleanup macros
 */
#define CGEN_SCOPE_BEGIN() \
    do { \
        cgen_scope_allocator_t* __scope = cgen_scope_new(); \
        if (!__scope) break;

#define CGEN_SCOPE_END() \
        cgen_scope_free(__scope); \
    } while(0)

#define CGEN_SCOPE_ALLOC(size) \
    cgen_scope_alloc(__scope, (size))

#define CGEN_SCOPE_REGISTER(ptr) \
    cgen_scope_register(__scope, (ptr))

/**
 * Memory pool macros for common patterns
 */
#define CGEN_POOL_BEGIN(size) \
    do { \
        cgen_memory_pool_t* __pool = cgen_memory_pool_new(size); \
        if (!__pool) break;

#define CGEN_POOL_END() \
        cgen_memory_pool_free(__pool); \
    } while(0)

#define CGEN_POOL_ALLOC(size) \
    cgen_memory_pool_alloc(__pool, (size))

#ifdef __cplusplus
}
#endif

#endif // CGEN_MEMORY_OPS_H