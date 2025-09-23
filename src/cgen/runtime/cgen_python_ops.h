/**
 * CGen Runtime Library - Python-specific Operations
 *
 * Provides Python-specific operations that complement STC containers.
 * This module focuses on Python semantics not naturally provided by STC.
 */

#ifndef CGEN_PYTHON_OPS_H
#define CGEN_PYTHON_OPS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "cgen_error_handling.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Python built-in functions that aren't container-specific
 */

/**
 * Python bool() function
 */
int cgen_bool(const void* obj, int (*is_truthy)(const void*));

/**
 * Python bool() for integers
 */
int cgen_bool_int(int value);

/**
 * Python bool() for floats
 */
int cgen_bool_float(double value);

/**
 * Python bool() for strings (C string version)
 */
int cgen_bool_cstring(const char* str);

/**
 * Python abs() function
 */
int cgen_abs_int(int value);
double cgen_abs_float(double value);

/**
 * Python min() and max() for arrays
 */
int cgen_min_int_array(const int* arr, size_t size);
int cgen_max_int_array(const int* arr, size_t size);
double cgen_min_float_array(const double* arr, size_t size);
double cgen_max_float_array(const double* arr, size_t size);

/**
 * Python sum() for arrays
 */
int cgen_sum_int_array(const int* arr, size_t size);
double cgen_sum_float_array(const double* arr, size_t size);

/**
 * Python range() functionality
 */
typedef struct {
    int start;
    int stop;
    int step;
    int current;
} cgen_range_t;

cgen_range_t cgen_range(int stop);
cgen_range_t cgen_range_start_stop(int start, int stop);
cgen_range_t cgen_range_full(int start, int stop, int step);

int cgen_range_next(cgen_range_t* range);
int cgen_range_has_next(const cgen_range_t* range);

/**
 * Python-style string character classification
 */
int cgen_isalpha_char(char c);
int cgen_isdigit_char(char c);
int cgen_isspace_char(char c);
int cgen_isalnum_char(char c);

/**
 * Python-style string case conversion for single characters
 */
char cgen_lower_char(char c);
char cgen_upper_char(char c);

/**
 * Python ord() and chr() functions
 */
int cgen_ord(char c);
char cgen_chr(int code);

/**
 * Python-style comparison functions
 */
int cgen_cmp_int(int a, int b);
int cgen_cmp_float(double a, double b);
int cgen_cmp_string(const char* a, const char* b);

/**
 * Python-style slice object
 */
typedef struct {
    int start;
    int stop;
    int step;
    int has_start;
    int has_stop;
    int has_step;
} cgen_python_slice_t;

cgen_python_slice_t cgen_slice_new(void);
cgen_python_slice_t cgen_slice_start_stop(int start, int stop);
cgen_python_slice_t cgen_slice_full(int start, int stop, int step);

/**
 * Normalize Python slice for a given sequence length
 */
typedef struct {
    size_t start;
    size_t stop;
    size_t step;
    size_t length;
} cgen_normalized_slice_t;

cgen_error_t cgen_normalize_python_slice(const cgen_python_slice_t* slice,
                                        size_t seq_len,
                                        cgen_normalized_slice_t* result);

/**
 * Python-style exception information
 */
typedef struct {
    cgen_error_t type;
    char message[256];
    char traceback[512];
} cgen_exception_t;

extern cgen_exception_t cgen_current_exception;

void cgen_raise_exception(cgen_error_t type, const char* message);
void cgen_clear_exception(void);
int cgen_has_exception(void);
const cgen_exception_t* cgen_get_exception(void);

/**
 * Python-style assert
 */
#define cgen_assert(condition, message) \
    do { \
        if (!(condition)) { \
            cgen_raise_exception(CGEN_ERROR_RUNTIME, message); \
            return; \
        } \
    } while(0)

#define cgen_assert_return(condition, message, retval) \
    do { \
        if (!(condition)) { \
            cgen_raise_exception(CGEN_ERROR_RUNTIME, message); \
            return (retval); \
        } \
    } while(0)

/**
 * Python-style try/except simulation
 */
#define CGEN_TRY \
    do { \
        cgen_clear_exception(); \

#define CGEN_EXCEPT(error_type) \
        if (cgen_has_exception() && cgen_get_exception()->type == (error_type)) {

#define CGEN_EXCEPT_ANY \
        if (cgen_has_exception()) {

#define CGEN_FINALLY \
        } \
        if (1) {

#define CGEN_END_TRY \
        } \
    } while(0)

/**
 * Python-style truthiness testing
 */
int cgen_is_truthy_int(int value);
int cgen_is_truthy_float(double value);
int cgen_is_truthy_cstring(const char* str);
int cgen_is_truthy_pointer(const void* ptr);

/**
 * Python-style type checking
 */
typedef enum {
    CGEN_TYPE_NONE,
    CGEN_TYPE_BOOL,
    CGEN_TYPE_INT,
    CGEN_TYPE_FLOAT,
    CGEN_TYPE_STRING,
    CGEN_TYPE_LIST,
    CGEN_TYPE_DICT,
    CGEN_TYPE_SET,
    CGEN_TYPE_TUPLE
} cgen_python_type_t;

const char* cgen_type_name(cgen_python_type_t type);

/**
 * Python-style format string operations (simplified)
 */
char* cgen_format_simple(const char* template_str, const char* arg);
char* cgen_format_int(const char* template_str, int value);
char* cgen_format_float(const char* template_str, double value);

/**
 * Python zip() functionality for two arrays
 */
typedef struct {
    void* first;
    void* second;
    size_t index;
    size_t size1;
    size_t size2;
    size_t element_size1;
    size_t element_size2;
} cgen_zip_iterator_t;

cgen_zip_iterator_t cgen_zip_arrays(void* arr1, size_t size1, size_t elem_size1,
                                   void* arr2, size_t size2, size_t elem_size2);

int cgen_zip_next(cgen_zip_iterator_t* iter, void** elem1, void** elem2);

/**
 * Python-style iteration helpers
 */
typedef struct {
    size_t index;
    void* element;
} cgen_enumerate_item_t;

typedef void (*cgen_python_enumerate_callback_t)(const cgen_enumerate_item_t* item, void* userdata);

void cgen_enumerate_array(void* array, size_t size, size_t element_size,
                         cgen_python_enumerate_callback_t callback, void* userdata);

#ifdef __cplusplus
}
#endif

#endif // CGEN_PYTHON_OPS_H