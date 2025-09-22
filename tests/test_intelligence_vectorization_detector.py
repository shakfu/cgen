"""Tests for the VectorizationDetector optimizer."""

import ast
from unittest.mock import Mock, patch

import pytest

from src.cgen.intelligence.optimizers.vectorization_detector import (
    MemoryAccess,
    VectorizationCandidate,
    VectorizationConstraint,
    VectorizationDetector,
    VectorizationReport,
    VectorizationType,
)


class TestVectorizationDetector:
    """Test cases for VectorizationDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = VectorizationDetector(target_arch="x86_64", vector_width=4)

    def test_initialization(self):
        """Test VectorizationDetector initialization."""
        assert self.detector.target_arch == "x86_64"
        assert self.detector.default_vector_width == 4
        assert "simd_extensions" in self.detector.arch_capabilities

    def test_arch_capabilities_x86_64(self):
        """Test x86_64 architecture capabilities."""
        capabilities = self.detector.arch_capabilities
        assert "SSE" in capabilities["simd_extensions"]
        assert "AVX" in capabilities["simd_extensions"]
        assert capabilities["vector_widths"]["float"] == [4, 8, 16]

    def test_arch_capabilities_arm(self):
        """Test ARM architecture capabilities."""
        arm_detector = VectorizationDetector(target_arch="arm")
        capabilities = arm_detector.arch_capabilities
        assert "NEON" in capabilities["simd_extensions"]
        assert capabilities["vector_widths"]["float"] == [4, 8]

    def test_simple_loop_analysis(self):
        """Test analysis of a simple vectorizable loop."""
        code = """
for i in range(n):
    c[i] = a[i] + b[i]
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        assert report.total_loops_analyzed == 1
        assert report.vectorizable_loops == 1
        assert len(report.candidates) == 1

        candidate = report.candidates[0]
        assert candidate.vectorization_type == VectorizationType.ELEMENT_WISE
        assert len(candidate.memory_accesses) == 3
        assert candidate.estimated_speedup > 1.0

    def test_reduction_loop_analysis(self):
        """Test analysis of a reduction loop."""
        code = """
for i in range(n):
    sum += a[i]
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        assert report.vectorizable_loops == 1
        candidate = report.candidates[0]
        assert candidate.vectorization_type == VectorizationType.REDUCTION_LOOP
        assert VectorizationConstraint.DATA_DEPENDENCIES in candidate.constraints

    def test_array_copy_analysis(self):
        """Test analysis of an array copy pattern."""
        code = """
for i in range(n):
    b[i] = a[i]
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        assert report.vectorizable_loops == 1
        candidate = report.candidates[0]
        assert candidate.vectorization_type == VectorizationType.ARRAY_COPY

    def test_dot_product_analysis(self):
        """Test analysis of a dot product pattern."""
        code = """
for i in range(n):
    result += a[i] * b[i]
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        assert report.vectorizable_loops == 1
        candidate = report.candidates[0]
        assert candidate.vectorization_type == VectorizationType.DOT_PRODUCT

    def test_non_vectorizable_while_loop(self):
        """Test that while loops are not considered vectorizable."""
        code = """
while condition:
    a[i] = b[i]
    i += 1
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        assert report.total_loops_analyzed == 1
        assert report.vectorizable_loops == 0

    def test_loop_with_early_exit(self):
        """Test that loops with early exits are not vectorizable."""
        code = """
for i in range(n):
    if condition:
        break
    a[i] = b[i]
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        assert report.vectorizable_loops == 0

    def test_memory_access_analysis(self):
        """Test memory access pattern analysis."""
        code = """
for i in range(n):
    a[i] = b[i + 1]
"""
        tree = ast.parse(code)
        loop_node = tree.body[0]

        accesses = self.detector._analyze_memory_accesses(loop_node)
        assert len(accesses) == 2

        write_access = next(a for a in accesses if a.is_write)
        read_access = next(a for a in accesses if a.is_read)

        assert write_access.variable == "a"
        assert read_access.variable == "b"
        assert write_access.access_pattern == "linear"
        assert read_access.access_pattern == "linear"

    def test_strided_access_pattern(self):
        """Test detection of strided access patterns."""
        code = """
for i in range(n):
    a[i * 2] = b[i]
"""
        tree = ast.parse(code)
        loop_node = tree.body[0]

        accesses = self.detector._analyze_memory_accesses(loop_node)
        strided_access = next(a for a in accesses if a.stride == 2)
        assert strided_access.access_pattern == "strided"

    def test_irregular_access_pattern(self):
        """Test detection of irregular access patterns."""
        code = """
