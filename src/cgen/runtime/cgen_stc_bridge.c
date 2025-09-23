/**
 * CGen Runtime Library - STC Bridge Implementation
 */

#include "cgen_stc_bridge.h"
#include <ctype.h>

#ifdef STC_ENABLED

/**
 * Python str.split() using STC cstr
 */
cgen_string_list_t cgen_cstr_split(const cstr* s, const char* delimiter) {
    cgen_string_list_t result = vec_cstr_init();

    if (!s) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return result;
    }

    const char* str = cstr_str(s);
    size_t len = cstr_size(s);

    if (!str || len == 0) {
        return result; // Empty result for empty string
    }

    if (!delimiter || strlen(delimiter) == 0) {
        // Split on whitespace like Python
        const char* start = str;
        const char* end = str + len;

        while (start < end) {
            // Skip whitespace
            while (start < end && isspace((unsigned char)*start)) {
                start++;
            }

            if (start >= end) break;

            // Find end of word
            const char* word_end = start;
            while (word_end < end && !isspace((unsigned char)*word_end)) {
                word_end++;
            }

            // Add word to result
            cstr word = cstr_from_n(start, word_end - start);
            vec_cstr_push(&result, word);

            start = word_end;
        }
    } else {
        // Split on specific delimiter
        size_t delim_len = strlen(delimiter);
        const char* start = str;
        const char* pos;

        while ((pos = strstr(start, delimiter)) != NULL) {
            // Add substring before delimiter
            cstr part = cstr_from_n(start, pos - start);
            vec_cstr_push(&result, part);

            start = pos + delim_len;
        }

        // Add remaining part
        if (start < str + len) {
            cstr part = cstr_from_n(start, (str + len) - start);
            vec_cstr_push(&result, part);
        }
    }

    return result;
}

/**
 * Python str.join() using STC
 */
cstr cgen_cstr_join(const char* delimiter, const cgen_string_list_t* strings) {
    cstr result = cstr_init();

    if (!strings) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String list is NULL");
        return result;
    }

    if (!delimiter) delimiter = "";

    size_t count = vec_cstr_size(strings);
    for (size_t i = 0; i < count; i++) {
        const cstr* s = vec_cstr_at(strings, i);
        cstr_append(&result, cstr_str(s));

        if (i < count - 1) {
            cstr_append(&result, delimiter);
        }
    }

    return result;
}

/**
 * Python str.strip() using STC
 */
cstr cgen_cstr_strip(const cstr* s) {
    if (!s) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return cstr_init();
    }

    const char* str = cstr_str(s);
    size_t len = cstr_size(s);

    if (len == 0) {
        return cstr_init();
    }

    // Find start of non-whitespace
    const char* start = str;
    while (start < str + len && isspace((unsigned char)*start)) {
        start++;
    }

    // Find end of non-whitespace
    const char* end = str + len;
    while (end > start && isspace((unsigned char)*(end - 1))) {
        end--;
    }

    return cstr_from_n(start, end - start);
}

/**
 * Python str.startswith()
 */
int cgen_cstr_startswith(const cstr* s, const char* prefix) {
    if (!s || !prefix) return 0;

    const char* str = cstr_str(s);
    size_t str_len = cstr_size(s);
    size_t prefix_len = strlen(prefix);

    if (str_len < prefix_len) return 0;

    return strncmp(str, prefix, prefix_len) == 0;
}

/**
 * Python str.endswith()
 */
int cgen_cstr_endswith(const cstr* s, const char* suffix) {
    if (!s || !suffix) return 0;

    const char* str = cstr_str(s);
    size_t str_len = cstr_size(s);
    size_t suffix_len = strlen(suffix);

    if (str_len < suffix_len) return 0;

    return strcmp(str + str_len - suffix_len, suffix) == 0;
}

/**
 * Python str.find() with -1 for not found
 */
int cgen_cstr_find(const cstr* s, const char* substr) {
    if (!s || !substr) return -1;

    isize pos = cstr_find(s, substr);
    return (pos == c_NPOS) ? -1 : (int)pos;
}

/**
 * Python str.count()
 */
int cgen_cstr_count(const cstr* s, const char* substr) {
    if (!s || !substr) return 0;

    const char* str = cstr_str(s);
    size_t substr_len = strlen(substr);

    if (substr_len == 0) return 0;

    int count = 0;
    const char* pos = str;

    while ((pos = strstr(pos, substr)) != NULL) {
        count++;
        pos += substr_len;
    }

    return count;
}

