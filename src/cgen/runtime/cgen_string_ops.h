/**
 * CGen Runtime Library - String Operations
 *
 * Provides C implementations of common Python string operations.
 * These functions handle memory management and error reporting automatically.
 */

#ifndef CGEN_STRING_OPS_H
#define CGEN_STRING_OPS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "cgen_error_handling.h"

#ifdef __cplusplus
extern "C" {
#endif

// String array structure for storing multiple strings
typedef struct {
    char** strings;
    size_t count;
    size_t capacity;
} cgen_string_array_t;

/**
 * Create a new string array
 */
cgen_string_array_t* cgen_string_array_new(void);

/**
 * Free a string array and all its strings
 */
void cgen_string_array_free(cgen_string_array_t* arr);

/**
 * Add a string to the array (takes ownership of the string)
 */
cgen_error_t cgen_string_array_add(cgen_string_array_t* arr, char* str);

/**
 * Get string at index (returns NULL if out of bounds)
 */
const char* cgen_string_array_get(cgen_string_array_t* arr, size_t index);

/**
 * Get the number of strings in the array
 */
size_t cgen_string_array_size(cgen_string_array_t* arr);

/**
 * Python str.split() equivalent
 * Splits a string by delimiter and returns a string array
 * If delimiter is NULL or empty, splits on whitespace
 */
cgen_string_array_t* cgen_split(const char* str, const char* delimiter);

/**
 * Python str.lower() equivalent
 * Returns a new lowercase string (caller must free)
 */
char* cgen_lower(const char* str);

/**
 * Python str.upper() equivalent
 * Returns a new uppercase string (caller must free)
 */
char* cgen_upper(const char* str);

/**
 * Python str.strip() equivalent
 * Returns a new string with leading/trailing whitespace removed (caller must free)
 */
char* cgen_strip(const char* str);

/**
 * Python str.strip(chars) equivalent
 * Returns a new string with leading/trailing chars removed (caller must free)
 */
char* cgen_strip_chars(const char* str, const char* chars);

/**
 * Python str.join() equivalent
 * Joins strings in array with delimiter (caller must free result)
 */
char* cgen_join(const char* delimiter, cgen_string_array_t* strings);

/**
 * Python str.startswith() equivalent
 */
int cgen_startswith(const char* str, const char* prefix);

/**
 * Python str.endswith() equivalent
 */
int cgen_endswith(const char* str, const char* suffix);

/**
 * Python str.find() equivalent
 * Returns index of substring or -1 if not found
 */
int cgen_find(const char* str, const char* substring);

/**
 * Python str.replace() equivalent
 * Returns a new string with all occurrences replaced (caller must free)
 */
char* cgen_replace(const char* str, const char* old_str, const char* new_str);

/**
 * Python len(str) equivalent
 */
size_t cgen_strlen(const char* str);

/**
 * Python str.isalpha() equivalent
 */
int cgen_isalpha_str(const char* str);

/**
 * Python str.isdigit() equivalent
 */
int cgen_isdigit_str(const char* str);

/**
 * Python str.isspace() equivalent
 */
int cgen_isspace_str(const char* str);

/**
 * Safe string duplication with error handling
 */
char* cgen_strdup(const char* str);

/**
 * Safe string concatenation with error handling
 */
char* cgen_strcat_new(const char* str1, const char* str2);

/**
 * Format string similar to Python f-strings (simplified)
 * Replaces {0}, {1}, etc. with provided arguments
 */
char* cgen_format_string(const char* template_str, ...);

// Type-specific wrapper functions for generated code compatibility
static inline char* cgen_str_upper(const char* str) { return cgen_upper(str); }
static inline char* cgen_str_lower(const char* str) { return cgen_lower(str); }
static inline int cgen_str_find(const char* str, const char* substring) { return cgen_find(str, substring); }

#ifdef __cplusplus
}
#endif

#endif // CGEN_STRING_OPS_H
