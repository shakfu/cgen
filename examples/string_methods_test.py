def test_string_methods() -> str:
    """Test string methods"""
    text: str = "Hello World"

    # Test string methods
    upper_text: str = text.upper()
    index: int = text.find("World")

    return upper_text