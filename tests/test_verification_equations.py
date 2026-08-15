"""
Unit Tests for Symbolic Mathematical Verification Engine (Prompt 6, TEST-EQ-01..10)
"""

import pytest
from research_agent.core.enums import (
    EquationType,
    IntellectualOwnership,
    SymbolicEqualityState,
    TransformationOp,
)
from research_agent.schemas.equation import Equation, EquationDerivation, SymbolDefinition
from research_agent.schemas.verification import ScopedSymbol, TransformationStep
from research_agent.verification.equations.symbolic_engine import SymbolicVerificationEngine
from research_agent.verification.equations.symbol_registry import SymbolRegistry
from research_agent.verification.equations.provenance import EquationProvenanceAuditor


class TestSymbolicEquationVerification:
    def setup_method(self):
        self.engine = SymbolicVerificationEngine()
        self.registry = SymbolRegistry()
        self.auditor = EquationProvenanceAuditor()

    def test_eq_01_algebraic_equivalence_proven(self):
        """TEST-EQ-01: Correctly identifies identical algebraic expressions."""
        state, details = self.engine.verify_algebraic_equivalence("(x + y)**2", "x**2 + 2*x*y + y**2")
        assert state == SymbolicEqualityState.PROVEN_EQUIVALENT
        assert details["method"] == "SYMPY_SIMPLIFY"

    def test_eq_02_algebraic_inequivalence(self):
        """TEST-EQ-02: Correctly rejects inequivalent mathematical expressions."""
        state, details = self.engine.verify_algebraic_equivalence("x**2 + 1", "x**2 + 2")
        assert state == SymbolicEqualityState.NOT_EQUIVALENT

    def test_eq_03_derivative_verification(self):
        """TEST-EQ-03: Verifies symbolic derivatives."""
        state, details = self.engine.verify_derivative("x**3 + 2*x", "x", "3*x**2 + 2")
        assert state == SymbolicEqualityState.PROVEN_EQUIVALENT

    def test_eq_04_derivative_incorrect_rejected(self):
        """TEST-EQ-04: Rejects false derivative derivations."""
        state, details = self.engine.verify_derivative("x**3", "x", "2*x**2")
        assert state == SymbolicEqualityState.NOT_EQUIVALENT

    def test_eq_05_domain_validity_division_by_zero(self):
        """TEST-EQ-05: Flags potential division by zero."""
        issues = self.engine.audit_domain_validity("1 / (x - 1)")
        assert len(issues) > 0
        assert any(i["issue_type"] == "POTENTIAL_DIVISION_BY_ZERO" for i in issues)

    def test_eq_06_tensor_shape_compatibility(self):
        """TEST-EQ-06: Verifies ML representation tensor shape alignment."""
        valid, msg = self.engine.audit_tensor_shape_compatibility("ALIGNMENT_COSINE", [(32, 128), (32, 128)])
        assert valid is True

        invalid, err = self.engine.audit_tensor_shape_compatibility("ALIGNMENT_COSINE", [(32, 128), (32, 64)])
        assert invalid is False
        assert "Dimensionality mismatch" in err

    def test_eq_07_loss_function_composition_audit(self):
        """TEST-EQ-07: Audits multi-term loss function scalar and positive weight constraints."""
        valid_terms = [
            {"name": "L_seq", "lambda_weight": 1.0, "is_scalar": True, "provenance_source_id": "SRC-000001"},
            {"name": "L_graph", "lambda_weight": 0.5, "is_scalar": True, "provenance_source_id": "SRC-000002"},
        ]
        ok, issues = self.engine.audit_loss_function_composition(valid_terms)
        assert ok is True
        assert len(issues) == 0

        invalid_terms = [
            {"name": "L_neg", "lambda_weight": -0.5, "is_scalar": True, "provenance_source_id": "SRC-000001"},
            {"name": "L_nonscalar", "lambda_weight": 1.0, "is_scalar": False, "provenance_source_id": None},
        ]
        not_ok, issues = self.engine.audit_loss_function_composition(invalid_terms)
        assert not_ok is False
        assert len(issues) >= 2

    def test_eq_08_symbol_registry_ambiguity_detection(self):
        """TEST-EQ-08: Detects symbol naming ambiguity across equations."""
        s1 = ScopedSymbol(symbol_id="SYM-01", symbol_latex="\\lambda", equation_id="EQ-01", name="Learning Rate")
        s2 = ScopedSymbol(symbol_id="SYM-02", symbol_latex="\\lambda", equation_id="EQ-02", name="Loss Weight")
        self.registry.register_symbol(s1)
        self.registry.register_symbol(s2)

        ambiguities = self.registry.detect_symbol_ambiguity("\\lambda")
        assert len(ambiguities) == 1
        assert "EQ-01" in ambiguities[0][2] and "EQ-02" in ambiguities[0][2]

    def test_eq_09_equation_provenance_source_missing_locator(self):
        """TEST-EQ-09: Flags SOURCE_EQUATION lacking locator (RC-08)."""
        eq = Equation(
            equation_id="EQ-TEST-01",
            latex="E = mc^2",
            name="Mass-Energy Equivalence",
            equation_type=EquationType.SOURCE_EQUATION,
            ownership=IntellectualOwnership.SOURCE,
            source_id="SRC-000001",
            source_locator="",  # Missing locator
        )
        valid, issues = self.auditor.audit_equation(eq)
        assert valid is False
        assert any("source_locator" in i for i in issues)

    def test_eq_10_equation_provenance_derived_missing_steps(self):
        """TEST-EQ-10: Flags DERIVED_EQUATION lacking derivation steps."""
        eq = Equation(
            equation_id="EQ-TEST-02",
            latex="y = 2x",
            name="Derived Scaling",
            equation_type=EquationType.DERIVED_EQUATION,
            ownership=IntellectualOwnership.OURS,
            derivation=EquationDerivation(parent_equation_ids=["EQ-TEST-01"], derivation_steps=[]),
        )
        valid, issues = self.auditor.audit_equation(eq)
        assert valid is False
        assert any("derivation_steps" in i for i in issues)
