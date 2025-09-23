#!/usr/bin/env python3
"""
Simplified Text Analyzer Conversion Script

This script creates a C version of the text analyzer using CGen and builds it.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from cgen.core import CFactory, Writer, StyleOptions
from cgen.builder.makefilegen import MakefileGenerator


def create_c_version():
    """Create a C version of the text analyzer using CGen."""

    # Setup paths
    examples_dir = Path(__file__).parent
    build_dir = project_root / "build"
    build_dir.mkdir(exist_ok=True)

    c_file = build_dir / "text_analyzer_advanced.c"
    makefile = build_dir / "Makefile"

    print("=" * 60)
    print("CGEN TEXT ANALYZER CONVERSION")
    print("=" * 60)
    print(f"C output: {c_file}")
    print(f"Makefile: {makefile}")
    print()

    # Create the C program with raw code approach for simplicity
    print("Creating C equivalent...")

    c_program = '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#define MAX_WORDS 10000
#define MAX_WORD_LENGTH 100
#define MAX_LINE_LENGTH 1024
#define AVERAGE_READING_SPEED 250.0

typedef struct {
    char word[MAX_WORD_LENGTH];
    int count;
} WordCount;

typedef struct {
    long total_characters;
    long total_words;
    long total_sentences;
    long total_paragraphs;
    long total_lines;
    long unique_words;
    double average_word_length;
    double average_sentence_length;
    double reading_time_minutes;
    double complexity_score;
} TextStatistics;

typedef struct {
    char* filename;
    char* content;
    long content_size;
    WordCount words[MAX_WORDS];
    int word_count;
    TextStatistics stats;
    double analysis_time;
} TextAnalyzer;

void clean_word(const char* input, char* output) {
    int j = 0;
    for (int i = 0; input[i]; i++) {
        if (isalpha(input[i])) {
            output[j++] = tolower(input[i]);
        }
    }
    output[j] = '\\0';
}

int find_or_add_word(TextAnalyzer* analyzer, const char* word) {
    char clean[MAX_WORD_LENGTH];
    clean_word(word, clean);

    if (strlen(clean) == 0) return -1;

    // Find existing word
    for (int i = 0; i < analyzer->word_count; i++) {
        if (strcmp(analyzer->words[i].word, clean) == 0) {
            analyzer->words[i].count++;
            return i;
        }
    }

    // Add new word
    if (analyzer->word_count < MAX_WORDS) {
        strcpy(analyzer->words[analyzer->word_count].word, clean);
        analyzer->words[analyzer->word_count].count = 1;
        analyzer->word_count++;
        return analyzer->word_count - 1;
    }

    return -1;
}

int load_file(TextAnalyzer* analyzer) {
    FILE* file = fopen(analyzer->filename, "r");
    if (file == NULL) {
        printf("Error: Cannot open file %s\\n", analyzer->filename);
        return 0;
    }

    // Get file size
    fseek(file, 0, SEEK_END);
    analyzer->content_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    // Allocate memory
    analyzer->content = malloc(analyzer->content_size + 1);
    if (analyzer->content == NULL) {
        printf("Error: Cannot allocate memory\\n");
        fclose(file);
        return 0;
    }

    // Read file
    size_t bytes_read = fread(analyzer->content, 1, analyzer->content_size, file);
    analyzer->content[bytes_read] = '\\0';
    analyzer->content_size = bytes_read;

    fclose(file);
    return 1;
}

void tokenize_words(TextAnalyzer* analyzer) {
    char* content_copy = strdup(analyzer->content);
    char* token = strtok(content_copy, " \\t\\n\\r.,!?;:\\"()[]{}");

    while (token != NULL) {
        if (strlen(token) > 0) {
            find_or_add_word(analyzer, token);
        }
        token = strtok(NULL, " \\t\\n\\r.,!?;:\\"()[]{}");
    }

    free(content_copy);
}

void calculate_statistics(TextAnalyzer* analyzer) {
    TextStatistics* stats = &analyzer->stats;
    const char* content = analyzer->content;

    // Basic counts
    stats->total_characters = analyzer->content_size;
    stats->total_words = 0;
    stats->total_sentences = 0;
    stats->total_lines = 1;
    stats->total_paragraphs = 1;

    // Count words from word frequency analysis
    for (int i = 0; i < analyzer->word_count; i++) {
        stats->total_words += analyzer->words[i].count;
    }
    stats->unique_words = analyzer->word_count;

    // Count sentences, lines, and paragraphs
    int empty_line = 0;
    for (long i = 0; i < analyzer->content_size; i++) {
        char c = content[i];
        if (c == '.' || c == '!' || c == '?') {
            stats->total_sentences++;
        }
        if (c == '\\n') {
            stats->total_lines++;
            if (empty_line) {
                stats->total_paragraphs++;
                empty_line = 0;
            } else {
                empty_line = 1;
            }
        } else if (!isspace(c)) {
            empty_line = 0;
        }
    }

    // Calculate averages
    if (stats->total_words > 0) {
        long total_word_length = 0;
        for (int i = 0; i < analyzer->word_count; i++) {
            total_word_length += strlen(analyzer->words[i].word) * analyzer->words[i].count;
        }
        stats->average_word_length = (double)total_word_length / stats->total_words;
    }

    if (stats->total_sentences > 0) {
        stats->average_sentence_length = (double)stats->total_words / stats->total_sentences;
    }

    // Calculate reading time and complexity
    stats->reading_time_minutes = stats->total_words / AVERAGE_READING_SPEED;
    stats->complexity_score = 1.0;
    if (stats->average_word_length > 5.0) stats->complexity_score += 0.5;
    if (stats->average_sentence_length > 20.0) stats->complexity_score += 0.5;
    if (stats->average_sentence_length > 30.0) stats->complexity_score += 0.5;
    stats->reading_time_minutes *= stats->complexity_score;
}

void sort_words_by_frequency(TextAnalyzer* analyzer) {
    // Simple bubble sort
    for (int i = 0; i < analyzer->word_count - 1; i++) {
        for (int j = 0; j < analyzer->word_count - 1 - i; j++) {
            if (analyzer->words[j].count < analyzer->words[j + 1].count) {
                WordCount temp = analyzer->words[j];
                analyzer->words[j] = analyzer->words[j + 1];
                analyzer->words[j + 1] = temp;
            }
        }
    }
}

void print_results(TextAnalyzer* analyzer) {
    TextStatistics* stats = &analyzer->stats;

    printf("\\n");
    printf("============================================================\\n");
    printf("TEXT ANALYSIS RESULTS: %s\\n", analyzer->filename);
    printf("============================================================\\n");

    printf("\\nBASIC STATISTICS:\\n");
    printf("  Total characters: %ld\\n", stats->total_characters);
    printf("  Total words: %ld\\n", stats->total_words);
    printf("  Total sentences: %ld\\n", stats->total_sentences);
    printf("  Total paragraphs: %ld\\n", stats->total_paragraphs);
    printf("  Total lines: %ld\\n", stats->total_lines);
    printf("  Unique words: %ld\\n", stats->unique_words);

    printf("\\nADVANCED METRICS:\\n");
    printf("  Average word length: %.2f characters\\n", stats->average_word_length);
    printf("  Average sentence length: %.2f words\\n", stats->average_sentence_length);
    printf("  Estimated reading time: %.1f minutes\\n", stats->reading_time_minutes);
    printf("  Text complexity score: %.2f\\n", stats->complexity_score);

    printf("\\nTOP 10 MOST FREQUENT WORDS:\\n");
    sort_words_by_frequency(analyzer);

    int limit = (analyzer->word_count < 10) ? analyzer->word_count : 10;
    for (int i = 0; i < limit; i++) {
        double percentage = ((double)analyzer->words[i].count / stats->total_words) * 100.0;
        printf("  %2d. %-15s - %5d times (%5.2f%%)\\n",
               i + 1, analyzer->words[i].word, analyzer->words[i].count, percentage);
    }

    printf("\\nAnalysis completed in %.3f seconds\\n", analyzer->analysis_time);
}

void cleanup(TextAnalyzer* analyzer) {
    if (analyzer->content) {
        free(analyzer->content);
    }
}

void print_usage(const char* program_name) {
    printf("Advanced Text File Analyzer (C Version)\\n");
    printf("Usage: %s <input_file>\\n", program_name);
    printf("\\n");
    printf("Arguments:\\n");
    printf("  input_file   - Text file to analyze\\n");
    printf("\\n");
    printf("Examples:\\n");
    printf("  %s document.txt\\n", program_name);
    printf("  %s ../examples/sample_text.txt\\n", program_name);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    TextAnalyzer analyzer = {0};
    analyzer.filename = argv[1];

    clock_t start_time = clock();

    printf("Analyzing file: %s\\n", analyzer.filename);

    if (!load_file(&analyzer)) {
        return 1;
    }

    printf("Preprocessing text...\\n");
    printf("Analyzing word frequency...\\n");
    tokenize_words(&analyzer);

    printf("Calculating statistics...\\n");
    calculate_statistics(&analyzer);

    clock_t end_time = clock();
    analyzer.analysis_time = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;

    print_results(&analyzer);

    cleanup(&analyzer);

    printf("\\nAnalysis completed successfully!\\n");
    return 0;
}'''

    # Write C file
    with open(c_file, 'w') as f:
        f.write(c_program)
    print(f"C code written to: {c_file}")

    # Generate Makefile using CGen's makefilegen
    print("Generating Makefile...")
    makegen = MakefileGenerator(
        name="text_analyzer_advanced",
        source_dir=".",
        build_dir=".",
        compiler="gcc",
        std="c99",
        flags=["-Wall", "-Wextra", "-O2", "-g"],
        use_stc=False  # We're using plain C for this example
    )

    # Generate and write makefile
    makegen.generate_header()
    makegen.generate_variables()
    makegen.generate_targets()
    makefile_content = makegen.generate_makefile()
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