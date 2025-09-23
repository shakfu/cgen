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
from ..common import log


class SimpleCGenCLI:
    """Simple CLI for CGen pipeline operations."""

    def __init__(self):
        """Initialize the CLI."""
        self.log = log.config(self.__class__.__name__)
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
  cgen batch                             # Batch translate all files in a directory
  cgen batch --summary-only              # Quick batch test with summary only
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

        # Batch command
        batch_parser = subparsers.add_parser(
            "batch",
            help="Batch translate all Python files in a directory",
            description="Translate all Python files in a directory to C code in build/src"
        )
        batch_parser.add_argument(
            "-s",
            "--source-dir",
            help="Directory containing Python files to translate"
        )
        batch_parser.add_argument(
            "-o",
            "--output-dir",
            default="build/src",
            help="Output directory for generated C files (default: build/src)"
        )
        batch_parser.add_argument(
            "--continue-on-error",
            action="store_true",
            help="Continue processing other files if one fails"
        )
        batch_parser.add_argument(
            "--summary-only",
            action="store_true",
            help="Show only summary statistics, not detailed output"
        )
        batch_parser.add_argument(
            "-O", "--optimization",
            choices=["none", "basic", "moderate", "aggressive"],
            default="moderate",
            help="Optimization level (default: moderate)"
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

        self.log.debug(f"Build directory: {build_dir}")
        self.log.debug(f"Source directory: {src_dir}")

        if self.verbose:
            self.log.debug(f"Build directory: {build_dir}")
            self.log.debug(f"Source directory: {src_dir}")

    def copy_stc_library(self, build_dir: Path) -> None:
        """Copy relevant STC library components to build directory."""
        src_stc_dir = Path(__file__).parent.parent / "ext" / "stc" / "include"
        if src_stc_dir.exists():
            dest_stc_dir = build_dir / "src" / "stc"
            if dest_stc_dir.exists():
                shutil.rmtree(dest_stc_dir)
            shutil.copytree(src_stc_dir, dest_stc_dir)
            self.log.debug(f"Copied STC library to: {dest_stc_dir}")
            if self.verbose:
                self.log.debug(f"Copied STC library to: {dest_stc_dir}")

    def convert_command(self, args) -> int:
        """Execute convert command."""
        input_path = Path(args.input_file)
        if not input_path.exists():
            self.log.error(f"Input file not found: {input_path}")
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
            self.log.error("Conversion failed")
            for error in result.errors:
                self.log.error(f"Error: {error}")
            return 1

        # Copy STC library
        self.copy_stc_library(build_dir)

        self.log.info(f"Conversion successful! C source: {result.output_files.get('c_source', 'N/A')}")
        if result.warnings:
            for warning in result.warnings:
                self.log.warning(f"Warning: {warning}")
        return 0

    def build_command(self, args) -> int:
        """Execute build command (compile directly or generate Makefile based on -m flag)."""
        input_path = Path(args.input_file)
        if not input_path.exists():
            self.log.error(f"Input file not found: {input_path}")
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
            self.log.error(error_msg)
            for error in result.errors:
                self.log.error(f"Error: {error}")
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

            self.log.info(f"Build preparation successful! C source: {result.output_files.get('c_source', 'N/A')}, Makefile: {result.output_files.get('makefile', 'N/A')}")
        else:
            # Direct compilation mode
            # Move executable to build root
            if result.executable_path:
                exe_src = Path(result.executable_path)
                exe_dest = build_dir / exe_src.name
                if exe_src != exe_dest:
                    shutil.move(str(exe_src), str(exe_dest))
                    result.executable_path = str(exe_dest)

            self.log.info(f"Compilation successful! Executable: {result.executable_path}")
            if result.executable_path:
                exe_name = Path(result.executable_path).name

        if result.warnings:
            for warning in result.warnings:
                self.log.warning(f"Warning: {warning}")

        return 0

    def clean_command(self, args) -> int:
        """Execute clean command."""
        build_dir = Path(args.build_dir)

        if build_dir.exists():
            shutil.rmtree(build_dir)
            self.log.info(f"Cleaned build directory: {build_dir}")
        else:
            self.log.info(f"Build directory doesn't exist: {build_dir}")

        return 0

    def batch_command(self, args) -> int:
        """Execute batch command."""
        import os

        source_dir = args.source_dir
        output_dir = args.output_dir
        continue_on_error = args.continue_on_error
        summary_only = args.summary_only

        self.log.info("Starting CGen batch translation")

        # Check if source_dir directory exists
        if not os.path.exists(source_dir):
            self.log.error(f"Source directory not found: {source_dir}")
            return 1

        # Create output directory
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.log.error(f"Failed to create output directory {output_dir}: {e}")
            return 1

        # Find all Python files in source_dir directory
        python_files = []
        for filename in os.listdir(source_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(source_dir, filename)
                python_files.append(filepath)

        if not python_files:
            self.log.warning(f"No Python files found in {source_dir}")
            return 1

        python_files.sort()  # Process in alphabetical order

        self.log.info(f"Batch processing {len(python_files)} files from {source_dir} to {output_dir}")

        # Process each file
        successful_translations = 0
        failed_translations = 0
        translation_results = []

        for i, input_file in enumerate(python_files, 1):
            filename = os.path.basename(input_file)
            output_filename = filename.replace('.py', '.c')
            output_file = os.path.join(output_dir, output_filename)

            if not summary_only:
                self.log.info(f"[{i}/{len(python_files)}] Processing {filename}")

            try:
                # Use the pipeline to convert the file
                config = PipelineConfig(
                    optimization_level=self.get_optimization_level(args.optimization),
                    output_dir=output_dir,
                    build_mode=BuildMode.NONE
                )

                pipeline = CGenPipeline(config)
                result = pipeline.convert(Path(input_file))

                if result.success:
                    successful_translations += 1
                    # Count lines in generated C file
                    try:
                        with open(output_file, 'r') as f:
                            lines_generated = len(f.readlines())
                    except:
                        lines_generated = 0

                    translation_results.append({
                        'input': filename,
                        'output': output_filename,
                        'status': 'SUCCESS',
                        'lines': lines_generated
                    })

                    if not summary_only:
                        self.log.info(f"    -> {output_filename} ({lines_generated} lines)")
                else:
                    failed_translations += 1
                    error_msg = "; ".join(result.errors) if result.errors else "Unknown error"
                    translation_results.append({
                        'input': filename,
                        'output': output_filename,
                        'status': 'FAILED',
                        'error': error_msg
                    })

                    if not summary_only:
                        self.log.error(f"Failed: {error_msg}")

                    if not continue_on_error:
                        self.log.info(f"Stopping due to error in {filename}. Use --continue-on-error to continue processing.")
                        break

            except Exception as e:
                failed_translations += 1
                error_msg = str(e)
                translation_results.append({
                    'input': filename,
                    'output': output_filename,
                    'status': 'FAILED',
                    'error': error_msg
                })

                if not summary_only:
                    self.log.error(f"Failed: {error_msg}")

                if not continue_on_error:
                    self.log.warn(f"Stopping due to error in {filename}. Use --continue-on-error to continue processing.")
                    break

        # Print summary
        self.log.info(f"Total files processed: {len(translation_results)}")
        self.log.info(f"Successful translations: {successful_translations}")
        self.log.info(f"Failed translations: {failed_translations}")

        # if failed_translations > 0:
        #     print()
        #     print("Failed translations:")
        #     for result in translation_results:
        #         if result['status'] == 'FAILED':
        #             print(f"  {result['input']}: {result['error']}")

        # if successful_translations > 0:
        #     total_lines = sum(result['lines'] for result in translation_results if result['status'] == 'SUCCESS')
        #     print(f"Total C code lines generated: {total_lines}")

        return 0 if failed_translations == 0 else 1

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
        elif args.command == "batch":
            return self.batch_command(args)
        else:
            self.log.error(f"Unknown command: {args.command}")
            return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    try:
        cli = SimpleCGenCLI()
        return cli.run(argv)
    except KeyboardInterrupt:
        self.log.error("Interrupted")
        return 1
    except Exception as e:
        self.log.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())