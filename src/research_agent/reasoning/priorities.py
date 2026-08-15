"""
Information-Gain Research Action Prioritizer (Prompt 5 Sections 106, 107)
"""

from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import (
    ResearchActionPriority,
    EvidenceGap,
    AssumptionRecord,
    VerificationRequest,
)
from research_agent.core.enums import ResearchPriorityLevel, EpistemicStatus


class ResearchActionPrioritizer:
    """
    Ranks next best research actions ordered by expected uncertainty reduction.
    Focuses effort on falsifying discriminating tests rather than redundant support gathering.
    """

    def prioritize_actions(
        self,
        gaps: List[EvidenceGap],
        assumptions: List[AssumptionRecord],
        verification_requests: List[VerificationRequest],
        contested_hypotheses: List[str],
    ) -> List[ResearchActionPriority]:
        """
        Computes ordered list of research priorities.
        """
        actions: List[ResearchActionPriority] = []

        # 1. Contested Hypotheses (CRITICAL)
        for hyp_id in contested_hypotheses:
            actions.append(
                ResearchActionPriority(
                    action_id=f"ACT-CRIT-{abs(hash(hyp_id)) % 10000:04d}",
                    priority=ResearchPriorityLevel.CRITICAL,
                    title=f"Resolve empirical contradiction on {hyp_id}",
                    rationale=f"Active contradiction threatens core hypothesis {hyp_id}. Requires discriminating negative control.",
                    action_type="RUN_EXPERIMENT",
                    related_hyp_id=hyp_id,
                )
            )

        # 2. Open High/Critical Evidence Gaps (CRITICAL / HIGH)
        for gap in gaps:
            if gap.status == "OPEN":
                pri = ResearchPriorityLevel.CRITICAL if gap.severity == "CRITICAL" else ResearchPriorityLevel.HIGH
                actions.append(
                    ResearchActionPriority(
                        action_id=f"ACT-GAP-{gap.gap_id}",
                        priority=pri,
                        title=f"Close Evidence Gap: {gap.missing_evidence[:50]}...",
                        rationale=gap.why_required,
                        action_type="RUN_EXPERIMENT" if gap.suggested_experiment else "SEARCH_LITERATURE",
                        related_gap_id=gap.gap_id,
                    )
                )

        # 3. Untested Fragile Assumptions (HIGH)
        for ass in assumptions:
            if ass.status == "UNTESTED" and ass.testability in ["TESTABLE_BY_EXPERIMENT", "TESTABLE_BY_AUDIT"]:
                actions.append(
                    ResearchActionPriority(
                        action_id=f"ACT-ASM-{ass.assumption_id}",
                        priority=ResearchPriorityLevel.HIGH,
                        title=f"Test Assumption: {ass.statement[:50]}...",
                        rationale=f"Violation consequence: {ass.violation_consequence}",
                        action_type="AUDIT_SHORTCUT" if "AUDIT" in ass.testability else "RUN_EXPERIMENT",
                    )
                )

        # 4. Pending Verification Requests (HIGH / MEDIUM)
        for req in verification_requests:
            if req.status.value == "PENDING":
                actions.append(
                    ResearchActionPriority(
                        action_id=f"ACT-VERIF-{req.request_id}",
                        priority=ResearchPriorityLevel.HIGH,
                        title=f"Execute Verification: {req.request_type.value} ({req.description[:40]}...)",
                        rationale="Formal scientific verification gate required for Prompt 6 hand-off.",
                        action_type="VERIFY_EQUATION" if "EQUATION" in req.request_type.value else "VERIFY_DATA",
                    )
                )

        # Sort by Priority: CRITICAL -> HIGH -> MEDIUM -> LOW
        pri_order = {
            ResearchPriorityLevel.CRITICAL: 0,
            ResearchPriorityLevel.HIGH: 1,
            ResearchPriorityLevel.MEDIUM: 2,
            ResearchPriorityLevel.LOW: 3,
        }
        actions.sort(key=lambda a: pri_order.get(a.priority, 4))
        return actions
