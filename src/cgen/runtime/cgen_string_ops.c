/**
 * CGen Runtime Library - String Operations Implementation
 */

#include "cgen_string_ops.h"
#include <stdarg.h>

// String array implementation
cgen_string_array_t* cgen_string_array_new(void) {
    cgen_string_array_t* arr = malloc(sizeof(cgen_string_array_t));
    if (!arr) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate string array");
        return NULL;
    }

    arr->strings = NULL;
    arr->count = 0;
    arr->capacity = 0;
    return arr;
}

void cgen_string_array_free(cgen_string_array_t* arr) {
    if (!arr) return;

    for (size_t i = 0; i < arr->count; i++) {
        free(arr->strings[i]);
    }
    free(arr->strings);
    free(arr);
}

cgen_error_t cgen_string_array_add(cgen_string_array_t* arr, char* str) {
    if (!arr) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String array is NULL");
        return CGEN_ERROR_VALUE;
    }

    if (arr->count >= arr->capacity) {
        size_t new_capacity = arr->capacity == 0 ? 8 : arr->capacity * 2;
        char** new_strings = realloc(arr->strings, new_capacity * sizeof(char*));
        if (!new_strings) {
            CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to resize string array");
            return CGEN_ERROR_MEMORY;
        }
        arr->strings = new_strings;
        arr->capacity = new_capacity;
    }

    arr->strings[arr->count++] = str;
    return CGEN_OK;
}

const char* cgen_string_array_get(cgen_string_array_t* arr, size_t index) {
    if (!arr || index >= arr->count) {
        return NULL;
    }
    return arr->strings[index];
}

size_t cgen_string_array_size(cgen_string_array_t* arr) {
    return arr ? arr->count : 0;
}

// String operations implementation
cgen_string_array_t* cgen_split(const char* str, const char* delimiter) {
    if (!str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return NULL;
    }

    cgen_string_array_t* result = cgen_string_array_new();
    if (!result) return NULL;

    char* str_copy = cgen_strdup(str);
    if (!str_copy) {
        cgen_string_array_free(result);
        return NULL;
    }

    if (!delimiter || strlen(delimiter) == 0) {
        // Split on whitespace
        char* token = strtok(str_copy, " \t\n\r\f\v");
        while (token) {
            char* token_copy = cgen_strdup(token);
            if (!token_copy || cgen_string_array_add(result, token_copy) != CGEN_OK) {
                free(str_copy);
                cgen_string_array_free(result);
                return NULL;
            }
            token = strtok(NULL, " \t\n\r\f\v");
        }
    } else {
        // Split on specific delimiter
        char* token = strtok(str_copy, delimiter);
        while (token) {
            char* token_copy = cgen_strdup(token);
            if (!token_copy || cgen_string_array_add(result, token_copy) != CGEN_OK) {
                free(str_copy);
                cgen_string_array_free(result);
                return NULL;
            }
            token = strtok(NULL, delimiter);
        }
    }

    free(str_copy);
    return result;
}

char* cgen_lower(const char* str) {
    if (!str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return NULL;
    }

    size_t len = strlen(str);
    char* result = malloc(len + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for lowercase string");
        return NULL;
    }

    for (size_t i = 0; i < len; i++) {
        result[i] = tolower((unsigned char)str[i]);
    }
    result[len] = '\0';

    return result;
}

char* cgen_upper(const char* str) {
    if (!str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return NULL;
    }

    size_t len = strlen(str);
    char* result = malloc(len + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for uppercase string");
        return NULL;
    }

    for (size_t i = 0; i < len; i++) {
        result[i] = toupper((unsigned char)str[i]);
    }
    result[len] = '\0';

    return result;
}

char* cgen_strip(const char* str) {
    return cgen_strip_chars(str, " \t\n\r\f\v");
}

char* cgen_strip_chars(const char* str, const char* chars) {
    if (!str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return NULL;
    }

    if (!chars) chars = " \t\n\r\f\v";

    // Find start of non-stripped content
    const char* start = str;
    while (*start && strchr(chars, *start)) {
        start++;
    }

    // Find end of non-stripped content
    const char* end = str + strlen(str);
    while (end > start && strchr(chars, *(end - 1))) {
        end--;
    }

    size_t len = end - start;
    char* result = malloc(len + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for stripped string");
        return NULL;
    }

    memcpy(result, start, len);
    result[len] = '\0';

    return result;
}

