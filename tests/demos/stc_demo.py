def list_operations_demo() -> int:
    """Demonstrate STC list integration"""
    numbers: list[int] = []
    numbers.append(10)
    numbers.append(20)
    numbers.append(30)

    size: int = len(numbers)
    return size

def string_list_demo() -> int:
    """Demonstrate STC list with strings"""
    names: list[str] = []
    names.append("Alice")
    names.append("Bob")

    total_names: int = len(names)
    return total_names

def dict_operations_demo() -> int:
    """Demonstrate STC dict integration"""
    scores: dict[str, int] = {}
    scores["Alice"] = 95
    scores["Bob"] = 87
    scores["Charlie"] = 92

    alice_score: int = scores["Alice"]
    return alice_score

def set_operations_demo() -> int:
    """Demonstrate STC set integration"""
    unique_values: set[int] = set()
    unique_values.add(10)
    unique_values.add(20)
    unique_values.add(10)  # Duplicate ignored

    # Test membership
    has_10: bool = 10 in unique_values
    has_99: bool = 99 not in unique_values

    # Remove element
    unique_values.discard(20)

    size: int = len(unique_values)
    return size

def comprehensive_demo() -> int:
    """Demonstrate all container types working together"""
    # Lists
    numbers: list[int] = []
    numbers.append(1)
    numbers.append(2)
    numbers.append(3)

    # Dictionaries
    scores: dict[str, int] = {}
    scores["test1"] = numbers[0] * 10
    scores["test2"] = numbers[1] * 10

    # Sets
    unique_scores: set[int] = set()
    unique_scores.add(scores["test1"])
    unique_scores.add(scores["test2"])

    # Complex operations
    total_unique: int = len(unique_scores)
    total_numbers: int = len(numbers)
    total_scores: int = len(scores)

    return total_unique + total_numbers + total_scores