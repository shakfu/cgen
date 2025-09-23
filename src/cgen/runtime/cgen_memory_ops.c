/**
 * CGen Runtime Library - Memory Management Utilities Implementation
 */

#include "cgen_memory_ops.h"
#include <stdarg.h>

// Memory tracking globals
static int memory_tracking_enabled = 0;
static cgen_memory_stats_t memory_stats = {0};

// Memory pool structure
struct cgen_memory_pool {
    char* data;
    size_t size;
    size_t capacity;
    size_t used;
};

// Scope allocator structure
typedef struct alloc_entry {
    void* ptr;
    struct alloc_entry* next;
} alloc_entry_t;

struct cgen_scope_allocator {
    alloc_entry_t* head;
    size_t count;
};

// Safe memory allocation functions
void* cgen_malloc(size_t size) {
    if (size == 0) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Attempted to allocate 0 bytes");
        return NULL;
    }

    void* ptr = malloc(size);
    if (!ptr) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_MEMORY, "Failed to allocate %zu bytes", size);
        return NULL;
    }

    if (memory_tracking_enabled) {
        memory_stats.total_allocated += size;
        memory_stats.current_allocated += size;
        memory_stats.allocation_count++;
        if (memory_stats.current_allocated > memory_stats.peak_allocated) {
            memory_stats.peak_allocated = memory_stats.current_allocated;
        }
    }

    return ptr;
}

void* cgen_realloc(void* ptr, size_t new_size) {
    if (new_size == 0) {
        if (ptr) {
            cgen_free((void**)&ptr);
        }
        return NULL;
    }

    void* new_ptr = realloc(ptr, new_size);
    if (!new_ptr) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_MEMORY, "Failed to reallocate to %zu bytes", new_size);
        return NULL;
    }

    // Note: tracking size changes in realloc is complex, simplified here
    if (memory_tracking_enabled && !ptr) {
        memory_stats.total_allocated += new_size;
        memory_stats.current_allocated += new_size;
        memory_stats.allocation_count++;
    }

    return new_ptr;
}

void* cgen_calloc(size_t count, size_t size) {
    if (count == 0 || size == 0) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Attempted to allocate 0 elements or 0 bytes");
        return NULL;
    }

    // Check for overflow
    if (count > SIZE_MAX / size) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Integer overflow in calloc");
        return NULL;
    }

    void* ptr = calloc(count, size);
    if (!ptr) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_MEMORY, "Failed to allocate %zu elements of %zu bytes",
                           count, size);
        return NULL;
    }

    if (memory_tracking_enabled) {
        size_t total_size = count * size;
        memory_stats.total_allocated += total_size;
        memory_stats.current_allocated += total_size;
        memory_stats.allocation_count++;
        if (memory_stats.current_allocated > memory_stats.peak_allocated) {
            memory_stats.peak_allocated = memory_stats.current_allocated;
        }
    }

    return ptr;
}

void cgen_free(void** ptr) {
    if (!ptr || !*ptr) {
        return;
    }

    if (memory_tracking_enabled) {
        // Note: We can't track exact size freed without additional bookkeeping
        memory_stats.free_count++;
    }

    free(*ptr);
    *ptr = NULL;
}

// Safe memory operations
cgen_error_t cgen_memcpy_safe(void* dest, size_t dest_size,
                             const void* src, size_t src_size) {
    if (!dest || !src) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "NULL pointer in memcpy");
        return CGEN_ERROR_VALUE;
    }

    if (src_size > dest_size) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_VALUE,
                           "Source size %zu exceeds destination size %zu",
                           src_size, dest_size);
        return CGEN_ERROR_VALUE;
    }

    memcpy(dest, src, src_size);
    return CGEN_OK;
}

cgen_error_t cgen_memmove_safe(void* dest, size_t dest_size,
                              const void* src, size_t src_size) {
    if (!dest || !src) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "NULL pointer in memmove");
        return CGEN_ERROR_VALUE;
    }

    if (src_size > dest_size) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_VALUE,
                           "Source size %zu exceeds destination size %zu",
                           src_size, dest_size);
        return CGEN_ERROR_VALUE;
    }

    memmove(dest, src, src_size);
    return CGEN_OK;
}

cgen_error_t cgen_memset_safe(void* dest, int value, size_t count, size_t dest_size) {
    if (!dest) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "NULL pointer in memset");
        return CGEN_ERROR_VALUE;
    }

    if (count > dest_size) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_VALUE,
                           "Count %zu exceeds destination size %zu",
                           count, dest_size);
        return CGEN_ERROR_VALUE;
    }

    memset(dest, value, count);
    return CGEN_OK;
}

