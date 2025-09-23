# CGen Runtime Library Makefile

CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -O2 -g
LDFLAGS =

# Source files
SOURCES = cgen_error_handling.c cgen_string_ops.c cgen_file_ops.c cgen_container_ops.c cgen_memory_ops.c
HEADERS = cgen_error_handling.h cgen_string_ops.h cgen_file_ops.h cgen_container_ops.h cgen_memory_ops.h
OBJECTS = $(SOURCES:.c=.o)

# Library
LIBRARY = libcgen_runtime.a

# Test program
TEST_PROGRAM = test_runtime
TEST_SOURCE = test_runtime.c

.PHONY: all clean test install

all: $(LIBRARY) $(TEST_PROGRAM)

$(LIBRARY): $(OBJECTS)
	ar rcs $@ $^
	@echo "Runtime library built: $(LIBRARY)"

$(TEST_PROGRAM): $(TEST_SOURCE) $(LIBRARY)
	$(CC) $(CFLAGS) -o $@ $< -L. -lcgen_runtime $(LDFLAGS)
	@echo "Test program built: $(TEST_PROGRAM)"

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

test: $(TEST_PROGRAM)
	@echo "Running runtime library tests..."
	./$(TEST_PROGRAM)

clean:
	rm -f $(OBJECTS) $(LIBRARY) $(TEST_PROGRAM)
	@echo "Cleaned build artifacts"

install: $(LIBRARY)
	@echo "Installing runtime library..."
	mkdir -p ../../../include/cgen
	cp $(HEADERS) ../../../include/cgen/
	mkdir -p ../../../lib
	cp $(LIBRARY) ../../../lib/
	@echo "Runtime library installed"

# Individual object file dependencies
cgen_error_handling.o: cgen_error_handling.c cgen_error_handling.h
cgen_string_ops.o: cgen_string_ops.c cgen_string_ops.h cgen_error_handling.h
cgen_file_ops.o: cgen_file_ops.c cgen_file_ops.h cgen_error_handling.h cgen_string_ops.h
cgen_container_ops.o: cgen_container_ops.c cgen_container_ops.h cgen_error_handling.h cgen_string_ops.h
cgen_memory_ops.o: cgen_memory_ops.c cgen_memory_ops.h cgen_error_handling.h

# Documentation
doc:
	@echo "CGen Runtime Library Documentation"
	@echo "=================================="
	@echo ""
	@echo "Components:"
	@echo "  - cgen_error_handling: Error handling and reporting"
	@echo "  - cgen_string_ops: String manipulation functions"
	@echo "  - cgen_file_ops: File I/O operations"
	@echo "  - cgen_container_ops: STC container helpers"
	@echo "  - cgen_memory_ops: Memory management utilities"
	@echo ""
	@echo "Usage:"
	@echo "  1. Build: make"
	@echo "  2. Test: make test"
	@echo "  3. Install: make install"
	@echo ""
	@echo "Integration:"
	@echo "  - Link with: -L../../../lib -lcgen_runtime"
	@echo "  - Include: #include <cgen/cgen_*.h>"

help: doc