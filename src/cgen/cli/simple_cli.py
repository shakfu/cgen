#!/usr/bin/env python3
"""CGen - Simple CLI for Python-to-C Pipeline.

A streamlined command-line interface that provides easy access to the complete
Python-to-C translation pipeline with structured build directory management.

Usage:
    cgen convert input.py                 # Convert to C (generates build/src/input.c)
    cgen build input.py                   # Convert and create Makefile
    cgen compile input.py                 # Convert and compile to executable
    cgen clean                            # Clean build directory
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional

# Import the pipeline
from ..pipeline import CGenPipeline, PipelineConfig, BuildMode, OptimizationLevel


class SimpleCGenCLI:
    """Simple CLI for CGen pipeline operations."""

    def __init__(self):
        """Initialize the CLI."""
        self.default_build_dir = Path("build")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            prog="cgen",
            description="CGen - Python-to-C Translation Pipeline",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  cgen convert my_module.py              # Generate C code in build/src/
  cgen build my_module.py                # Generate C code and compile executable
  cgen build my_module.py -m             # Generate C code and Makefile
  cgen build my_module.py -O aggressive  # Compile with aggressive optimization
  cgen clean                             # Clean build directory

Build Directory Structure:
  build/
  ├── src/                 # Generated C source files
  ├── Makefile             # Generated build system (if -m flag used)
  └── executable           # Compiled binary (if -m flag not used)
            """
        )

        # Global options
        parser.add_argument(
            "--build-dir", "-d",
            type=str,
            default="build",
            help="Build directory (default: build)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Verbose output"
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Convert command
        convert_parser = subparsers.add_parser(
            "convert",
            help="Convert Python to C code"
        )
        convert_parser.add_argument(
            "input_file",
            help="Python file to convert"
        )
        convert_parser.add_argument(
            "-O", "--optimization",
            choices=["none", "basic", "moderate", "aggressive"],
            default="moderate",
            help="Optimization level (default: moderate)"
        )

        # Build command
        build_parser = subparsers.add_parser(
            "build",
            help="Convert Python to C and build (compile directly or generate Makefile)"
        )
        build_parser.add_argument(
            "input_file",
            help="Python file to convert"
        )
        build_parser.add_argument(
            "-m", "--makefile",
            action="store_true",
            help="Generate Makefile instead of compiling directly"
        )
        build_parser.add_argument(
            "-O", "--optimization",
            choices=["none", "basic", "moderate", "aggressive"],
            default="moderate",
            help="Optimization level (default: moderate)"
        )
        build_parser.add_argument(
            "--compiler",
            default="gcc",
            help="C compiler to use (default: gcc)"
        )

        # Clean command
        clean_parser = subparsers.add_parser(
            "clean",
            help="Clean build directory"
        )

        return parser

    def get_optimization_level(self, level_str: str) -> OptimizationLevel:
        """Convert string to OptimizationLevel."""
        mapping = {
            "none": OptimizationLevel.NONE,
            "basic": OptimizationLevel.BASIC,
            "moderate": OptimizationLevel.MODERATE,
            "aggressive": OptimizationLevel.AGGRESSIVE
        }
        return mapping.get(level_str, OptimizationLevel.MODERATE)

    def setup_build_directory(self, build_dir: Path) -> None:
        """Set up the build directory structure."""
        # Create build directory structure
        build_dir.mkdir(exist_ok=True)
        src_dir = build_dir / "src"
        src_dir.mkdir(exist_ok=True)

        if self.verbose:
            print(f"Build directory: {build_dir}")
            print(f"Source directory: {src_dir}")

    def copy_stc_library(self, build_dir: Path) -> None:
        """Copy relevant STC library components to build directory."""
        src_stc_dir = Path(__file__).parent.parent / "ext" / "stc" / "include"
        if src_stc_dir.exists():
            dest_stc_dir = build_dir / "src" / "stc"
            if dest_stc_dir.exists():
                shutil.rmtree(dest_stc_dir)
            shutil.copytree(src_stc_dir, dest_stc_dir)
            if self.verbose:
                print(f"Copied STC library to: {dest_stc_dir}")

    def convert_command(self, args) -> int:
        """Execute convert command."""
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1

        build_dir = Path(args.build_dir)
        self.setup_build_directory(build_dir)

        # Configure pipeline
        config = PipelineConfig(
            optimization_level=self.get_optimization_level(args.optimization),
            output_dir=str(build_dir / "src"),
            build_mode=BuildMode.NONE
        )

        # Run pipeline
        pipeline = CGenPipeline(config)
        result = pipeline.convert(input_path)

        if not result.success:
            print("Conversion failed:", file=sys.stderr)
            for error in result.errors:
                print(f"  Error: {error}", file=sys.stderr)
            return 1

        # Copy STC library
        self.copy_stc_library(build_dir)

        print(f"✓ Conversion successful!")
        print(f"  C source: {result.output_files.get('c_source', 'N/A')}")
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  Warning: {warning}")

        return 0

    def build_command(self, args) -> int:
        """Execute build command (compile directly or generate Makefile based on -m flag)."""
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1

        build_dir = Path(args.build_dir)
        self.setup_build_directory(build_dir)

        # Determine build mode based on -m flag
        if args.makefile:
            build_mode = BuildMode.MAKEFILE
        else:
            build_mode = BuildMode.DIRECT

        # Configure pipeline
        config = PipelineConfig(
            optimization_level=self.get_optimization_level(args.optimization),
            output_dir=str(build_dir / "src"),
            build_mode=build_mode,
            compiler=getattr(args, 'compiler', 'gcc')
        )

        # Run pipeline
        pipeline = CGenPipeline(config)
        result = pipeline.convert(input_path)

        if not result.success:
            error_msg = "Build failed:" if args.makefile else "Compilation failed:"
            print(error_msg, file=sys.stderr)
            for error in result.errors:
                print(f"  Error: {error}", file=sys.stderr)
            return 1

        # Copy STC library
        self.copy_stc_library(build_dir)

        if args.makefile:
            # Makefile generation mode
            # Move Makefile to build root
            if 'makefile' in result.output_files:
                makefile_src = Path(result.output_files['makefile'])
                makefile_dest = build_dir / "Makefile"
                if makefile_src != makefile_dest:
                    shutil.move(str(makefile_src), str(makefile_dest))
                    result.output_files['makefile'] = str(makefile_dest)

            print(f"✓ Build preparation successful!")
            print(f"  C source: {result.output_files.get('c_source', 'N/A')}")
            print(f"  Makefile: {result.output_files.get('makefile', 'N/A')}")
            print(f"  To build: cd {build_dir} && make")
        else:
            # Direct compilation mode
            # Move executable to build root
            if result.executable_path:
                exe_src = Path(result.executable_path)
                exe_dest = build_dir / exe_src.name
                if exe_src != exe_dest:
                    shutil.move(str(exe_src), str(exe_dest))
                    result.executable_path = str(exe_dest)

            print(f"✓ Compilation successful!")
            print(f"  C source: {result.output_files.get('c_source', 'N/A')}")
            print(f"  Executable: {result.executable_path}")
            if result.executable_path:
                exe_name = Path(result.executable_path).name
                print(f"  To run: ./{build_dir}/{exe_name}")

        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  Warning: {warning}")

        return 0

    def clean_command(self, args) -> int:
        """Execute clean command."""
        build_dir = Path(args.build_dir)

        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"✓ Cleaned build directory: {build_dir}")
        else:
            print(f"Build directory doesn't exist: {build_dir}")

        return 0

    def run(self, argv: Optional[list] = None) -> int:
        """Run the CLI."""
        parser = self.create_parser()
        args = parser.parse_args(argv)

        # Set verbose flag
        self.verbose = args.verbose

        # Handle no command
        if not args.command:
            parser.print_help()
            return 1

        # Dispatch to command handlers
        if args.command == "convert":
            return self.convert_command(args)
        elif args.command == "build":
            return self.build_command(args)
        elif args.command == "clean":
            return self.clean_command(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    try:
        cli = SimpleCGenCLI()
        return cli.run(argv)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())