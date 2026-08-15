"""
Hypothesis & Research Question Evaluation Engine (Prompt 5 Sections 36, 37, 46, 69)
"""

from typing import List, Dict, Any, Optional, Tuple
from research_agent.core.enums import (
    EpistemicStatus,
    RQStatus,
    NegativeResultType,
)
from research_agent.schemas.roadmap import Hypothesis, ResearchQuestion
from research_agent.schemas.memory import EpisodeRecord
from research_agent.schemas.reasoning import ReasoningIssue
from research_agent.core.enums import ReasoningIssueType


class HypothesisEvaluationResult:
    """Outcome report for a hypothesis evaluation."""

    def __init__(
        self,
        hyp_id: str,
        status: EpistemicStatus,
        supporting_evidence_ids: List[str],
        contradicting_evidence_ids: List[str],
        negative_runs_count: int,
        limitations: List[str],
        missing_tests: List[str],
        rationale: str,
    ):
        self.hyp_id = hyp_id
        self.status = status
        self.supporting_evidence_ids = supporting_evidence_ids
        self.contradicting_evidence_ids = contradicting_evidence_ids
        self.negative_runs_count = negative_runs_count
        self.limitations = limitations
        self.missing_tests = missing_tests
        self.rationale = rationale


class HypothesisEvaluator:
    """
    Evaluates scientific hypotheses against empirical evidence and negative results.
    Enforces anti-HARKing and anti-hypothesis rescue rules (Sections 46, 69).
    """

    def evaluate_hypothesis(
        self,
        hypothesis: Hypothesis,
        episodes: List[EpisodeRecord],
        linked_evidence_ids: List[str],
        contradiction_ids: List[str],
    ) -> HypothesisEvaluationResult:
        """
        Calculates grounded EpistemicStatus for a hypothesis.
        """
        failures = [ep for ep in episodes if ep.is_failure]
        neg_types = []
        for f in failures:
            reason = (f.failure_reason or "").lower()
            if "crash" in reason or "oom" in reason or "timeout" in reason:
                neg_types.append(NegativeResultType.TECHNICAL_FAILURE)
            elif "falsif" in reason or "contradict" in reason:
                neg_types.append(NegativeResultType.HYPOTHESIS_FALSIFICATION)
            elif "no improvement" in reason or "insignificant" in reason:
                neg_types.append(NegativeResultType.NULL_RESULT)
            else:
                neg_types.append(NegativeResultType.NEGATIVE_RESULT)

        # Falsification check
        if NegativeResultType.HYPOTHESIS_FALSIFICATION in neg_types:
            return HypothesisEvaluationResult(
                hyp_id=hypothesis.code,
                status=EpistemicStatus.FALSIFIED,
                supporting_evidence_ids=linked_evidence_ids,
                contradicting_evidence_ids=contradiction_ids,
                negative_runs_count=len(failures),
                limitations=["Direct empirical test contradicted predicted outcome."],
                missing_tests=[],
                rationale=f"Hypothesis falsified by experimental failure run: {[f.episode_id for f in failures]}",
            )

        # Contested check
        if contradiction_ids:
            return HypothesisEvaluationResult(
                hyp_id=hypothesis.code,
                status=EpistemicStatus.CONTESTED,
                supporting_evidence_ids=linked_evidence_ids,
                contradicting_evidence_ids=contradiction_ids,
                negative_runs_count=len(failures),
                limitations=["Contradictory findings exist in literature or baseline replications."],
                missing_tests=["Discriminative negative control experiment"],
                rationale=f"Hypothesis contested by active contradiction units: {contradiction_ids}",
            )

        # Partially Supported check
        if linked_evidence_ids and failures:
            return HypothesisEvaluationResult(
                hyp_id=hypothesis.code,
                status=EpistemicStatus.PARTIALLY_SUPPORTED,
                supporting_evidence_ids=linked_evidence_ids,
                contradicting_evidence_ids=[],
                negative_runs_count=len(failures),
                limitations=["Supported under subset of configurations, but failed under stress conditions."],
                missing_tests=["Cross-domain holdout evaluation"],
                rationale="Positive evidence present but bounded by negative experimental episodes.",
            )

        # Supported check
        if linked_evidence_ids and not failures:
            return HypothesisEvaluationResult(
                hyp_id=hypothesis.code,
                status=EpistemicStatus.SUPPORTED,
                supporting_evidence_ids=linked_evidence_ids,
                contradicting_evidence_ids=[],
                negative_runs_count=0,
                limitations=["Bounded by verified experimental split scope."],
                missing_tests=[],
                rationale=f"Empirically supported by verified evidence units: {linked_evidence_ids}",
            )

        # Default Unverified
        return HypothesisEvaluationResult(
            hyp_id=hypothesis.code,
            status=EpistemicStatus.UNVERIFIED,
            supporting_evidence_ids=[],
            contradicting_evidence_ids=[],
            negative_runs_count=0,
            limitations=["Awaiting empirical benchmark execution."],
            missing_tests=["Initial ablation and probe experiment"],
            rationale="No direct evidence units or benchmark runs registered yet.",
        )

    def evaluate_rq_status(
        self,
        rq_code: str,
        hypothesis_statuses: List[EpistemicStatus],
        open_gap_count: int = 0,
    ) -> Tuple[RQStatus, str]:
        """
        Determines RQ status (OPEN, PARTIALLY_ANSWERED, ANSWERED_WITH_LIMITATIONS, CONTESTED, BLOCKED).
        """
        if all(s == EpistemicStatus.UNVERIFIED for s in hypothesis_statuses):
            return RQStatus.OPEN, "No empirical tests completed for linked hypotheses."

        if any(s == EpistemicStatus.CONTESTED for s in hypothesis_statuses):
            return RQStatus.CONTESTED, "Underlying hypotheses face active empirical contradictions."

        if open_gap_count > 0:
            return RQStatus.PARTIALLY_ANSWERED, f"Addressed partially, but {open_gap_count} critical evidence gaps remain."

        if all(s in [EpistemicStatus.SUPPORTED, EpistemicStatus.PARTIALLY_SUPPORTED] for s in hypothesis_statuses):
            return RQStatus.ANSWERED_WITH_LIMITATIONS, "Supported within verified benchmark scope with stated operational bounds."

        return RQStatus.OPEN, "Research investigation in progress."
