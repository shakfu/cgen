/**
 * CGen Runtime Library - STC Container Helper Operations
 *
 * Provides helper functions for STC (Smart Template Containers) operations.
 * These functions bridge Python container semantics with STC implementations.
 */

#ifndef CGEN_CONTAINER_OPS_H
#define CGEN_CONTAINER_OPS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cgen_error_handling.h"
#include "cgen_string_ops.h"

#ifdef __cplusplus
extern "C" {
#endif

// Forward declarations for STC containers
// These will be defined when STC headers are included
struct cstr;
struct vec_cstr;
struct hmap_cstr_int;
struct hset_cstr;

/**
 * String container helpers
 */

/**
 * Create a new STC cstr from C string
 */
struct cstr* cgen_cstr_from(const char* str);

/**
 * Get C string from STC cstr
 */
const char* cgen_cstr_to_cstring(struct cstr* cstr);

/**
 * Free STC cstr safely
 */
void cgen_cstr_free(struct cstr* cstr);

/**
 * Vector container helpers
 */

/**
 * Check if vector index is valid
 */
int cgen_vec_bounds_check(size_t index, size_t size, const char* container_name);

/**
 * Print vector bounds error
 */
void cgen_vec_index_error(size_t index, size_t size, const char* container_name);

/**
 * Safe vector access with bounds checking
 */
void* cgen_vec_at_safe(void* vec_ptr, size_t index, size_t element_size,
                       size_t (*size_func)(void*), const char* container_name);

/**
 * HashMap container helpers
 */

/**
 * Check if key exists in hashmap
 */
int cgen_hmap_contains_key(void* hmap_ptr, const void* key,
                          int (*contains_func)(void*, const void*));

/**
 * Safe hashmap get with KeyError on missing key
 */
void* cgen_hmap_get_safe(void* hmap_ptr, const void* key,
                        void* (*get_func)(void*, const void*),
                        const char* key_str);

/**
 * HashSet container helpers
 */

/**
 * Check if element exists in hashset
 */
int cgen_hset_contains(void* hset_ptr, const void* element,
                      int (*contains_func)(void*, const void*));

/**
 * Container iteration helpers
 */

/**
 * Python-style enumerate for vectors
 * Calls callback for each (index, element) pair
 */
typedef void (*cgen_enumerate_callback_t)(size_t index, void* element, void* userdata);

void cgen_vec_enumerate(void* vec_ptr, size_t element_size,
                       size_t (*size_func)(void*),
                       void* (*at_func)(void*, size_t),
                       cgen_enumerate_callback_t callback,
                       void* userdata);

/**
 * Python-style items() iteration for hashmaps
 * Calls callback for each (key, value) pair
 */
typedef void (*cgen_items_callback_t)(void* key, void* value, void* userdata);

void cgen_hmap_items(void* hmap_ptr,
                    void (*iter_func)(void*, cgen_items_callback_t, void*),
                    cgen_items_callback_t callback,
                    void* userdata);

/**
 * Container comparison helpers
 */

/**
 * Compare two vectors element by element
 */
int cgen_vec_equal(void* vec1, void* vec2,
                  size_t (*size_func)(void*),
                  void* (*at_func)(void*, size_t),
                  int (*element_equal)(const void*, const void*));

/**
 * Compare two hashmaps
 */
int cgen_hmap_equal(void* hmap1, void* hmap2,
                   size_t (*size_func)(void*),
                   int (*equal_func)(void*, void*));

/**
 * Container conversion helpers
 */

/**
 * Convert string array to STC vector of cstr
 */
struct vec_cstr* cgen_string_array_to_vec_cstr(cgen_string_array_t* str_array);

/**
 * Convert STC vector of cstr to string array
 */
cgen_string_array_t* cgen_vec_cstr_to_string_array(struct vec_cstr* vec);

/**
 * Container memory management helpers
 */

/**
 * Register container for automatic cleanup
 */
typedef struct cgen_container_registry cgen_container_registry_t;

cgen_container_registry_t* cgen_container_registry_new(void);
void cgen_container_registry_free(cgen_container_registry_t* registry);

cgen_error_t cgen_register_container(cgen_container_registry_t* registry,
                                    void* container,
                                    void (*cleanup_func)(void*),
                                    const char* name);

void cgen_cleanup_containers(cgen_container_registry_t* registry);

/**
 * Python-style container operations
 */

/**
 * Python len() for any container
 */
size_t cgen_len(void* container, size_t (*size_func)(void*));

/**
 * Python bool() for containers (True if not empty)
 */
int cgen_bool_container(void* container, size_t (*size_func)(void*));

/**
 * Python in operator for vectors
 */
int cgen_in_vec(void* vec_ptr, const void* element,
               size_t (*size_func)(void*),
               void* (*at_func)(void*, size_t),
               int (*element_equal)(const void*, const void*));

/**
 * Python in operator for hashmaps (check key)
 */
int cgen_in_hmap(void* hmap_ptr, const void* key,
                int (*contains_func)(void*, const void*));

/**
 * Python-style string formatting for containers
 */
char* cgen_vec_repr(void* vec_ptr,
                   size_t (*size_func)(void*),
                   void* (*at_func)(void*, size_t),
                   char* (*element_repr)(const void*));

char* cgen_hmap_repr(void* hmap_ptr,
                    char* (*repr_func)(void*));

#ifdef __cplusplus
}
#endif

#endif // CGEN_CONTAINER_OPS_H