"""Main CGen CLI entry point."""

import argparse
import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for cgen CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="cgen", description="Intelligent Python-to-C code generation")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # py2c subcommand
    py2c_parser = subparsers.add_parser("py2c", help="Convert Python to C")
    py2c_parser.add_argument("input", help="Input Python file")
    py2c_parser.add_argument("-o", "--output", help="Output C file")
    py2c_parser.add_argument("--optimize", action="store_true", help="Enable optimizations")

    # version subcommand
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args(argv)

    if args.command == "py2c":
        return handle_py2c(args)
    elif args.command == "version":
        return handle_version()
    else:
        parser.print_help()
        return 1


def handle_py2c(args) -> int:
    """Handle py2c command."""
    try:
        from ..core import convert_python_file_to_c

        output_file = args.output or args.input.replace(".py", ".c")

        print(f"Converting {args.input} to {output_file}...")
        convert_python_file_to_c(args.input, output_file)
        print("Conversion completed successfully.")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_version() -> int:
    """Handle version command."""
    from .. import __version__

    print(f"cgen {__version__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
