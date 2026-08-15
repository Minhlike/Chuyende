"""
Writing Gates & Node Readiness Evaluator (Prompt 7 Section 4-5)
"""

from typing import List, Optional, Tuple
from research_agent.core.enums import (
    IntellectualOwnership,
    VerificationStatus,
    WritingReadiness,
    AuditSeverity,
)
from research_agent.schemas.composition import NodeWritingStatus
from research_agent.schemas.reasoning import ArgumentBundle
from research_agent.storage.repository import ResearchRepository


class WritingGate:
    """
    Evaluates whether a Roadmap Node has met all epistemic and scientific
    prerequisites to enter academic drafting and final composition.
    """

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def evaluate_node_readiness(self, node_code: str) -> NodeWritingStatus:
        """
        Evaluates node writing readiness based on canonical roadmap requirements,
        argument bundles, source verification, equations, and verified results.
        """
        node = self.repo.get_roadmap_node_by_code(node_code)
        if not node:
            return NodeWritingStatus(
                node_code=node_code,
                title="Unknown Node",
                readiness=WritingReadiness.NOT_READY,
                is_blocked=True,
                blocking_reasons=[f"Roadmap node '{node_code}' does not exist in canonical roadmap."],
            )

        blocking_reasons: List[str] = []

        # 1. Check ArgumentBundle
        bundles = self.repo.list_argument_bundles_by_node(node_code)
        bundle: Optional[ArgumentBundle] = bundles[-1] if bundles else None
        bundle_id = bundle.bundle_id if bundle else None

        # 2. Query associated claims and evidences
        claims = self.repo.list_claims_by_node(node_code)
        evidences = [e for c in claims for e in self.repo.get_claim_evidences(c.claim_id)]
        contradictions = self.repo.list_contradictions_by_node(node_code)
        num_claims = self.repo.list_numerical_claims()
        node_num_claims = [nc for nc in num_claims if nc.scope_dataset and node_code in nc.scope_dataset]
        equations = self.repo.list_equations_by_node(node_code)

        # 3. Node Type Specific Gate Requirements (Prompt 7 Section 5)
        title_lower = node.title.lower()
        is_background = any(k in title_lower for k in ["background", "foundation", "definition", "overview", "survey"])
        is_gap = any(k in title_lower for k in ["gap", "challenge", "limitation", "problem", "motivation"])
        is_method = any(k in title_lower for k in ["method", "architecture", "design", "mechanism", "representation", "framework"])
        is_experiment = any(k in title_lower for k in ["experiment", "protocol", "setup", "benchmark", "dataset", "evaluation"])
        is_result = any(k in title_lower for k in ["result", "finding", "empirical", "performance", "ablation", "robustness"])
        is_discussion = any(k in title_lower for k in ["discussion", "analysis", "implication", "threat", "limitation"])

        # Check critical reasoning issues
        if bundle:
            crit_issues = [
                i for i in bundle.reasoning_issues
                if (getattr(i.severity, "value", str(i.severity)) in ("FATAL", "CRITICAL"))
            ]
            if crit_issues:
                blocking_reasons.append(f"Unresolved critical reasoning issues in ArgumentBundle: {[i.message for i in crit_issues]}")

        # Gate checks per category
        if is_background or is_gap:
            if not claims and not evidences:
                blocking_reasons.append(f"Node '{node_code}' lacks registered claims/evidence from peer-reviewed literature.")

        if is_method:
            # Check equation verification if equations exist
            unverified_eqs = [eq for eq in equations if not getattr(eq, "is_verified", True)]
            if unverified_eqs:
                blocking_reasons.append(f"Method node '{node_code}' contains unverified equations: {[eq.equation_id for eq in unverified_eqs]}")

        if is_result:
            # Result nodes require verified ResultBundle or NumericalClaims
            unverified_nums = [nc for nc in node_num_claims if nc.verification_status != VerificationStatus.VERIFIED]
            if unverified_nums:
                blocking_reasons.append(f"Result node '{node_code}' contains unverified numerical claims: {[nc.numerical_claim_id for nc in unverified_nums]}")

        # Determine readiness status
        if blocking_reasons:
            readiness = WritingReadiness.BLOCKED
            is_blocked = True
        elif not bundle and not is_background:
            readiness = WritingReadiness.PROVISIONAL
            is_blocked = False
        else:
            readiness = WritingReadiness.READY
            is_blocked = False

        # Check if already drafted
        paragraphs = self.repo.list_paragraphs_by_node(node_code)
        if paragraphs:
            if all(p.review_status.value in ("MACHINE_AUDITED", "HUMAN_ACCEPTED") for p in paragraphs):
                readiness = WritingReadiness.AUDITED
            else:
                readiness = WritingReadiness.DRAFTED

        return NodeWritingStatus(
            node_code=node_code,
            title=node.title,
            readiness=readiness,
            argument_bundle_id=bundle_id,
            total_sources=len(set(e.source_id for e in evidences if hasattr(e, "source_id") and e.source_id)),
            total_claims=len(claims),
            total_evidences=len(evidences),
            total_contradictions=len(contradictions),
            total_numerical_claims=len(node_num_claims),
            total_equations=len(equations),
            is_blocked=is_blocked,
            blocking_reasons=blocking_reasons,
            paragraph_count=len(paragraphs),
        )
