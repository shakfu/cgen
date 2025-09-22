"""Test module for CGen makefilegen functionality."""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from cgen.builder.makefilegen import (
    Builder,
    MakefileGenerator,
    CGenMakefileGenerator,
    unique_list,
)


class TestUniqueList(unittest.TestCase):
    """Test the unique_list utility function."""

    def test_empty_list(self):
        """Test unique_list with empty list."""
        result = unique_list([])
        self.assertEqual(result, [])

    def test_no_duplicates(self):
        """Test unique_list with no duplicates."""
        input_list = [1, 2, 3, 4, 5]
        result = unique_list(input_list)
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_with_duplicates(self):
        """Test unique_list with duplicates."""
        input_list = [1, 2, 2, 3, 1, 4, 3, 5]
        result = unique_list(input_list)
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_preserves_order(self):
        """Test that unique_list preserves the original order."""
        input_list = ['c', 'a', 'b', 'a', 'c']
        result = unique_list(input_list)
        self.assertEqual(result, ['c', 'a', 'b'])


class TestBuilder(unittest.TestCase):
    """Test the Builder class for direct compilation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_file = Path(self.temp_dir) / "test.c"
        self.source_file.write_text("""
#include <stdio.h>
int main() {
    printf("Hello, World!\\n");
    return 0;
}
""")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_basic_initialization(self):
        """Test basic Builder initialization."""
        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            compiler="gcc",
            std="c99"
        )

        self.assertEqual(builder.name, "test_program")
        self.assertEqual(builder.source_dir, Path(self.temp_dir))
        self.assertEqual(builder.compiler, "gcc")
        self.assertEqual(builder.std, "c99")
        self.assertTrue(builder.use_stc)

    def test_disable_stc(self):
        """Test Builder with STC disabled."""
        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            use_stc=False
        )

        self.assertFalse(builder.use_stc)
        self.assertIsNone(builder.stc_include_path)

    def test_get_source_files(self):
        """Test getting source files from directory."""
        builder = Builder(source_dir=self.temp_dir)
        source_files = builder.get_source_files()

        self.assertEqual(len(source_files), 1)
        self.assertEqual(source_files[0].name, "test.c")

    def test_build_command_generation(self):
        """Test build command generation."""
        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            compiler="gcc",
            std="c99",
            flags=["-Wall", "-O2"],
            include_dirs=["/usr/include"],
            libraries=["m"],
            use_stc=False
        )

        cmd = builder.build_command()

        self.assertIn("gcc", cmd)
        self.assertIn("-std=c99", cmd)
        self.assertIn("-Wall", cmd)
        self.assertIn("-O2", cmd)
        self.assertIn("-I", cmd)
        self.assertIn("/usr/include", cmd)
        self.assertIn("-l", cmd)
        self.assertIn("m", cmd)
        self.assertIn("-o", cmd)
        self.assertIn("test_program", cmd)

    @patch('subprocess.run')
    def test_build_success(self, mock_run):
        """Test successful build execution."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            use_stc=False
        )

        result = builder.build(verbose=False)
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_build_failure(self, mock_run):
        """Test build failure handling."""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "gcc", stderr="compilation error")

        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            use_stc=False
        )

        result = builder.build(verbose=False)
        self.assertFalse(result)


