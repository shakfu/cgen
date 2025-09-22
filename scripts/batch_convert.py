#!/usr/bin/env python3
"""Batch convert remaining unittest files to pytest."""

import re
from pathlib import Path

# List of files to convert
files_to_convert = [
    "tests/test_frontend.py",
    "tests/test_intelligence_bounds_checker.py",
    "tests/test_intelligence_call_graph.py",
    "tests/test_intelligence_compile_time_evaluator.py",
    "tests/test_intelligence_function_specializer.py",
    "tests/test_intelligence_loop_analyzer.py",
    "tests/test_intelligence_static_analyzer.py",
    "tests/test_intelligence_symbolic_executor.py",
    "tests/test_intelligence_vectorization_detector.py",
    "tests/test_makefilegen.py",
    "tests/test_cli.py"
]

def convert_file(file_path: Path):
    """Convert a single unittest file to pytest."""
    print(f"Converting {file_path}...")

    content = file_path.read_text()

    # Store original first to backup if needed
    backup_path = file_path.with_suffix('.py.backup')
    backup_path.write_text(content)

    # Basic replacements
    replacements = [
        # Remove unittest imports
        (r'import unittest\n', ''),
        (r'from unittest\.mock import.*\n', lambda m: m.group(0)),  # Keep mock imports
        (r'from unittest import.*\n', ''),

        # Add pytest import
        (r'("""[^"]*"""\n\n)', r'\1import pytest\n'),

        # Remove sys.path modifications
        (r'sys\.path\.insert\([^)]*\)\n', ''),
        (r'sys\.path\.append\([^)]*\)\n', ''),

        # Convert class inheritance
        (r'class ([^(]+)\(unittest\.TestCase\):', r'class \1:'),

        # Convert setUp/tearDown methods
        (r'def setUp\(self\):', r'def setup_method(self):'),
        (r'def tearDown\(self\):', r'def teardown_method(self):'),

        # Convert basic assertions
        (r'self\.assertEqual\(([^,]+),\s*([^)]+)\)', r'assert \1 == \2'),
        (r'self\.assertNotEqual\(([^,]+),\s*([^)]+)\)', r'assert \1 != \2'),
        (r'self\.assertTrue\(([^)]+)\)', r'assert \1'),
        (r'self\.assertFalse\(([^)]+)\)', r'assert not \1'),
        (r'self\.assertIsNone\(([^)]+)\)', r'assert \1 is None'),
        (r'self\.assertIsNotNone\(([^)]+)\)', r'assert \1 is not None'),
        (r'self\.assertIn\(([^,]+),\s*([^)]+)\)', r'assert \1 in \2'),
        (r'self\.assertNotIn\(([^,]+),\s*([^)]+)\)', r'assert \1 not in \2'),
        (r'self\.assertGreater\(([^,]+),\s*([^)]+)\)', r'assert \1 > \2'),
        (r'self\.assertLess\(([^,]+),\s*([^)]+)\)', r'assert \1 < \2'),
        (r'self\.assertGreaterEqual\(([^,]+),\s*([^)]+)\)', r'assert \1 >= \2'),
        (r'self\.assertLessEqual\(([^,]+),\s*([^)]+)\)', r'assert \1 <= \2'),
        (r'self\.assertIsInstance\(([^,]+),\s*([^)]+)\)', r'assert isinstance(\1, \2)'),

        # Handle assertRaises
        (r'with self\.assertRaises\(([^)]+)\):', r'with pytest.raises(\1):'),

        # Remove if __name__ == '__main__' block
        (r'\n\nif __name__ == \'__main__\':\n\s+unittest\.main\(\)\n?$', '\n\n# This file has been converted to pytest style\n'),
        (r'\nif __name__ == \'__main__\':\n\s+unittest\.main\(\)\n?$', '\n# This file has been converted to pytest style\n'),
    ]

    # Apply replacements
    for pattern, replacement in replacements:
        if callable(replacement):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Make sure pytest is imported
    if 'import pytest' not in content:
        # Find the right place to add pytest import
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_idx = i + 1
            elif line.strip() == '' and insert_idx > 0:
                break
        lines.insert(insert_idx, 'import pytest')
        content = '\n'.join(lines)

    # Write the converted content
    file_path.write_text(content)
    print(f"✓ Converted {file_path}")

def main():
    """Convert all files."""
    for file_name in files_to_convert:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                convert_file(file_path)
            except Exception as e:
                print(f"❌ Error converting {file_path}: {e}")
        else:
            print(f"❌ File not found: {file_path}")

if __name__ == "__main__":
    main()