// Memory pool implementation
cgen_memory_pool_t* cgen_memory_pool_new(size_t initial_size) {
    if (initial_size == 0) {
        initial_size = 4096; // Default 4KB
    }

    cgen_memory_pool_t* pool = malloc(sizeof(cgen_memory_pool_t));
    if (!pool) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory pool");
        return NULL;
    }

    pool->data = malloc(initial_size);
    if (!pool->data) {
        free(pool);
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory pool data");
        return NULL;
    }

    pool->size = 0;
    pool->capacity = initial_size;
    pool->used = 0;

    return pool;
}

void* cgen_memory_pool_alloc(cgen_memory_pool_t* pool, size_t size) {
    if (!pool) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Memory pool is NULL");
        return NULL;
    }

    // Align size to pointer boundary
    size = (size + sizeof(void*) - 1) & ~(sizeof(void*) - 1);

    if (pool->used + size > pool->capacity) {
        // Grow pool
        size_t new_capacity = pool->capacity * 2;
        while (new_capacity < pool->used + size) {
            new_capacity *= 2;
        }

        char* new_data = realloc(pool->data, new_capacity);
        if (!new_data) {
            CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to grow memory pool");
            return NULL;
        }

        pool->data = new_data;
        pool->capacity = new_capacity;
    }

    void* ptr = pool->data + pool->used;
    pool->used += size;
    pool->size++;

    return ptr;
}

void cgen_memory_pool_reset(cgen_memory_pool_t* pool) {
    if (!pool) return;

    pool->used = 0;
    pool->size = 0;
}

void cgen_memory_pool_free(cgen_memory_pool_t* pool) {
    if (!pool) return;

    free(pool->data);
    free(pool);
}

// Scope allocator implementation
cgen_scope_allocator_t* cgen_scope_new(void) {
    cgen_scope_allocator_t* scope = malloc(sizeof(cgen_scope_allocator_t));
    if (!scope) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate scope allocator");
        return NULL;
    }

    scope->head = NULL;
    scope->count = 0;

    return scope;
}

void* cgen_scope_alloc(cgen_scope_allocator_t* scope, size_t size) {
    if (!scope) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Scope allocator is NULL");
        return NULL;
    }

    void* ptr = cgen_malloc(size);
    if (!ptr) return NULL;

    if (cgen_scope_register(scope, ptr) != CGEN_OK) {
        cgen_free(&ptr);
        return NULL;
    }

    return ptr;
}

cgen_error_t cgen_scope_register(cgen_scope_allocator_t* scope, void* ptr) {
    if (!scope) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Scope allocator is NULL");
        return CGEN_ERROR_VALUE;
    }

    if (!ptr) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Pointer is NULL");
        return CGEN_ERROR_VALUE;
    }

    alloc_entry_t* entry = malloc(sizeof(alloc_entry_t));
    if (!entry) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate scope entry");
        return CGEN_ERROR_MEMORY;
    }

    entry->ptr = ptr;
    entry->next = scope->head;
    scope->head = entry;
    scope->count++;

    return CGEN_OK;
}

void cgen_scope_free(cgen_scope_allocator_t* scope) {
    if (!scope) return;

    alloc_entry_t* current = scope->head;
    while (current) {
        alloc_entry_t* next = current->next;
        cgen_free(&current->ptr);
        free(current);
        current = next;
    }

    free(scope);
}

// Memory tracking functions
void cgen_memory_tracking_enable(void) {
    memory_tracking_enabled = 1;
    memset(&memory_stats, 0, sizeof(memory_stats));
}

void cgen_memory_tracking_disable(void) {
    memory_tracking_enabled = 0;
}

cgen_memory_stats_t cgen_get_memory_stats(void) {
    return memory_stats;
}

void cgen_print_memory_stats(void) {
    printf("Memory Statistics:\n");
    printf("  Total allocated: %zu bytes\n", memory_stats.total_allocated);
    printf("  Total freed: %zu bytes\n", memory_stats.total_freed);
    printf("  Currently allocated: %zu bytes\n", memory_stats.current_allocated);
    printf("  Peak allocated: %zu bytes\n", memory_stats.peak_allocated);
    printf("  Allocation count: %zu\n", memory_stats.allocation_count);
    printf("  Free count: %zu\n", memory_stats.free_count);
}

int cgen_check_memory_leaks(void) {
    return memory_stats.current_allocated > 0;
}

