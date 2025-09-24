#!/usr/bin/env python3
"""Test current CGen CLI functionality."""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest

# Add src to path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

from cgen.cli.main import SimpleCGenCLI, main
from cgen.pipeline import OptimizationLevel


class TestSimpleCGenCLI:
    """Test current CLI functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.cli = SimpleCGenCLI()

        # Create a temporary Python file for testing
        self.test_code = """def add(a: int, b: int) -> int:
    return a + b

def main():
    result: int = add(5, 3)
    return result
"""
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        self.temp_file.write(self.test_code)
        self.temp_file.close()

        # Create temporary build directory
        self.temp_build_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        if os.path.exists(self.temp_build_dir):
            shutil.rmtree(self.temp_build_dir)

    def test_cli_creation(self):
        """Test CLI object creation."""
        assert isinstance(self.cli, SimpleCGenCLI)
        assert hasattr(self.cli, 'log')
        assert hasattr(self.cli, 'default_build_dir')
        assert self.cli.default_build_dir == Path("build")

    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = self.cli.create_parser()
        assert parser is not None
        assert parser.prog == "cgen"

        # Test that all current commands are available
        help_text = parser.format_help()
        expected_commands = ["convert", "build", "clean", "batch"]

        for command in expected_commands:
            assert command in help_text

    def test_convert_command_parsing(self):
        """Test convert command argument parsing."""
        parser = self.cli.create_parser()

        # Test basic convert command
        args = parser.parse_args(["convert", self.temp_file.name])
        assert args.command == "convert"
        assert args.input_file == self.temp_file.name
        assert args.optimization == "moderate"

        # Test convert with optimization flag
        args = parser.parse_args(["convert", self.temp_file.name, "-O", "aggressive"])
        assert args.optimization == "aggressive"

    def test_build_command_parsing(self):
        """Test build command argument parsing."""
        parser = self.cli.create_parser()

        # Test basic build command
        args = parser.parse_args(["build", self.temp_file.name])
        assert args.command == "build"
        assert args.input_file == self.temp_file.name
        assert args.optimization == "moderate"
        assert not args.makefile
        assert args.compiler == "gcc"

        # Test build with makefile flag
        args = parser.parse_args(["build", self.temp_file.name, "-m"])
        assert args.makefile is True

        # Test build with compiler option
        args = parser.parse_args(["build", self.temp_file.name, "--compiler", "clang"])
        assert args.compiler == "clang"

    def test_clean_command_parsing(self):
        """Test clean command argument parsing."""
        parser = self.cli.create_parser()

        # Test clean command
        args = parser.parse_args(["clean"])
        assert args.command == "clean"

    def test_batch_command_parsing(self):
        """Test batch command argument parsing."""
        parser = self.cli.create_parser()

        # Test basic batch command
        args = parser.parse_args(["batch", "-s", "/tmp/test"])
        assert args.command == "batch"
        assert args.source_dir == "/tmp/test"
        assert args.output_dir == "build/src"
        assert not args.continue_on_error
        assert not args.summary_only

        # Test batch with all flags
        args = parser.parse_args([
            "batch", "-s", "/tmp/test", "-o", "/tmp/output",
            "--continue-on-error", "--summary-only", "-O", "aggressive"
        ])
        assert args.source_dir == "/tmp/test"
        assert args.output_dir == "/tmp/output"
        assert args.continue_on_error is True
        assert args.summary_only is True
        assert args.optimization == "aggressive"

    def test_optimization_level_mapping(self):
        """Test optimization level string conversion."""
        assert self.cli.get_optimization_level("none") == OptimizationLevel.NONE
        assert self.cli.get_optimization_level("basic") == OptimizationLevel.BASIC
        assert self.cli.get_optimization_level("moderate") == OptimizationLevel.MODERATE
        assert self.cli.get_optimization_level("aggressive") == OptimizationLevel.AGGRESSIVE

        # Test unknown level defaults to moderate
        assert self.cli.get_optimization_level("unknown") == OptimizationLevel.MODERATE

    def test_setup_build_directory(self):
        """Test build directory setup."""
        build_dir = Path(self.temp_build_dir) / "test_build"

        # Set verbose flag first to avoid AttributeError
        self.cli.verbose = False
        self.cli.setup_build_directory(build_dir)

        assert build_dir.exists()
        assert (build_dir / "src").exists()

    def test_copy_stc_library(self):
        """Test STC library copying."""
        build_dir = Path(self.temp_build_dir) / "test_build"
        build_dir.mkdir(exist_ok=True)
        (build_dir / "src").mkdir(exist_ok=True)

        # Set verbose flag first to avoid AttributeError
        self.cli.verbose = False
        # This should not fail even if STC library doesn't exist
        self.cli.copy_stc_library(build_dir)

    @patch('cgen.cli.main.CGenPipeline')
    def test_convert_command_execution(self, mock_pipeline_class):
        """Test convert command execution."""
        # Mock pipeline result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.errors = []
        mock_result.warnings = []
        mock_result.output_files = {'c_source': '/tmp/test.c'}

        mock_pipeline = MagicMock()
        mock_pipeline.convert.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        # Create args mock
        args = MagicMock()
        args.input_file = self.temp_file.name
        args.build_dir = self.temp_build_dir
        args.optimization = "moderate"

        # Set verbose flag to avoid AttributeError
        self.cli.verbose = False

        result = self.cli.convert_command(args)

        assert result == 0
        mock_pipeline_class.assert_called_once()
        mock_pipeline.convert.assert_called_once()

    @patch('cgen.cli.main.CGenPipeline')
    def test_convert_command_failure(self, mock_pipeline_class):
        """Test convert command with failure."""
        # Mock pipeline result
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.errors = ["Test error"]
        mock_result.warnings = []

        mock_pipeline = MagicMock()
        mock_pipeline.convert.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        # Create args mock
        args = MagicMock()
        args.input_file = self.temp_file.name
        args.build_dir = self.temp_build_dir
        args.optimization = "moderate"

        # Set verbose flag to avoid AttributeError
        self.cli.verbose = False

        result = self.cli.convert_command(args)

        assert result == 1

    def test_convert_command_nonexistent_file(self):
        """Test convert command with non-existent file."""
        args = MagicMock()
        args.input_file = "/nonexistent/file.py"
        args.build_dir = self.temp_build_dir

        result = self.cli.convert_command(args)

        assert result == 1

    @patch('shutil.move')
    @patch('cgen.cli.main.CGenPipeline')
    def test_build_command_execution(self, mock_pipeline_class, mock_move):
        """Test build command execution."""
        # Mock pipeline result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.errors = []
        mock_result.warnings = []
        mock_result.output_files = {'c_source': '/tmp/test.c'}
        mock_result.executable_path = '/tmp/test'

        mock_pipeline = MagicMock()
        mock_pipeline.convert.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        # Create args mock
        args = MagicMock()
        args.input_file = self.temp_file.name
        args.build_dir = self.temp_build_dir
        args.optimization = "moderate"
        args.makefile = False
        args.compiler = "gcc"

        # Set verbose flag to avoid AttributeError
        self.cli.verbose = False

        result = self.cli.build_command(args)

        assert result == 0
        mock_pipeline_class.assert_called_once()
        mock_pipeline.convert.assert_called_once()

    @patch('shutil.move')
    @patch('cgen.cli.main.CGenPipeline')
    def test_build_command_makefile_mode(self, mock_pipeline_class, mock_move):
        """Test build command in makefile mode."""
        # Mock pipeline result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.errors = []
        mock_result.warnings = []
        mock_result.output_files = {'c_source': '/tmp/test.c', 'makefile': '/tmp/Makefile'}

        mock_pipeline = MagicMock()
        mock_pipeline.convert.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        # Create args mock
        args = MagicMock()
        args.input_file = self.temp_file.name
        args.build_dir = self.temp_build_dir
        args.optimization = "moderate"
        args.makefile = True
        args.compiler = "gcc"

        # Set verbose flag to avoid AttributeError
        self.cli.verbose = False

        result = self.cli.build_command(args)

        assert result == 0

    def test_clean_command_execution(self):
        """Test clean command execution."""
        # Create a build directory to clean
        build_dir = Path(self.temp_build_dir) / "to_clean"
        build_dir.mkdir(exist_ok=True)
        (build_dir / "test_file").touch()

        assert build_dir.exists()

        # Create args mock
        args = MagicMock()
        args.build_dir = str(build_dir)

        result = self.cli.clean_command(args)

        assert result == 0
        assert not build_dir.exists()

    def test_clean_command_nonexistent_dir(self):
        """Test clean command with non-existent directory."""
        args = MagicMock()
        args.build_dir = "/nonexistent/build/dir"

        result = self.cli.clean_command(args)

        assert result == 0  # Should succeed even if directory doesn't exist

    @patch('cgen.cli.main.CGenPipeline')
    def test_batch_command_execution(self, mock_pipeline_class):
        """Test batch command execution."""
        # Create temporary source directory with Python files
        source_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()

        try:
            # Create test Python files
            test_file1 = Path(source_dir) / "test1.py"
            test_file2 = Path(source_dir) / "test2.py"
            test_file1.write_text("def func1(): pass")
            test_file2.write_text("def func2(): pass")

            # Mock pipeline result
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.errors = []
            mock_result.warnings = []

            mock_pipeline = MagicMock()
            mock_pipeline.convert.return_value = mock_result
            mock_pipeline_class.return_value = mock_pipeline

            # Create args mock
            args = MagicMock()
            args.source_dir = source_dir
            args.output_dir = output_dir
            args.continue_on_error = True
            args.summary_only = False
            args.optimization = "moderate"

            # Mock the output files to simulate successful translation
            with patch('builtins.open', MagicMock()):
                result = self.cli.batch_command(args)

            assert result == 0

        finally:
            shutil.rmtree(source_dir)
            shutil.rmtree(output_dir)

    def test_batch_command_no_python_files(self):
        """Test batch command with no Python files."""
        source_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()

        try:
            # Create args mock
            args = MagicMock()
            args.source_dir = source_dir
            args.output_dir = output_dir
            args.continue_on_error = True
            args.summary_only = False
            args.optimization = "moderate"

            result = self.cli.batch_command(args)

            assert result == 1  # Should fail when no Python files found

        finally:
            shutil.rmtree(source_dir)
            shutil.rmtree(output_dir)

    def test_batch_command_nonexistent_source_dir(self):
        """Test batch command with non-existent source directory."""
        args = MagicMock()
        args.source_dir = "/nonexistent/source/dir"
        args.output_dir = "/tmp/output"

        result = self.cli.batch_command(args)

        assert result == 1

    def test_run_no_command(self):
        """Test run method with no command."""
        with patch('sys.stdout', new_callable=StringIO):
            result = self.cli.run([])
            assert result == 1

    def test_run_unknown_command(self):
        """Test run method with unknown command."""
        with patch('sys.stderr', new_callable=StringIO):
            with pytest.raises(SystemExit) as exc_info:
                self.cli.run(["unknown_command"])
            assert exc_info.value.code == 2  # argparse error exit code

    @patch('cgen.cli.main.CGenPipeline')
    def test_run_convert_command(self, mock_pipeline_class):
        """Test run method with convert command."""
        # Mock pipeline result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.errors = []
        mock_result.warnings = []
        mock_result.output_files = {'c_source': '/tmp/test.c'}

        mock_pipeline = MagicMock()
        mock_pipeline.convert.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        result = self.cli.run(["--build-dir", self.temp_build_dir, "convert", self.temp_file.name])
        assert result == 0

    def test_verbose_flag(self):
        """Test verbose flag setting."""
        # Test that verbose flag is properly set
        parser = self.cli.create_parser()
        args = parser.parse_args(["--verbose", "convert", self.temp_file.name])
        assert args.verbose is True

        args = parser.parse_args(["convert", self.temp_file.name])
        assert args.verbose is False

        # Test that run() method sets the verbose attribute correctly
        with patch('cgen.cli.main.CGenPipeline'):
            self.cli.run(["--verbose", "--build-dir", self.temp_build_dir, "convert", self.temp_file.name])
            assert hasattr(self.cli, 'verbose')
            assert self.cli.verbose is True


class TestMainFunction:
    """Test the main entry point function."""

    def setup_method(self):
        """Set up test environment."""
        self.test_code = "def test(): pass"
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        self.temp_file.write(self.test_code)
        self.temp_file.close()

        self.temp_build_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        if os.path.exists(self.temp_build_dir):
            shutil.rmtree(self.temp_build_dir)

    @patch('cgen.cli.main.SimpleCGenCLI')
    def test_main_function_success(self, mock_cli_class):
        """Test main function with successful execution."""
        mock_cli = MagicMock()
        mock_cli.run.return_value = 0
        mock_cli_class.return_value = mock_cli

        result = main(["convert", self.temp_file.name])
        assert result == 0
        mock_cli.run.assert_called_once()

    @patch('cgen.cli.main.SimpleCGenCLI')
    def test_main_function_keyboard_interrupt(self, mock_cli_class):
        """Test main function with keyboard interrupt."""
        mock_cli = MagicMock()
        mock_cli.run.side_effect = KeyboardInterrupt()
        mock_cli_class.return_value = mock_cli

        result = main(["convert", self.temp_file.name])
        assert result == 1

    @patch('cgen.cli.main.SimpleCGenCLI')
    def test_main_function_exception(self, mock_cli_class):
        """Test main function with exception."""
        mock_cli = MagicMock()
        mock_cli.run.side_effect = Exception("Test error")
        mock_cli_class.return_value = mock_cli

        result = main(["convert", self.temp_file.name])
        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])