#!/usr/bin/env python3
"""
Simplified Text Analysis Tool - STC Integration Demo

A practical text analysis program optimized for current STC translation capabilities.
Uses only supported language constructs while demonstrating all STC container types:
- Dict[str, int]: Word frequency counting
- Set[str]: Unique word tracking
- List[str]: Line and word storage
- str: Text manipulation

Written in static Python style compatible with current translator limitations.
"""

def analyze_word_frequency() -> dict:
    """
    Analyze word frequency from predefined sample words.
    Demonstrates dict[str, int] container operations.

    Returns:
        Dictionary of word frequencies
    """
    # Sample words for analysis
    words: List[str] = ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog", "the", "fox", "and", "the", "dog"]

    # Initialize frequency counter
    frequency: Dict[str, int] = {}

    # Count word frequencies (using supported constructs)
    frequency["the"] = 4
    frequency["fox"] = 2
    frequency["dog"] = 2
    frequency["quick"] = 1
    frequency["brown"] = 1
    frequency["jumps"] = 1
    frequency["over"] = 1
    frequency["lazy"] = 1
    frequency["and"] = 1

    return frequency


def collect_unique_words() -> Set[str]:
    """
    Collect unique words from text analysis.
    Demonstrates set[str] container operations.

    Returns:
        Set of unique words
    """
    # Initialize unique words set
    unique_words: Set[str] = {"the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "and"}

    return unique_words


def process_text_lines() -> List[str]:
    """
    Process text lines for analysis.
    Demonstrates list[str] container operations.

    Returns:
        List of processed text lines
    """
    # Sample text lines
    lines: List[str] = [
        "The quick brown fox jumps over the lazy dog",
        "This sentence contains every letter of the alphabet",
        "Text analysis reveals patterns in language",
        "Word frequency shows important terms",
        "Statistical analysis helps understand content"
    ]

    return lines


def calculate_text_statistics(word_freq: Dict[str, int], unique_words: Set[str], lines: List[str]) -> Dict[str, int]:
    """
    Calculate comprehensive text statistics.
    Demonstrates multi-container operations and string processing.

    Args:
        word_freq: Word frequency dictionary
        unique_words: Set of unique words
        lines: List of text lines

    Returns:
        Dictionary containing calculated statistics
    """
    # Initialize statistics dictionary
    stats: Dict[str, int] = {}

    # Basic counts
    total_unique_words: int = len(unique_words)
    total_lines: int = len(lines)

    # Calculate word frequency statistics
    total_word_occurrences: int = 0
    total_word_occurrences = total_word_occurrences + word_freq.get("the", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("fox", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("dog", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("quick", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("brown", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("jumps", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("over", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("lazy", 0)
    total_word_occurrences = total_word_occurrences + word_freq.get("and", 0)

    # Calculate character counts for sample text
    sample_text: str = "The quick brown fox jumps over the lazy dog. Text analysis example."
    total_characters: int = len(sample_text)

    # Store calculated statistics
    stats["total_characters"] = total_characters
    stats["total_words"] = total_word_occurrences
    stats["total_lines"] = total_lines
    stats["unique_words"] = total_unique_words

    # Calculate derived metrics
    if total_word_occurrences > 0:
        avg_word_length: int = total_characters // total_word_occurrences
        stats["avg_word_length"] = avg_word_length
    else:
        stats["avg_word_length"] = 0

    if total_lines > 0:
        avg_words_per_line: int = total_word_occurrences // total_lines
        stats["avg_words_per_line"] = avg_words_per_line
    else:
        stats["avg_words_per_line"] = 0

    # Vocabulary richness calculation
    if total_word_occurrences > 0:
        vocabulary_richness: int = (total_unique_words * 100) // total_word_occurrences
        stats["vocabulary_richness"] = vocabulary_richness
    else:
        stats["vocabulary_richness"] = 0

    return stats


def find_top_words(word_freq: Dict[str, int]) -> List[str]:
    """
    Find the most frequently used words.
    Demonstrates dict access and list building.

    Args:
        word_freq: Word frequency dictionary

    Returns:
        List of top words
    """
    # Create list of words with high frequency (simplified for static style)
    top_words: List[str] = []

    # Check frequency and add high-frequency words
    if word_freq.get("the", 0) > 2:
        top_words.append("the")

    if word_freq.get("fox", 0) > 1:
        top_words.append("fox")

    if word_freq.get("dog", 0) > 1:
        top_words.append("dog")

    return top_words


def generate_analysis_report(stats: Dict[str, int], top_words: List[str]) -> str:
    """
    Generate a text analysis report.
    Demonstrates string operations and formatting.

    Args:
        stats: Statistics dictionary
        top_words: List of top words

    Returns:
        Formatted report string
    """
    # Build report string (simplified for static style)
    report: str = "Text Analysis Report"
    report = report + "\n===================="
    report = report + "\nCharacters: " + str(stats.get("total_characters", 0))
    report = report + "\nWords: " + str(stats.get("total_words", 0))
    report = report + "\nLines: " + str(stats.get("total_lines", 0))
    report = report + "\nUnique Words: " + str(stats.get("unique_words", 0))
    report = report + "\nVocabulary Richness: " + str(stats.get("vocabulary_richness", 0)) + "%"

    return report


def main() -> int:
    """
    Main text analysis function demonstrating all STC container types.

    Returns:
        Success status (0 for success)
    """
    # Perform word frequency analysis
    word_frequencies: Dict[str, int] = analyze_word_frequency()

    # Collect unique words
    unique_word_set: Set[str] = collect_unique_words()

    # Process text lines
    text_lines: List[str] = process_text_lines()

    # Calculate comprehensive statistics
    analysis_stats: Dict[str, int] = calculate_text_statistics(word_frequencies, unique_word_set, text_lines)

    # Find top words
    most_common: List[str] = find_top_words(word_frequencies)

    # Generate analysis report
    report: str = generate_analysis_report(analysis_stats, most_common)

    # Display results (simplified output for static style)
    print("=== STC Text Analysis Tool ===")
    print("")
    print("Analysis Results:")
    print("Total Characters:", analysis_stats.get("total_characters", 0))
    print("Total Words:", analysis_stats.get("total_words", 0))
    print("Total Lines:", analysis_stats.get("total_lines", 0))
    print("Unique Words:", analysis_stats.get("unique_words", 0))
    print("Vocabulary Richness:", analysis_stats.get("vocabulary_richness", 0), "%")
    print("")
    print("Top Words:")
    if len(most_common) > 0:
        print("1.", most_common[0] if len(most_common) > 0 else "none")
    if len(most_common) > 1:
        print("2.", most_common[1] if len(most_common) > 1 else "none")
    if len(most_common) > 2:
        print("3.", most_common[2] if len(most_common) > 2 else "none")

    print("")
    print("Analysis completed successfully!")
    print("STC containers processed:", len(word_frequencies) + len(unique_word_set) + len(text_lines))

    return 0


if __name__ == "__main__":
    exit_code: int = main()
    exit(exit_code)