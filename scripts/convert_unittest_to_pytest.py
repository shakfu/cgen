#!/usr/bin/env python3
"""Script to convert unittest-style tests to pytest-style tests."""

import re
import sys
from pathlib import Path


def convert_unittest_to_pytest(content: str) -> str:
    """Convert unittest-style test file content to pytest-style."""

    # Remove unittest imports and add pytest
    content = re.sub(r'import unittest\n', '', content)
    content = re.sub(r'from unittest.*import.*\n', '', content)

    # Add pytest import if not present
    if 'import pytest' not in content:
        # Find the right place to insert pytest import
        lines = content.split('\n')
        import_section = []
        other_lines = []
        in_import_section = True

        for line in lines:
            if line.strip() == '' or line.startswith('"""') or line.startswith('#'):
                if in_import_section:
                    import_section.append(line)
                else:
                    other_lines.append(line)
            elif line.startswith('import ') or line.startswith('from '):
                import_section.append(line)
            else:
                in_import_section = False
                other_lines.append(line)

        # Add pytest import
        import_section.append('import pytest')
        content = '\n'.join(import_section + other_lines)

    # Remove sys.path.insert lines commonly found in unittest files
    content = re.sub(r'sys\.path\.insert\(.*?\)\n', '', content)
    content = re.sub(r'sys\.path\.append\(.*?\)\n', '', content)

    # Convert class inheritance
    content = re.sub(r'class (\w+)\(unittest\.TestCase\):', r'class \1:', content)

    # Convert assert methods to pytest assertions
    conversions = [
        # Basic equality
        (r'self\.assertEqual\(([^,]+),\s*([^,)]+)\)', r'assert \1 == \2'),
        (r'self\.assertNotEqual\(([^,]+),\s*([^,)]+)\)', r'assert \1 != \2'),

        # Truthiness
        (r'self\.assertTrue\(([^,)]+)\)', r'assert \1'),
        (r'self\.assertFalse\(([^,)]+)\)', r'assert not \1'),

        # None checks
        (r'self\.assertIsNone\(([^,)]+)\)', r'assert \1 is None'),
        (r'self\.assertIsNotNone\(([^,)]+)\)', r'assert \1 is not None'),

        # Type checks
        (r'self\.assertIsInstance\(([^,]+),\s*([^,)]+)\)', r'assert isinstance(\1, \2)'),

        # Contains/In checks
        (r'self\.assertIn\(([^,]+),\s*([^,)]+)\)', r'assert \1 in \2'),
        (r'self\.assertNotIn\(([^,]+),\s*([^,)]+)\)', r'assert \1 not in \2'),

        # Greater/Less comparisons
        (r'self\.assertGreater\(([^,]+),\s*([^,)]+)\)', r'assert \1 > \2'),
        (r'self\.assertGreaterEqual\(([^,]+),\s*([^,)]+)\)', r'assert \1 >= \2'),
        (r'self\.assertLess\(([^,]+),\s*([^,)]+)\)', r'assert \1 < \2'),
        (r'self\.assertLessEqual\(([^,]+),\s*([^,)]+)\)', r'assert \1 <= \2'),

        # Length checks
        (r'self\.assertEqual\(len\(([^,)]+)\),\s*([^,)]+)\)', r'assert len(\1) == \2'),

        # Regex matches
        (r'self\.assertRegex\(([^,]+),\s*([^,)]+)\)', r'assert re.search(\2, \1)'),
    ]

    for pattern, replacement in conversions:
        content = re.sub(pattern, replacement, content)

    # Convert setUp methods to pytest fixtures or setup_method
    content = re.sub(r'def setUp\(self\):', r'def setup_method(self):', content)
    content = re.sub(r'def tearDown\(self\):', r'def teardown_method(self):', content)

    # Handle assertRaises - this is more complex, let's handle it specially
    content = re.sub(
        r'with self\.assertRaises\(([^,)]+)\):',
        r'with pytest.raises(\1):',
        content
    )

    # Handle multi-line assert patterns that might be missed
    content = re.sub(r'self\.assert(\w+)\(', lambda m: f'assert_helper_{m.group(1).lower()}(', content)

    return content


def main():
    """Convert a unittest file to pytest style."""
    if len(sys.argv) != 2:
        print("Usage: python convert_unittest_to_pytest.py <test_file.py>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        sys.exit(1)

    # Read original content
    original_content = file_path.read_text()

    # Convert to pytest style
    converted_content = convert_unittest_to_pytest(original_content)

    # Write back
    file_path.write_text(converted_content)
    print(f"Converted {file_path} to pytest style")


if __name__ == "__main__":
    main()