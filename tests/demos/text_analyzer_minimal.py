#!/usr/bin/env python3
"""
Minimal Text Analysis Tool - STC Integration Demo

A minimal practical text analysis program demonstrating STC container integration.
Uses only the most basic supported language constructs while showcasing all container types.

Written to be compatible with current STC translator limitations.
"""

def test_dict_operations() -> int:
    """
    Test dictionary operations with STC hmap integration.

    Returns:
        Total word frequency count
    """
    # Create and populate word frequency dictionary
    word_freq: dict[str, int] = {"the": 4, "fox": 2, "dog": 2, "quick": 1, "brown": 1}

    # Access dictionary values
    count_the: int = word_freq.get("the", 0)
    count_fox: int = word_freq.get("fox", 0)
    count_dog: int = word_freq.get("dog", 0)

    # Calculate total
    total: int = count_the + count_fox + count_dog
    return total


def test_set_operations() -> int:
    """
    Test set operations with STC hset integration.

    Returns:
        Number of unique words
    """
    # Create unique words set
    unique_words: set[str] = {"the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "and"}

    # Get set size
    unique_count: int = len(unique_words)
    return unique_count


def test_list_operations() -> int:
    """
    Test list operations with STC vec integration.

    Returns:
        Total number of text lines
    """
    # Create text lines list
    lines: list[str] = [
        "The quick brown fox jumps over the lazy dog",
        "Text analysis reveals patterns in language",
        "Word frequency shows important terms",
        "Statistical analysis helps understand content",
        "Container operations demonstrate STC integration"
    ]

    # Get list size
    line_count: int = len(lines)
    return line_count


def test_string_operations() -> int:
    """
    Test string operations with STC cstr integration.

    Returns:
        Length of sample text
    """
    # Create sample text string
    sample_text: str = "The quick brown fox jumps over the lazy dog. STC integration demo."

    # Get string length
    text_length: int = len(sample_text)
    return text_length


def calculate_combined_metrics() -> int:
    """
    Calculate combined metrics from all container operations.

    Returns:
        Combined analysis score
    """
    # Call all test functions
    dict_result: int = test_dict_operations()
    set_result: int = test_set_operations()
    list_result: int = test_list_operations()
    string_result: int = test_string_operations()

    # Combine all results
    combined_score: int = dict_result + set_result + list_result + string_result
    return combined_score


def generate_simple_report() -> str:
    """
    Generate a simple analysis report.

    Returns:
        Report string with results
    """
    # Get individual results
    dict_score: int = test_dict_operations()
    set_score: int = test_set_operations()
    list_score: int = test_list_operations()
    string_score: int = test_string_operations()
    total_score: int = calculate_combined_metrics()

    # Build simple report
    report: str = "Analysis: Dict="
    report = report + str(dict_score)
    report = report + " Set="
    report = report + str(set_score)
    report = report + " List="
    report = report + str(list_score)
    report = report + " String="
    report = report + str(string_score)
    report = report + " Total="
    report = report + str(total_score)

    return report


def main() -> int:
    """
    Main function demonstrating STC container integration.

    Returns:
        Success status (0 for success)
    """
    print("=== Minimal STC Text Analysis Demo ===")
    print("")

    # Test each container type
    dict_result: int = test_dict_operations()
    set_result: int = test_set_operations()
    list_result: int = test_list_operations()
    string_result: int = test_string_operations()

    # Calculate combined metrics
    total_result: int = calculate_combined_metrics()

    # Generate report
    report: str = generate_simple_report()

    # Display results
    print("Container Test Results:")
    print("Dictionary Operations:", dict_result)
    print("Set Operations:", set_result)
    print("List Operations:", list_result)
    print("String Operations:", string_result)
    print("Combined Score:", total_result)
    print("")
    print("Summary Report:")
    print(report)
    print("")
    print("STC Integration Success!")
    print("All container types working:")
    print("- dict[str, int] -> STC hmap")
    print("- set[str] -> STC hset")
    print("- list[str] -> STC vec")
    print("- str -> STC cstr")

    return 0


if __name__ == "__main__":
    result: int = main()
    exit(result)