class TestMakefileGenerator(unittest.TestCase):
    """Test the MakefileGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use build directory for test outputs
        self.test_build_dir = Path("build/test_outputs")
        self.test_build_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_basic_initialization(self):
        """Test basic MakefileGenerator initialization."""
        generator = MakefileGenerator(
            name="test_project",
            source_dir=self.temp_dir,
            build_dir=str(self.test_build_dir),
            compiler="gcc",
            std="c99"
        )

        self.assertEqual(generator.name, "test_project")
        self.assertEqual(generator.source_dir, Path(self.temp_dir))
        self.assertEqual(generator.build_dir, self.test_build_dir)
        self.assertEqual(generator.compiler, "gcc")
        self.assertEqual(generator.std, "c99")
        self.assertTrue(generator.use_stc)

    def test_disable_stc(self):
        """Test MakefileGenerator with STC disabled."""
        generator = MakefileGenerator(
            name="test_project",
            source_dir=self.temp_dir,
            build_dir=str(self.test_build_dir),
            use_stc=False
        )

        self.assertFalse(generator.use_stc)
        self.assertIsNone(generator.stc_include_path)

    def test_comment_addition(self):
        """Test adding comments to Makefile."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.comment("Test comment")

        self.assertIn("# Test comment", generator.content)

    def test_variable_definition(self):
        """Test adding variable definitions."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.variable("CC", "gcc")
        generator.variable("CFLAGS", "-Wall", conditional=True)

        self.assertIn("CC = gcc", generator.content)
        self.assertIn("CFLAGS ?= -Wall", generator.content)

    def test_target_definition(self):
        """Test adding target definitions."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.target(
            "all",
            dependencies=["main"],
            commands=["@echo 'Build complete'"],
            phony=True
        )

        content_str = "\n".join(generator.content)
        self.assertIn(".PHONY: all", content_str)
        self.assertIn("all: main", content_str)
        self.assertIn("\t@echo 'Build complete'", content_str)

    def test_pattern_rule(self):
        """Test adding pattern rules."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.pattern_rule(
            "%.o",
            "%.c",
            ["$(CC) $(CFLAGS) -c $< -o $@"]
        )

        content_str = "\n".join(generator.content)
        self.assertIn("%.o: %.c", content_str)
        self.assertIn("\t$(CC) $(CFLAGS) -c $< -o $@", content_str)

    def test_makefile_generation(self):
        """Test complete Makefile generation."""
        generator = MakefileGenerator(
            name="test_project",
            source_dir="src",
            build_dir=str(self.test_build_dir),
            flags=["-Wall", "-O2"],
            include_dirs=["include"],
            libraries=["m"],
            use_stc=False
        )

        makefile_content = generator.generate_makefile()

        # Check for basic Makefile structure
        self.assertIn("CC = gcc", makefile_content)
        self.assertIn("TARGET = test_project", makefile_content)
        self.assertIn("SRCDIR = src", makefile_content)
        self.assertIn("CFLAGS = -Wall -O2", makefile_content)
        self.assertIn("INCLUDES = -Iinclude", makefile_content)
        self.assertIn("LIBS = -lm", makefile_content)
        self.assertIn("all: test_project", makefile_content)
        self.assertIn(".PHONY:", makefile_content)

    def test_stc_configuration(self):
        """Test STC configuration in Makefile."""
        generator = MakefileGenerator(
            name="test_project",
            build_dir=str(self.test_build_dir),
            use_stc=True,
            stc_include_path="/path/to/stc"
        )

        makefile_content = generator.generate_makefile()

        self.assertIn("STC_INCLUDE = /path/to/stc", makefile_content)
        self.assertIn("STC_FLAGS = -DSTC_ENABLED", makefile_content)
        self.assertIn("STC container support", makefile_content)

    def test_write_makefile(self):
        """Test writing Makefile to build directory."""
        generator = MakefileGenerator(
            name="test_project",
            build_dir=str(self.test_build_dir),
            use_stc=False
        )
        makefile_path = self.test_build_dir / "Makefile"

        result = generator.write_makefile(str(makefile_path))

        self.assertTrue(result)
        self.assertTrue(makefile_path.exists())

        content = makefile_path.read_text()
        self.assertIn("test_project", content)


class TestCGenMakefileGenerator(unittest.TestCase):
    """Test the CGenMakefileGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use build directory for test outputs
        self.test_build_dir = Path("build/test_outputs")
        self.test_build_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = tempfile.mkdtemp()
        self.test_c_file = Path(self.temp_dir) / "test.c"
        self.test_c_file.write_text("""
#include <stdio.h>
int main() {
    printf("Hello, World!\\n");
    return 0;
}
""")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test CGenMakefileGenerator initialization."""
        generator = CGenMakefileGenerator("my_project")
        self.assertEqual(generator.project_name, "my_project")

    def test_create_for_generated_code_makefile(self):
        """Test creating Makefile for generated C code."""
        cgen_generator = CGenMakefileGenerator("test_project")

        makefile_generator = cgen_generator.create_for_generated_code(
            str(self.test_c_file),
            output_name="test_program",
            use_stc=False,
            additional_flags=["-DDEBUG"],
            additional_includes=["include"]
        )

        self.assertIsInstance(makefile_generator, MakefileGenerator)
        self.assertEqual(makefile_generator.name, "test_program")
        self.assertIn("-DDEBUG", makefile_generator.flags)
        self.assertIn("include", makefile_generator.include_dirs)
        self.assertFalse(makefile_generator.use_stc)

    def test_create_for_generated_code_builder(self):
        """Test creating Builder for generated C code."""
        cgen_generator = CGenMakefileGenerator("test_project")

        builder = cgen_generator.create_builder_for_generated_code(
            str(self.test_c_file),
            output_name="test_program",
            use_stc=False,
            additional_flags=["-DDEBUG"],
            additional_includes=["include"]
        )

        self.assertIsInstance(builder, Builder)
        self.assertEqual(builder.name, "test_program")
        self.assertIn("-DDEBUG", builder.flags)
        self.assertIn("include", builder.include_dirs)
        self.assertFalse(builder.use_stc)

    def test_file_not_found_error(self):
        """Test error handling for non-existent C file."""
        cgen_generator = CGenMakefileGenerator("test_project")

        with self.assertRaises(FileNotFoundError):
            cgen_generator.create_for_generated_code("nonexistent.c")

        with self.assertRaises(FileNotFoundError):
            cgen_generator.create_builder_for_generated_code("nonexistent.c")

    def test_default_output_name(self):
        """Test default output name generation."""
        cgen_generator = CGenMakefileGenerator("test_project")

        makefile_generator = cgen_generator.create_for_generated_code(
            str(self.test_c_file),
            use_stc=False
        )

        self.assertEqual(makefile_generator.name, "test")  # stem of test.c


if __name__ == '__main__':
    unittest.main()