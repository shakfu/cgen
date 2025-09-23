/**
 * CGen Runtime Library - Error Handling
 *
 * Provides error handling and reporting utilities for generated C code.
 * This module handles runtime errors in a consistent, Python-like manner.
 */

#ifndef CGEN_ERROR_HANDLING_H
#define CGEN_ERROR_HANDLING_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#ifdef __cplusplus
extern "C" {
#endif

// Error codes matching common Python exceptions
typedef enum {
    CGEN_OK = 0,
    CGEN_ERROR_GENERIC = 1,
    CGEN_ERROR_MEMORY = 2,          // MemoryError
    CGEN_ERROR_INDEX = 3,           // IndexError
    CGEN_ERROR_KEY = 4,             // KeyError
    CGEN_ERROR_VALUE = 5,           // ValueError
    CGEN_ERROR_TYPE = 6,            // TypeError
    CGEN_ERROR_IO = 7,              // IOError/OSError
    CGEN_ERROR_FILE_NOT_FOUND = 8, // FileNotFoundError
    CGEN_ERROR_PERMISSION = 9,      // PermissionError
    CGEN_ERROR_RUNTIME = 10         // RuntimeError
} cgen_error_t;

// Error context structure
typedef struct {
    cgen_error_t code;
    char message[512];
    const char* file;
    int line;
    const char* function;
} cgen_error_context_t;

// Global error context (thread-local in multi-threaded environments)
extern cgen_error_context_t cgen_last_error;

/**
 * Set error with detailed context information
 */
void cgen_set_error(cgen_error_t code, const char* message,
                   const char* file, int line, const char* function);

/**
 * Set error with formatted message
 */
void cgen_set_error_fmt(cgen_error_t code, const char* file, int line,
                       const char* function, const char* format, ...);

/**
 * Get the last error code
 */
cgen_error_t cgen_get_last_error(void);

/**
 * Get the last error message
 */
const char* cgen_get_last_error_message(void);

/**
 * Clear the last error
 */
void cgen_clear_error(void);

/**
 * Check if there's a pending error
 */
int cgen_has_error(void);

/**
 * Print error information to stderr
 */
void cgen_print_error(void);

/**
 * Convert system errno to CGen error code
 */
cgen_error_t cgen_errno_to_error(int errno_val);

/**
 * Get error name as string
 */
const char* cgen_error_name(cgen_error_t code);

// Convenience macros for error handling
#define CGEN_SET_ERROR(code, msg) \
    cgen_set_error((code), (msg), __FILE__, __LINE__, __func__)

#define CGEN_SET_ERROR_FMT(code, fmt, ...) \
    cgen_set_error_fmt((code), __FILE__, __LINE__, __func__, (fmt), ##__VA_ARGS__)

#define CGEN_RETURN_IF_ERROR(expr) \
    do { \
        if ((expr) != CGEN_OK) { \
            return cgen_get_last_error(); \
        } \
    } while(0)

#define CGEN_CHECK_NULL(ptr, msg) \
    do { \
        if ((ptr) == NULL) { \
            CGEN_SET_ERROR(CGEN_ERROR_MEMORY, (msg)); \
            return CGEN_ERROR_MEMORY; \
        } \
    } while(0)

#define CGEN_CHECK_BOUNDS(index, size, msg) \
    do { \
        if ((index) < 0 || (index) >= (size)) { \
            CGEN_SET_ERROR_FMT(CGEN_ERROR_INDEX, "%s: index %d out of bounds [0, %d)", \
                               (msg), (index), (size)); \
            return CGEN_ERROR_INDEX; \
        } \
    } while(0)

#ifdef __cplusplus
}
#endif

#endif // CGEN_ERROR_HANDLING_H
