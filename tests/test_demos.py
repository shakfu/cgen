"""
Pytest-style tests to verify all demo scripts work correctly.

This module discovers and tests all demo scripts in the tests/demos folder,
ensuring they run successfully without errors.
"""

import subprocess
import os
import glob
import pytest
from pathlib import Path


class TestDemos:
    """Test class for CGen Intelligence Layer demo scripts."""

    @classmethod
    def setup_class(cls):
        """Set up test class - discover demo scripts."""
        # Get the project root directory (parent of tests)
        cls.project_root = Path(__file__).parent.parent
        cls.demos_dir = cls.project_root / "tests" / "demos"

        # Discover all Python demo scripts
        cls.demo_scripts = []
        if cls.demos_dir.exists():
            for demo_file in cls.demos_dir.glob("*.py"):
                if demo_file.name != "__init__.py":
                    cls.demo_scripts.append(demo_file)

        print(f"\n🔍 Discovered {len(cls.demo_scripts)} demo scripts in {cls.demos_dir}")

    def _run_demo_script(self, script_path: Path) -> tuple[bool, str, str]:
        """Run a demo script and return success status with output.

        Args:
            script_path: Path to the demo script

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Change to project root directory for proper imports
            # Add project root to Python path so demo scripts can import src modules
            env = os.environ.copy()
            current_path = env.get('PYTHONPATH', '')
            if current_path:
                env['PYTHONPATH'] = f"{self.project_root}:{current_path}"
            else:
                env['PYTHONPATH'] = str(self.project_root)

            result = subprocess.run(
                ["python", str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                env=env,
                timeout=120  # 2 minute timeout for comprehensive demos
            )

            success = result.returncode == 0
            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", "Demo script timed out after 120 seconds"
        except Exception as e:
            return False, "", f"Exception running demo: {str(e)}"

    def _validate_demo_output(self, stdout: str, script_name: str) -> list[str]:
        """Validate demo output for expected content.

        Args:
            stdout: Standard output from demo
            script_name: Name of the demo script

        Returns:
            List of validation messages
        """
        messages = []
        output_lower = stdout.lower()

        # Check for successful completion indicators
        success_indicators = [
            "demo complete", "showcase complete", "demonstration complete",
            "✅", "success", "passed"
        ]

        has_success_indicator = any(indicator in output_lower for indicator in success_indicators)
        if has_success_indicator:
            messages.append("✅ Found success indicators")
        else:
            messages.append("⚠️  No clear success indicators found")

        # Check for expected demo content based on script name
        if "intelligence_layer" in script_name:
            expected_sections = [
                "static analyzer", "symbolic executor", "bounds checker",
                "call graph", "compile-time", "loop analyzer",
                "function specializer", "vectorization"
            ]
            found_sections = sum(1 for section in expected_sections if section in output_lower)
            messages.append(f"📊 Found {found_sections}/{len(expected_sections)} expected sections")

        elif "optimization" in script_name:
            optimization_terms = ["speedup", "optimization", "performance", "simd", "vectoriz"]
            found_terms = sum(1 for term in optimization_terms if term in output_lower)
            messages.append(f"🚀 Found {found_terms} optimization-related terms")

        elif "performance" in script_name:
            perf_terms = ["benchmark", "speedup", "performance", "gain", "improvement"]
            found_terms = sum(1 for term in perf_terms if term in output_lower)
            messages.append(f"📈 Found {found_terms} performance-related terms")

        # Check for error indicators (warnings, not failures)
        error_indicators = ["error:", "exception:", "traceback:", "failed:"]
        has_errors = any(indicator in output_lower for indicator in error_indicators)
        if has_errors:
            messages.append("⚠️  Found error indicators in output")

        return messages

    def test_all_demos_run_successfully(self):
        """Test that all discovered demo scripts run successfully without errors."""
        if not self.demo_scripts:
            pytest.skip("No demo scripts found to test")

        failures = []

        for demo_script in self.demo_scripts:
            print(f"\n🧪 Testing {demo_script.name}...")
            success, stdout, stderr = self._run_demo_script(demo_script)

            if not success:
                failures.append(f"{demo_script.name}: {stderr[:200]}")
                print(f"❌ {demo_script.name} failed")
            else:
                print(f"✅ {demo_script.name} passed")

                # Validate output content
                messages = self._validate_demo_output(stdout, demo_script.name)
                for message in messages:
                    print(f"   {message}")

        if failures:
            failure_msg = "\n".join(failures)
            pytest.fail(f"Demo scripts failed:\n{failure_msg}")

        print(f"\n🎉 All {len(self.demo_scripts)} demo scripts passed!")

    def test_simple_demo(self):
        """Test the simple demo script."""
        demo_path = self.demos_dir / "simple_demo.py"
        if not demo_path.exists():
            pytest.skip(f"Demo script not found: {demo_path}")

        success, stdout, stderr = self._run_demo_script(demo_path)

        # Validate the demo ran successfully
        assert success, f"Simple demo failed. STDERR: {stderr[:500]}"

        # Validate output content
        messages = self._validate_demo_output(stdout, "simple_demo")
        print("\n".join(messages))

        # Check for specific simple demo content
        assert "intelligence layer" in stdout.lower(), "Demo should mention intelligence layer"
        assert len(stdout) > 1000, "Demo output should be substantial"

    def test_comprehensive_demo(self):
        """Test the comprehensive intelligence layer demo."""
        demo_path = self.demos_dir / "demo_intelligence_layer.py"
        if not demo_path.exists():
            pytest.skip(f"Demo script not found: {demo_path}")

        success, stdout, stderr = self._run_demo_script(demo_path)

        # Validate the demo ran successfully
        assert success, f"Comprehensive demo failed. STDERR: {stderr[:500]}"

        # Validate output content
        messages = self._validate_demo_output(stdout, "intelligence_layer")
        print("\n".join(messages))

        # Check for all 8 intelligence layer components
        components = [
            "static analyzer", "symbolic executor", "bounds checker", "call graph",
            "compile-time", "loop analyzer", "function specializer", "vectorization"
        ]

        found_components = []
        for component in components:
            if component in stdout.lower():
                found_components.append(component)

        assert len(found_components) >= 6, f"Should find most components. Found: {found_components}"

    def test_optimization_showcase(self):
        """Test the optimization showcase demo."""
        demo_path = self.demos_dir / "optimization_showcase.py"
        if not demo_path.exists():
            pytest.skip(f"Demo script not found: {demo_path}")

        success, stdout, stderr = self._run_demo_script(demo_path)

        # Validate the demo ran successfully
        assert success, f"Optimization showcase failed. STDERR: {stderr[:500]}"

        # Validate output content
        messages = self._validate_demo_output(stdout, "optimization")
        print("\n".join(messages))

        # Check for optimization-specific content
        assert "optimization" in stdout.lower(), "Should discuss optimizations"
        assert "performance" in stdout.lower(), "Should mention performance"

    def test_performance_benefits(self):
        """Test the performance benefits demo."""
        demo_path = self.demos_dir / "performance_benefits.py"
        if not demo_path.exists():
            pytest.skip(f"Demo script not found: {demo_path}")

        success, stdout, stderr = self._run_demo_script(demo_path)

        # Validate the demo ran successfully
        assert success, f"Performance benefits demo failed. STDERR: {stderr[:500]}"

        # Validate output content
        messages = self._validate_demo_output(stdout, "performance")
        print("\n".join(messages))

        # Check for performance-specific content
        assert "performance" in stdout.lower(), "Should discuss performance"
        assert "speedup" in stdout.lower() or "gain" in stdout.lower(), "Should mention speedup/gains"

    def test_all_demos_discovery(self):
        """Test that we can discover demo scripts in the demos directory."""
        assert len(self.demo_scripts) > 0, f"Should discover demo scripts in {self.demos_dir}"

        # Verify each discovered script exists and is a Python file
        for script in self.demo_scripts:
            assert script.exists(), f"Demo script should exist: {script}"
            assert script.suffix == ".py", f"Demo script should be Python file: {script}"
            assert script.stat().st_size > 0, f"Demo script should not be empty: {script}"

    def test_demos_import_correctly(self):
        """Test that demo scripts can be imported without syntax errors."""
        import ast

        for script in self.demo_scripts:
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    source = f.read()

                # Parse the AST to check for syntax errors
                ast.parse(source, filename=str(script))
                print(f"✅ {script.name} - Valid Python syntax")

            except SyntaxError as e:
                pytest.fail(f"Syntax error in {script.name}: {e}")
            except Exception as e:
                pytest.fail(f"Error parsing {script.name}: {e}")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "demos: mark test as a demo script test"
    )


# For backwards compatibility - allow running as script
def main():
    """Run tests when executed as a script."""
    import sys

    # Run pytest with this file
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()