#else

// Fallback implementation when STC is not available
cgen_string_list_t* cgen_string_list_new(void) {
    cgen_string_list_t* list = malloc(sizeof(cgen_string_list_t));
    if (!list) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate string list");
        return NULL;
    }

    list->strings = NULL;
    list->count = 0;
    list->capacity = 0;
    return list;
}

void cgen_string_list_free(cgen_string_list_t* list) {
    if (!list) return;

    for (size_t i = 0; i < list->count; i++) {
        free(list->strings[i]);
    }
    free(list->strings);
    free(list);
}

cgen_error_t cgen_string_list_add(cgen_string_list_t* list, const char* str) {
    if (!list || !str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid parameters");
        return CGEN_ERROR_VALUE;
    }

    if (list->count >= list->capacity) {
        size_t new_capacity = list->capacity == 0 ? 8 : list->capacity * 2;
        char** new_strings = realloc(list->strings, new_capacity * sizeof(char*));
        if (!new_strings) {
            CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to resize string list");
            return CGEN_ERROR_MEMORY;
        }
        list->strings = new_strings;
        list->capacity = new_capacity;
    }

    list->strings[list->count] = malloc(strlen(str) + 1);
    if (!list->strings[list->count]) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate string");
        return CGEN_ERROR_MEMORY;
    }

    strcpy(list->strings[list->count], str);
    list->count++;

    return CGEN_OK;
}

const char* cgen_string_list_get(const cgen_string_list_t* list, size_t index) {
    if (!list || index >= list->count) {
        return NULL;
    }
    return list->strings[index];
}

size_t cgen_string_list_size(const cgen_string_list_t* list) {
    return list ? list->count : 0;
}

#endif

/**
 * Common implementations (work with or without STC)
 */

size_t cgen_len_safe(const void* container, size_t (*size_func)(const void*)) {
    if (!container || !size_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid container or size function");
        return 0;
    }
    return size_func(container);
}

int cgen_normalize_index(int index, size_t size) {
    if (index < 0) {
        index += (int)size;
    }

    if (index < 0 || index >= (int)size) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_INDEX,
                           "Index %d out of range [0, %zu)", index, size);
        return -1;
    }

    return index;
}

void* cgen_vec_at_safe_impl(void* vec_ptr, int index,
                           size_t (*size_func)(const void*),
                           void* (*at_func)(void*, size_t),
                           const char* type_name) {
    if (!vec_ptr || !size_func || !at_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid vector parameters");
        return NULL;
    }

    size_t size = size_func(vec_ptr);
    int normalized_index = cgen_normalize_index(index, size);

    if (normalized_index < 0) {
        // Error already set by cgen_normalize_index
        return NULL;
    }

    return at_func(vec_ptr, (size_t)normalized_index);
}

void* cgen_map_get_safe_impl(void* map_ptr, const void* key,
                            void* (*get_func)(void*, const void*),
                            int (*contains_func)(void*, const void*),
                            const char* type_name) {
    if (!map_ptr || !key || !get_func || !contains_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid map parameters");
        return NULL;
    }

    if (!contains_func(map_ptr, key)) {
        CGEN_SET_ERROR_FMT(CGEN_ERROR_KEY, "Key not found in %s",
                           type_name ? type_name : "map");
        return NULL;
    }

    return get_func(map_ptr, key);
}

int cgen_in_vec_impl(void* vec_ptr, const void* element,
                    size_t (*size_func)(const void*),
                    void* (*at_func)(void*, size_t),
                    size_t element_size) {
    if (!vec_ptr || !element || !size_func || !at_func) {
        return 0;
    }

    size_t size = size_func(vec_ptr);
    for (size_t i = 0; i < size; i++) {
        void* vec_element = at_func(vec_ptr, i);
        if (vec_element && memcmp(element, vec_element, element_size) == 0) {
            return 1;
        }
    }

    return 0;
}

int cgen_in_map_impl(void* map_ptr, const void* key,
                    int (*contains_func)(void*, const void*)) {
    if (!map_ptr || !key || !contains_func) {
        return 0;
    }

    return contains_func(map_ptr, key);
}

