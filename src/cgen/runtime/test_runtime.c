/**
 * CGen Runtime Library - Test Program
 *
 * This test program validates the runtime library functionality.
 * It can be compiled and run to verify all components work correctly.
 */

#include "cgen_error_handling.h"
#include "cgen_string_ops.h"
#include "cgen_file_ops.h"
#include "cgen_container_ops.h"
#include "cgen_memory_ops.h"

#include <stdio.h>
#include <assert.h>

// Test counters
static int tests_run = 0;
static int tests_passed = 0;

#define TEST(name) \
    do { \
        printf("Running test: %s\n", #name); \
        tests_run++; \
        cgen_clear_error(); \
        if (test_##name()) { \
            tests_passed++; \
            printf("  PASSED\n"); \
        } else { \
            printf("  FAILED"); \
            if (cgen_has_error()) { \
                printf(": %s", cgen_get_last_error_message()); \
            } \
            printf("\n"); \
        } \
    } while(0)

// Error handling tests
int test_error_handling() {
    // Test setting and getting errors
    cgen_set_error(CGEN_ERROR_VALUE, "Test error message", __FILE__, __LINE__, __func__);

    if (cgen_get_last_error() != CGEN_ERROR_VALUE) return 0;
    if (strcmp(cgen_get_last_error_message(), "Test error message") != 0) return 0;
    if (!cgen_has_error()) return 0;

    cgen_clear_error();
    if (cgen_has_error()) return 0;
    if (cgen_get_last_error() != CGEN_OK) return 0;

    return 1;
}

// String operations tests
int test_string_operations() {
    // Test string duplication
    char* str = cgen_strdup("Hello, World!");
    if (!str || strcmp(str, "Hello, World!") != 0) {
        free(str);
        return 0;
    }
    free(str);

    // Test string lowering
    char* lower = cgen_lower("HELLO");
    if (!lower || strcmp(lower, "hello") != 0) {
        free(lower);
        return 0;
    }
    free(lower);

    // Test string splitting
    cgen_string_array_t* parts = cgen_split("one,two,three", ",");
    if (!parts || cgen_string_array_size(parts) != 3) {
        cgen_string_array_free(parts);
        return 0;
    }

    if (strcmp(cgen_string_array_get(parts, 0), "one") != 0 ||
        strcmp(cgen_string_array_get(parts, 1), "two") != 0 ||
        strcmp(cgen_string_array_get(parts, 2), "three") != 0) {
        cgen_string_array_free(parts);
        return 0;
    }
    cgen_string_array_free(parts);

    // Test string joining
    cgen_string_array_t* arr = cgen_string_array_new();
    cgen_string_array_add(arr, cgen_strdup("a"));
    cgen_string_array_add(arr, cgen_strdup("b"));
    cgen_string_array_add(arr, cgen_strdup("c"));

    char* joined = cgen_join("-", arr);
    if (!joined || strcmp(joined, "a-b-c") != 0) {
        free(joined);
        cgen_string_array_free(arr);
        return 0;
    }

    free(joined);
    cgen_string_array_free(arr);

    return 1;
}

// File operations tests
int test_file_operations() {
    const char* test_content = "Hello, File World!\nThis is a test file.\n";
    const char* filename = "/tmp/cgen_test.txt";

    // Test file writing
    if (cgen_write_file(filename, test_content) != CGEN_OK) {
        return 0;
    }

    // Test file existence
    if (!cgen_exists(filename)) {
        return 0;
    }

    // Test file reading
    char* content = cgen_read_file(filename);
    if (!content || strcmp(content, test_content) != 0) {
        free(content);
        return 0;
    }
    free(content);

    // Test file size
    long size = cgen_getsize(filename);
    if (size != (long)strlen(test_content)) {
        return 0;
    }

    // Clean up
    remove(filename);

    return 1;
}

// Memory operations tests
int test_memory_operations() {
    // Test safe allocation
    void* ptr = cgen_malloc(100);
    if (!ptr) return 0;
    cgen_free(&ptr);
    if (ptr != NULL) return 0;

    // Test memory pool
    cgen_memory_pool_t* pool = cgen_memory_pool_new(1024);
    if (!pool) return 0;

    void* ptr1 = cgen_memory_pool_alloc(pool, 50);
    void* ptr2 = cgen_memory_pool_alloc(pool, 100);
    if (!ptr1 || !ptr2) {
        cgen_memory_pool_free(pool);
        return 0;
    }

    cgen_memory_pool_free(pool);

    // Test scope allocator
    cgen_scope_allocator_t* scope = cgen_scope_new();
    if (!scope) return 0;

    void* scope_ptr = cgen_scope_alloc(scope, 200);
    if (!scope_ptr) {
        cgen_scope_free(scope);
        return 0;
    }

    cgen_scope_free(scope);

    // Test buffer
    cgen_buffer_t* buffer = cgen_buffer_new(10);
    if (!buffer) return 0;

    if (cgen_buffer_append_str(buffer, "Hello") != CGEN_OK ||
        cgen_buffer_append_str(buffer, ", World!") != CGEN_OK) {
        cgen_buffer_free(buffer);
        return 0;
    }

    if (strcmp(cgen_buffer_cstr(buffer), "Hello, World!") != 0) {
        cgen_buffer_free(buffer);
        return 0;
    }

    cgen_buffer_free(buffer);

    return 1;
}

// Container operations tests
int test_container_operations() {
    // Test container registry
    cgen_container_registry_t* registry = cgen_container_registry_new();
    if (!registry) return 0;

    void* test_ptr = malloc(100);
    if (cgen_register_container(registry, test_ptr, free, "test") != CGEN_OK) {
        free(test_ptr);
        cgen_container_registry_free(registry);
        return 0;
    }

    cgen_container_registry_free(registry);

    // Test bounds checking
    if (cgen_vec_bounds_check(5, 3, "test_vector")) {
        return 0; // Should return false for out-of-bounds
    }

    if (!cgen_vec_bounds_check(2, 5, "test_vector")) {
        return 0; // Should return true for in-bounds
    }

    return 1;
}

// Integration test
int test_integration() {
    // Test error propagation across modules
    cgen_string_array_t* arr = cgen_split(NULL, ",");
    if (arr != NULL || !cgen_has_error()) {
        return 0;
    }
    cgen_clear_error();

    // Test memory allocation in string operations
    char* str = cgen_lower("TEST");
    if (!str) return 0;

    cgen_buffer_t* buffer = cgen_buffer_new(10);
    if (!buffer) {
        free(str);
        return 0;
    }

    if (cgen_buffer_append_str(buffer, str) != CGEN_OK) {
        free(str);
        cgen_buffer_free(buffer);
        return 0;
    }

    if (strcmp(cgen_buffer_cstr(buffer), "test") != 0) {
        free(str);
        cgen_buffer_free(buffer);
        return 0;
    }

    free(str);
    cgen_buffer_free(buffer);

    return 1;
}

int main() {
    printf("CGen Runtime Library Test Suite\n");
    printf("===============================\n\n");

    // Run all tests
    TEST(error_handling);
    TEST(string_operations);
    TEST(file_operations);
    TEST(memory_operations);
    TEST(container_operations);
    TEST(integration);

    // Print results
    printf("\nTest Results:\n");
    printf("  Tests run: %d\n", tests_run);
    printf("  Tests passed: %d\n", tests_passed);
    printf("  Tests failed: %d\n", tests_run - tests_passed);

    if (tests_passed == tests_run) {
        printf("\nAll tests PASSED! ✓\n");
        return 0;
    } else {
        printf("\nSome tests FAILED! ✗\n");
        return 1;
    }
}