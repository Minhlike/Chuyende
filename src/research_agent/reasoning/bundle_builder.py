"""
Argument Bundle Builder & Reasoning Readiness Gate (Prompt 5 Sections 56..64)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from research_agent.schemas.reasoning import (
    ArgumentBundle,
    AssumptionRecord,
    CounterargumentRecord,
    InferenceRecord,
    FalsificationPlan,
    ReasoningIssue,
    VerificationRequest,
    DiscoursePlan,
)
from research_agent.core.enums import (
    ArgumentReadinessState,
    ReasoningIssueType,
)


class ArgumentBundleBuilder:
    """
    Assembles complete typed ArgumentBundle instances.
    Evaluates strict multi-criteria readiness gate (Section 64) before handing off to writing.
    """

    def build_bundle(
        self,
        roadmap_node: str,
        objective: str,
        research_questions: List[str],
        hypotheses: List[str],
        claims: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        contradicting_evidence: List[Dict[str, Any]],
        assumptions: List[AssumptionRecord],
        counterarguments: List[CounterargumentRecord],
        candidate_inferences: List[InferenceRecord],
        falsification_plans: List[FalsificationPlan],
        ownership_summary: Dict[str, str],
        open_questions: List[str],
        discourse_plan: Optional[DiscoursePlan] = None,
        issues: Optional[List[ReasoningIssue]] = None,
        verification_requests: Optional[List[VerificationRequest]] = None,
        uncertainty: str = "Low to moderate remaining variance.",
    ) -> ArgumentBundle:
        """
        Builds and gates an ArgumentBundle.
        """
        all_issues = issues or []
        all_verifs = verification_requests or []
        seq = abs(hash(roadmap_node + objective)) % 1000000
        bundle_id = f"BND-{seq:06d}"

        # Evaluate Readiness Gate (Section 64)
        readiness = self._evaluate_readiness_gate(
            claims=claims,
            evidence=evidence,
            contradicting_evidence=contradicting_evidence,
            assumptions=assumptions,
            counterarguments=counterarguments,
            issues=all_issues,
        )

        return ArgumentBundle(
            bundle_id=bundle_id,
            roadmap_node=roadmap_node,
            objective=objective,
            research_questions=research_questions,
            hypotheses=hypotheses,
            claims=claims,
            evidence=evidence,
            contradicting_evidence=contradicting_evidence,
            assumptions=assumptions,
            counterarguments=counterarguments,
            candidate_inferences=candidate_inferences,
            falsification_plans=falsification_plans,
            ownership_summary=ownership_summary,
            uncertainty=uncertainty,
            open_questions=open_questions,
            discourse_plan=discourse_plan,
            readiness_state=readiness,
            issues=all_issues,
            verification_requests=all_verifs,
            generated_at=datetime.now(timezone.utc),
            version="1.0.0",
        )

    def _evaluate_readiness_gate(
        self,
        claims: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        contradicting_evidence: List[Dict[str, Any]],
        assumptions: List[AssumptionRecord],
        counterarguments: List[CounterargumentRecord],
        issues: List[ReasoningIssue],
    ) -> ArgumentReadinessState:
        """
        Computes readiness state based on gate conditions.
        """
        # Critical Issue Gate -> BLOCKED
        critical_issues = [iss for iss in issues if iss.severity == "CRITICAL"]
        if critical_issues:
            return ArgumentReadinessState.BLOCKED

        # Active Unresolved Contradictions -> CONTESTED
        if contradicting_evidence and any(not c.get("is_resolved", False) for c in contradicting_evidence):
            return ArgumentReadinessState.CONTESTED

        # Missing Evidence for Claims -> EVIDENCE_INCOMPLETE
        if claims and not evidence:
            return ArgumentReadinessState.EVIDENCE_INCOMPLETE

        # High Issues or Untested Fatal Assumptions -> REVIEW_REQUIRED
        high_issues = [iss for iss in issues if iss.severity == "HIGH"]
        if high_issues or any(a.status == "VIOLATED" for a in assumptions):
            return ArgumentReadinessState.REVIEW_REQUIRED

        return ArgumentReadinessState.READY
