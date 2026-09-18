"""
Người lập kế hoạch diễn ngôn tu từ & Người kiểm tra thu hút mẫu (Nhắc 5 Phần 53..55, 62)
"""

from typing import List, Dict, Any, Optional
from research_agent.core.enums import (
    DiscourseFunction,
    ArgumentPatternType,
    ReasoningIssueType,
)
from research_agent.schemas.reasoning import (
    DiscourseStep,
    DiscoursePlan,
    ReasoningIssue,
)


class DiscoursePlanner:
    """
    Xây dựng kế hoạch diễn ngôn tu từ đa dạng, không cứng nhắc.
    Kiểm tra các cấu trúc thu hút mẫu lặp đi lặp lại trên các đối số.
    """

    # 10 mẫu đối số có thể tái sử dụng (Phần 55)
    PATTERN_DEFINITIONS = {
        ArgumentPatternType.PROBLEM_MECHANISM_CONSEQUENCE: [
            DiscourseFunction.DEFINE,
            DiscourseFunction.EXPLAIN_MECHANISM,
            DiscourseFunction.LIMIT,
        ],
        ArgumentPatternType.CLAIM_EVIDENCE_QUALIFICATION: [
            DiscourseFunction.HYPOTHESIZE,
            DiscourseFunction.PRESENT_EVIDENCE,
            DiscourseFunction.QUALIFY,
        ],
        ArgumentPatternType.METHOD_A_VS_METHOD_B_TRADEOFF: [
            DiscourseFunction.COMPARE,
            DiscourseFunction.CONTRAST,
            DiscourseFunction.SYNTHESIZE,
        ],
        ArgumentPatternType.ASSUMPTION_VIOLATION_FAILURE: [
            DiscourseFunction.DEFINE,
            DiscourseFunction.EXPLAIN_MECHANISM,
            DiscourseFunction.COUNTERARGUE,
            DiscourseFunction.FALSIFY,
        ],
        ArgumentPatternType.OBSERVATION_ALTERNATIVES_DISCRIMINATING_TEST: [
            DiscourseFunction.PRESENT_EVIDENCE,
            DiscourseFunction.DISTINGUISH,
            DiscourseFunction.RESOLVE_CONFLICT,
        ],
        ArgumentPatternType.PRIOR_WORK_LIMITATION_GAP: [
            DiscourseFunction.SYNTHESIZE,
            DiscourseFunction.DELIMIT,
            DiscourseFunction.MOTIVATE,
        ],
        ArgumentPatternType.RESULT_ALTERNATIVE_CONTROL_INTERPRETATION: [
            DiscourseFunction.PRESENT_EVIDENCE,
            DiscourseFunction.COUNTERARGUE,
            DiscourseFunction.INTERPRET,
        ],
        ArgumentPatternType.BENEFIT_COST_BOUNDARY: [
            DiscourseFunction.EXPLAIN_MECHANISM,
            DiscourseFunction.QUALIFY,
            DiscourseFunction.LIMIT,
        ],
        ArgumentPatternType.CLAIM_COUNTEREXAMPLE_REFINED_CLAIM: [
            DiscourseFunction.HYPOTHESIZE,
            DiscourseFunction.COUNTERARGUE,
            DiscourseFunction.QUALIFY,
        ],
        ArgumentPatternType.EVIDENCE_LIMITATION_NARROWED_CONCLUSION: [
            DiscourseFunction.PRESENT_EVIDENCE,
            DiscourseFunction.LIMIT,
            DiscourseFunction.INTERPRET,
        ],
    }

    def plan_discourse(
        self,
        roadmap_node: str,
        preferred_pattern: Optional[ArgumentPatternType] = None,
        subject_entity_ids: Optional[List[str]] = None,
    ) -> DiscoursePlan:
        """
        Tạo DiscoursePlan được chọn động để tránh kiểu dáng thống nhất cứng nhắc.
        """
        # Chọn mẫu một cách xác định dựa trên hàm băm nút lộ trình nếu không được chỉ định
        if not preferred_pattern:
            patterns = list(self.PATTERN_DEFINITIONS.keys())
            idx = abs(hash(roadmap_node)) % len(patterns)
            pattern_type = patterns[idx]
        else:
            pattern_type = preferred_pattern

        functions = self.PATTERN_DEFINITIONS[pattern_type]
        steps: List[DiscourseStep] = []
        for i, fn in enumerate(functions, start=1):
            steps.append(
                DiscourseStep(
                    step_index=i,
                    function=fn,
                    subject_entity_ids=subject_entity_ids or [roadmap_node],
                    intent=f"Execute {fn.value} within {pattern_type.value} argumentation structure.",
                    argument_pattern=pattern_type,
                )
            )

        seq = abs(hash(roadmap_node + pattern_type.value)) % 1000000
        return DiscoursePlan(
            plan_id=f"DISC-{seq:06d}",
            roadmap_node=roadmap_node,
            argument_pattern_name=pattern_type,
            steps=steps,
            estimated_paragraphs=len(steps),
            notes="Designed with varied rhetorical functions to prevent template attractor collapse.",
        )

    def audit_template_attractors(self, plans: List[DiscoursePlan]) -> List[ReasoningIssue]:
        """
        Phát hiện các mẫu cấu trúc lặp đi lặp lại trên nhiều phương án đối số (Phần 62).
        """
        issues: List[ReasoningIssue] = []
        if len(plans) < 3:
            return issues

        # Kiểm tra xem 3 kế hoạch liên tiếp có sử dụng mẫu giống nhau không
        for i in range(len(plans) - 2):
            p1, p2, p3 = plans[i], plans[i + 1], plans[i + 2]
            if p1.argument_pattern_name == p2.argument_pattern_name == p3.argument_pattern_name:
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-TPL-{abs(hash(p1.plan_id + p3.plan_id)) % 1000000:06d}",
                        issue_type=ReasoningIssueType.TEMPLATE_ATTRACTOR_RISK,
                        affected_entity_id=p3.plan_id,
                        message=f"Repetitive Argument Pattern: 3 consecutive sections ({p1.roadmap_node}, {p2.roadmap_node}, {p3.roadmap_node}) use identical pattern '{p1.argument_pattern_name.value}'.",
                        severity="MEDIUM",
                        mitigation="Diversify rhetorical pattern using alternative argument structures (e.g. METHOD_A_VS_METHOD_B_TRADEOFF or BENEFIT_COST_BOUNDARY).",
                    )
                )

        return issues
