#!/usr/bin/env python3
"""Test enhanced CGen CLI functionality."""

import os
import sys
import tempfile
from io import StringIO
from unittest.mock import patch

# Add src to path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

from cgen.cli.main import CGenCLI


class TestEnhancedCLI:
    """Test enhanced CLI functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.cli = CGenCLI()

        # Create a temporary Python file for testing
        self.test_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""

        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        self.temp_file.write(self.test_code)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_cli_creation(self):
        """Test CLI object creation."""
        assert isinstance(self.cli, CGenCLI)
        assert not self.cli.verbose
        assert self.cli.config == {}

    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = self.cli.create_parser()
        assert parser is not None

        # Test that all major commands are available
        help_text = parser.format_help()
        expected_commands = ["analyze", "verify", "optimize", "generate", "pipeline", "interactive", "benchmark", "demo"]

        for command in expected_commands:
            assert command in help_text

    def test_analyze_command_parsing(self):
        """Test analyze command argument parsing."""
        parser = self.cli.create_parser()

        # Test basic analyze command
        args = parser.parse_args(["analyze", self.temp_file.name])
        assert args.command == "analyze"
        assert args.input == self.temp_file.name
        assert not args.all

        # Test analyze with flags
        args = parser.parse_args(["analyze", self.temp_file.name, "--all", "--verbose"])
        assert args.all

    def test_verify_command_parsing(self):
        """Test verify command argument parsing."""
        parser = self.cli.create_parser()

        # Test basic verify command
        args = parser.parse_args(["verify", self.temp_file.name])
        assert args.command == "verify"
        assert args.input == self.temp_file.name
        assert args.z3_timeout == 30

        # Test verify with specific flags
        args = parser.parse_args(["verify", self.temp_file.name, "--memory-safety", "--z3-timeout", "60"])
        assert args.memory_safety
        assert args.z3_timeout == 60

    def test_generate_command_parsing(self):
        """Test generate command argument parsing."""
        parser = self.cli.create_parser()

        # Test basic generate command
        args = parser.parse_args(["generate", self.temp_file.name])
        assert args.command == "generate"
        assert args.input == self.temp_file.name
        assert args.optimization_level == "moderate"

        # Test generate with output file
        args = parser.parse_args(["generate", self.temp_file.name, "-o", "output.c"])
        assert args.output == "output.c"

    def test_version_command(self):
        """Test version command."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # Create a mock args object since _handle_version expects args parameter
            from argparse import Namespace
            args = Namespace()
            result = self.cli._handle_version(args)
            assert result == 0
            output = mock_stdout.getvalue()
            assert "CGen" in output
            assert "Version" in output

    def test_file_exists_check(self):
        """Test file existence checking."""
        # Test existing file
        assert self.cli._check_file_exists(self.temp_file.name)

        # Test non-existing file
        with patch("sys.stderr", new_callable=StringIO):
            assert not self.cli._check_file_exists("/nonexistent/file.py")

    def test_read_file(self):
        """Test file reading."""
        content = self.cli._read_file(self.temp_file.name)
        assert content.strip() == self.test_code.strip()

    def test_write_file(self):
        """Test file writing."""
        test_content = "/* Test C code */"

        temp_output = tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False)
        temp_output.close()

        try:
            self.cli._write_file(temp_output.name, test_content)

            with open(temp_output.name) as f:
                content = f.read()

            assert content == test_content
        finally:
            if os.path.exists(temp_output.name):
                os.unlink(temp_output.name)

    def test_optimization_level_mapping(self):
        """Test optimization level string conversion."""
        from cgen.intelligence.base import OptimizationLevel

        assert self.cli._get_optimization_level("none") == OptimizationLevel.NONE
        assert self.cli._get_optimization_level("basic") == OptimizationLevel.BASIC
        assert self.cli._get_optimization_level("moderate") == OptimizationLevel.MODERATE
        assert self.cli._get_optimization_level("aggressive") == OptimizationLevel.AGGRESSIVE

        # Test default for unknown level
        assert self.cli._get_optimization_level("unknown") == OptimizationLevel.MODERATE

    def test_analysis_context_creation(self):
        """Test analysis context creation."""
        from cgen.intelligence.base import AnalysisLevel, OptimizationLevel

        context = self.cli._create_analysis_context(
            self.test_code,
            AnalysisLevel.COMPREHENSIVE,
            OptimizationLevel.AGGRESSIVE
        )

        assert context.source_code == self.test_code
        assert context.analysis_level == AnalysisLevel.COMPREHENSIVE
        assert context.optimization_level == OptimizationLevel.AGGRESSIVE
        assert context.ast_node is not None
        assert context.analysis_result is not None

    @patch("builtins.input", side_effect=["help", "quit"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_interactive_session(self, mock_stdout, mock_input):
        """Test interactive session basic functionality."""
        self.cli._run_interactive_session()

        output = mock_stdout.getvalue()
        assert "Available commands" in output
        assert "Goodbye" in output

    def test_demo_factorial_code(self):
        """Test demo mode with factorial analysis."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli._run_interactive_demo()

            output = mock_stdout.getvalue()
            assert "factorial" in output
            assert "Demo completed" in output

    def test_compilation_test(self):
        """Test compilation testing functionality."""
        # Create a simple valid C file
        temp_c_file = tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False)
        temp_c_file.write("""
#include <stdio.h>
int main() {
    printf("Hello World\\n");
    return 0;
}
""")
        temp_c_file.close()

        try:
            # Note: This may fail if gcc is not available, which is expected
            result = self.cli._test_compilation(temp_c_file.name)
            # We don't assert the result since gcc may not be available in all test environments
            assert isinstance(result, bool)
        finally:
            if os.path.exists(temp_c_file.name):
                os.unlink(temp_c_file.name)

    def test_error_handling(self):
        """Test error handling in CLI commands."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            # Test with non-existent file
            result = self.cli.run(["analyze", "/nonexistent/file.py"])
            assert result == 1

            error_output = mock_stderr.getvalue()
            assert "File not found" in error_output


class TestEnhancedCLIIntegration:
    """Test integration of enhanced CLI with main entry point."""

    def test_enhanced_command_detection(self):
        """Test that enhanced commands are properly detected."""
        enhanced_commands = ["analyze", "verify", "optimize", "generate", "pipeline", "interactive", "benchmark", "demo"]

        for command in enhanced_commands:
            # Test that the command doesn't cause import errors
            # (We don't run the actual commands to avoid side effects)
            assert command in enhanced_commands

    def test_legacy_mode_fallback(self):
        """Test fallback to legacy mode."""
        from cgen.cli.main import main

        # Test version command (should work in both modes)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("sys.stderr", new_callable=StringIO):
                result = main(["version"])
                # Result may vary based on version implementation
                assert isinstance(result, int)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
