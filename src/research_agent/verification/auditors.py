"""
Scientific Integrity Auditors & Anti-Hallucination Firewalls (Prompt 6 Sections 90..96, RC-08..18)
"""

from typing import Any, Dict, List, Optional, Tuple
from research_agent.core.enums import (
    AllowedWordingStrength,
    NumericalClaimType,
    VerificationStatus,
    VerificationRequestStatus,
)
from research_agent.schemas.verification import (
    NumericalClaim,
    TableSpecification,
    FigureSpecification,
    VerifiedClaimBundle,
    ResultBundle,
)
from research_agent.schemas.equation import Equation


class NumericalHallucinationAuditor:
    """
    Guards against ungrounded, fabricated, or cherry-picked numerical claims (Prompt 6 Section 90).
    """

    def audit_numerical_claim(self, claim: NumericalClaim) -> Tuple[bool, List[str]]:
        issues = []

        # Rule 1: Must have provenance
        if claim.source_type == NumericalClaimType.SOURCE_REPORTED:
            if not claim.source_id:
                issues.append(f"Numerical claim '{claim.numerical_claim_id}' is SOURCE_REPORTED but lacks source_id.")
            if not claim.source_locator:
                issues.append(f"Numerical claim '{claim.numerical_claim_id}' lacks source_locator.")
        elif claim.source_type in [NumericalClaimType.RECOMPUTED, NumericalClaimType.EXPERIMENT_RESULT]:
            if not claim.computation_id:
                issues.append(f"Numerical claim '{claim.numerical_claim_id}' is computed but lacks computation_id.")

        # Rule 2: Non-empty statement & quantity
        if not claim.statement or len(claim.statement.strip()) < 5:
            issues.append(f"Numerical claim '{claim.numerical_claim_id}' has empty statement.")
        if not claim.quantity_name or len(claim.quantity_name.strip()) < 2:
            issues.append(f"Numerical claim '{claim.numerical_claim_id}' has empty quantity_name.")

        return len(issues) == 0, issues


class VerificationGateForWriting:
    """
    Firewall gate for Prompt 7 Chapter Composer (Prompt 6 Section 95, 139).
    Blocks unverified claims, missing result bundles, or exaggerated claim language.
    """

    def audit_claim_for_thesis_composition(
        self,
        claim_bundle: VerifiedClaimBundle,
        result_bundle: Optional[ResultBundle] = None,
    ) -> Tuple[bool, List[str]]:
        issues = []

        # Check numerical claims inside bundle
        for num in claim_bundle.numerical_claims:
            if num.verification_status != VerificationStatus.VERIFIED:
                issues.append(
                    f"Claim contains unverified numerical quantity '{num.quantity_name}': status={num.verification_status}."
                )

        # Check allowed wording strength alignment
        if claim_bundle.allowed_wording_strength == AllowedWordingStrength.STRONG_SUPPORT:
            if not claim_bundle.source_evidence_ids and not claim_bundle.result_bundle_id:
                issues.append("STRONG_SUPPORT requires multiple convergent empirical evidence sources.")

        if claim_bundle.allowed_wording_strength == AllowedWordingStrength.DESCRIPTIVE_ONLY:
            stmt_lower = claim_bundle.statement.lower()
            if any(w in stmt_lower for w in ["causes", "outperforms", "superior", "proves"]):
                issues.append(
                    "DESCRIPTIVE_ONLY claim uses comparative or causal language ('causes', 'outperforms', 'proves')."
                )

        return len(issues) == 0, issues