// Reference counting implementation
cgen_refcounted_t* cgen_refcounted_new(size_t data_size, void (*destructor)(void*)) {
    cgen_refcounted_t* obj = malloc(sizeof(cgen_refcounted_t) + data_size);
    if (!obj) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate reference counted object");
        return NULL;
    }

    obj->refcount = 1;
    obj->destructor = destructor;

    return obj;
}

cgen_refcounted_t* cgen_refcounted_retain(cgen_refcounted_t* obj) {
    if (!obj) return NULL;

    obj->refcount++;
    return obj;
}

void cgen_refcounted_release(cgen_refcounted_t* obj) {
    if (!obj) return;

    obj->refcount--;
    if (obj->refcount <= 0) {
        if (obj->destructor) {
            obj->destructor(obj->data);
        }
        free(obj);
    }
}

int cgen_refcounted_count(cgen_refcounted_t* obj) {
    return obj ? obj->refcount : 0;
}

void* cgen_refcounted_data(cgen_refcounted_t* obj) {
    return obj ? obj->data : NULL;
}

// Buffer implementation
cgen_buffer_t* cgen_buffer_new(size_t initial_capacity) {
    if (initial_capacity == 0) {
        initial_capacity = 256; // Default 256 bytes
    }

    cgen_buffer_t* buffer = malloc(sizeof(cgen_buffer_t));
    if (!buffer) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate buffer");
        return NULL;
    }

    buffer->data = malloc(initial_capacity);
    if (!buffer->data) {
        free(buffer);
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate buffer data");
        return NULL;
    }

    buffer->size = 0;
    buffer->capacity = initial_capacity;
    buffer->data[0] = '\0';

    return buffer;
}

cgen_error_t cgen_buffer_append(cgen_buffer_t* buffer, const char* data, size_t len) {
    if (!buffer || !data) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Buffer or data is NULL");
        return CGEN_ERROR_VALUE;
    }

    if (buffer->size + len + 1 > buffer->capacity) {
        size_t new_capacity = buffer->capacity;
        while (new_capacity < buffer->size + len + 1) {
            new_capacity *= 2;
        }

        char* new_data = realloc(buffer->data, new_capacity);
        if (!new_data) {
            CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to grow buffer");
            return CGEN_ERROR_MEMORY;
        }

        buffer->data = new_data;
        buffer->capacity = new_capacity;
    }

    memcpy(buffer->data + buffer->size, data, len);
    buffer->size += len;
    buffer->data[buffer->size] = '\0';

    return CGEN_OK;
}

cgen_error_t cgen_buffer_append_str(cgen_buffer_t* buffer, const char* str) {
    if (!str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return CGEN_ERROR_VALUE;
    }

    return cgen_buffer_append(buffer, str, strlen(str));
}

cgen_error_t cgen_buffer_append_fmt(cgen_buffer_t* buffer, const char* format, ...) {
    if (!buffer || !format) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Buffer or format is NULL");
        return CGEN_ERROR_VALUE;
    }

    va_list args;
    va_start(args, format);

    // Calculate required size
    va_list args_copy;
    va_copy(args_copy, args);
    int len = vsnprintf(NULL, 0, format, args_copy);
    va_end(args_copy);

    if (len < 0) {
        va_end(args);
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid format string");
        return CGEN_ERROR_VALUE;
    }

    // Ensure buffer has enough space
    if (buffer->size + len + 1 > buffer->capacity) {
        size_t new_capacity = buffer->capacity;
        while (new_capacity < buffer->size + len + 1) {
            new_capacity *= 2;
        }

        char* new_data = realloc(buffer->data, new_capacity);
        if (!new_data) {
            va_end(args);
            CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to grow buffer");
            return CGEN_ERROR_MEMORY;
        }

        buffer->data = new_data;
        buffer->capacity = new_capacity;
    }

    vsnprintf(buffer->data + buffer->size, len + 1, format, args);
    buffer->size += len;
    va_end(args);

    return CGEN_OK;
}

const char* cgen_buffer_cstr(cgen_buffer_t* buffer) {
    return buffer ? buffer->data : NULL;
}

size_t cgen_buffer_size(cgen_buffer_t* buffer) {
    return buffer ? buffer->size : 0;
}

void cgen_buffer_clear(cgen_buffer_t* buffer) {
    if (!buffer) return;

    buffer->size = 0;
    if (buffer->data) {
        buffer->data[0] = '\0';
    }
}

void cgen_buffer_free(cgen_buffer_t* buffer) {
    if (!buffer) return;

    free(buffer->data);
    free(buffer);
}