char* cgen_join(const char* delimiter, cgen_string_array_t* strings) {
    if (!strings || strings->count == 0) {
        return cgen_strdup("");
    }

    if (!delimiter) delimiter = "";

    // Calculate total length needed
    size_t total_len = 0;
    size_t delim_len = strlen(delimiter);

    for (size_t i = 0; i < strings->count; i++) {
        if (strings->strings[i]) {
            total_len += strlen(strings->strings[i]);
        }
        if (i < strings->count - 1) {
            total_len += delim_len;
        }
    }

    char* result = malloc(total_len + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for joined string");
        return NULL;
    }

    result[0] = '\0';
    for (size_t i = 0; i < strings->count; i++) {
        if (strings->strings[i]) {
            strcat(result, strings->strings[i]);
        }
        if (i < strings->count - 1) {
            strcat(result, delimiter);
        }
    }

    return result;
}

int cgen_startswith(const char* str, const char* prefix) {
    if (!str || !prefix) return 0;
    size_t prefix_len = strlen(prefix);
    if (strlen(str) < prefix_len) return 0;
    return strncmp(str, prefix, prefix_len) == 0;
}

int cgen_endswith(const char* str, const char* suffix) {
    if (!str || !suffix) return 0;
    size_t str_len = strlen(str);
    size_t suffix_len = strlen(suffix);
    if (str_len < suffix_len) return 0;
    return strcmp(str + str_len - suffix_len, suffix) == 0;
}

int cgen_find(const char* str, const char* substring) {
    if (!str || !substring) return -1;
    char* found = strstr(str, substring);
    return found ? (int)(found - str) : -1;
}

char* cgen_replace(const char* str, const char* old_str, const char* new_str) {
    if (!str || !old_str || !new_str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "NULL parameter in string replace");
        return NULL;
    }

    size_t old_len = strlen(old_str);
    size_t new_len = strlen(new_str);

    if (old_len == 0) {
        return cgen_strdup(str);
    }

    // Count occurrences
    int count = 0;
    const char* pos = str;
    while ((pos = strstr(pos, old_str)) != NULL) {
        count++;
        pos += old_len;
    }

    if (count == 0) {
        return cgen_strdup(str);
    }

    // Allocate result
    size_t result_len = strlen(str) + count * (new_len - old_len);
    char* result = malloc(result_len + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for string replacement");
        return NULL;
    }

    // Perform replacement
    char* dst = result;
    const char* src = str;
    while ((pos = strstr(src, old_str)) != NULL) {
        size_t prefix_len = pos - src;
        memcpy(dst, src, prefix_len);
        dst += prefix_len;
        memcpy(dst, new_str, new_len);
        dst += new_len;
        src = pos + old_len;
    }
    strcpy(dst, src);

    return result;
}

size_t cgen_strlen(const char* str) {
    return str ? strlen(str) : 0;
}

int cgen_isalpha_str(const char* str) {
    if (!str || *str == '\0') return 0;
    while (*str) {
        if (!isalpha((unsigned char)*str)) return 0;
        str++;
    }
    return 1;
}

int cgen_isdigit_str(const char* str) {
    if (!str || *str == '\0') return 0;
    while (*str) {
        if (!isdigit((unsigned char)*str)) return 0;
        str++;
    }
    return 1;
}

int cgen_isspace_str(const char* str) {
    if (!str || *str == '\0') return 0;
    while (*str) {
        if (!isspace((unsigned char)*str)) return 0;
        str++;
    }
    return 1;
}

char* cgen_strdup(const char* str) {
    if (!str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return NULL;
    }

    size_t len = strlen(str);
    char* result = malloc(len + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for string duplication");
        return NULL;
    }

    strcpy(result, str);
    return result;
}

char* cgen_strcat_new(const char* str1, const char* str2) {
    if (!str1 || !str2) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "String is NULL");
        return NULL;
    }

    size_t len1 = strlen(str1);
    size_t len2 = strlen(str2);
    char* result = malloc(len1 + len2 + 1);
    if (!result) {
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for string concatenation");
        return NULL;
    }

    strcpy(result, str1);
    strcat(result, str2);
    return result;
}

char* cgen_format_string(const char* template_str, ...) {
    if (!template_str) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Template string is NULL");
        return NULL;
    }

    // Simple implementation: just use vsnprintf for now
    // A more sophisticated implementation would parse {0}, {1}, etc.
    va_list args;
    va_start(args, template_str);

    // Calculate required size
    va_list args_copy;
    va_copy(args_copy, args);
    int len = vsnprintf(NULL, 0, template_str, args_copy);
    va_end(args_copy);

    if (len < 0) {
        va_end(args);
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid format string");
        return NULL;
    }

    char* result = malloc(len + 1);
    if (!result) {
        va_end(args);
        CGEN_SET_ERROR(CGEN_ERROR_MEMORY, "Failed to allocate memory for formatted string");
        return NULL;
    }

    vsnprintf(result, len + 1, template_str, args);
    va_end(args);

    return result;
}
