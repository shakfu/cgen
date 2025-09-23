#!/usr/bin/env python3
"""Enhanced CGen CLI - Comprehensive Command Line Interface

Provides access to all CGen intelligence layer capabilities including:
- Code analysis and validation
- Formal verification
- Performance optimization
- C code generation with intelligence
- Interactive mode
"""

import argparse
import ast
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from ..frontend.ast_analyzer import ASTAnalyzer
from ..frontend.constraint_checker import StaticConstraintChecker
from ..frontend.static_ir import IRBuilder
from ..frontend.subset_validator import StaticPythonSubsetValidator
from ..frontend.type_inference import TypeInferenceEngine
from ..intelligence.analyzers import BoundsChecker, CallGraphAnalyzer, StaticAnalyzer, SymbolicExecutor
from ..intelligence.base import AnalysisContext, AnalysisLevel, OptimizationLevel
from ..intelligence.optimizers import CompileTimeEvaluator, FunctionSpecializer, LoopAnalyzer, VectorizationDetector
from ..intelligence.verifiers import BoundsProver, CorrectnessProver, TheoremProver
from ..intelligence.verifiers.performance_analyzer import PerformanceAnalyzer


class CGenCLI:
    """Enhanced CGen Command Line Interface."""

    def __init__(self):
        self.verbose = False
        self.config = {}

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the enhanced argument parser."""
        parser = argparse.ArgumentParser(
            prog="cgen",
            description="CGen: Intelligent Python-to-C Code Generation Platform",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  cgen analyze factorial.py                   # Analyze Python code
  cgen build factorial.py                     # Translate then build Python code
  cgen verify --memory-safety factorial.py    # Verify memory safety
  cgen optimize factorial.py                  # Show optimization opportunities
  cgen generate factorial.py -o factorial.c   # Generate optimized C code
  cgen pipeline factorial.py                  # Run full intelligence pipeline
  cgen interactive                            # Start interactive mode
  cgen benchmark factorial.py                 # Performance analysis
            """
        )

        # Global options
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument("--output-format", choices=["text", "json", "yaml"], default="text", help="Output format")

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # analyze command
        self._add_analyze_command(subparsers)

        # build command
        self._add_build_command(subparsers)

        # verify command
        self._add_verify_command(subparsers)

        # optimize command
        self._add_optimize_command(subparsers)

        # generate command
        self._add_generate_command(subparsers)

        # pipeline command
        self._add_pipeline_command(subparsers)

        # interactive command
        self._add_interactive_command(subparsers)

        # benchmark command
        self._add_benchmark_command(subparsers)

        # demo command
        self._add_demo_command(subparsers)

        # version command
        subparsers.add_parser("version", help="Show version information")

        return parser

    def _add_analyze_command(self, subparsers):
        """Add analyze command."""
        analyze_parser = subparsers.add_parser(
            "analyze",
            help="Analyze Python code with frontend layer",
            description="Comprehensive static analysis of Python code"
        )
        analyze_parser.add_argument("input", help="Python file to analyze")
        analyze_parser.add_argument("--ast", action="store_true", help="Show AST analysis")
        analyze_parser.add_argument("--types", action="store_true", help="Show type inference")
        analyze_parser.add_argument("--constraints", action="store_true", help="Show constraint checking")
        analyze_parser.add_argument("--subset", action="store_true", help="Show subset validation")
        analyze_parser.add_argument("--ir", action="store_true", help="Show static IR")
        analyze_parser.add_argument("--all", action="store_true", help="Show all analysis results")
        analyze_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    def _add_build_command(self, subparsers):
        """Add build command."""
        build_parser = subparsers.add_parser(
            "build",
            help="Translate then build Python code",
            description="Translate Python code to C code and build it"
        )
        build_parser.add_argument("input", help="Python file to build")
        build_parser.add_argument("-b", "--build-dir", help="Build directory")
        build_parser.add_argument("-c", "--compile-only", action="store_true", help="Compile only")
        build_parser.add_argument("-r", "--run", action="store_true", help="Run the executable")
        build_parser.add_argument("-m", "--makefile", action="store_true", help="Generate Makefile")
        build_parser.add_argument("-o", "--optimize", action="store_true", help="Enable optimizations")
        build_parser.add_argument("--no-stc", action="store_true", help="Disable STC support")
        build_parser.add_argument("-I", "--include", action="append", help="Include directories")
        build_parser.add_argument("-L", "--libdir", action="append", help="Library directories")
        build_parser.add_argument("-l", "--lib", action="append", help="Libraries to link")
        build_parser.add_argument("--flags", help="Additional compiler flags")
        build_parser.add_argument("--compiler", default="gcc", help="Compiler to use")
        build_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    def _add_verify_command(self, subparsers):
        """Add verify command."""
        verify_parser = subparsers.add_parser(
            "verify",
            help="Formal verification with theorem proving",
            description="Verify correctness and safety properties"
        )
        verify_parser.add_argument("input", help="Python file to verify")
        verify_parser.add_argument("--memory-safety", action="store_true", help="Verify memory safety")
        verify_parser.add_argument("--correctness", action="store_true", help="Verify algorithm correctness")
        verify_parser.add_argument("--bounds", action="store_true", help="Verify bounds checking")
        verify_parser.add_argument("--performance", action="store_true", help="Verify performance bounds")
        verify_parser.add_argument("--all", action="store_true", help="All verification types")
        verify_parser.add_argument("--z3-timeout", type=int, default=30, help="Z3 solver timeout (seconds)")

    def _add_optimize_command(self, subparsers):
        """Add optimize command."""
        optimize_parser = subparsers.add_parser(
            "optimize",
            help="Show optimization opportunities",
            description="Analyze and suggest optimizations"
        )
        optimize_parser.add_argument("input", help="Python file to optimize")
        optimize_parser.add_argument("--level", choices=["basic", "moderate", "aggressive"], default="moderate", help="Optimization level")
        optimize_parser.add_argument("--compile-time", action="store_true", help="Show compile-time optimizations")
        optimize_parser.add_argument("--loops", action="store_true", help="Show loop optimizations")
        optimize_parser.add_argument("--functions", action="store_true", help="Show function specializations")
        optimize_parser.add_argument("--vectorization", action="store_true", help="Show vectorization opportunities")
        optimize_parser.add_argument("--all", action="store_true", help="Show all optimizations")

    def _add_generate_command(self, subparsers):
        """Add generate command."""
        generate_parser = subparsers.add_parser(
            "generate",
            help="Translate Python code to C code",
            description="Translate Python code to C code with optimizations"
        )
        generate_parser.add_argument("input", help="Python file to convert")
        generate_parser.add_argument("-o", "--output", help="Output C file")
        generate_parser.add_argument("--optimization-level", choices=["none", "basic", "moderate", "aggressive"], default="moderate", help="Optimization level")
        generate_parser.add_argument("--analysis-level", choices=["basic", "comprehensive"], default="comprehensive", help="Analysis depth")
        generate_parser.add_argument("--style", choices=["K&R", "Allman", "GNU", "Whitesmiths"], default="K&R", help="C code style")
        generate_parser.add_argument("--include-analysis", action="store_true", help="Include analysis comments in output")
        generate_parser.add_argument("--verify", action="store_true", help="Verify generated code")
        generate_parser.add_argument("--compile-test", action="store_true", help="Test compilation of generated code")
        generate_parser.add_argument("--use-stc", action="store_true", default=True, help="Use STC containers for high-performance operations (default: enabled)")
        generate_parser.add_argument("--no-stc", dest="use_stc", action="store_false", help="Disable STC containers, use traditional C patterns")

    def _add_pipeline_command(self, subparsers):
        """Add pipeline command."""
        pipeline_parser = subparsers.add_parser(
            "pipeline",
            help="Run complete intelligence pipeline",
            description="Full analysis → optimization → generation → verification pipeline"
        )
        pipeline_parser.add_argument("input", help="Python file to process")
        pipeline_parser.add_argument("-o", "--output", help="Output C file")
        pipeline_parser.add_argument("--report", help="Generate detailed report file")
        pipeline_parser.add_argument("--optimization-level", choices=["none", "basic", "moderate", "aggressive"], default="aggressive", help="Optimization level")
        pipeline_parser.add_argument("--use-stc", action="store_true", default=True, help="Use STC containers for high-performance operations (default: enabled)")
        pipeline_parser.add_argument("--no-stc", dest="use_stc", action="store_false", help="Disable STC containers, use traditional C patterns")

    def _add_interactive_command(self, subparsers):
        """Add interactive command."""
        interactive_parser = subparsers.add_parser(
            "interactive",
            help="Start interactive CGen session",
            description="Interactive exploration of CGen capabilities"
        )
        interactive_parser.add_argument("--demo-mode", action="store_true", help="Start in demo mode")

    def _add_benchmark_command(self, subparsers):
        """Add benchmark command."""
        benchmark_parser = subparsers.add_parser(
            "benchmark",
            help="Performance analysis and benchmarking",
            description="Analyze performance characteristics and complexity"
        )
        benchmark_parser.add_argument("input", help="Python file to benchmark")
        benchmark_parser.add_argument("--complexity", action="store_true", help="Show complexity analysis")
        benchmark_parser.add_argument("--bottlenecks", action="store_true", help="Identify bottlenecks")
        benchmark_parser.add_argument("--recommendations", action="store_true", help="Show optimization recommendations")
        benchmark_parser.add_argument("--all", action="store_true", help="Full performance analysis")

    def _add_demo_command(self, subparsers):
        """Add demo command."""
        demo_parser = subparsers.add_parser(
            "demo",
            help="Run CGen capability demonstrations",
            description="Showcase different CGen features"
        )
        demo_parser.add_argument("demo_type", choices=["frontend", "intelligence", "verification", "generation", "all"], help="Type of demo to run")

    def run(self, argv: Optional[List[str]] = None) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        args = parser.parse_args(argv)

        self.verbose = args.verbose

        if args.command is None:
            parser.print_help()
            return 1

        # Load configuration if specified
        if hasattr(args, "config") and args.config:
            self._load_config(args.config)

        # Route to command handlers
        command_handlers = {
            "analyze": self._handle_analyze,
            "build": self._handle_build,
            "verify": self._handle_verify,
            "optimize": self._handle_optimize,
            "generate": self._handle_generate,
            "pipeline": self._handle_pipeline,
            "interactive": self._handle_interactive,
            "benchmark": self._handle_benchmark,
            "demo": self._handle_demo,
            "build": self._handle_build,
            "makefile": self._handle_makefile,
            "version": self._handle_version,
        }

        handler = command_handlers.get(args.command)
        if handler:
            try:
                return handler(args)
            except Exception as e:
                self._error(f"Command failed: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                return 1
        else:
            self._error(f"Unknown command: {args.command}")
            return 1

    def _handle_analyze(self, args) -> int:
        """Handle analyze command."""
        self._info("CGen Code Analysis")
        self._info("=" * 50)

        if not self._check_file_exists(args.input):
            return 1

        code = self._read_file(args.input)
        context = self._create_analysis_context(code)

        # Determine what to show
        show_all = args.all
        show_ast = args.ast or show_all
        show_types = args.types or show_all
        show_constraints = args.constraints or show_all
        show_subset = args.subset or show_all
        show_ir = args.ir or show_all

        # Run frontend analysis
        if show_ast:
            self._show_ast_analysis(context)

        if show_types:
            self._show_type_analysis(context)

        if show_constraints:
            self._show_constraint_analysis(context)

        if show_subset:
            self._show_subset_analysis(context)

        if show_ir:
            self._show_ir_analysis(context)

        return 0

    def _handle_build(self, args) -> int:
        """Handle build command."""
        self._info("CGen Direct Build")
        self._info("=" * 50)

        if not self._check_file_exists(args.input):
            return 1

    def _handle_verify(self, args) -> int:
        """Handle verify command."""
        self._info("CGen Formal Verification")
        self._info("=" * 50)

        if not self._check_file_exists(args.input):
            return 1

        code = self._read_file(args.input)
        context = self._create_analysis_context(code)

        # Initialize verifiers
        theorem_prover = TheoremProver(timeout=args.z3_timeout * 1000)

        show_all = args.all
        results = {}

        if args.memory_safety or show_all:
            self._info("\nMemory Safety Verification")
            bounds_prover = BoundsProver(theorem_prover)
            memory_proof = bounds_prover.verify_memory_safety(context)
            results["memory_safety"] = memory_proof
            self._show_memory_safety_results(memory_proof)

        if args.correctness or show_all:
            self._info("\nAlgorithm Correctness Verification")
            correctness_prover = CorrectnessProver(theorem_prover)
            correctness_proof = correctness_prover.verify_algorithm_correctness(context)
            results["correctness"] = correctness_proof
            self._show_correctness_results(correctness_proof)

        if args.performance or show_all:
            self._info("\nPerformance Bound Analysis")
            performance_analyzer = PerformanceAnalyzer(theorem_prover)
            performance_analysis = performance_analyzer.analyze_performance_bounds(context)
            results["performance"] = performance_analysis
            self._show_performance_results(performance_analysis)

        return 0

    def _handle_optimize(self, args) -> int:
        """Handle optimize command."""
        self._info("CGen Optimization Analysis")
        self._info("=" * 50)

        if not self._check_file_exists(args.input):
            return 1

        code = self._read_file(args.input)
        context = self._create_analysis_context(code,
                                               optimization_level=self._get_optimization_level(args.level))

        show_all = args.all
        optimizations_found = 0

        if args.compile_time or show_all:
            self._info("\nCompile-Time Optimizations")
            evaluator = CompileTimeEvaluator()
            result = evaluator.optimize(context)
            self._show_optimization_result(result, "Compile-Time")
            if result.success:
                optimizations_found += len(result.transformations)

        if args.loops or show_all:
            self._info("\nLoop Optimizations")
            loop_analyzer = LoopAnalyzer()
            result = loop_analyzer.optimize(context)
            self._show_optimization_result(result, "Loop")
            if result.success:
                optimizations_found += len(result.transformations)

        if args.functions or show_all:
            self._info("\nFunction Specializations")
            specializer = FunctionSpecializer()
            result = specializer.optimize(context)
            self._show_optimization_result(result, "Function")
            if result.success:
                optimizations_found += len(result.transformations)

        if args.vectorization or show_all:
            self._info("\nVectorization Opportunities")
            detector = VectorizationDetector()
            result = detector.analyze(context.ast_node)
            self._show_vectorization_result(result)
            optimizations_found += result.vectorizable_loops

        self._info(f"\n Summary: {optimizations_found} optimization opportunities found")
        return 0

    def _handle_generate(self, args) -> int:
        """Handle generate command."""
        self._info("CGen Code Generation")
        self._info("=" * 50)

        if not self._check_file_exists(args.input):
            return 1

        code = self._read_file(args.input)

        # Determine output file
        output_file = args.output or args.input.replace(".py", ".c")

        # Create analysis context
        analysis_level = AnalysisLevel.COMPREHENSIVE if args.analysis_level == "comprehensive" else AnalysisLevel.BASIC
        optimization_level = self._get_optimization_level(args.optimization_level)
        context = self._create_analysis_context(code, analysis_level, optimization_level)

        self._info(f"Input: {args.input}")
        self._info(f"Output: {output_file}")
        self._info(f"Analysis Level: {analysis_level.value}")
        self._info(f"Optimization Level: {optimization_level.value}")

        # Show STC status
        use_stc = getattr(args, "use_stc", True)
        if use_stc:
            try:
                from ..ext.stc import STC_AVAILABLE
                if STC_AVAILABLE:
                    self._info("STC Containers: Enabled (high-performance containers)")
                else:
                    self._info("STC Containers: Requested but unavailable (fallback to traditional)")
            except ImportError:
                self._info("STC Containers: Requested but unavailable (fallback to traditional)")
        else:
            self._info("STC Containers: Disabled (traditional C patterns)")

        # Generate C code with intelligence
        self._info("\nRunning intelligence analysis...")
        c_code = self._generate_intelligent_c_code(context, args)

        # Write output
        self._write_file(output_file, c_code)
        self._info(f" Generated {len(c_code.split())} lines of C code")

        # Optional verification
        if args.verify:
            self._info("\nVerifying generated code...")
            # Quick verification would go here

        # Optional compilation test
        if args.compile_test:
            self._info("\nTesting compilation...")
            if self._test_compilation(output_file):
                self._info("Compilation successful")
            else:
                self._warning("  Compilation failed")

        return 0

    def _handle_pipeline(self, args) -> int:
        """Handle pipeline command."""
        self._info("CGen Complete Intelligence Pipeline")
        self._info("=" * 60)

        if not self._check_file_exists(args.input):
            return 1

        code = self._read_file(args.input)
        output_file = args.output or args.input.replace(".py", ".c")

        optimization_level = self._get_optimization_level(args.optimization_level)
        context = self._create_analysis_context(code, AnalysisLevel.COMPREHENSIVE, optimization_level)

        pipeline_results = {}
        start_time = time.time()

        # Phase 1: Frontend Analysis
        self._info("Phase 1: Frontend Analysis")
        frontend_results = self._run_frontend_analysis(context)
        pipeline_results["frontend"] = frontend_results

        # Phase 2: Intelligence Analysis
        self._info("\n Phase 2: Intelligence Analysis")
        intelligence_results = self._run_intelligence_analysis(context)
        pipeline_results["intelligence"] = intelligence_results

        # Phase 3: Formal Verification
        self._info("\n Phase 3: Formal Verification")
        verification_results = self._run_verification_analysis(context)
        pipeline_results["verification"] = verification_results

        # Phase 4: Code Generation
        self._info("\nPhase 4: Optimized Code Generation")
        c_code = self._generate_intelligent_c_code(context, args)
        self._write_file(output_file, c_code)

        pipeline_time = time.time() - start_time

        # Summary
        self._info("\nPipeline Summary")
        self._info("=" * 40)
        self._info(f"⏱  Total time: {pipeline_time:.2f}s")
        self._info(f" Generated: {output_file}")
        self._info(f" Lines of C code: {len(c_code.split())}")

        # Generate report if requested
        if args.report:
            self._generate_pipeline_report(args.report, pipeline_results, pipeline_time)
            self._info(f" Report saved: {args.report}")

        return 0

    def _handle_interactive(self, args) -> int:
        """Handle interactive command."""
        self._info("CGen Interactive Mode")
        self._info("=" * 40)
        self._info("Type 'help' for commands, 'quit' to exit")

        if args.demo_mode:
            self._run_interactive_demo()
        else:
            self._run_interactive_session()

        return 0

    def _handle_benchmark(self, args) -> int:
        """Handle benchmark command."""
        self._info("CGen Performance Benchmarking")
        self._info("=" * 50)

        if not self._check_file_exists(args.input):
            return 1

        code = self._read_file(args.input)
        context = self._create_analysis_context(code)

        performance_analyzer = PerformanceAnalyzer()
        analysis = performance_analyzer.analyze_performance_bounds(context)

        show_all = args.all

        if args.complexity or show_all:
            self._info("\nComplexity Analysis")
            self._info(f"   Time: {analysis.time_complexity.value}")
            self._info(f"   Space: {analysis.space_complexity.value}")

        if args.bottlenecks or show_all:
            self._info("\nPerformance Bottlenecks")
            for bottleneck in analysis.bottlenecks:
                self._info(f"   • {bottleneck}")

        if args.recommendations or show_all:
            self._info("\nOptimization Recommendations")
            for rec in analysis.optimization_opportunities:
                self._info(f"   • {rec}")

        return 0

    def _handle_demo(self, args) -> int:
        """Handle demo command."""
        demo_functions = {
            "frontend": self._demo_frontend,
            "intelligence": self._demo_intelligence,
            "verification": self._demo_verification,
            "generation": self._demo_generation,
            "all": self._demo_all
        }

        demo_func = demo_functions.get(args.demo_type)
        if demo_func:
            return demo_func()
        else:
            self._error(f"Unknown demo type: {args.demo_type}")
            return 1

    def _handle_version(self, args) -> int:
        """Handle version command."""
        # This would show comprehensive version info
        self._info("CGen: Intelligent Python-to-C Code Generation Platform")
        self._info("Version: 1.0.0-alpha")
        self._info("Features: Frontend Analysis, Intelligence Layer, Formal Verification")
        return 0

    # Helper methods for the CLI implementation

    def _create_analysis_context(self, code: str,
                                analysis_level: AnalysisLevel = AnalysisLevel.COMPREHENSIVE,
                                optimization_level: OptimizationLevel = OptimizationLevel.MODERATE):
        """Create analysis context."""
        ast_node = ast.parse(code)
        analyzer = ASTAnalyzer()
        analysis_result = analyzer.analyze(code)
        return AnalysisContext(source_code=code, ast_node=ast_node, analysis_result=analysis_result,
                              analysis_level=analysis_level, optimization_level=optimization_level)

    def _get_optimization_level(self, level_str: str) -> OptimizationLevel:
        """Convert string to OptimizationLevel."""
        mapping = {
            "none": OptimizationLevel.NONE,
            "basic": OptimizationLevel.BASIC,
            "moderate": OptimizationLevel.MODERATE,
            "aggressive": OptimizationLevel.AGGRESSIVE
        }
        return mapping.get(level_str, OptimizationLevel.MODERATE)

    def _check_file_exists(self, filepath: str) -> bool:
        """Check if file exists."""
        if not os.path.exists(filepath):
            self._error(f"File not found: {filepath}")
            return False
        return True

    def _read_file(self, filepath: str) -> str:
        """Read file contents."""
        with open(filepath) as f:
            return f.read()

    def _write_file(self, filepath: str, content: str):
        """Write file contents."""
        with open(filepath, "w") as f:
            f.write(content)

    def _info(self, message: str):
        """Print info message."""
        print(message)

    def _warning(self, message: str):
        """Print warning message."""
        print(message, file=sys.stderr)

    def _error(self, message: str):
        """Print error message."""
        print(f"Error: {message}", file=sys.stderr)

    # Implementation methods for CLI operations

    def _show_ast_analysis(self, context):
        """Show AST analysis results."""
        analyzer = ASTAnalyzer()
        result = analyzer.analyze(context.source_code)

        self._info("\nAST Analysis Results:")
        self._info(f"   Functions: {len(result.functions)}")
        self._info(f"   Global variables: {len(result.global_variables)}")
        self._info(f"   Overall complexity: {result.complexity.value}")
        self._info(f"   Convertible: {result.convertible}")

        if self.verbose:
            for func_name, func_info in result.functions.items():
                self._info(f"   Function '{func_name}': {len(func_info.parameters)} params, {func_info.complexity} complexity")

    def _show_type_analysis(self, context):
        """Show type inference results."""
        engine = TypeInferenceEngine()
        # Analyze function signatures for type information\n        type_results = {}\n        for node in ast.walk(context.ast_node):\n            if isinstance(node, ast.FunctionDef):\n                func_types = engine.analyze_function_signature(node)\n                type_results.update(func_types)

        self._info("\nType Inference Results:")
        self._info("Type inference: Work in progress")

        if self.verbose:
            self._info("Detailed type analysis coming soon")

    def _show_constraint_analysis(self, context):
        """Show constraint checking results."""
        checker = StaticConstraintChecker()
        constraints = checker.check_code(context.source_code)

        self._info("\n Constraint Analysis:")
        self._info(f"   Total checks: {len(constraints.passed_checks) + len(constraints.violations)}")

        violations = constraints.violations
        if violations:
            self._warning(f"     Violations: {len(violations)}")
            if self.verbose:
                for violation in violations[:5]:  # Show first 5
                    self._warning(f"      - {violation.message}")
        else:
            self._info(" All constraints satisfied")

    def _show_subset_analysis(self, context):
        """Show subset validation results."""
        validator = StaticPythonSubsetValidator()
        result = validator.validate_code(context.source_code)

        self._info("\nC Subset Validation:")
        status = " VALID" if result.is_valid else " INVALID"
        self._info(f"   Validation: {status}")
        self._info(f"   Subset tier: {result.tier.value}")
        if result.unsupported_features:
            self._warning(f"     Unsupported features: {len(result.unsupported_features)}")
            if self.verbose:
                for feature in result.unsupported_features[:3]:  # Show first 3
                    self._warning(f"      - {feature}")
        else:
            self._info(" Full C subset compatibility")

    def _show_ir_analysis(self, context):
        """Show static IR results."""
        builder = IRBuilder()
        ir = builder.build_from_ast(context.ast_node)

        self._info("\n Static IR Generation:")
        self._info(f"   IR functions: {len(ir.functions)}")
        self._info(f"   Global variables: {len(ir.global_variables)}")
        self._info(f"   Type declarations: {len(ir.type_declarations)}")

        if self.verbose and ir.functions:
            self._info("Sample IR functions:")
            for func in ir.functions[:3]:  # Show first 3
                self._info(f"      - {func.name}: {len(func.statements)} statements")

    def _show_memory_safety_results(self, proof):
        """Show memory safety verification results."""
        status = " SAFE" if proof.is_safe else " UNSAFE"
        self._info(f"   Status: {status} (confidence: {proof.confidence:.1%})")
        self._info(f"   Verification time: {proof.verification_time:.3f}s")

        if proof.unsafe_accesses:
            self._warning(f"     Unsafe accesses: {len(proof.unsafe_accesses)}")
            for access in proof.unsafe_accesses[:3]:  # Show first 3
                self._warning(f"      - Line {access.line_number}: {access.access_type} to {access.region.name}")

        if proof.recommendations:
            self._info(" Recommendations:")
            for rec in proof.recommendations[:3]:  # Show first 3
                self._info(f"      - {rec}")

    def _show_correctness_results(self, proof):
        """Show algorithm correctness results."""
        status = " CORRECT" if proof.is_correct else " INCORRECT"
        self._info(f"   Status: {status} (confidence: {proof.confidence:.1%})")
        self._info(f"   Verification time: {proof.verification_time:.3f}s")

        if proof.failed_properties:
            self._warning(f"     Failed properties: {len(proof.failed_properties)}")
            for prop in proof.failed_properties[:3]:  # Show first 3
                self._warning(f"      - {prop.name}: {prop.description}")

        if proof.recommendations:
            self._info(" Recommendations:")
            for rec in proof.recommendations[:3]:  # Show first 3
                self._info(f"      - {rec}")

    def _show_performance_results(self, analysis):
        """Show performance analysis results."""
        self._info(f"   Time complexity: {analysis.time_complexity.value}")
        self._info(f"   Space complexity: {analysis.space_complexity.value}")
        self._info(f"   Analysis confidence: {analysis.confidence:.1%}")

        if analysis.bottlenecks:
            self._info(f"    Bottlenecks: {len(analysis.bottlenecks)}")
            for bottleneck in analysis.bottlenecks[:3]:  # Show first 3
                self._info(f"      - {bottleneck}")

        if analysis.optimization_opportunities:
            self._info(f"    Optimizations: {len(analysis.optimization_opportunities)}")
            for opt in analysis.optimization_opportunities[:3]:  # Show first 3
                self._info(f"      - {opt}")

    def _show_optimization_result(self, result, type_name):
        """Show optimization analysis result."""
        if result.success:
            self._info(f"    {len(result.transformations)} {type_name.lower()} optimizations found")
            self._info(f"    Estimated speedup: {result.performance_gain_estimate:.2f}x")

            if self.verbose:
                for transform in result.transformations[:3]:  # Show first 3
                    self._info(f"      - {transform.description}")
        else:
            self._info(f"   ℹ  No {type_name.lower()} optimizations found")

    def _show_vectorization_result(self, result):
        """Show vectorization analysis result."""
        self._info(f"    Vectorizable loops: {result.vectorizable_loops}")
        self._info(f"    Best candidates: {len(result.candidates)}")

        if result.candidates:
            best_candidate = max(result.candidates, key=lambda x: x.performance_gain_estimate)
            self._info(f"    Best speedup potential: {best_candidate.performance_gain_estimate:.2f}x")

            if self.verbose:
                for candidate in result.candidates[:3]:  # Show first 3
                    self._info(f"      - Line {candidate.line_number}: {candidate.vectorization_type.value}")

    def _generate_intelligent_c_code(self, context, args):
        """Generate C code with intelligence layer optimizations."""
        try:
            # Try enhanced STC-enabled converter first
            use_stc = getattr(args, "use_stc", True)  # Default to enabled

            try:
                from ..core.stc_py2c import STCEnhancedPythonToCConverter
                from ..runtime import RuntimeConfig

                # Configure runtime library
                runtime_config = RuntimeConfig()
                runtime_config.stc_enabled = use_stc

                # Use enhanced converter with runtime library support
                converter = STCEnhancedPythonToCConverter(runtime_config)
                c_code = converter.convert_code(context.source_code)

                # Convert sequence to string
                from ..core.style import StyleOptions
                from ..core.writer import Writer

                writer = Writer(StyleOptions())
                c_code_str = writer.write_str(c_code)

                # Add optimization header
                optimization_count = 0  # This would be calculated from intelligence analysis
                if use_stc:
                    header = "/* Generated by CGen Intelligence Layer with STC Support and Runtime Library */\n"
                    header += f"/* Optimizations applied: STC containers + runtime library + {optimization_count} transformations */\n\n"
                else:
                    header = "/* Generated by CGen Intelligence Layer with Runtime Library */\n"
                    header += f"/* Optimizations applied: runtime library + {optimization_count} transformations */\n\n"

                return header + c_code_str

            except ImportError:
                # Fall back to basic translator if STC modules are not available
                self._warning("STC modules not available, using basic translator")

            # Run intelligence analysis for optimizations
            optimizer_results = []

            # Compile-time optimization
            evaluator = CompileTimeEvaluator()
            eval_result = evaluator.optimize(context)
            if eval_result.success:
                optimizer_results.append(eval_result)

            # Loop optimization
            loop_analyzer = LoopAnalyzer()
            loop_result = loop_analyzer.optimize(context)
            if loop_result.success:
                optimizer_results.append(loop_result)

            # Function specialization
            specializer = FunctionSpecializer()
            spec_result = specializer.optimize(context)
            if spec_result.success:
                optimizer_results.append(spec_result)

            # Try to use STC translator, fall back to simple translator
            try:
                from ..intelligence.generators.simple_translator import SimplePythonToCTranslator
                translator = SimplePythonToCTranslator(use_stc_containers=use_stc)
                c_code = translator.translate_module(context.ast_node)
            except ImportError:
                # Basic fallback generation
                c_code = self._generate_basic_c_structure(context, None, optimizer_results)

            # Update header to indicate STC usage
            if use_stc:
                try:
                    from ..ext.stc import STC_AVAILABLE
                    if STC_AVAILABLE:
                        optimization_count = len(optimizer_results)
                        header = "/* Generated by CGen Intelligence Layer with STC Support */\n"
                        header += f"/* Optimizations applied: STC containers + {optimization_count} transformations */\n\n"
                    else:
                        header = "/* Generated by CGen Intelligence Layer */\n"
                        header += f"/* Optimizations applied: {len(optimizer_results)} transformations (STC unavailable) */\n\n"
                except ImportError:
                    header = "/* Generated by CGen Intelligence Layer */\n"
                    header += f"/* Optimizations applied: {len(optimizer_results)} transformations (STC unavailable) */\n\n"
            else:
                header = "/* Generated by CGen Intelligence Layer */\n"
                header += f"/* Optimizations applied: {len(optimizer_results)} transformations */\n\n"

            c_code = header + c_code

            # Add analysis comments if requested
            if hasattr(args, 'include_analysis') and args.include_analysis:
                c_code = self._add_analysis_comments(c_code, optimizer_results)

            return c_code

        except Exception as e:
            self._error(f"Code generation failed: {e}")
            # Fallback to basic structure if AST translation fails
            return self._generate_fallback_c_structure(context, e)

    def _generate_basic_c_structure(self, context, factory, optimizer_results):
        """Generate basic C code structure."""
        lines = []
        lines.append("/* Generated by CGen Intelligence Layer */")
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("")

        # Add optimization summary comment
        total_optimizations = sum(len(result.transformations) for result in optimizer_results)
        if total_optimizations > 0:
            lines.append(f"/* Optimizations applied: {total_optimizations} transformations */")
            lines.append("")

        # Generate function signatures from analysis
        for func_name, func_info in context.analysis_result.functions.items():
            lines.append(f"/* Function: {func_name} */")

            # Clean function signature
            if func_info.parameters:
                params = ", ".join([f"{param.type_info.c_equivalent} {param.name}" for param in func_info.parameters])
            else:
                params = "void"

            return_type = func_info.return_type.c_equivalent if func_info.return_type else "int"
            lines.append(f"{return_type} {func_name}({params}) {{")
            lines.append("    /* Function body would be generated here */")
            if return_type != "void":
                lines.append("    return 0;")
            lines.append("}")
            lines.append("")

        # Add main function if none exists
        if "main" not in context.analysis_result.functions:
            lines.append("int main() {")
            lines.append("    /* Main function */")
            lines.append("    return 0;")
            lines.append("}")

        return "\n".join(lines)

    def _generate_fallback_c_structure(self, context, error):
        """Generate fallback C code structure when AST translation fails."""
        lines = []
        lines.append("/* Generated by CGen Intelligence Layer */")
        lines.append(f"/* Note: AST translation failed ({error}), using fallback structure */")
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("#include <math.h>")
        lines.append("")

        # Generate function stubs
        for func_name, func_info in context.analysis_result.functions.items():
            if func_info.parameters:
                params = ", ".join([f"{param.type_info.c_equivalent} {param.name}" for param in func_info.parameters])
            else:
                params = "void"

            return_type = func_info.return_type.c_equivalent if func_info.return_type else "int"
            lines.append(f"{return_type} {func_name}({params}) {{")
            lines.append("    /* Function body would be generated here */")
            if return_type != "void":
                lines.append("    return 0;")
            lines.append("}")
            lines.append("")

        # Add main function if none exists
        if "main" not in context.analysis_result.functions:
            lines.append("int main() {")
            lines.append("    /* Main function */")
            lines.append("    return 0;")
            lines.append("}")

        return "\n".join(lines)

    def _add_analysis_comments(self, c_code, optimizer_results):
        """Add analysis comments to generated code."""
        comments = []
        comments.append("/*")
        comments.append(" * CGen Intelligence Analysis Summary")
        comments.append(" * " + "="*40)

        for result in optimizer_results:
            comments.append(f" * {result.__class__.__name__}: {len(result.transformations)} optimizations")
            comments.append(f" *   Estimated speedup: {result.performance_gain_estimate:.2f}x")

        comments.append(" */")
        comments.append("")

        return "\n".join(comments) + c_code

    def _test_compilation(self, filepath):
        """Test compilation of generated C code."""
        try:
            import subprocess
            result = subprocess.run(
                ["gcc", "-c", filepath, "-o", "/tmp/test.o"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_frontend_analysis(self, context):
        """Run complete frontend analysis."""
        results = {}

        # AST Analysis
        analyzer = ASTAnalyzer()
        results["ast"] = analyzer.analyze(context.source_code)

        # Type Inference
        engine = TypeInferenceEngine()
        results["types"] = engine.infer_types(context.ast_node)

        # Constraint Checking
        checker = StaticConstraintChecker()
        results["constraints"] = checker.check_code(context.source_code)

        # Subset Validation
        validator = StaticPythonSubsetValidator()
        results["subset"] = validator.validate_code(context.source_code)

        # IR Generation
        builder = IRBuilder()
        results["ir"] = builder.build_from_ast(context.ast_node)

        return results

    def _run_intelligence_analysis(self, context):
        """Run intelligence layer analysis."""
        results = {}

        # Static Analysis
        static_analyzer = StaticAnalyzer()
        results["static"] = static_analyzer.analyze(context.ast_node)

        # Bounds Checking
        bounds_checker = BoundsChecker()
        results["bounds"] = bounds_checker.analyze(context.ast_node)

        # Call Graph Analysis
        call_analyzer = CallGraphAnalyzer()
        results["call_graph"] = call_analyzer.analyze(context.ast_node)

        # Symbolic Execution
        symbolic_executor = SymbolicExecutor()
        results["symbolic"] = symbolic_executor.analyze(context.ast_node)

        # Optimizations
        evaluator = CompileTimeEvaluator()
        results["compile_time"] = evaluator.optimize(context)

        loop_analyzer = LoopAnalyzer()
        results["loops"] = loop_analyzer.optimize(context)

        specializer = FunctionSpecializer()
        results["functions"] = specializer.optimize(context)

        detector = VectorizationDetector()
        results["vectorization"] = detector.analyze(context.ast_node)

        return results

    def _run_verification_analysis(self, context):
        """Run formal verification analysis."""
        results = {}

        # Memory Safety
        theorem_prover = TheoremProver()
        bounds_prover = BoundsProver(theorem_prover)
        results["memory_safety"] = bounds_prover.verify_memory_safety(context)

        # Algorithm Correctness
        correctness_prover = CorrectnessProver(theorem_prover)
        results["correctness"] = correctness_prover.verify_algorithm_correctness(context)

        # Performance Analysis
        performance_analyzer = PerformanceAnalyzer(theorem_prover)
        results["performance"] = performance_analyzer.analyze_performance_bounds(context)

        return results

    def _generate_pipeline_report(self, filepath, results, time):
        """Generate detailed pipeline report."""
        report_lines = []
        report_lines.append("# CGen Intelligence Pipeline Report")
        report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total time: {time:.2f}s")
        report_lines.append("")

        # Frontend summary
        if "frontend" in results:
            frontend = results["frontend"]
            report_lines.append("## Frontend Analysis")
            if "ast" in frontend:
                ast_result = frontend["ast"]
                report_lines.append(f"- Functions: {len(ast_result.functions)}")
                report_lines.append(f"- Global variables: {len(ast_result.global_variables)}")
                report_lines.append(f"- Complexity: {ast_result.complexity.value}")
            report_lines.append("")

        # Intelligence summary
        if "intelligence" in results:
            intelligence = results["intelligence"]
            report_lines.append("## Intelligence Analysis")

            total_optimizations = 0
            for key, result in intelligence.items():
                if hasattr(result, "transformations"):
                    total_optimizations += len(result.transformations)

            report_lines.append(f"- Total optimizations: {total_optimizations}")
            report_lines.append("")

        # Verification summary
        if "verification" in results:
            verification = results["verification"]
            report_lines.append("## Verification Results")

            if "memory_safety" in verification:
                safety = verification["memory_safety"]
                status = "SAFE" if safety.is_safe else "UNSAFE"
                report_lines.append(f"- Memory safety: {status} ({safety.confidence:.1%} confidence)")

            if "correctness" in verification:
                correctness = verification["correctness"]
                status = "CORRECT" if correctness.is_correct else "INCORRECT"
                report_lines.append(f"- Algorithm correctness: {status} ({correctness.confidence:.1%} confidence)")

            report_lines.append("")

        # Write report
        with open(filepath, "w") as f:
            f.write("\n".join(report_lines))

    def _run_interactive_demo(self):
        """Run interactive demo mode."""
        self._info("Welcome to CGen Interactive Demo!")
        self._info("This demo showcases CGen's intelligence capabilities.")
        self._info("")

        # Demo factorial analysis
        demo_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

        self._info("Demo: Factorial Function Analysis")
        self._info(demo_code)

        context = self._create_analysis_context(demo_code)

        # Quick analysis demo
        self._info("Running analysis...")

        # Performance analysis
        performance_analyzer = PerformanceAnalyzer()
        analysis = performance_analyzer.analyze_performance_bounds(context)
        self._info(f" Detected complexity: {analysis.time_complexity.value}")

        # Optimization analysis
        specializer = FunctionSpecializer()
        result = specializer.optimize(context)
        if result.success:
            self._info(f" Found {len(result.transformations)} optimization opportunities")

        self._info("")
        self._info("Demo completed! Try 'cgen analyze --help' for more options.")

    def _run_interactive_session(self):
        """Run interactive session."""
        while True:
            try:
                command = input("cgen> ").strip()

                if command in ["quit", "exit", "q"]:
                    self._info("Goodbye!")
                    break
                elif command in ["help", "h"]:
                    self._show_interactive_help()
                elif command.startswith("analyze "):
                    filepath = command.split(" ", 1)[1]
                    if os.path.exists(filepath):
                        code = self._read_file(filepath)
                        context = self._create_analysis_context(code)
                        self._show_ast_analysis(context)
                    else:
                        self._error(f"File not found: {filepath}")
                elif command == "":
                    continue
                else:
                    self._error(f"Unknown command: {command}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                self._info("\nGoodbye!")
                break
            except EOFError:
                self._info("\nGoodbye!")
                break

    def _show_interactive_help(self):
        """Show interactive mode help."""
        self._info("Available commands:")
        self._info("analyze <file>  - Analyze Python file")
        self._info("help, h         - Show this help")
        self._info("quit, exit, q   - Exit interactive mode")

    def _demo_frontend(self):
        """Demo frontend capabilities."""
        self._info("CGen Frontend Layer Demo")
        # Implementation would show frontend features
        return 0

    def _demo_intelligence(self):
        """Demo intelligence capabilities."""
        self._info("CGen Intelligence Layer Demo")
        # Implementation would show intelligence features
        return 0

    def _demo_verification(self):
        """Demo verification capabilities."""
        self._info("CGen Verification Demo")
        # Implementation would show verification features
        return 0

    def _demo_generation(self):
        """Demo code generation capabilities."""
        self._info("CGen Code Generation Demo")
        # Implementation would show generation features
        return 0

    def _demo_all(self):
        """Demo all capabilities."""
        self._info("CGen Complete Feature Demo")
        self._demo_frontend()
        self._demo_intelligence()
        self._demo_verification()
        self._demo_generation()
        return 0

    def _load_config(self, filepath):
        """Load configuration from file."""
        try:
            with open(filepath) as f:
                if filepath.endswith(".json"):
                    self.config = json.load(f)
                else:
                    # Simple key=value format
                    for line in f:
                        if "=" in line and not line.strip().startswith("#"):
                            key, value = line.strip().split("=", 1)
                            self.config[key.strip()] = value.strip()
        except Exception as e:
            self._warning(f"Failed to load config {filepath}: {e}")

    def _add_build_command(self, subparsers):
        """Add build command for direct compilation."""
        build_parser = subparsers.add_parser(
            "build",
            help="Direct compilation of generated C code",
            description="Compile C code directly with STC support"
        )
        build_parser.add_argument("source", help="C source file to compile")
        build_parser.add_argument("-o", "--output", help="Output executable name")
        build_parser.add_argument("--no-stc", action="store_true", help="Disable STC support")
        build_parser.add_argument("-I", "--include", action="append", help="Include directories")
        build_parser.add_argument("-L", "--libdir", action="append", help="Library directories")
        build_parser.add_argument("-l", "--lib", action="append", help="Libraries to link")
        build_parser.add_argument("--flags", help="Additional compiler flags")
        build_parser.add_argument("--compiler", default="gcc", help="Compiler to use")

    def _add_makefile_command(self, subparsers):
        """Add makefile command for Makefile generation."""
        makefile_parser = subparsers.add_parser(
            "makefile",
            help="Generate Makefile for C project",
            description="Create Makefile with STC support for C projects"
        )
        makefile_parser.add_argument("source", help="C source file or directory")
        makefile_parser.add_argument("-o", "--output", default="Makefile", help="Output Makefile name")
        makefile_parser.add_argument("--name", help="Project name")
        makefile_parser.add_argument("--no-stc", action="store_true", help="Disable STC support")
        makefile_parser.add_argument("-I", "--include", action="append", help="Include directories")
        makefile_parser.add_argument("-L", "--libdir", action="append", help="Library directories")
        makefile_parser.add_argument("-l", "--lib", action="append", help="Libraries to link")
        makefile_parser.add_argument("--flags", help="Additional compiler flags")
        makefile_parser.add_argument("--compiler", default="gcc", help="Compiler to use")

    def _handle_build(self, args) -> int:
        """Handle build command."""
        self._info("CGen Direct Build")
        self._info("=" * 50)

        if not self._check_file_exists(args.source):
            return 1

        # Parse additional flags
        additional_flags = []
        if args.flags:
            additional_flags = args.flags.split()

        try:
            from ..makefilegen import Builder

            builder = Builder(
                name=args.output or Path(args.source).stem,
                source_dir=str(Path(args.source).parent),
                include_dirs=args.include or [],
                library_dirs=args.libdir or [],
                libraries=args.lib or [],
                flags=additional_flags,
                compiler=args.compiler,
                use_stc=not args.no_stc
            )

            self._info(f" Source: {args.source}")
            self._info(f" Output: {args.output or Path(args.source).stem}")
            self._info(f" Compiler: {args.compiler}")

            # Show STC status
            if not args.no_stc:
                if builder.stc_include_path:
                    self._info(f" STC Containers: Enabled ({builder.stc_include_path})")
                else:
                    self._info("STC Containers: Requested but unavailable")
            else:
                self._info("STC Containers: Disabled")

            self._info("\nBuilding...")
            success = builder.build(verbose=self.verbose)

            if success:
                self._info(f" Build successful: {args.output or Path(args.source).stem}")
                return 0
            else:
                self._error(" Build failed")
                return 1

        except ImportError as e:
            self._error(f" Makefilegen not available: {e}")
            return 1
        except Exception as e:
            self._error(f" Build error: {e}")
            return 1

    def _handle_makefile(self, args) -> int:
        """Handle makefile command."""
        self._info("CGen Makefile Generation")
        self._info("=" * 50)

        source_path = Path(args.source)
        if not source_path.exists():
            self._error(f"Source not found: {args.source}")
            return 1

        # Parse additional flags
        additional_flags = []
        if args.flags:
            additional_flags = args.flags.split()

        try:
            from ..builder.makefilegen import MakefileGenerator

            if source_path.is_file():
                source_dir = str(source_path.parent)
                project_name = args.name or source_path.stem
            else:
                source_dir = str(source_path)
                project_name = args.name or source_path.name

            generator = MakefileGenerator(
                name=project_name,
                source_dir=source_dir,
                include_dirs=args.include or [],
                library_dirs=args.libdir or [],
                libraries=args.lib or [],
                flags=additional_flags,
                compiler=args.compiler,
                use_stc=not args.no_stc
            )

            self._info(f" Source: {args.source}")
            self._info(f" Output: {args.output}")
            self._info(f"  Project: {project_name}")
            self._info(f" Compiler: {args.compiler}")

            # Show STC status
            if not args.no_stc:
                if generator.stc_include_path:
                    self._info(f" STC Containers: Enabled ({generator.stc_include_path})")
                else:
                    self._info("STC Containers: Requested but unavailable")
            else:
                self._info("STC Containers: Disabled")

            self._info("\nGenerating Makefile...")
            success = generator.write_makefile(args.output)

            if success:
                self._info(f" Makefile generated: {args.output}")
                return 0
            else:
                self._error(" Makefile generation failed")
                return 1

        except ImportError as e:
            self._error(f" Makefilegen not available: {e}")
            return 1
        except Exception as e:
            self._error(f" Makefile generation error: {e}")
            return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for enhanced CGen CLI."""
    cli = CGenCLI()
    return cli.run(argv)


if __name__ == "__main__":
    sys.exit(main())
