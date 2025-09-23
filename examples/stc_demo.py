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
    """Demonstrate STC dict integration (when implemented)"""
    scores: dict[str, int] = {}
    # scores["Alice"] = 95  # Will be implemented in future
    return 0