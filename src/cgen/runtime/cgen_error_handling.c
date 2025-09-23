/**
 * CGen Runtime Library - Error Handling Implementation
 */

#include "cgen_error_handling.h"
#include <stdarg.h>

// Global error context
cgen_error_context_t cgen_last_error = {CGEN_OK, "", NULL, 0, NULL};

void cgen_set_error(cgen_error_t code, const char* message,
                   const char* file, int line, const char* function) {
    cgen_last_error.code = code;
    cgen_last_error.file = file;
    cgen_last_error.line = line;
    cgen_last_error.function = function;

    if (message) {
        strncpy(cgen_last_error.message, message, sizeof(cgen_last_error.message) - 1);
        cgen_last_error.message[sizeof(cgen_last_error.message) - 1] = '\0';
    } else {
        cgen_last_error.message[0] = '\0';
    }
}

void cgen_set_error_fmt(cgen_error_t code, const char* file, int line,
                       const char* function, const char* format, ...) {
    cgen_last_error.code = code;
    cgen_last_error.file = file;
    cgen_last_error.line = line;
    cgen_last_error.function = function;

    if (format) {
        va_list args;
        va_start(args, format);
        vsnprintf(cgen_last_error.message, sizeof(cgen_last_error.message), format, args);
        va_end(args);
    } else {
        cgen_last_error.message[0] = '\0';
    }
}

cgen_error_t cgen_get_last_error(void) {
    return cgen_last_error.code;
}

const char* cgen_get_last_error_message(void) {
    return cgen_last_error.message;
}

void cgen_clear_error(void) {
    cgen_last_error.code = CGEN_OK;
    cgen_last_error.message[0] = '\0';
    cgen_last_error.file = NULL;
    cgen_last_error.line = 0;
    cgen_last_error.function = NULL;
}

int cgen_has_error(void) {
    return cgen_last_error.code != CGEN_OK;
}

void cgen_print_error(void) {
    if (cgen_has_error()) {
        fprintf(stderr, "CGen Runtime Error [%s]: %s\n",
                cgen_error_name(cgen_last_error.code),
                cgen_last_error.message);

        if (cgen_last_error.file && cgen_last_error.function) {
            fprintf(stderr, "  at %s:%d in %s()\n",
                    cgen_last_error.file,
                    cgen_last_error.line,
                    cgen_last_error.function);
        }
    }
}

cgen_error_t cgen_errno_to_error(int errno_val) {
    switch (errno_val) {
        case ENOMEM:
            return CGEN_ERROR_MEMORY;
        case ENOENT:
            return CGEN_ERROR_FILE_NOT_FOUND;
        case EACCES:
        case EPERM:
            return CGEN_ERROR_PERMISSION;
        case EIO:
            return CGEN_ERROR_IO;
        case EINVAL:
            return CGEN_ERROR_VALUE;
        default:
            return CGEN_ERROR_RUNTIME;
    }
}

const char* cgen_error_name(cgen_error_t code) {
    switch (code) {
        case CGEN_OK:
            return "OK";
        case CGEN_ERROR_GENERIC:
            return "GenericError";
        case CGEN_ERROR_MEMORY:
            return "MemoryError";
        case CGEN_ERROR_INDEX:
            return "IndexError";
        case CGEN_ERROR_KEY:
            return "KeyError";
        case CGEN_ERROR_VALUE:
            return "ValueError";
        case CGEN_ERROR_TYPE:
            return "TypeError";
        case CGEN_ERROR_IO:
            return "IOError";
        case CGEN_ERROR_FILE_NOT_FOUND:
            return "FileNotFoundError";
        case CGEN_ERROR_PERMISSION:
            return "PermissionError";
        case CGEN_ERROR_RUNTIME:
            return "RuntimeError";
        default:
            return "UnknownError";
    }
}
