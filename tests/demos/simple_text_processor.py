#!/usr/bin/env python3
"""
Simple Text Processor - Designed for CGen Translation
A simpler version optimized for automatic Python-to-C translation.
"""

from typing import List, Dict
import sys
import os


def count_words(content: str) -> Dict[str, int]:
    """Count word frequencies in text content."""
    word_counts: Dict[str, int] = {}
    words = content.lower().split()

    for word in words:
        # Clean word of punctuation
        clean_word = ""
        for char in word:
            if char.isalpha():
                clean_word += char

        if len(clean_word) > 0:
            if clean_word in word_counts:
                word_counts[clean_word] += 1
            else:
                word_counts[clean_word] = 1

    return word_counts


def get_top_words(word_counts: Dict[str, int], limit: int) -> List[str]:
    """Get the most frequent words."""
    words: List[str] = []
    counts: List[int] = []

    # Convert dict to lists
    for word, count in word_counts.items():
        words.append(word)
        counts.append(count)

    # Simple bubble sort by count
    for i in range(len(counts)):
        for j in range(len(counts) - 1 - i):
            if counts[j] < counts[j + 1]:
                # Swap both lists
                temp_count = counts[j]
                counts[j] = counts[j + 1]
                counts[j + 1] = temp_count

                temp_word = words[j]
                words[j] = words[j + 1]
                words[j + 1] = temp_word

    # Return top words
    result: List[str] = []
    for i in range(min(limit, len(words))):
        result.append(words[i])

    return result


def analyze_text_file(filename: str) -> None:
    """Analyze a text file and print statistics."""
    # Read file
    try:
        with open(filename, 'r') as file:
            content = file.read()
    except:
        print(f"Error: Cannot read file {filename}")
        return

    # Basic statistics
    char_count = len(content)
    word_count = len(content.split())
    line_count = len(content.split('\n'))

    # Word frequency analysis
    word_frequencies = count_words(content)
    unique_words = len(word_frequencies)
    top_words = get_top_words(word_frequencies, 5)

    # Print results
    print(f"File: {filename}")
    print(f"Characters: {char_count}")
    print(f"Words: {word_count}")
    print(f"Lines: {line_count}")
    print(f"Unique words: {unique_words}")
    print("Top 5 words:")

    for i in range(len(top_words)):
        word = top_words[i]
        count = word_frequencies[word]
        print(f"  {i+1}. {word}: {count}")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_text_processor.py <filename>")
        return 1

    filename = sys.argv[1]

    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist")
        return 1

    analyze_text_file(filename)
    return 0


if __name__ == "__main__":
    result = main()
    sys.exit(result)