void cgen_vec_enumerate_impl(void* vec_ptr,
                            cgen_enumerate_callback_t callback,
                            void* userdata,
                            size_t (*size_func)(const void*),
                            void* (*at_func)(void*, size_t)) {
    if (!vec_ptr || !callback || !size_func || !at_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid enumeration parameters");
        return;
    }

    size_t size = size_func(vec_ptr);
    for (size_t i = 0; i < size; i++) {
        void* element = at_func(vec_ptr, i);
        if (element) {
            callback(i, element, userdata);
        }
    }
}

void cgen_map_items_impl(void* map_ptr,
                        cgen_items_callback_t callback,
                        void* userdata,
                        void (*iter_func)(void*, cgen_items_callback_t, void*)) {
    if (!map_ptr || !callback || !iter_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid map iteration parameters");
        return;
    }

    iter_func(map_ptr, callback, userdata);
}

char* cgen_container_repr(void* container, const char* type_name,
                         char* (*element_repr)(const void*),
                         size_t (*size_func)(const void*),
                         void* (*at_func)(void*, size_t)) {
    if (!container || !size_func || !at_func || !element_repr) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid representation parameters");
        return NULL;
    }

    // Simplified implementation - would use cgen_buffer for full version
    return malloc(1); // Placeholder
}

// STC registry implementation
typedef struct stc_entry {
    void* container;
    void (*cleanup_func)(void*);
    char* type_name;
    struct stc_entry* next;
} stc_entry_t;

struct cgen_stc_registry {
    stc_entry_t* head;
    size_t count;
};

cgen_stc_registry_t* cgen_stc_registry_new(void) {
    cgen_stc_registry_t* registry = malloc(sizeof(cgen_stc_registry_t));
    if (!registry) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate STC registry");
        return NULL;
    }

    registry->head = NULL;
    registry->count = 0;
    return registry;
}

void cgen_stc_registry_free(cgen_stc_registry_t* registry) {
    if (!registry) return;

    cgen_stc_cleanup_all(registry);
    free(registry);
}

cgen_error_t cgen_stc_register_container(cgen_stc_registry_t* registry,
                                        void* container,
                                        void (*cleanup_func)(void*),
                                        const char* type_name) {
    if (!registry || !container || !cleanup_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid registry parameters");
        return CGEN_ERROR_VALUE;
    }

    stc_entry_t* entry = malloc(sizeof(stc_entry_t));
    if (!entry) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate registry entry");
        return CGEN_ERROR_MEMORY;
    }

    entry->container = container;
    entry->cleanup_func = cleanup_func;
    entry->type_name = type_name ? strdup(type_name) : NULL;
    entry->next = registry->head;

    registry->head = entry;
    registry->count++;

    return CGEN_OK;
}

void cgen_stc_cleanup_all(cgen_stc_registry_t* registry) {
    if (!registry) return;

    stc_entry_t* current = registry->head;
    while (current) {
        stc_entry_t* next = current->next;

        if (current->cleanup_func && current->container) {
            current->cleanup_func(current->container);
        }
        free(current->type_name);
        free(current);

        current = next;
    }

    registry->head = NULL;
    registry->count = 0;
}

#ifdef STC_ENABLED
cgen_error_t cgen_cstr_from_cstring(cstr* dest, const char* src) {
    if (!dest || !src) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid parameters for cstr conversion");
        return CGEN_ERROR_VALUE;
    }

    *dest = cstr_from(src);
    return CGEN_OK;
}
#endif

cgen_error_t cgen_normalize_slice(cgen_slice_t* slice, size_t container_size) {
    if (!slice) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Slice is NULL");
        return CGEN_ERROR_VALUE;
    }

    // Python slice normalization logic
    if (slice->step == 0) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Slice step cannot be zero");
        return CGEN_ERROR_VALUE;
    }

    // Normalize start and stop based on container size
    // This is a simplified implementation
    if (slice->start >= container_size) {
        slice->start = container_size;
    }
    if (slice->stop >= container_size) {
        slice->stop = container_size;
    }

    return CGEN_OK;
}

void* cgen_vec_slice_impl(void* src_vec, const cgen_slice_t* slice,
                         size_t (*size_func)(const void*),
                         void* (*at_func)(void*, size_t),
                         size_t element_size) {
    if (!src_vec || !slice || !size_func || !at_func) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid slice parameters");
        return NULL;
    }

    // Simplified implementation - would create new vector with sliced elements
    CGEN_SET_ERROR(CGEN_ERROR_RUNTIME, "Vector slicing not yet implemented");
    return NULL;
}