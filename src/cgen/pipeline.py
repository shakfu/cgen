"""CGen Pipeline - Complete Python-to-C Translation Pipeline.

This module implements the core CGen pipeline that transforms Python modules
into optimized C code and optionally builds executables. The pipeline consists
of six clear phases:

1. Validation Phase: Static-python style validation and translatability assessment
2. Analysis Phase: AST parsing and semantic element breakdown
3. Python Optimization Phase: Python-level optimizations
4. Mapping Phase: Python semantics to C semantics mapping
5. C Optimization Phase: C-level optimizations
6. Generation Phase: C code generation
7. Build Phase: Direct compilation or Makefile generation

Usage:
    from cgen.pipeline import CGenPipeline

    # Basic usage
    pipeline = CGenPipeline()
    result = pipeline.convert("my_module.py")

    # With build
    result = pipeline.convert("my_module.py", build="direct")
    result = pipeline.convert("my_module.py", build="makefile")
"""

import ast
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import existing components
from .frontend import (
    ASTAnalyzer,
    StaticPythonSubsetValidator,
    StaticConstraintChecker,
    CompileTimeEvaluator,
    LoopAnalyzer,
    FunctionSpecializer,
    VectorizationDetector,
    AnalysisContext,
    OptimizationLevel,
)
from .generator import PythonToCConverter, StyleOptions
from .builder import MakefileGenerator, CGenMakefileGenerator


class BuildMode(Enum):
    """Build mode options for the pipeline."""
    NONE = "none"           # Generate C code only
    DIRECT = "direct"       # Compile directly to executable
    MAKEFILE = "makefile"   # Generate Makefile


class PipelinePhase(Enum):
    """Pipeline phase identifiers."""
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    PYTHON_OPTIMIZATION = "python_optimization"
    MAPPING = "mapping"
    C_OPTIMIZATION = "c_optimization"
    GENERATION = "generation"
    BUILD = "build"


@dataclass
class PipelineResult:
    """Result of running the complete CGen pipeline."""
    success: bool
    input_file: str
    output_files: Dict[str, str]  # file_type -> file_path
    c_code: Optional[str] = None
    makefile_content: Optional[str] = None
    executable_path: Optional[str] = None
    phase_results: Dict[PipelinePhase, Any] = None
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.phase_results is None:
            self.phase_results = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class PipelineConfig:
    """Configuration for the CGen pipeline."""
    optimization_level: OptimizationLevel = OptimizationLevel.MODERATE
    style_options: Optional[StyleOptions] = None
    output_dir: Optional[str] = None
    build_mode: BuildMode = BuildMode.NONE
    enable_stc: bool = True
    compiler: str = "gcc"
    compiler_flags: List[str] = None
    include_dirs: List[str] = None
    libraries: List[str] = None

    def __post_init__(self):
        if self.style_options is None:
            self.style_options = StyleOptions()
        if self.compiler_flags is None:
            self.compiler_flags = ["-O2", "-Wall"]
        if self.include_dirs is None:
            self.include_dirs = []
        if self.libraries is None:
            self.libraries = []


