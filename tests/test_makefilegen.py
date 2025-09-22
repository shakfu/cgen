"""Test module for CGen makefilegen functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cgen.builder.makefilegen import (
    Builder,
    CGenMakefileGenerator,
    MakefileGenerator,
    unique_list,
)


class TestUniqueList:
    """Test the unique_list utility function."""

    def test_empty_list(self):
        """Test unique_list with empty list."""
        result = unique_list([])
        assert result == []

    def test_no_duplicates(self):
        """Test unique_list with no duplicates."""
        input_list = [1, 2, 3, 4, 5]
        result = unique_list(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_with_duplicates(self):
        """Test unique_list with duplicates."""
        input_list = [1, 2, 2, 3, 1, 4, 3, 5]
        result = unique_list(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_preserves_order(self):
        """Test that unique_list preserves the original order."""
        input_list = ["c", "a", "b", "a", "c"]
        result = unique_list(input_list)
        assert result == ["c", "a", "b"]


class TestBuilder:
    """Test the Builder class for direct compilation."""

    def setup_method(self):
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

    def teardown_method(self):
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

        assert builder.name == "test_program"
        assert builder.source_dir == Path(self.temp_dir)
        assert builder.compiler == "gcc"
        assert builder.std == "c99"
        assert builder.use_stc

    def test_disable_stc(self):
        """Test Builder with STC disabled."""
        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            use_stc=False
        )

        assert not builder.use_stc
        assert builder.stc_include_path is None

    def test_get_source_files(self):
        """Test getting source files from directory."""
        builder = Builder(source_dir=self.temp_dir)
        source_files = builder.get_source_files()

        assert len(source_files) == 1
        assert source_files[0].name == "test.c"

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

        assert "gcc" in cmd
        assert "-std=c99" in cmd
        assert "-Wall" in cmd
        assert "-O2" in cmd
        assert "-I" in cmd
        assert "/usr/include" in cmd
        assert "-l" in cmd
        assert "m" in cmd
        assert "-o" in cmd
        assert "test_program" in cmd

    @patch("subprocess.run")
    def test_build_success(self, mock_run):
        """Test successful build execution."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        builder = Builder(
            name="test_program",
            source_dir=self.temp_dir,
            use_stc=False
        )

        result = builder.build(verbose=False)
        assert result
        mock_run.assert_called_once()

    @patch("subprocess.run")
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
        assert not result


class TestMakefileGenerator:
    """Test the MakefileGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use build directory for test outputs
        self.test_build_dir = Path("build/test_outputs")
        self.test_build_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
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

        assert generator.name == "test_project"
        assert generator.source_dir == Path(self.temp_dir)
        assert generator.build_dir == self.test_build_dir
        assert generator.compiler == "gcc"
        assert generator.std == "c99"
        assert generator.use_stc

    def test_disable_stc(self):
        """Test MakefileGenerator with STC disabled."""
        generator = MakefileGenerator(
            name="test_project",
            source_dir=self.temp_dir,
            build_dir=str(self.test_build_dir),
            use_stc=False
        )

        assert not generator.use_stc
        assert generator.stc_include_path is None

    def test_comment_addition(self):
        """Test adding comments to Makefile."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.comment("Test comment")

        assert "# Test comment" in generator.content

    def test_variable_definition(self):
        """Test adding variable definitions."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.variable("CC", "gcc")
        generator.variable("CFLAGS", "-Wall", conditional=True)

        assert "CC = gcc" in generator.content
        assert "CFLAGS ?= -Wall" in generator.content

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
        assert ".PHONY: all" in content_str
        assert "all: main" in content_str
        assert "\t@echo 'Build complete'" in content_str

    def test_pattern_rule(self):
        """Test adding pattern rules."""
        generator = MakefileGenerator(build_dir=str(self.test_build_dir))
        generator.pattern_rule(
            "%.o",
            "%.c",
            ["$(CC) $(CFLAGS) -c $< -o $@"]
        )

        content_str = "\n".join(generator.content)
        assert "%.o: %.c" in content_str
        assert "\t$(CC) $(CFLAGS) -c $< -o $@" in content_str

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
        assert "CC = gcc" in makefile_content
        assert "TARGET = test_project" in makefile_content
        assert "SRCDIR = src" in makefile_content
        assert "CFLAGS = -Wall -O2" in makefile_content
        assert "INCLUDES = -Iinclude" in makefile_content
        assert "LIBS = -lm" in makefile_content
        assert "all: test_project" in makefile_content
        assert ".PHONY:" in makefile_content

    def test_stc_configuration(self):
        """Test STC configuration in Makefile."""
        generator = MakefileGenerator(
            name="test_project",
            build_dir=str(self.test_build_dir),
            use_stc=True,
            stc_include_path="/path/to/stc"
        )

        makefile_content = generator.generate_makefile()

        assert "STC_INCLUDE = /path/to/stc" in makefile_content
        assert "STC_FLAGS = -DSTC_ENABLED" in makefile_content
        assert "STC container support" in makefile_content

    def test_write_makefile(self):
        """Test writing Makefile to build directory."""
        generator = MakefileGenerator(
            name="test_project",
            build_dir=str(self.test_build_dir),
            use_stc=False
        )
        makefile_path = self.test_build_dir / "Makefile"

        result = generator.write_makefile(str(makefile_path))

        assert result
        assert makefile_path.exists()

        content = makefile_path.read_text()
        assert "test_project" in content


class TestCGenMakefileGenerator:
    """Test the CGenMakefileGenerator class."""

    def setup_method(self):
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

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test CGenMakefileGenerator initialization."""
        generator = CGenMakefileGenerator("my_project")
        assert generator.project_name == "my_project"

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

        assert isinstance(makefile_generator, MakefileGenerator)
        assert makefile_generator.name == "test_program"
        assert "-DDEBUG" in makefile_generator.flags
        assert "include" in makefile_generator.include_dirs
        assert not makefile_generator.use_stc

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

        assert isinstance(builder, Builder)
        assert builder.name == "test_program"
        assert "-DDEBUG" in builder.flags
        assert "include" in builder.include_dirs
        assert not builder.use_stc

    def test_file_not_found_error(self):
        """Test error handling for non-existent C file."""
        cgen_generator = CGenMakefileGenerator("test_project")

        with pytest.raises(FileNotFoundError):
            cgen_generator.create_for_generated_code("nonexistent.c")

        with pytest.raises(FileNotFoundError):
            cgen_generator.create_builder_for_generated_code("nonexistent.c")

    def test_default_output_name(self):
        """Test default output name generation."""
        cgen_generator = CGenMakefileGenerator("test_project")

        makefile_generator = cgen_generator.create_for_generated_code(
            str(self.test_c_file),
            use_stc=False
        )

        assert makefile_generator.name == "test"  # stem of test.c


# This file has been converted to pytest style
