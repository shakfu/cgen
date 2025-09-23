#!/usr/bin/env python3
"""
Advanced Text File Analyzer
============================

A comprehensive text analysis tool that processes text files and provides
detailed statistics including word frequency, reading metrics, and content analysis.

Features:
- Word frequency analysis with top N most common words
- Reading speed and time estimation
- Text complexity metrics (average word length, sentence length)
- Character and whitespace analysis
- File statistics (size, line count)
- Export results to multiple formats

Author: CGen Python-to-C Translation Demo
License: MIT
"""

import sys
import os
import re
from typing import Dict, List, Tuple
from collections import defaultdict
import time


class TextStatistics:
    """Container for comprehensive text analysis results."""

    def __init__(self):
        self.total_characters: int = 0
        self.total_words: int = 0
        self.total_sentences: int = 0
        self.total_paragraphs: int = 0
        self.total_lines: int = 0
        self.unique_words: int = 0
        self.average_word_length: float = 0.0
        self.average_sentence_length: float = 0.0
        self.reading_time_minutes: float = 0.0
        self.complexity_score: float = 0.0


class WordFrequencyAnalyzer:
    """Analyzes word frequency and provides ranking statistics."""

    def __init__(self):
        self.word_counts: Dict[str, int] = {}
        self.total_words: int = 0

    def add_word(self, word: str) -> None:
        """Add a word to the frequency counter."""
        clean_word = word.lower().strip('.,!?;:"()[]{}')
        if len(clean_word) > 0 and clean_word.isalpha():
            if clean_word in self.word_counts:
                self.word_counts[clean_word] += 1
            else:
                self.word_counts[clean_word] = 1
            self.total_words += 1

    def get_top_words(self, count: int) -> List[Tuple[str, int]]:
        """Get the top N most frequent words."""
        # Convert dict to list of tuples and sort by frequency
        word_list: List[Tuple[str, int]] = []
        for word, freq in self.word_counts.items():
            word_list.append((word, freq))

        # Simple bubble sort for deterministic results
        for i in range(len(word_list)):
            for j in range(len(word_list) - 1 - i):
                if word_list[j][1] < word_list[j + 1][1]:
                    # Swap elements
                    temp = word_list[j]
                    word_list[j] = word_list[j + 1]
                    word_list[j + 1] = temp

        # Return top N words
        result: List[Tuple[str, int]] = []
        for i in range(min(count, len(word_list))):
            result.append(word_list[i])

        return result

    def get_word_frequency_percentage(self, word: str) -> float:
        """Get the frequency percentage of a specific word."""
        if self.total_words == 0:
            return 0.0
        clean_word = word.lower().strip('.,!?;:"()[]{}')
        if clean_word in self.word_counts:
            return (float(self.word_counts[clean_word]) / float(self.total_words)) * 100.0
        return 0.0


