"""Dedicated py2c CLI command."""

import argparse
import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for py2c CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="py2c", description="Convert Python code to C")

    parser.add_argument("input", help="Input Python file")
    parser.add_argument("-o", "--output", help="Output C file")
    parser.add_argument("--optimize", action="store_true", help="Enable optimizations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args(argv)

    try:
        from ..core import convert_python_file_to_c

        output_file = args.output or args.input.replace(".py", ".c")

        if args.verbose:
            print(f"Converting {args.input} to {output_file}...")

        convert_python_file_to_c(args.input, output_file)

        if args.verbose:
            print("Conversion completed successfully.")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
