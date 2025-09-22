"""Main CGen CLI entry point."""

import argparse
import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for cgen CLI."""
    if argv is None:
        argv = sys.argv[1:]

    # Check if user is requesting enhanced CLI features
    enhanced_commands = {
        "analyze", "verify", "optimize", "generate", "pipeline",
        "interactive", "benchmark", "demo"
    }

    if argv and argv[0] in enhanced_commands:
        # Use enhanced CLI for intelligence layer features
        try:
            from .enhanced_main import main as enhanced_main
            return enhanced_main(argv)
        except ImportError as e:
            print(f"Enhanced CLI not available: {e}", file=sys.stderr)
            print("Using basic CLI mode...", file=sys.stderr)

    # Basic CLI mode (legacy)
    parser = argparse.ArgumentParser(prog="cgen", description="Intelligent Python-to-C code generation")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # py2c subcommand
    py2c_parser = subparsers.add_parser("py2c", help="Convert Python to C")
    py2c_parser.add_argument("input", help="Input Python file")
    py2c_parser.add_argument("-o", "--output", help="Output C file")
    py2c_parser.add_argument("--optimize", action="store_true", help="Enable optimizations")

    # version subcommand
    subparsers.add_parser("version", help="Show version information")

    # Add help message about enhanced features
    parser.epilog = """
Enhanced Commands (use cgen <command> --help for details):
  analyze      - Comprehensive code analysis
  verify       - Formal verification with theorem proving
  optimize     - Show optimization opportunities
  generate     - Generate optimized C code with intelligence
  pipeline     - Run complete intelligence pipeline
  interactive  - Interactive CGen session
  benchmark    - Performance analysis
  demo         - Capability demonstrations
"""

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
