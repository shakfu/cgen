#!/usr/bin/env python3
"""Test runner script demonstrating different test categories and markers."""

import subprocess
import sys
import argparse
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")

    return result.returncode == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run cgen tests with different categories")
    parser.add_argument("--category", choices=[
        "all", "unit", "integration", "py2c", "core", "slow", "benchmark", "legacy"
    ], default="all", help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, help="Run tests in parallel")

    args = parser.parse_args()

    # Base pytest command
    base_cmd = ["python3", "-m", "pytest"]

    if args.verbose:
        base_cmd.append("-v")

    if args.parallel:
        base_cmd.extend(["-n", str(args.parallel)])

    # Change to project root
    original_cwd = Path.cwd()
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    try:
        success = True

        if args.category == "all":
            # Run all tests
            success &= run_command(
                base_cmd + ["tests/"],
                "All Tests (unittest + pytest)"
            )

        elif args.category == "legacy":
            # Run original unittest tests
            success &= run_command(
                ["python3", "-m", "unittest", "discover", "-v", "tests"],
                "Legacy unittest Tests"
            )

        elif args.category == "unit":
            # Run unit tests only
            success &= run_command(
                base_cmd + ["-m", "unit", "tests/"],
                "Unit Tests Only"
            )

        elif args.category == "integration":
            # Run integration tests only
            success &= run_command(
                base_cmd + ["-m", "integration", "tests/"],
                "Integration Tests Only"
            )

        elif args.category == "py2c":
            # Run Python-to-C conversion tests
            success &= run_command(
                base_cmd + ["-m", "py2c", "tests/"],
                "Python-to-C Conversion Tests"
            )

        elif args.category == "core":
            # Run core C generation tests
            success &= run_command(
                base_cmd + ["-m", "core", "tests/"],
                "Core C Generation Tests"
            )

        elif args.category == "slow":
            # Run only slow tests
            success &= run_command(
                base_cmd + ["-m", "slow", "tests/"],
                "Slow Tests Only"
            )

        elif args.category == "benchmark":
            # Run benchmark tests
            success &= run_command(
                base_cmd + ["-m", "benchmark", "tests/"],
                "Benchmark Tests"
            )

        # Summary
        print(f"\n{'='*60}")
        if success:
            print("🎉 All selected tests PASSED!")
            return 0
        else:
            print("💥 Some tests FAILED!")
            return 1

    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    import os
    sys.exit(main())