for i in range(n):
    a[func(i)] = b[i]
"""
        tree = ast.parse(code)
        loop_node = tree.body[0]

        accesses = self.detector._analyze_memory_accesses(loop_node)
        # Irregular accesses should be filtered out
        assert all(a.access_pattern != "irregular" for a in accesses)

    def test_constraint_detection_control_flow(self):
        """Test detection of control flow constraints."""
        code = """
for i in range(n):
    if condition:
        a[i] = b[i]
"""
        tree = ast.parse(code)
        loop_node = tree.body[0]

        constraints = self.detector._identify_constraints(loop_node, [])
        assert VectorizationConstraint.CONTROL_FLOW in constraints

    def test_constraint_detection_function_calls(self):
        """Test detection of function call constraints."""
        code = """
for i in range(n):
    a[i] = func(b[i])
"""
        tree = ast.parse(code)
        loop_node = tree.body[0]

        constraints = self.detector._identify_constraints(loop_node, [])
        assert VectorizationConstraint.FUNCTION_CALLS in constraints

    def test_vector_length_determination(self):
        """Test vector length determination."""
        accesses = [
            MemoryAccess("a", [], True, False, "linear", 1),
            MemoryAccess("b", [], False, True, "linear", 1)
        ]

        length = self.detector._determine_vector_length(accesses, VectorizationType.ELEMENT_WISE)
        assert length == 4  # Default vector width

    def test_vector_length_with_stride(self):
        """Test vector length determination with strided access."""
        accesses = [
            MemoryAccess("a", [], True, False, "strided", 4)
        ]

        length = self.detector._determine_vector_length(accesses, VectorizationType.SIMPLE_LOOP)
        assert length == 2  # 8 // 4

    def test_speedup_estimation(self):
        """Test speedup estimation."""
        constraints = set()
        speedup = self.detector._estimate_speedup(
            VectorizationType.ELEMENT_WISE, 4, constraints
        )
        assert speedup > 1.0
        assert speedup < 4.0  # Less than ideal due to overhead

    def test_speedup_with_constraints(self):
        """Test speedup estimation with constraints."""
        constraints = {VectorizationConstraint.CONTROL_FLOW}
        speedup = self.detector._estimate_speedup(
            VectorizationType.SIMPLE_LOOP, 4, constraints
        )

        constraints_empty = set()
        speedup_no_constraints = self.detector._estimate_speedup(
            VectorizationType.SIMPLE_LOOP, 4, constraints_empty
        )

        assert speedup < speedup_no_constraints

    def test_confidence_calculation(self):
        """Test confidence calculation."""
        accesses = [MemoryAccess("a", [], True, False, "linear", 1)]
        constraints = set()

        confidence = self.detector._calculate_confidence(constraints, accesses)
        assert confidence > 0.8

    def test_confidence_with_constraints(self):
        """Test confidence calculation with constraints."""
        accesses = []
        constraints = {VectorizationConstraint.DATA_DEPENDENCIES}

        confidence = self.detector._calculate_confidence(constraints, accesses)
        assert confidence < 0.5

    def test_transformation_complexity_assessment(self):
        """Test transformation complexity assessment."""
        constraints_trivial = set()
        complexity = self.detector._assess_transformation_complexity(
            VectorizationType.SIMPLE_LOOP, constraints_trivial
        )
        assert complexity == "trivial"

        constraints_complex = {VectorizationConstraint.DATA_DEPENDENCIES}
        complexity = self.detector._assess_transformation_complexity(
            VectorizationType.REDUCTION_LOOP, constraints_complex
        )
        assert complexity == "complex"

    def test_intrinsics_suggestions_x86_64(self):
        """Test SIMD intrinsics suggestions for x86_64."""
        intrinsics = self.detector._suggest_intrinsics(VectorizationType.SIMPLE_LOOP, 4)
        assert "_mm_load_ps" in intrinsics
        assert "_mm_add_ps" in intrinsics

        intrinsics_avx = self.detector._suggest_intrinsics(VectorizationType.SIMPLE_LOOP, 8)
        assert "_mm256_load_ps" in intrinsics_avx

    def test_intrinsics_suggestions_dot_product(self):
        """Test intrinsics suggestions for dot product."""
        intrinsics = self.detector._suggest_intrinsics(VectorizationType.DOT_PRODUCT, 4)
        assert "_mm_dp_ps" in intrinsics

    def test_vector_width_recommendations(self):
        """Test vector width recommendations."""
        candidates = [
            Mock(vector_length=4),
            Mock(vector_length=8),
            Mock(vector_length=4)
        ]

        recommendations = self.detector._recommend_vector_widths(candidates)
        expected_avg = (4 + 8 + 4) // 3
        assert recommendations["float"] == expected_avg
        assert recommendations["double"] == max(2, expected_avg // 2)

    def test_architecture_recommendations(self):
        """Test architecture-specific recommendations."""
        candidates = [Mock(vector_length=8, transformation_complexity="simple")]

        recommendations = self.detector._generate_arch_recommendations(candidates)
        assert any("AVX" in rec for rec in recommendations)

    def test_complexity_distribution_analysis(self):
        """Test complexity distribution analysis."""
        candidates = [
            Mock(transformation_complexity="trivial"),
            Mock(transformation_complexity="moderate"),
            Mock(transformation_complexity="trivial")
        ]

        distribution = self.detector._analyze_complexity_distribution(candidates)
        assert distribution["trivial"] == 2
        assert distribution["moderate"] == 1
        assert distribution["complex"] == 0

    def test_constraint_frequency_analysis(self):
        """Test constraint frequency analysis."""
        candidates = [
            Mock(constraints={VectorizationConstraint.CONTROL_FLOW}),
            Mock(constraints={VectorizationConstraint.CONTROL_FLOW, VectorizationConstraint.ALIASING}),
            Mock(constraints={VectorizationConstraint.ALIASING})
        ]

        frequency = self.detector._analyze_constraint_frequency(candidates)
        assert frequency["control_flow"] == 2
        assert frequency["aliasing"] == 2

    def test_vectorization_candidate_validation(self):
        """Test VectorizationCandidate validation."""
        loop_node = Mock()
        accesses = []
        constraints = set()

        # Valid candidate
        candidate = VectorizationCandidate(
            loop_node=loop_node,
            vectorization_type=VectorizationType.SIMPLE_LOOP,
            vector_length=4,
            memory_accesses=accesses,
            constraints=constraints,
            estimated_speedup=2.0,
            confidence=0.8,
            transformation_complexity="trivial"
        )
        assert candidate.vector_length == 4

        # Invalid vector length
        with pytest.raises(ValueError):
            VectorizationCandidate(
                loop_node=loop_node,
                vectorization_type=VectorizationType.SIMPLE_LOOP,
                vector_length=0,
                memory_accesses=accesses,
                constraints=constraints,
                estimated_speedup=2.0,
                confidence=0.8,
                transformation_complexity="trivial"
            )

        # Invalid confidence
        with pytest.raises(ValueError):
            VectorizationCandidate(
                loop_node=loop_node,
                vectorization_type=VectorizationType.SIMPLE_LOOP,
                vector_length=4,
                memory_accesses=accesses,
                constraints=constraints,
                estimated_speedup=2.0,
                confidence=1.5,
                transformation_complexity="trivial"
            )

    def test_empty_code_analysis(self):
        """Test analysis of empty code."""
        tree = ast.parse("")
        report = self.detector.analyze(tree)

        assert report.total_loops_analyzed == 0
        assert report.vectorizable_loops == 0
        assert len(report.candidates) == 0

    def test_complex_nested_structure(self):
        """Test analysis of complex nested structures."""
        code = """
for i in range(n):
    for j in range(m):
        if condition:
            a[i][j] = b[i][j] + c[i][j]
"""
        tree = ast.parse(code)
        report = self.detector.analyze(tree)

        # Should detect both loops but may not vectorize due to complexity
        assert report.total_loops_analyzed == 2

    def test_loop_variable_extraction(self):
        """Test loop variable extraction."""
        code = "for i in range(n): pass"
        tree = ast.parse(code)
        loop_node = tree.body[0]

        var = self.detector._get_loop_variable(loop_node)
        assert var == "i"

    def test_is_vectorizable_loop_checks(self):
        """Test various vectorizable loop checks."""
        # Simple for loop
        code = "for i in range(n): a[i] = b[i]"
        tree = ast.parse(code)
        loop_node = tree.body[0]
        assert self.detector._is_vectorizable_loop(loop_node)

        # While loop (not vectorizable)
        code = "while condition: a[i] = b[i]"
        tree = ast.parse(code)
        loop_node = tree.body[0]
        assert not self.detector._is_vectorizable_loop(loop_node)


if __name__ == "__main__":
    unittest.main()