class TextFileAnalyzer:
    """Main text file analyzer with comprehensive analysis capabilities."""

    def __init__(self, filename: str):
        self.filename: str = filename
        self.content: str = ""
        self.lines: List[str] = []
        self.words: List[str] = []
        self.sentences: List[str] = []
        self.stats: TextStatistics = TextStatistics()
        self.word_analyzer: WordFrequencyAnalyzer = WordFrequencyAnalyzer()
        self.analysis_time: float = 0.0

    def load_file(self) -> bool:
        """Load and read the text file."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.content = file.read()
            return True
        except Exception as e:
            print(f"Error loading file {self.filename}: {str(e)}")
            return False

    def preprocess_text(self) -> None:
        """Preprocess the text content for analysis."""
        # Split into lines
        self.lines = self.content.split('\n')

        # Split into words (simple whitespace splitting)
        words_raw = self.content.split()
        self.words = []
        for word in words_raw:
            if len(word) > 0:
                self.words.append(word)

        # Split into sentences (simple approach)
        sentence_endings = ['.', '!', '?']
        current_sentence = ""
        self.sentences = []

        for char in self.content:
            current_sentence += char
            if char in sentence_endings:
                if len(current_sentence.strip()) > 0:
                    self.sentences.append(current_sentence.strip())
                current_sentence = ""

        # Add final sentence if exists
        if len(current_sentence.strip()) > 0:
            self.sentences.append(current_sentence.strip())

    def analyze_basic_statistics(self) -> None:
        """Perform basic statistical analysis."""
        self.stats.total_characters = len(self.content)
        self.stats.total_words = len(self.words)
        self.stats.total_sentences = len(self.sentences)
        self.stats.total_lines = len(self.lines)

        # Count paragraphs (empty lines separate paragraphs)
        paragraph_count = 1
        for line in self.lines:
            if len(line.strip()) == 0:
                paragraph_count += 1
        self.stats.total_paragraphs = paragraph_count

        # Calculate averages
        if self.stats.total_words > 0:
            total_word_length = 0
            for word in self.words:
                clean_word = word.strip('.,!?;:"()[]{}')
                total_word_length += len(clean_word)
            self.stats.average_word_length = float(total_word_length) / float(self.stats.total_words)

        if self.stats.total_sentences > 0:
            self.stats.average_sentence_length = float(self.stats.total_words) / float(self.stats.total_sentences)

    def analyze_word_frequency(self) -> None:
        """Perform word frequency analysis."""
        for word in self.words:
            self.word_analyzer.add_word(word)

        self.stats.unique_words = len(self.word_analyzer.word_counts)

    def calculate_reading_metrics(self) -> None:
        """Calculate reading time and complexity metrics."""
        # Average reading speed: 200-300 words per minute, use 250
        average_reading_speed = 250.0
        if self.stats.total_words > 0:
            self.stats.reading_time_minutes = float(self.stats.total_words) / average_reading_speed

        # Simple complexity score based on average word and sentence length
        complexity_factor = 1.0
        if self.stats.average_word_length > 5.0:
            complexity_factor += 0.5
        if self.stats.average_sentence_length > 20.0:
            complexity_factor += 0.5
        if self.stats.average_sentence_length > 30.0:
            complexity_factor += 0.5

        self.stats.complexity_score = complexity_factor

        # Adjust reading time based on complexity
        self.stats.reading_time_minutes *= complexity_factor

    def perform_full_analysis(self) -> bool:
        """Perform complete text analysis."""
        start_time = time.time()

        print(f"Analyzing file: {self.filename}")

        # Load file
        if not self.load_file():
            return False

        # Preprocess
        print("Preprocessing text...")
        self.preprocess_text()

        # Perform analysis
        print("Analyzing basic statistics...")
        self.analyze_basic_statistics()

        print("Analyzing word frequency...")
        self.analyze_word_frequency()

        print("Calculating reading metrics...")
        self.calculate_reading_metrics()

        end_time = time.time()
        self.analysis_time = end_time - start_time

        print(f"Analysis completed in {self.analysis_time:.3f} seconds")
        return True

    def print_results(self) -> None:
        """Print comprehensive analysis results."""
        print("\n" + "=" * 60)
        print(f"TEXT ANALYSIS RESULTS: {os.path.basename(self.filename)}")
        print("=" * 60)

        # Basic statistics
        print("\nBASIC STATISTICS:")
        print(f"  Total characters: {self.stats.total_characters:,}")
        print(f"  Total words: {self.stats.total_words:,}")
        print(f"  Total sentences: {self.stats.total_sentences:,}")
        print(f"  Total paragraphs: {self.stats.total_paragraphs:,}")
        print(f"  Total lines: {self.stats.total_lines:,}")
        print(f"  Unique words: {self.stats.unique_words:,}")

        # Advanced metrics
        print("\nADVANCED METRICS:")
        print(f"  Average word length: {self.stats.average_word_length:.2f} characters")
        print(f"  Average sentence length: {self.stats.average_sentence_length:.2f} words")
        print(f"  Estimated reading time: {self.stats.reading_time_minutes:.1f} minutes")
        print(f"  Text complexity score: {self.stats.complexity_score:.2f}")

        # Word frequency analysis
        print("\nTOP 10 MOST FREQUENT WORDS:")
        top_words = self.word_analyzer.get_top_words(10)
        for i, (word, count) in enumerate(top_words):
            percentage = self.word_analyzer.get_word_frequency_percentage(word)
            print(f"  {i+1:2d}. {word:15s} - {count:5d} times ({percentage:5.2f}%)")

        # File information
        try:
            file_size = os.path.getsize(self.filename)
            print(f"\nFILE INFORMATION:")
            print(f"  File size: {file_size:,} bytes")
            print(f"  Analysis time: {self.analysis_time:.3f} seconds")
        except:
            pass

    def export_results_to_text(self, output_filename: str) -> bool:
        """Export analysis results to a text file."""
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(f"Text Analysis Report: {os.path.basename(self.filename)}\n")
                file.write("=" * 60 + "\n\n")

                file.write("Basic Statistics:\n")
                file.write(f"Total characters: {self.stats.total_characters}\n")
                file.write(f"Total words: {self.stats.total_words}\n")
                file.write(f"Total sentences: {self.stats.total_sentences}\n")
                file.write(f"Total paragraphs: {self.stats.total_paragraphs}\n")
                file.write(f"Total lines: {self.stats.total_lines}\n")
                file.write(f"Unique words: {self.stats.unique_words}\n\n")

                file.write("Advanced Metrics:\n")
                file.write(f"Average word length: {self.stats.average_word_length:.2f}\n")
                file.write(f"Average sentence length: {self.stats.average_sentence_length:.2f}\n")
                file.write(f"Reading time (minutes): {self.stats.reading_time_minutes:.1f}\n")
                file.write(f"Complexity score: {self.stats.complexity_score:.2f}\n\n")

                file.write("Top 20 Most Frequent Words:\n")
                top_words = self.word_analyzer.get_top_words(20)
                for i, (word, count) in enumerate(top_words):
                    percentage = self.word_analyzer.get_word_frequency_percentage(word)
                    file.write(f"{i+1}. {word} - {count} times ({percentage:.2f}%)\n")

            return True
        except Exception as e:
            print(f"Error exporting results: {str(e)}")
            return False


def print_usage() -> None:
    """Print program usage information."""
    print("Advanced Text File Analyzer")
    print("Usage: python text_analyzer_advanced.py <input_file> [output_file]")
    print("")
    print("Arguments:")
    print("  input_file   - Text file to analyze")
    print("  output_file  - Optional output file for results export")
    print("")
    print("Examples:")
    print("  python text_analyzer_advanced.py document.txt")
    print("  python text_analyzer_advanced.py book.txt analysis_report.txt")


def main() -> int:
    """Main program entry point."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print_usage()
        return 1

    input_filename = sys.argv[1]
    output_filename = ""

    if len(sys.argv) >= 3:
        output_filename = sys.argv[2]

    # Verify input file exists
    if not os.path.exists(input_filename):
        print(f"Error: Input file '{input_filename}' does not exist.")
        return 1

    # Create analyzer and perform analysis
    analyzer = TextFileAnalyzer(input_filename)

    if not analyzer.perform_full_analysis():
        print("Failed to analyze the file.")
        return 1

    # Print results to console
    analyzer.print_results()

    # Export results if output file specified
    if len(output_filename) > 0:
        print(f"\nExporting results to: {output_filename}")
        if analyzer.export_results_to_text(output_filename):
            print("Results exported successfully.")
        else:
            print("Failed to export results.")
            return 1

    print("\nAnalysis completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)