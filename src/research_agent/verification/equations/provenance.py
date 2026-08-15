"""
Equation Provenance & Invariant Auditor (Prompt 6 Sections 6..12, RC-08)
"""

from typing import Any, Dict, List, Optional, Tuple
from research_agent.core.enums import EquationType, IntellectualOwnership, VerificationStatus
from research_agent.schemas.equation import Equation
from research_agent.core.exceptions import ProvenanceError


class EquationProvenanceAuditor:
    """
    Enforces strict typing and provenance invariants for mathematical equations.
    Guarantees isolation of SOURCE, DERIVED, and PROPOSED equations.
    """

    def audit_equation(self, eq: Equation) -> Tuple[bool, List[str]]:
        """Audits an Equation for constitutional provenance invariants (RC-08)."""
        issues: List[str] = []

        # Invariant 1: SOURCE_EQUATION requires external source_id and locator
        if eq.equation_type == EquationType.SOURCE_EQUATION:
            if not eq.source_id or not eq.source_id.strip():
                issues.append(f"SOURCE_EQUATION '{eq.equation_id}' lacks mandatory source_id.")
            if not eq.source_locator or not eq.source_locator.strip():
                issues.append(f"SOURCE_EQUATION '{eq.equation_id}' lacks mandatory source_locator (page/equation number).")
            if eq.ownership != IntellectualOwnership.SOURCE:
                issues.append(f"SOURCE_EQUATION '{eq.equation_id}' must have ownership=SOURCE, got {eq.ownership}.")

        # Invariant 2: DERIVED_EQUATION requires parent equations and derivation steps
        elif eq.equation_type == EquationType.DERIVED_EQUATION:
            if not eq.derivation:
                issues.append(f"DERIVED_EQUATION '{eq.equation_id}' lacks mandatory derivation record.")
            else:
                if not eq.derivation.parent_equation_ids:
                    issues.append(f"DERIVED_EQUATION '{eq.equation_id}' has empty parent_equation_ids.")
                if not eq.derivation.derivation_steps:
                    issues.append(f"DERIVED_EQUATION '{eq.equation_id}' has empty derivation_steps.")

        # Invariant 3: PROPOSED_EQUATION should have OURS ownership with constituent tracking
        elif eq.equation_type == EquationType.PROPOSED_EQUATION:
            if eq.ownership != IntellectualOwnership.OURS:
                issues.append(f"PROPOSED_EQUATION '{eq.equation_id}' should have ownership=OURS.")

        # Invariant 4: No empty LaTeX
        if not eq.latex or not eq.latex.strip():
            issues.append(f"Equation '{eq.equation_id}' has empty LaTeX content.")

        return len(issues) == 0, issues
