def test_string_membership() -> bool:
    """Test string membership operations"""
    text: str = "Hello World"
    substring: str = "Hello"

    # String contains
    has_hello: bool = substring in text

    return has_hello