#!/usr/bin/env python3
"""
Basic Text Analysis Tool - STC Integration Demo

A practical text analysis program demonstrating STC container integration.
Uses simple, supported language constructs while showcasing all container types.

Written in static Python style compatible with current STC translator.
"""

def analyze_word_frequency() -> int:
    """
    Analyze word frequency from predefined sample words.
    Demonstrates dict container operations.

    Returns:
        Total word count processed
    """
    # Initialize frequency counter
    frequency: dict[str, int] = {"the": 4, "fox": 2, "dog": 2, "quick": 1, "brown": 1}

    # Calculate total words
    total_words: int = 0
    total_words = total_words + frequency.get("the", 0)
    total_words = total_words + frequency.get("fox", 0)
    total_words = total_words + frequency.get("dog", 0)
    total_words = total_words + frequency.get("quick", 0)
    total_words = total_words + frequency.get("brown", 0)

    return total_words


def collect_unique_words() -> int:
    """
    Collect unique words from text analysis.
    Demonstrates set container operations.

    Returns:
        Number of unique words
    """
    # Initialize unique words set
    unique_words: set[str] = {"the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "and"}

    # Return count of unique words
    unique_count: int = len(unique_words)
    return unique_count


def process_text_lines() -> int:
    """
    Process text lines for analysis.
    Demonstrates list container operations.

    Returns:
        Number of text lines processed
    """
    # Sample text lines
    lines: list[str] = [
        "The quick brown fox jumps over the lazy dog",
        "This sentence contains letters of the alphabet",
        "Text analysis reveals patterns in language",
        "Word frequency shows important terms",
        "Statistical analysis helps understand content"
    ]

    # Return line count
    line_count: int = len(lines)
    return line_count


def calculate_text_statistics() -> int:
    """
    Calculate comprehensive text statistics.
    Demonstrates multi-container operations and string processing.

    Returns:
        Combined statistics score
    """
    # Get results from other analysis functions
    word_count: int = analyze_word_frequency()
    unique_count: int = collect_unique_words()
    line_count: int = process_text_lines()

    # Calculate character counts for sample text
    sample_text: str = "The quick brown fox jumps over the lazy dog. Text analysis example."
    character_count: int = len(sample_text)

    # Calculate combined score
    combined_score: int = word_count + unique_count + line_count + character_count
    return combined_score


def find_top_words() -> int:
    """
    Find the most frequently used words.
    Demonstrates dict access and list building.

    Returns:
        Number of top words found
    """
    # Sample word frequencies
    word_freq: dict[str, int] = {"the": 4, "fox": 2, "dog": 2, "and": 1}

    # Create list of words with high frequency
    top_words: list[str] = []

    # Check frequency and add high-frequency words
    if word_freq.get("the", 0) > 2:
        top_words.append("the")

    if word_freq.get("fox", 0) > 1:
        top_words.append("fox")

    if word_freq.get("dog", 0) > 1:
        top_words.append("dog")

    top_count: int = len(top_words)
    return top_count


def generate_analysis_report() -> str:
    """
    Generate a text analysis report.
    Demonstrates string operations.

    Returns:
        Formatted report string
    """
    # Get analysis results
    word_count: int = analyze_word_frequency()
    unique_count: int = collect_unique_words()
    line_count: int = process_text_lines()
    top_count: int = find_top_words()

    # Build report string
    report: str = "Text Analysis Report: "
    report = report + "Words=" + str(word_count)
    report = report + " Unique=" + str(unique_count)
    report = report + " Lines=" + str(line_count)
    report = report + " TopWords=" + str(top_count)

    return report


def main() -> int:
    """
    Main text analysis function demonstrating all STC container types.

    Returns:
        Success status (0 for success)
    """
    # Perform comprehensive analysis
    word_total: int = analyze_word_frequency()
    unique_total: int = collect_unique_words()
    line_total: int = process_text_lines()
    stats_total: int = calculate_text_statistics()
    top_total: int = find_top_words()

    # Generate final report
    report: str = generate_analysis_report()

    # Display results
    print("=== STC Text Analysis Tool ===")
    print("")
    print("Analysis Results:")
    print("Word Frequency Total:", word_total)
    print("Unique Words Count:", unique_total)
    print("Text Lines Count:", line_total)
    print("Statistics Score:", stats_total)
    print("Top Words Found:", top_total)
    print("")
    print("Report:", report)
    print("")
    print("Analysis completed successfully!")
    print("All STC container types demonstrated:")
    print("- dict[str, int] for word frequency")
    print("- set[str] for unique word tracking")
    print("- list[str] for line processing")
    print("- str for text manipulation")

    return 0


if __name__ == "__main__":
    exit_code: int = main()
    exit(exit_code)