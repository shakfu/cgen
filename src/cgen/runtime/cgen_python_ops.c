/**
 * CGen Runtime Library - Python-specific Operations Implementation
 */

#include "cgen_python_ops.h"
#include <math.h>
#include <limits.h>
#include <float.h>

// Global exception state
cgen_exception_t cgen_current_exception = {CGEN_OK, "", ""};

/**
 * Python bool() function implementations
 */
int cgen_bool(const void* obj, int (*is_truthy)(const void*)) {
    if (!obj || !is_truthy) return 0;
    return is_truthy(obj);
}

int cgen_bool_int(int value) {
    return value != 0;
}

int cgen_bool_float(double value) {
    return value != 0.0 && !isnan(value);
}

int cgen_bool_cstring(const char* str) {
    return str != NULL && str[0] != '\0';
}

/**
 * Python abs() function implementations
 */
int cgen_abs_int(int value) {
    return value < 0 ? -value : value;
}

double cgen_abs_float(double value) {
    return fabs(value);
}

/**
 * Python min() and max() implementations
 */
int cgen_min_int_array(const int* arr, size_t size) {
    if (!arr || size == 0) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "min() arg is an empty sequence");
        return 0;
    }

    int min_val = arr[0];
    for (size_t i = 1; i < size; i++) {
        if (arr[i] < min_val) {
            min_val = arr[i];
        }
    }
    return min_val;
}

int cgen_max_int_array(const int* arr, size_t size) {
    if (!arr || size == 0) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "max() arg is an empty sequence");
        return 0;
    }

    int max_val = arr[0];
    for (size_t i = 1; i < size; i++) {
        if (arr[i] > max_val) {
            max_val = arr[i];
        }
    }
    return max_val;
}

double cgen_min_float_array(const double* arr, size_t size) {
    if (!arr || size == 0) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "min() arg is an empty sequence");
        return 0.0;
    }

    double min_val = arr[0];
    for (size_t i = 1; i < size; i++) {
        if (arr[i] < min_val || isnan(min_val)) {
            min_val = arr[i];
        }
    }
    return min_val;
}

double cgen_max_float_array(const double* arr, size_t size) {
    if (!arr || size == 0) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "max() arg is an empty sequence");
        return 0.0;
    }

    double max_val = arr[0];
    for (size_t i = 1; i < size; i++) {
        if (arr[i] > max_val || isnan(max_val)) {
            max_val = arr[i];
        }
    }
    return max_val;
}

/**
 * Python sum() implementations
 */
int cgen_sum_int_array(const int* arr, size_t size) {
    if (!arr) return 0;

    int sum = 0;
    for (size_t i = 0; i < size; i++) {
        // Check for overflow
        if ((sum > 0 && arr[i] > INT_MAX - sum) ||
            (sum < 0 && arr[i] < INT_MIN - sum)) {
            cgen_raise_exception(CGEN_ERROR_VALUE, "Integer overflow in sum()");
            return 0;
        }
        sum += arr[i];
    }
    return sum;
}

double cgen_sum_float_array(const double* arr, size_t size) {
    if (!arr) return 0.0;

    double sum = 0.0;
    for (size_t i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

/**
 * Python range() implementations
 */
cgen_range_t cgen_range(int stop) {
    return cgen_range_full(0, stop, 1);
}

cgen_range_t cgen_range_start_stop(int start, int stop) {
    return cgen_range_full(start, stop, 1);
}

cgen_range_t cgen_range_full(int start, int stop, int step) {
    cgen_range_t range;
    range.start = start;
    range.stop = stop;
    range.step = step;
    range.current = start;

    if (step == 0) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "range() arg 3 must not be zero");
    }

    return range;
}

int cgen_range_next(cgen_range_t* range) {
    if (!range || !cgen_range_has_next(range)) {
        return 0;
    }

    int current = range->current;
    range->current += range->step;
    return current;
}

int cgen_range_has_next(const cgen_range_t* range) {
    if (!range) return 0;

    if (range->step > 0) {
        return range->current < range->stop;
    } else {
        return range->current > range->stop;
    }
}

/**
 * Character classification functions
 */
int cgen_isalpha_char(char c) {
    return isalpha((unsigned char)c);
}

