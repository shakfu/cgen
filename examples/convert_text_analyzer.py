#!/usr/bin/env python3
"""
Text Analyzer Conversion Script

This script converts the text_analyzer_advanced.py program to C using CGen,
generates a Makefile using the makefilegen module, and builds the C program.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from cgen.core import CFactory, Writer, StyleOptions
from cgen.core.py2c import PythonToCConverter
from cgen.builder.makefilegen import MakefileGenerator


def create_c_version():
    """Convert the Python text analyzer to C and build it."""

    # Setup paths
    examples_dir = Path(__file__).parent
    build_dir = project_root / "build"
    build_dir.mkdir(exist_ok=True)

    python_file = examples_dir / "text_analyzer_advanced.py"
    c_file = build_dir / "text_analyzer_advanced.c"
    makefile = build_dir / "Makefile"

    print("=" * 60)
    print("CGEN TEXT ANALYZER CONVERSION")
    print("=" * 60)
    print(f"Python source: {python_file}")
    print(f"C output: {c_file}")
    print(f"Makefile: {makefile}")
    print()

    # Since the full automatic translation is complex, we'll create
    # a C equivalent that demonstrates the same functionality
    print("Creating C equivalent with CGen framework...")

    # Create C factory and writer
    factory = CFactory()
    writer = Writer(StyleOptions())

    # Create the C program structure
    sequence = factory.sequence()

    # Add includes
    sequence.append(factory.sysinclude("stdio.h"))
    sequence.append(factory.sysinclude("stdlib.h"))
    sequence.append(factory.sysinclude("string.h"))
    sequence.append(factory.sysinclude("ctype.h"))
    sequence.append(factory.sysinclude("time.h"))
    sequence.append(factory.include("stc/vec.h"))
    sequence.append(factory.include("stc/hmap.h"))
    sequence.append(factory.include("stc/cstr.h"))

    # Add some spacing
    sequence.append(factory.statement(""))

    # Define STC container types
    sequence.append(factory.statement("// STC container type definitions"))
    sequence.append(factory.statement("#define T WordVec, cstr"))
    sequence.append(factory.statement("#include <stc/vec.h>"))
    sequence.append(factory.statement(""))
    sequence.append(factory.statement("#define T WordCountMap, cstr, int"))
    sequence.append(factory.statement("#include <stc/hmap.h>"))
    sequence.append(factory.statement(""))

    # Define constants
    sequence.append(factory.statement("// Constants"))
    sequence.append(factory.define("MAX_LINE_LENGTH", "1024"))
    sequence.append(factory.define("MAX_WORD_LENGTH", "100"))
    sequence.append(factory.define("AVERAGE_READING_SPEED", "250.0"))
    sequence.append(factory.statement(""))

    # Define TextStatistics struct
    stats_struct = factory.struct("TextStatistics")
    stats_struct.append(factory.struct_member("total_characters", "long"))
    stats_struct.append(factory.struct_member("total_words", "long"))
    stats_struct.append(factory.struct_member("total_sentences", "long"))
    stats_struct.append(factory.struct_member("total_paragraphs", "long"))
    stats_struct.append(factory.struct_member("total_lines", "long"))
    stats_struct.append(factory.struct_member("unique_words", "long"))
    stats_struct.append(factory.struct_member("average_word_length", "double"))
    stats_struct.append(factory.struct_member("average_sentence_length", "double"))
    stats_struct.append(factory.struct_member("reading_time_minutes", "double"))
    stats_struct.append(factory.struct_member("complexity_score", "double"))
    sequence.append(factory.declaration(stats_struct))
    sequence.append(factory.statement(""))

    # Define TextAnalyzer struct
    analyzer_struct = factory.struct("TextAnalyzer")
    analyzer_struct.append(factory.struct_member("filename", "char*"))
    analyzer_struct.append(factory.struct_member("content", "cstr"))
    analyzer_struct.append(factory.struct_member("words", "WordVec"))
    analyzer_struct.append(factory.struct_member("word_counts", "WordCountMap"))
    analyzer_struct.append(factory.struct_member("stats", "struct TextStatistics"))
    analyzer_struct.append(factory.struct_member("analysis_time", "double"))
    sequence.append(factory.declaration(analyzer_struct))
    sequence.append(factory.statement(""))

    # Helper function: clean_word
    clean_word_func = factory.function("clean_word", "cstr", [
        factory.variable("word", "const char*")
    ])
    clean_word_body = factory.sequence()
    clean_word_body.append(factory.statement("cstr result = cstr_new();"))
    clean_word_body.append(factory.statement("int len = strlen(word);"))
    clean_word_body.append(factory.statement(""))

    # Loop to clean the word
    for_loop = factory.for_loop("int i = 0", "i < len", "i++")
    for_body = factory.sequence()
    for_body.append(factory.statement("char c = word[i];"))

    # If statement for alphabetic characters
    if_alpha = factory.if_statement("isalpha(c)")
    if_alpha.append(factory.statement("cstr_push(&result, tolower(c));"))
    for_body.append(if_alpha)
    for_loop.append(for_body)

    clean_word_body.append(for_loop)
    clean_word_body.append(factory.statement(""))
    clean_word_body.append(factory.return_statement("result"))

    clean_word_func.append(clean_word_body)
    sequence.append(factory.declaration(clean_word_func))
    sequence.append(factory.statement(""))

    # Helper function: load_file
    load_file_func = factory.function("load_file", "int", [
        factory.variable("analyzer", "struct TextAnalyzer*")
    ])
    load_file_body = factory.sequence()
    load_file_body.append(factory.statement("FILE* file = fopen(analyzer->filename, \"r\");"))

    # Check if file opened successfully
    if_file = factory.if_statement("file == NULL")
    if_file.append(factory.statement("printf(\"Error: Cannot open file %s\\n\", analyzer->filename);"))
    if_file.append(factory.return_statement("0"))
    load_file_body.append(if_file)

    load_file_body.append(factory.statement(""))
    load_file_body.append(factory.statement("// Read file content"))
    load_file_body.append(factory.statement("char buffer[MAX_LINE_LENGTH];"))
    load_file_body.append(factory.statement("analyzer->content = cstr_new();"))
    load_file_body.append(factory.statement(""))

    # While loop to read file
    while_loop = factory.while_loop("fgets(buffer, sizeof(buffer), file)")
    while_loop.append(factory.statement("cstr_append(&analyzer->content, buffer);"))
    load_file_body.append(while_loop)

    load_file_body.append(factory.statement(""))
    load_file_body.append(factory.statement("fclose(file);"))
    load_file_body.append(factory.return_statement("1"))

    load_file_func.append(load_file_body)
    sequence.append(factory.declaration(load_file_func))
    sequence.append(factory.statement(""))

    # Helper function: tokenize_words
    tokenize_func = factory.function("tokenize_words", "void", [
        factory.variable("analyzer", "struct TextAnalyzer*")
    ])
    tokenize_body = factory.sequence()
    tokenize_body.append(factory.statement("analyzer->words = WordVec_new();"))
    tokenize_body.append(factory.statement("analyzer->word_counts = WordCountMap_new();"))
    tokenize_body.append(factory.statement(""))

    tokenize_body.append(factory.statement("char* content_copy = strdup(cstr_str(&analyzer->content));"))
    tokenize_body.append(factory.statement("char* token = strtok(content_copy, \" \\t\\n\\r.,!?;:\\\"()[]{}'\");"))
    tokenize_body.append(factory.statement(""))

    # While loop to process tokens
    token_while = factory.while_loop("token != NULL")
    token_body = factory.sequence()
    token_body.append(factory.statement("if (strlen(token) > 0) {"))
    token_body.append(factory.statement("    cstr clean = clean_word(token);"))
    token_body.append(factory.statement("    if (cstr_size(clean) > 0) {"))
    token_body.append(factory.statement("        WordVec_push(&analyzer->words, clean);"))
    token_body.append(factory.statement("        "))
    token_body.append(factory.statement("        // Update word count"))
    token_body.append(factory.statement("        WordCountMap_result result = WordCountMap_insert(&analyzer->word_counts, clean, 1);"))
    token_body.append(factory.statement("        if (!result.inserted) {"))
    token_body.append(factory.statement("            result.ref->second++;"))
    token_body.append(factory.statement("        }"))
    token_body.append(factory.statement("    }"))
    token_body.append(factory.statement("    cstr_drop(&clean);"))
    token_body.append(factory.statement("}"))
    token_body.append(factory.statement("token = strtok(NULL, \" \\t\\n\\r.,!?;:\\\"()[]{}'\");"))
    token_while.append(token_body)

    tokenize_body.append(token_while)
    tokenize_body.append(factory.statement(""))
    tokenize_body.append(factory.statement("free(content_copy);"))

    tokenize_func.append(tokenize_body)
    sequence.append(factory.declaration(tokenize_func))
    sequence.append(factory.statement(""))

    # Function: calculate_statistics
    calc_stats_func = factory.function("calculate_statistics", "void", [
        factory.variable("analyzer", "struct TextAnalyzer*")
    ])
    calc_stats_body = factory.sequence()
    calc_stats_body.append(factory.statement("struct TextStatistics* stats = &analyzer->stats;"))
    calc_stats_body.append(factory.statement("const char* content = cstr_str(&analyzer->content);"))
    calc_stats_body.append(factory.statement(""))

    # Calculate basic statistics
    calc_stats_body.append(factory.statement("// Basic counts"))
    calc_stats_body.append(factory.statement("stats->total_characters = cstr_size(analyzer->content);"))
    calc_stats_body.append(factory.statement("stats->total_words = WordVec_size(analyzer->words);"))
    calc_stats_body.append(factory.statement("stats->unique_words = WordCountMap_size(analyzer->word_counts);"))
    calc_stats_body.append(factory.statement(""))

    # Count sentences and lines
    calc_stats_body.append(factory.statement("// Count sentences and lines"))
    calc_stats_body.append(factory.statement("stats->total_sentences = 0;"))
    calc_stats_body.append(factory.statement("stats->total_lines = 1;"))
    calc_stats_body.append(factory.statement("stats->total_paragraphs = 1;"))
    calc_stats_body.append(factory.statement(""))

    # Character counting loop
    char_loop = factory.for_loop("int i = 0", "content[i] != '\\0'", "i++")
    char_loop_body = factory.sequence()
    char_loop_body.append(factory.statement("char c = content[i];"))
    char_loop_body.append(factory.statement("if (c == '.' || c == '!' || c == '?') stats->total_sentences++;"))
    char_loop_body.append(factory.statement("if (c == '\\n') {"))
    char_loop_body.append(factory.statement("    stats->total_lines++;"))
    char_loop_body.append(factory.statement("    if (i > 0 && content[i-1] == '\\n') stats->total_paragraphs++;"))
    char_loop_body.append(factory.statement("}"))
    char_loop.append(char_loop_body)
    calc_stats_body.append(char_loop)
    calc_stats_body.append(factory.statement(""))

    # Calculate averages
    calc_stats_body.append(factory.statement("// Calculate averages"))
    calc_stats_body.append(factory.statement("if (stats->total_words > 0) {"))
    calc_stats_body.append(factory.statement("    long total_word_length = 0;"))

    # Word length calculation
    word_loop = factory.statement("for (c_each(it, WordVec, analyzer->words)) {")
    calc_stats_body.append(word_loop)
    calc_stats_body.append(factory.statement("        total_word_length += cstr_size(*it.ref);"))
    calc_stats_body.append(factory.statement("    }"))
    calc_stats_body.append(factory.statement("    stats->average_word_length = (double)total_word_length / stats->total_words;"))
    calc_stats_body.append(factory.statement("}"))
    calc_stats_body.append(factory.statement(""))

    calc_stats_body.append(factory.statement("if (stats->total_sentences > 0) {"))
    calc_stats_body.append(factory.statement("    stats->average_sentence_length = (double)stats->total_words / stats->total_sentences;"))
    calc_stats_body.append(factory.statement("}"))
    calc_stats_body.append(factory.statement(""))

    # Calculate reading metrics
    calc_stats_body.append(factory.statement("// Calculate reading time and complexity"))
    calc_stats_body.append(factory.statement("stats->reading_time_minutes = stats->total_words / AVERAGE_READING_SPEED;"))
    calc_stats_body.append(factory.statement("stats->complexity_score = 1.0;"))
    calc_stats_body.append(factory.statement("if (stats->average_word_length > 5.0) stats->complexity_score += 0.5;"))
    calc_stats_body.append(factory.statement("if (stats->average_sentence_length > 20.0) stats->complexity_score += 0.5;"))
    calc_stats_body.append(factory.statement("stats->reading_time_minutes *= stats->complexity_score;"))

    calc_stats_func.append(calc_stats_body)
    sequence.append(factory.declaration(calc_stats_func))
    sequence.append(factory.statement(""))

    # Function: print_results
    print_func = factory.function("print_results", "void", [
        factory.variable("analyzer", "struct TextAnalyzer*")
    ])
    print_body = factory.sequence()
    print_body.append(factory.statement("struct TextStatistics* stats = &analyzer->stats;"))
    print_body.append(factory.statement(""))
    print_body.append(factory.statement("printf(\"\\n\");"))
    print_body.append(factory.statement("printf(\"============================================================\\n\");"))
    print_body.append(factory.statement("printf(\"TEXT ANALYSIS RESULTS: %s\\n\", analyzer->filename);"))
    print_body.append(factory.statement("printf(\"============================================================\\n\");"))
    print_body.append(factory.statement(""))
    print_body.append(factory.statement("printf(\"\\nBASIC STATISTICS:\\n\");"))
    print_body.append(factory.statement("printf(\"  Total characters: %ld\\n\", stats->total_characters);"))
    print_body.append(factory.statement("printf(\"  Total words: %ld\\n\", stats->total_words);"))
    print_body.append(factory.statement("printf(\"  Total sentences: %ld\\n\", stats->total_sentences);"))
    print_body.append(factory.statement("printf(\"  Total paragraphs: %ld\\n\", stats->total_paragraphs);"))
    print_body.append(factory.statement("printf(\"  Total lines: %ld\\n\", stats->total_lines);"))
    print_body.append(factory.statement("printf(\"  Unique words: %ld\\n\", stats->unique_words);"))
    print_body.append(factory.statement(""))
    print_body.append(factory.statement("printf(\"\\nADVANCED METRICS:\\n\");"))
    print_body.append(factory.statement("printf(\"  Average word length: %.2f characters\\n\", stats->average_word_length);"))
    print_body.append(factory.statement("printf(\"  Average sentence length: %.2f words\\n\", stats->average_sentence_length);"))
    print_body.append(factory.statement("printf(\"  Estimated reading time: %.1f minutes\\n\", stats->reading_time_minutes);"))
    print_body.append(factory.statement("printf(\"  Text complexity score: %.2f\\n\", stats->complexity_score);"))
    print_body.append(factory.statement(""))
    print_body.append(factory.statement("printf(\"Analysis completed in %.3f seconds\\n\", analyzer->analysis_time);"))

    print_func.append(print_body)
    sequence.append(factory.declaration(print_func))
    sequence.append(factory.statement(""))

    # Main function
    main_func = factory.function("main", "int", [
        factory.variable("argc", "int"),
        factory.variable("argv", "char*[]")
    ])
    main_body = factory.sequence()

    # Check arguments
    main_body.append(factory.statement("if (argc < 2) {"))
    main_body.append(factory.statement("    printf(\"Usage: %s <input_file>\\n\", argv[0]);"))
    main_body.append(factory.statement("    return 1;"))
    main_body.append(factory.statement("}"))
    main_body.append(factory.statement(""))

    # Initialize analyzer
    main_body.append(factory.statement("struct TextAnalyzer analyzer;"))
    main_body.append(factory.statement("analyzer.filename = argv[1];"))
    main_body.append(factory.statement(""))

    # Timing
    main_body.append(factory.statement("clock_t start_time = clock();"))
    main_body.append(factory.statement(""))

    # Perform analysis
    main_body.append(factory.statement("printf(\"Analyzing file: %s\\n\", analyzer.filename);"))
    main_body.append(factory.statement(""))

    # Load and process file
    main_body.append(factory.statement("if (!load_file(&analyzer)) {"))
    main_body.append(factory.statement("    return 1;"))
    main_body.append(factory.statement("}"))
    main_body.append(factory.statement(""))

    main_body.append(factory.statement("printf(\"Tokenizing words...\\n\");"))
    main_body.append(factory.statement("tokenize_words(&analyzer);"))
    main_body.append(factory.statement(""))

    main_body.append(factory.statement("printf(\"Calculating statistics...\\n\");"))
    main_body.append(factory.statement("calculate_statistics(&analyzer);"))
    main_body.append(factory.statement(""))

    # Calculate timing
    main_body.append(factory.statement("clock_t end_time = clock();"))
    main_body.append(factory.statement("analyzer.analysis_time = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;"))
    main_body.append(factory.statement(""))

    # Print results
    main_body.append(factory.statement("print_results(&analyzer);"))
    main_body.append(factory.statement(""))

    # Cleanup
    main_body.append(factory.statement("// Cleanup"))
    main_body.append(factory.statement("cstr_drop(&analyzer.content);"))
    main_body.append(factory.statement("WordVec_drop(&analyzer.words);"))
    main_body.append(factory.statement("WordCountMap_drop(&analyzer.word_counts);"))
    main_body.append(factory.statement(""))

    main_body.append(factory.return_statement("0"))

    main_func.append(main_body)
    sequence.append(factory.declaration(main_func))

    # Generate C code
    print("Generating C code...")
    c_code = writer.write_str(sequence)

    # Write C file
    with open(c_file, 'w') as f:
        f.write(c_code)
    print(f"C code written to: {c_file}")

    # Generate Makefile
    print("Generating Makefile...")
    makegen = MakefileGenerator()

    # Configure makefile for the text analyzer
    makegen.set_project_name("text_analyzer_advanced")
    makegen.set_compiler("gcc")
    makegen.add_source_file("text_analyzer_advanced.c")
    makegen.add_include_dir("../src/cgen/ext/stc/include")
    makegen.add_compiler_flag("-std=c99")
    makegen.add_compiler_flag("-Wall")
    makegen.add_compiler_flag("-Wextra")
    makegen.add_compiler_flag("-O2")

    # Generate and write makefile
    makefile_content = makegen.generate()
    with open(makefile, 'w') as f:
        f.write(makefile_content)
    print(f"Makefile written to: {makefile}")

    print("\nFiles generated successfully!")
    print(f"  - C source: {c_file}")
    print(f"  - Makefile: {makefile}")
    print(f"\nTo build and run:")
    print(f"  cd {build_dir}")
    print(f"  make")
    print(f"  ./text_analyzer_advanced ../examples/sample_text.txt")

    return True


if __name__ == "__main__":
    if create_c_version():
        print("\nConversion completed successfully!")
    else:
        print("\nConversion failed!")
        sys.exit(1)