class CGenPipeline:
    """Complete CGen Python-to-C translation pipeline."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the pipeline with configuration."""
        self.config = config or PipelineConfig()
        self._init_components()

    def _init_components(self):
        """Initialize pipeline components."""
        # Validation components
        self.subset_validator = StaticPythonSubsetValidator()
        self.constraint_checker = StaticConstraintChecker()

        # Analysis components
        self.ast_analyzer = ASTAnalyzer()

        # Optimization components
        self.compile_time_evaluator = CompileTimeEvaluator()
        self.loop_analyzer = LoopAnalyzer()
        self.function_specializer = FunctionSpecializer()
        self.vectorization_detector = VectorizationDetector()

        # Generation components
        self.py2c_converter = PythonToCConverter()

        # Writer for converting sequences to strings
        from .generator import Writer
        self.writer = Writer(self.config.style_options)

        # Build components
        self.makefile_generator = CGenMakefileGenerator()

    def convert(self,
                input_path: Union[str, Path],
                output_path: Optional[Union[str, Path]] = None,
                build: Optional[str] = None) -> PipelineResult:
        """
        Convert Python module through complete pipeline.

        Args:
            input_path: Path to Python file or module
            output_path: Output directory or file path
            build: Build mode ("none", "direct", "makefile")

        Returns:
            PipelineResult with all outputs and metadata
        """
        input_path = Path(input_path)
        if not input_path.exists():
            return PipelineResult(
                success=False,
                input_file=str(input_path),
                output_files={},
                errors=[f"Input file not found: {input_path}"]
            )

        # Set build mode if specified
        if build:
            self.config.build_mode = BuildMode(build)

        # Determine output directory
        if output_path:
            output_dir = Path(output_path)
        elif self.config.output_dir:
            output_dir = Path(self.config.output_dir)
        else:
            # Default to build/src structure
            output_dir = Path("build") / "src"

        output_dir.mkdir(parents=True, exist_ok=True)

        result = PipelineResult(
            success=True,
            input_file=str(input_path),
            output_files={}
        )

        try:
            # Read input file
            source_code = input_path.read_text()

            # Phase 1: Validation
            validation_result = self._validation_phase(source_code, input_path, result)
            if not validation_result:
                return result

            # Phase 2: Analysis
            analysis_result = self._analysis_phase(source_code, result)
            if not analysis_result:
                return result

            # Phase 3: Python Optimization
            python_opt_result = self._python_optimization_phase(analysis_result, result)

            # Phase 4: Mapping (currently combined with generation)
            # Phase 5: C Optimization (currently part of generation)
            # Phase 6: Generation
            generation_result = self._generation_phase(python_opt_result, output_dir, result)
            if not generation_result:
                return result

            # Phase 7: Build
            if self.config.build_mode != BuildMode.NONE:
                build_result = self._build_phase(output_dir, result)
                if not build_result:
                    return result

            return result

        except Exception as e:
            result.success = False
            result.errors.append(f"Pipeline error: {str(e)}")
            return result

    def _validation_phase(self, source_code: str, input_path: Path, result: PipelineResult) -> bool:
        """Phase 1: Validate static-python style and translatability."""
        try:
            # Parse AST for validation
            tree = ast.parse(source_code)

            # Validate Python subset compatibility
            validation_result = self.subset_validator.validate_code(source_code)
            result.phase_results[PipelinePhase.VALIDATION] = validation_result

            if not validation_result.is_valid:
                result.success = False
                result.errors.extend([str(issue) for issue in validation_result.issues])
                return False

            # Check static constraints
            constraint_report = self.constraint_checker.check_code(source_code)

            # Add warnings for constraint violations
            for violation in constraint_report.violations:
                if violation.severity.name in ['ERROR', 'CRITICAL']:
                    result.errors.append(f"Constraint violation: {violation.message}")
                else:
                    result.warnings.append(f"Constraint warning: {violation.message}")

            # Fail if there are critical constraint violations
            critical_errors = [v for v in constraint_report.violations
                             if v.severity.name in ['ERROR', 'CRITICAL']]
            if critical_errors:
                result.success = False
                return False

            return True

        except Exception as e:
            result.success = False
            result.errors.append(f"Validation phase error: {str(e)}")
            return False

    def _analysis_phase(self, source_code: str, result: PipelineResult) -> Optional[Any]:
        """Phase 2: AST parsing and semantic element breakdown."""
        try:
            # Analyze AST and extract semantic information
            analysis_result = self.ast_analyzer.analyze(source_code)
            result.phase_results[PipelinePhase.ANALYSIS] = analysis_result

            if not analysis_result.convertible:
                result.success = False
                result.errors.extend(analysis_result.errors)
                result.warnings.extend(analysis_result.warnings)
                return None

            # Store source code and AST for later phases
            analysis_result.source_code = source_code
            analysis_result.ast_root = ast.parse(source_code)
            return analysis_result

        except Exception as e:
            result.success = False
            result.errors.append(f"Analysis phase error: {str(e)}")
            return None

    def _python_optimization_phase(self, analysis_result: Any, result: PipelineResult) -> Any:
        """Phase 3: Python-level optimizations."""
        try:
            # Create analysis context
            context = AnalysisContext(
                source_code=analysis_result.source_code,
                ast_node=analysis_result.ast_root,
                analysis_result=analysis_result,
                optimization_level=self.config.optimization_level
            )

            optimizations = {}

            # Compile-time evaluation
            compile_time_result = self.compile_time_evaluator.optimize(context)
            optimizations['compile_time'] = compile_time_result

            # Loop analysis
            loop_result = self.loop_analyzer.optimize(context)
            optimizations['loops'] = loop_result

            # Function specialization
            specialization_result = self.function_specializer.optimize(context)
            optimizations['specialization'] = specialization_result

            result.phase_results[PipelinePhase.PYTHON_OPTIMIZATION] = optimizations
            return analysis_result  # For now, return original analysis

        except Exception as e:
            result.warnings.append(f"Python optimization phase warning: {str(e)}")
            return analysis_result  # Continue with unoptimized version

    def _generation_phase(self, analysis_result: Any, output_dir: Path, result: PipelineResult) -> bool:
        """Phase 6: C code generation (includes mapping and C optimization)."""
        try:
            # Generate C code using existing converter
            # This currently combines mapping, C optimization, and generation
            c_sequence = self.py2c_converter.convert_code(analysis_result.source_code)
            c_code = self.writer.write_str(c_sequence)

            # Write C file
            c_file_path = output_dir / (Path(result.input_file).stem + ".c")
            c_file_path.write_text(c_code)

            result.c_code = c_code
            result.output_files['c_source'] = str(c_file_path)
            result.phase_results[PipelinePhase.GENERATION] = {
                'c_file': str(c_file_path),
                'lines_of_code': len(c_code.splitlines())
            }

            return True

        except Exception as e:
            result.success = False
            result.errors.append(f"Generation phase error: {str(e)}")
            return False

    def _build_phase(self, output_dir: Path, result: PipelineResult) -> bool:
        """Phase 7: Build executable or generate Makefile."""
        try:
            c_file = result.output_files.get('c_source')
            if not c_file:
                result.errors.append("No C source file available for build phase")
                return False

            c_file_path = Path(c_file)

            if self.config.build_mode == BuildMode.MAKEFILE:
                # Generate Makefile
                makefile_gen = self.makefile_generator.create_for_generated_code(
                    c_file=str(c_file_path),
                    output_name=c_file_path.stem,
                    additional_flags=self.config.compiler_flags,
                    additional_includes=self.config.include_dirs
                )
                makefile_content = makefile_gen.generate_makefile()

                # Place Makefile in parent of source directory (build root)
                if output_dir.name == "src" and output_dir.parent.name == "build":
                    makefile_path = output_dir.parent / "Makefile"
                else:
                    makefile_path = output_dir / "Makefile"
                makefile_path.write_text(makefile_content)

                result.makefile_content = makefile_content
                result.output_files['makefile'] = str(makefile_path)

            elif self.config.build_mode == BuildMode.DIRECT:
                # Direct compilation - place executable in build root
                if output_dir.name == "src" and output_dir.parent.name == "build":
                    executable_path = output_dir.parent / c_file_path.stem
                else:
                    executable_path = output_dir / c_file_path.stem

                # Build compile command
                cmd = [self.config.compiler]
                cmd.extend(self.config.compiler_flags)
                cmd.extend([f"-I{inc}" for inc in self.config.include_dirs])
                cmd.extend([str(c_file_path), "-o", str(executable_path)])
                cmd.extend([f"-l{lib}" for lib in self.config.libraries])

                # Execute compilation
                import subprocess
                proc_result = subprocess.run(cmd, capture_output=True, text=True)

                if proc_result.returncode != 0:
                    result.success = False
                    result.errors.append(f"Compilation failed: {proc_result.stderr}")
                    return False

                result.executable_path = str(executable_path)
                result.output_files['executable'] = str(executable_path)

            result.phase_results[PipelinePhase.BUILD] = {
                'mode': self.config.build_mode.value,
                'outputs': result.output_files
            }

            return True

        except Exception as e:
            result.success = False
            result.errors.append(f"Build phase error: {str(e)}")
            return False


# Convenience functions for simple usage
def convert_python_to_c(input_path: Union[str, Path],
                       output_path: Optional[Union[str, Path]] = None,
                       optimization_level: OptimizationLevel = OptimizationLevel.MODERATE) -> PipelineResult:
    """Convert Python file to C code using default pipeline."""
    config = PipelineConfig(optimization_level=optimization_level)
    pipeline = CGenPipeline(config)
    return pipeline.convert(input_path, output_path)


def convert_and_build(input_path: Union[str, Path],
                     output_path: Optional[Union[str, Path]] = None,
                     build_mode: str = "makefile",
                     optimization_level: OptimizationLevel = OptimizationLevel.MODERATE) -> PipelineResult:
    """Convert Python file to C and build executable/Makefile."""
    config = PipelineConfig(
        optimization_level=optimization_level,
        build_mode=BuildMode(build_mode)
    )
    pipeline = CGenPipeline(config)
    return pipeline.convert(input_path, output_path)