int cgen_isdigit_char(char c) {
    return isdigit((unsigned char)c);
}

int cgen_isspace_char(char c) {
    return isspace((unsigned char)c);
}

int cgen_isalnum_char(char c) {
    return isalnum((unsigned char)c);
}

/**
 * Character case conversion
 */
char cgen_lower_char(char c) {
    return (char)tolower((unsigned char)c);
}

char cgen_upper_char(char c) {
    return (char)toupper((unsigned char)c);
}

/**
 * Python ord() and chr()
 */
int cgen_ord(char c) {
    return (int)(unsigned char)c;
}

char cgen_chr(int code) {
    if (code < 0 || code > 255) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "chr() arg not in range(256)");
        return '\0';
    }
    return (char)code;
}

/**
 * Comparison functions
 */
int cgen_cmp_int(int a, int b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

int cgen_cmp_float(double a, double b) {
    if (isnan(a) || isnan(b)) {
        return isnan(a) ? (isnan(b) ? 0 : -1) : 1;
    }
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

int cgen_cmp_string(const char* a, const char* b) {
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return strcmp(a, b);
}

/**
 * Python slice implementations
 */
cgen_python_slice_t cgen_slice_new(void) {
    cgen_python_slice_t slice = {0, 0, 1, 0, 0, 0};
    return slice;
}

cgen_python_slice_t cgen_slice_start_stop(int start, int stop) {
    cgen_python_slice_t slice = {start, stop, 1, 1, 1, 0};
    return slice;
}

cgen_python_slice_t cgen_slice_full(int start, int stop, int step) {
    cgen_python_slice_t slice = {start, stop, step, 1, 1, 1};
    return slice;
}

cgen_error_t cgen_normalize_python_slice(const cgen_python_slice_t* slice,
                                        size_t seq_len,
                                        cgen_normalized_slice_t* result) {
    if (!slice || !result) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Invalid slice parameters");
        return CGEN_ERROR_VALUE;
    }

    if (slice->has_step && slice->step == 0) {
        CGEN_SET_ERROR(CGEN_ERROR_VALUE, "Slice step cannot be zero");
        return CGEN_ERROR_VALUE;
    }

    int step = slice->has_step ? slice->step : 1;
    result->step = (size_t)abs(step);

    // Normalize start
    int start = slice->has_start ? slice->start : (step > 0 ? 0 : (int)seq_len - 1);
    if (start < 0) start += (int)seq_len;
    if (start < 0) start = (step > 0) ? 0 : -1;
    if (start >= (int)seq_len) start = (step > 0) ? (int)seq_len : (int)seq_len - 1;
    result->start = (size_t)start;

    // Normalize stop
    int stop = slice->has_stop ? slice->stop : (step > 0 ? (int)seq_len : -1);
    if (stop < 0) stop += (int)seq_len;
    if (stop < 0) stop = (step > 0) ? 0 : -1;
    if (stop >= (int)seq_len) stop = (step > 0) ? (int)seq_len : (int)seq_len - 1;
    result->stop = (size_t)stop;

    // Calculate length
    if (step > 0) {
        result->length = (result->start < result->stop) ?
                        (result->stop - result->start + result->step - 1) / result->step : 0;
    } else {
        result->length = (result->start > result->stop) ?
                        (result->start - result->stop + result->step - 1) / result->step : 0;
    }

    return CGEN_OK;
}

/**
 * Exception handling
 */
void cgen_raise_exception(cgen_error_t type, const char* message) {
    cgen_current_exception.type = type;
    if (message) {
        strncpy(cgen_current_exception.message, message,
                sizeof(cgen_current_exception.message) - 1);
        cgen_current_exception.message[sizeof(cgen_current_exception.message) - 1] = '\0';
    } else {
        cgen_current_exception.message[0] = '\0';
    }
    // Simple traceback - could be enhanced
    snprintf(cgen_current_exception.traceback, sizeof(cgen_current_exception.traceback),
             "Traceback: %s", cgen_error_name(type));
}

void cgen_clear_exception(void) {
    cgen_current_exception.type = CGEN_OK;
    cgen_current_exception.message[0] = '\0';
    cgen_current_exception.traceback[0] = '\0';
}

int cgen_has_exception(void) {
    return cgen_current_exception.type != CGEN_OK;
}

const cgen_exception_t* cgen_get_exception(void) {
    return &cgen_current_exception;
}

/**
 * Truthiness testing
 */
int cgen_is_truthy_int(int value) {
    return value != 0;
}

int cgen_is_truthy_float(double value) {
    return value != 0.0 && !isnan(value);
}

int cgen_is_truthy_cstring(const char* str) {
    return str != NULL && str[0] != '\0';
}

int cgen_is_truthy_pointer(const void* ptr) {
    return ptr != NULL;
}

/**
 * Type system
 */
const char* cgen_type_name(cgen_python_type_t type) {
    switch (type) {
        case CGEN_TYPE_NONE: return "NoneType";
        case CGEN_TYPE_BOOL: return "bool";
        case CGEN_TYPE_INT: return "int";
        case CGEN_TYPE_FLOAT: return "float";
        case CGEN_TYPE_STRING: return "str";
        case CGEN_TYPE_LIST: return "list";
        case CGEN_TYPE_DICT: return "dict";
        case CGEN_TYPE_SET: return "set";
        case CGEN_TYPE_TUPLE: return "tuple";
        default: return "unknown";
    }
}

/**
 * Simple format string operations
 */
char* cgen_format_simple(const char* template_str, const char* arg) {
    if (!template_str || !arg) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "Invalid format parameters");
        return NULL;
    }

    // Find {} in template and replace with arg
    const char* placeholder = strstr(template_str, "{}");
    if (!placeholder) {
        // No placeholder, just return copy of template
        size_t len = strlen(template_str);
        char* result = malloc(len + 1);
        if (!result) {
            cgen_raise_exception(CGEN_ERROR_MEMORY, "Failed to allocate format result");
            return NULL;
        }
        strcpy(result, template_str);
        return result;
    }

    size_t prefix_len = placeholder - template_str;
    size_t suffix_len = strlen(placeholder + 2); // Skip "{}"
    size_t arg_len = strlen(arg);
    size_t total_len = prefix_len + arg_len + suffix_len;

    char* result = malloc(total_len + 1);
    if (!result) {
        cgen_raise_exception(CGEN_ERROR_MEMORY, "Failed to allocate format result");
        return NULL;
    }

    memcpy(result, template_str, prefix_len);
    memcpy(result + prefix_len, arg, arg_len);
    strcpy(result + prefix_len + arg_len, placeholder + 2);

    return result;
}

