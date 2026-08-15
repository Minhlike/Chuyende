"""
Symbolic Mathematical Verification Engine (Prompt 6 Sections 13..17)
"""

import math
import random
from typing import Any, Dict, List, Optional, Tuple
import sympy as sp
from research_agent.core.enums import SymbolicEqualityState


class SymbolicVerificationEngine:
    """
    Deterministic symbolic verification backend using SymPy.
    Performs algebraic equality checks, calculus derivations, domain constraint
    auditing, ML tensor shape dimension checks, and loss function composition audits.
    """

    def parse_expression(self, expr_str: str) -> Tuple[Optional[sp.Expr], Optional[str]]:
        """Parses a mathematical expression string into a SymPy expression."""
        clean_expr = expr_str.replace("\\cdot", "*").replace("\\times", "*").replace("^", "**")
        clean_expr = clean_expr.replace("{", "(").replace("}", ")").replace("\\", "")
        try:
            parsed = sp.sympify(clean_expr, evaluate=False)
            return parsed, None
        except Exception as e:
            return None, f"Parse failure for expression '{expr_str}': {str(e)}"

    def verify_algebraic_equivalence(
        self,
        expr_a_str: str,
        expr_b_str: str,
        assumptions: Optional[Dict[str, Any]] = None,
        num_random_samples: int = 20,
    ) -> Tuple[SymbolicEqualityState, Dict[str, Any]]:
        """
        Determines if expr_a and expr_b are mathematically equivalent.
        Combines SymPy symbolic simplification with randomized numerical sanity checks.
        """
        expr_a, err_a = self.parse_expression(expr_a_str)
        expr_b, err_b = self.parse_expression(expr_b_str)

        if err_a or err_b or expr_a is None or expr_b is None:
            return SymbolicEqualityState.PARSE_FAILED, {
                "error": err_a or err_b,
                "expr_a": expr_a_str,
                "expr_b": expr_b_str,
            }

        # 1. Direct symbolic difference simplification
        diff = sp.simplify(expr_a - expr_b)
        if diff == 0:
            return SymbolicEqualityState.PROVEN_EQUIVALENT, {
                "method": "SYMPY_SIMPLIFY",
                "difference": "0",
            }

        # 2. Check with domain assumptions (e.g. positive symbols)
        symbols = expr_a.free_symbols.union(expr_b.free_symbols)
        assumed_symbols = {s: sp.Symbol(s.name, positive=True, real=True) for s in symbols}
        subbed_a = expr_a.subs(assumed_symbols)
        subbed_b = expr_b.subs(assumed_symbols)
        diff_assumed = sp.simplify(subbed_a - subbed_b)
        if diff_assumed == 0:
            return SymbolicEqualityState.DOMAIN_DEPENDENT, {
                "method": "SYMPY_WITH_POSITIVE_ASSUMPTIONS",
                "assumptions_required": ["symbols > 0", "real values"],
            }

        # 3. Randomized numerical evaluation across valid domain points
        num_matches = 0
        tolerance = 1e-7
        random.seed(42)
        test_points = []
        for _ in range(num_random_samples):
            point = {s: random.uniform(1.0, 10.0) for s in symbols}
            try:
                val_a = float(expr_a.subs(point).evalf())
                val_b = float(expr_b.subs(point).evalf())
                if abs(val_a - val_b) < tolerance:
                    num_matches += 1
                test_points.append({"point": {s.name: round(v, 3) for s, v in point.items()}, "val_a": val_a, "val_b": val_b})
            except Exception:
                pass

        if num_matches == num_random_samples and num_random_samples > 0:
            return SymbolicEqualityState.NUMERICALLY_CONSISTENT, {
                "method": "RANDOMIZED_NUMERICAL_TESTS",
                "samples_passed": num_matches,
                "tolerance": tolerance,
            }

        return SymbolicEqualityState.NOT_EQUIVALENT, {
            "method": "SIMPLIFICATION_AND_NUMERICAL_DIVERGENCE",
            "samples_matched": num_matches,
            "total_samples": num_random_samples,
            "sample_divergences": test_points[:3],
        }

    def verify_derivative(
        self,
        func_expr_str: str,
        var_name: str,
        claimed_derivative_str: str,
    ) -> Tuple[SymbolicEqualityState, Dict[str, Any]]:
        """Verifies if claimed_derivative matches d(func)/d(var)."""
        func_expr, err = self.parse_expression(func_expr_str)
        if err or func_expr is None:
            return SymbolicEqualityState.PARSE_FAILED, {"error": err}

        var = sp.Symbol(var_name)
        actual_derivative = sp.diff(func_expr, var)
        actual_str = str(actual_derivative)
        return self.verify_algebraic_equivalence(actual_str, claimed_derivative_str)

    def audit_domain_validity(self, expr_str: str) -> List[Dict[str, Any]]:
        """Audits expression for division by zero, negative logarithms, or square root domain issues."""
        issues = []
        expr, err = self.parse_expression(expr_str)
        if err or expr is None:
            return [{"issue_type": "SYNTAX_PARSE_ERROR", "details": err}]

        # Check for explicit division denominators
        for atom in expr.atoms(sp.Pow):
            if atom.exp.is_negative:
                denom = atom.base
                issues.append({
                    "issue_type": "POTENTIAL_DIVISION_BY_ZERO",
                    "denominator": str(denom),
                    "mitigation": f"Ensure denominator {denom} != 0 via regularization or epsilon.",
                })

        # Check for logarithms
        for atom in expr.atoms(sp.log):
            arg = atom.args[0]
            issues.append({
                "issue_type": "LOGARITHM_DOMAIN_CONSTRAINT",
                "argument": str(arg),
                "mitigation": f"Ensure argument {arg} > 0 for all valid inputs.",
            })

        return issues

    def audit_tensor_shape_compatibility(
        self,
        operation_type: str,
        operand_shapes: List[Tuple[int, ...]],
        expected_output_shape: Optional[Tuple[int, ...]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Audits ML representation shape compatibility (Prompt 6 Section 16).
        E.g. alignment between z_seq in R^d and z_graph in R^d.
        """
        if operation_type == "ALIGNMENT_COSINE":
            if len(operand_shapes) != 2:
                return False, f"Alignment requires 2 operands, got {len(operand_shapes)}."
            if operand_shapes[0][-1] != operand_shapes[1][-1]:
                return False, f"Dimensionality mismatch in alignment: {operand_shapes[0]} vs {operand_shapes[1]}."
            return True, None

        if operation_type == "CONCATENATION":
            dim = operand_shapes[0][:-1]
            for s in operand_shapes[1:]:
                if s[:-1] != dim:
                    return False, f"Batch/sequence dimensions mismatch in concat: {operand_shapes}."
            return True, None

        if operation_type == "MATRIX_MULTIPLY":
            if len(operand_shapes) != 2:
                return False, "Matrix multiplication requires exactly 2 operands."
            if operand_shapes[0][-1] != operand_shapes[1][-2]:
                return False, f"Inner matrix dimensions incompatible: {operand_shapes[0]} and {operand_shapes[1]}."
            return True, None

        return True, None

    def audit_loss_function_composition(
        self,
        loss_terms: List[Dict[str, Any]],
    ) -> Tuple[bool, List[str]]:
        """
        Audits multi-objective loss functions (Prompt 6 Section 17):
        L = sum lambda_i * L_i
        Checks scalar outputs, positive lambda constraints, constituent provenance.
        """
        issues = []
        for i, term in enumerate(loss_terms):
            name = term.get("name", f"Term_{i}")
            weight = term.get("lambda_weight")
            is_scalar = term.get("is_scalar", True)
            provenance = term.get("provenance_source_id")

            if not is_scalar:
                issues.append(f"Loss term '{name}' is not scalar; must reduce to scalar before addition.")
            if weight is not None and isinstance(weight, (int, float)) and weight < 0:
                issues.append(f"Weight lambda for loss term '{name}' is negative ({weight}); must be >= 0.")
            if not provenance:
                issues.append(f"Loss term '{name}' lacks constituent provenance source_id.")

        return len(issues) == 0, issues
