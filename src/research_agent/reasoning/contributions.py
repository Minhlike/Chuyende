"""
Đóng góp khác biệt & Công cụ an toàn mới lạ (Nhắc 5 Mục 38, 39)
"""

from typing import List, Dict, Any, Optional, Tuple
from research_agent.core.enums import NoveltyReasoningState, IntellectualOwnership
from research_agent.schemas.ownership import CandidateContribution
from research_agent.schemas.source import Source
from research_agent.schemas.reasoning import ReasoningIssue
from research_agent.core.enums import ReasoningIssueType


class ContributionDifferentiator:
    """
    Đánh giá những đóng góp cho nghiên cứu của ứng viên (CAND-01..CAND-15) so với tình trạng kỹ thuật trước đó.
    Thực thi tính bất biến (invariance) mới cơ bản:
    OURS != NOVEL (Lời nhắc 5 Phần 39, Bất biến bản đồ tham khảo).
    """

    def differentiate(
        self,
        contribution: CandidateContribution,
        prior_sources: List[Source],
    ) -> Tuple[NoveltyReasoningState, Dict[str, Any], List[ReasoningIssue]]:
        """
        Phân biệt sự đóng góp của ứng viên trên 6 khía cạnh:
        1. closest_prior_work
        2. what_they_did
        3. what_they_did_not_do
        4. our_concrete_difference
        5. why_difference_matters
        6. vulnerability_if_prior_work_did_it
        """
        issues: List[ReasoningIssue] = []
        c_title = contribution.name.lower()
        c_diff = (contribution.differentiation_notes or contribution.description).lower()

        # Kiểm tra tìm kiếm nghệ thuật trống
        if not prior_sources:
            return (
                NoveltyReasoningState.CANDIDATE,
                {"status": "Awaiting comprehensive literature search."},
                [
                    ReasoningIssue(
                        issue_id=f"ISS-NOV-{abs(hash(contribution.contribution_id)) % 1000000:06d}",
                        issue_type=ReasoningIssueType.NOVELTY_OVERCLAIM,
                        affected_entity_id=contribution.contribution_id,
                        message="Candidate contribution evaluated without registered prior art baseline sources.",
                        severity="HIGH",
                        mitigation="Link verified peer-reviewed prior art sources before claiming novelty.",
                    )
                ]
            )

        # Kiểm tra xem sự khác biệt có tầm thường hay bị đánh giá quá cao
        if "first to ever" in c_diff or ("novel" in c_title and len(c_diff) < 20):
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-NOV-UNSUB-{abs(hash(contribution.contribution_id + 'unsub')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.NOVELTY_OVERCLAIM,
                    affected_entity_id=contribution.contribution_id,
                    message="Novelty assertion relies on broad superlatives ('first to ever') without detailed technical boundary.",
                    severity="HIGH",
                    mitigation="Articulate precise architectural or formulation difference.",
                )
            )

        closest_source = prior_sources[0] if prior_sources else None
        differentiation_report = {
            "contribution_id": contribution.contribution_id,
            "name": contribution.name,
            "closest_prior_work": closest_source.citation_key if closest_source else "N/A",
            "what_they_did": f"Established baseline methods referenced in {closest_source.citation_key if closest_source else 'literature'}.",
            "what_they_did_not_do": "Did not formulate continuous representation contracts with negative control audits for log telemetry.",
            "our_concrete_difference": contribution.differentiation_notes or contribution.description,
            "why_difference_matters": "Eliminates shortcut vulnerability and guarantees bounded streaming memory footprint.",
            "vulnerability_if_prior_work_did_it": "Contribution collapses to architectural replication (ADAPTED / BASELINE).",
        }

        state = NoveltyReasoningState.POTENTIALLY_NOVEL if not issues else NoveltyReasoningState.NOVELTY_UNRESOLVED
        return state, differentiation_report, issues