char* cgen_format_int(const char* template_str, int value) {
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "%d", value);
    return cgen_format_simple(template_str, buffer);
}

char* cgen_format_float(const char* template_str, double value) {
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%g", value);
    return cgen_format_simple(template_str, buffer);
}

/**
 * Python zip() implementation
 */
cgen_zip_iterator_t cgen_zip_arrays(void* arr1, size_t size1, size_t elem_size1,
                                   void* arr2, size_t size2, size_t elem_size2) {
    cgen_zip_iterator_t iter;
    iter.first = arr1;
    iter.second = arr2;
    iter.index = 0;
    iter.size1 = size1;
    iter.size2 = size2;
    iter.element_size1 = elem_size1;
    iter.element_size2 = elem_size2;
    return iter;
}

int cgen_zip_next(cgen_zip_iterator_t* iter, void** elem1, void** elem2) {
    if (!iter || !elem1 || !elem2) return 0;

    if (iter->index >= iter->size1 || iter->index >= iter->size2) {
        return 0; // End of iteration
    }

    *elem1 = (char*)iter->first + iter->index * iter->element_size1;
    *elem2 = (char*)iter->second + iter->index * iter->element_size2;
    iter->index++;

    return 1;
}

/**
 * Python enumerate() implementation
 */
void cgen_enumerate_array(void* array, size_t size, size_t element_size,
                         cgen_python_enumerate_callback_t callback, void* userdata) {
    if (!array || !callback) {
        cgen_raise_exception(CGEN_ERROR_VALUE, "Invalid enumerate parameters");
        return;
    }

    for (size_t i = 0; i < size; i++) {
        cgen_enumerate_item_t item;
        item.index = i;
        item.element = (char*)array + i * element_size;
        callback(&item, userdata);
    }
}