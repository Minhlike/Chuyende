"""
Lược đồ Pydantic cho các yêu cầu lập luận, lập luận và xác minh khoa học (Nhắc 5)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from research_agent.core.enums import (
    IntellectualOwnership,
    EpistemicStatus,
    ClaimType,
    ReasoningMode,
    EvidenceAlignmentStatus,
    ContradictionType,
    NegativeResultType,
    ArgumentReadinessState,
    ReasoningIssueType,
    DiscourseFunction,
    ArgumentNodeType,
    ArgumentEdgeType,
    RQStatus,
    NoveltyReasoningState,
    VerificationRequestType,
    VerificationRequestStatus,
    ResearchPriorityLevel,
    ArgumentPatternType,
)


class ClaimScope(BaseModel):
    """Phạm vi hoạt động và môi trường rõ ràng giới hạn yêu cầu bồi thường (Nhắc 5 Phần 8)."""
    dataset: Optional[str] = None
    domain: Optional[str] = None
    timeframe: Optional[str] = None
    model_or_config: Optional[str] = None
    metric: Optional[str] = None
    experimental_setting: Optional[str] = None
    population_or_logs: Optional[str] = None
    known_exclusions: List[str] = Field(default_factory=list)


class AtomicClaimCandidate(BaseModel):
    """Tuyên bố nguyên tử được trích xuất và chuẩn hóa từ tài liệu hoặc thí nghiệm (Nhắc 5 Phần 6, 7)."""
    claim_id: Optional[str] = None
    statement: str
    original_wording: Optional[str] = None
    source_id: Optional[str] = None
    locator: Optional[str] = None
    claim_type: ClaimType = ClaimType.SOURCE_CLAIM
    ownership: IntellectualOwnership = IntellectualOwnership.SOURCE
    scope: ClaimScope = Field(default_factory=ClaimScope)
    qualifiers: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    confidence_basis: Optional[str] = None
    is_normalized: bool = True
    extracted_from: Optional[str] = None


class EvidenceGap(BaseModel):
    """Khoảng cách bằng chứng rõ ràng khi Yêu cầu bồi thường thiếu hỗ trợ thực nghiệm đầy đủ (Nhắc 5 Phần 11)."""
    gap_id: str
    claim_id: str
    missing_evidence: str
    why_required: str
    possible_source_search: Optional[str] = None
    suggested_experiment: Optional[str] = None
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    related_node_code: Optional[str] = None
    status: str = "OPEN"  # OPEN, INVESTIGATING, RESOLVED, WAIVING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssumptionRecord(BaseModel):
    """Giả định lý thuyết/thực nghiệm rõ ràng hoặc ngầm định (Nhắc 5 Mục 16, 17)."""
    assumption_id: str
    statement: str
    is_explicit: bool = False
    required_by: List[str] = Field(default_factory=list)  # claim_ids, inference_ids, hypothesis_ids
    evidence_or_basis: Optional[str] = None
    testability: str = "TESTABLE_BY_EXPERIMENT"  # TESTABLE_BY_EXPERIMENT, TESTABLE_BY_AUDIT, AXIOMATIC, UNTESTABLE
    violation_consequence: str = "Degrades claim validity."
    status: str = "UNTESTED"  # UNTESTED, VALIDATED, VIOLATED, FRAGILE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlternativeExplanation(BaseModel):
    """Giải thích cạnh tranh hoặc yếu tố gây nhiễu cho một kết quả thử nghiệm được quan sát (Nhắc 5 Phần 18)."""
    alt_id: str
    explanation: str
    confounder_type: str  # CAPACITY, LEAKAGE, SHORTCUT, TUNING, STOCHASTIC, ARTIFACT
    affected_claim_id: Optional[str] = None
    test_or_control: str
    likelihood: str = "PLAUSIBLE"  # HIGH, PLAUSIBLE, UNLIKELY
    is_tested: bool = False
    test_outcome: Optional[str] = None


class CounterargumentRecord(BaseModel):
    """Phản biện của Steelman thách thức một suy luận hoặc khẳng định (Nhắc 5 Mục 22, 23)."""
    counter_id: str
    objection: str
    basis: str
    evidence_ids: List[str] = Field(default_factory=list)
    affected_claim_id: str
    severity: str = "SERIOUS"  # FATAL, SERIOUS, MODERATE, MINOR
    is_steelman: bool = True
    origin: str = "OUR_COUNTERARGUMENT"  # OUR_COUNTERARGUMENT, EXTERNAL_LITERATURE
    response_options: List[str] = Field(default_factory=list)
    is_resolved: bool = False
    resolution_notes: Optional[str] = None


class FalsificationPlan(BaseModel):
    """Quy trình giả mạo và kiểm soát phủ định đối với một giả thuyết (Nhắc 5 Phần 20)."""
    plan_id: str
    target_hypothesis_id: str
    target_claim_id: Optional[str] = None
    potential_falsifying_observations: List[str] = Field(default_factory=list)
    controls: List[str] = Field(default_factory=list)
    negative_controls: List[str] = Field(default_factory=list)
    required_experiments: List[str] = Field(default_factory=list)
    confounders: List[str] = Field(default_factory=list)
    expected_outcomes_if_true: List[str] = Field(default_factory=list)
    expected_outcomes_if_false: List[str] = Field(default_factory=list)


class InferenceRecord(BaseModel):
    """Cấu trúc suy luận nghiên cứu được chứng minh rõ ràng (Nhắc 5 Mục 24, 25, 26)."""
    inference_id: str
    premises: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    assumption_ids: List[str] = Field(default_factory=list)
    reasoning_type: ReasoningMode = ReasoningMode.INDUCTIVE
    justified_scope: ClaimScope = Field(default_factory=ClaimScope)
    counterevidence_ids: List[str] = Field(default_factory=list)
    candidate_conclusion: str
    confidence_basis: str
    strength: str = "MODERATE"  # STRONG, MODERATE, WEAK, INSUFFICIENT
    remaining_uncertainty: str
    falsification_route: str
    actor: str = "RESEARCH_AGENT"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompetingHypothesis(BaseModel):
    """Giả thuyết phụ trợ hoặc cạnh tranh được lưu trữ riêng biệt với H1..H5 chính tắc (Nhắc 5 Phần 19)."""
    ch_id: str
    canonical_hyp_id: str  # H1..H5
    statement: str
    why_competing: str
    discriminating_test: str
    status: EpistemicStatus = EpistemicStatus.UNVERIFIED


class PredictionRecord(BaseModel):
    """Dự đoán thực nghiệm có thể kiểm chứng được bắt nguồn từ một giả thuyết (Nhắc 5 Phần 67, 68)."""
    prediction_id: str
    hypothesis_id: str
    prediction_statement: str
    discriminating_test: str
    is_post_hoc: bool = False
    status: str = "PENDING_TEST"  # PENDING_TEST, CONFIRMED, FALSIFIED, INCONCLUSIVE


class ReasoningIssue(BaseModel):
    """Khiếm khuyết về phương pháp hoặc logic được phát hiện trong quá trình kiểm tra đối nghịch (Lời nhắc 5 Phần 63)."""
    issue_id: str
    issue_type: ReasoningIssueType
    affected_entity_id: str
    message: str
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    mitigation: Optional[str] = None


class ArgumentNode(BaseModel):
    """Nút trong Biểu đồ đối số M4 (Dấu nhắc 5 Phần 40)."""
    node_id: str
    node_type: ArgumentNodeType
    title: str
    statement: str
    entity_ref_id: Optional[str] = None
    ownership: IntellectualOwnership = IntellectualOwnership.OURS
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArgumentEdge(BaseModel):
    """Mối quan hệ có hướng trong biểu đồ đối số M4 (Lời nhắc 5 Phần 40)."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: ArgumentEdgeType
    weight: float = 1.0
    notes: Optional[str] = None


class ArgumentGraph(BaseModel):
    """Hoàn thành biểu diễn đồ thị đối số."""
    graph_id: str
    roadmap_node: Optional[str] = None
    nodes: List[ArgumentNode] = Field(default_factory=list)
    edges: List[ArgumentEdge] = Field(default_factory=list)
    completeness_score: float = 1.0
    is_cyclic: bool = False
    root_claims: List[str] = Field(default_factory=list)


class DiscourseStep(BaseModel):
    """Bước vào Kế hoạch diễn thuyết tu từ (Gợi ý 5 Phần 53, 54)."""
    step_index: int
    function: DiscourseFunction
    subject_entity_ids: List[str] = Field(default_factory=list)
    intent: str
    argument_pattern: ArgumentPatternType = ArgumentPatternType.CLAIM_EVIDENCE_QUALIFICATION


class DiscoursePlan(BaseModel):
    """Sơ đồ trình tự tu từ để đóng gói lập luận (Nhắc 5 Mục 53, 54)."""
    plan_id: str
    roadmap_node: str
    argument_pattern_name: ArgumentPatternType
    steps: List[DiscourseStep] = Field(default_factory=list)
    estimated_paragraphs: int = 3
    notes: Optional[str] = None


class StructuredSynthesis(BaseModel):
    """Kết quả tổng hợp tài liệu có cấu trúc trên nhiều bài báo (Nhắc 5 Phần 12, 14)."""
    synthesis_id: str
    topic: str
    roadmap_node: Optional[str] = None
    consensus: List[str] = Field(default_factory=list)
    agreement_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    disagreements: List[Dict[str, Any]] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    methodological_differences: List[str] = Field(default_factory=list)
    dataset_differences: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    implications_for_our_research: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)


class VerificationRequest(BaseModel):
    """Giao diện Yêu cầu xác minh chính thức cho Chuỗi công cụ Nhắc 6 (Nhắc 5 Phần 102, 103)."""
    request_id: str
    request_type: VerificationRequestType
    target_claim_id: Optional[str] = None
    target_equation_id: Optional[str] = None
    target_table_or_figure_id: Optional[str] = None
    description: str
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    status: VerificationRequestStatus = VerificationRequestStatus.PENDING
    verification_result: Optional[Dict[str, Any]] = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class ResearchActionPriority(BaseModel):
    """Hành động nghiên cứu tiếp theo được xếp hạng thu thập thông tin (Nhắc 5 Mục 106, 107)."""
    action_id: str
    priority: ResearchPriorityLevel
    title: str
    rationale: str
    action_type: str  # RUN_EXPERIMENT, SEARCH_LITERATURE, AUDIT_SHORTCUT, VERIFY_EQUATION, RESOLVE_GAP
    related_rq_id: Optional[str] = None
    related_hyp_id: Optional[str] = None
    related_gap_id: Optional[str] = None


class ArgumentBundle(BaseModel):
    """Cần phải hoàn thành Cấu trúc Đối số Chuyển tiếp trước khi soạn chương (Nhắc 5 Phần 56, 57)."""
    bundle_id: str
    roadmap_node: str
    objective: str
    research_questions: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    contradicting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[AssumptionRecord] = Field(default_factory=list)
    counterarguments: List[CounterargumentRecord] = Field(default_factory=list)
    candidate_inferences: List[InferenceRecord] = Field(default_factory=list)
    falsification_plans: List[FalsificationPlan] = Field(default_factory=list)
    ownership_summary: Dict[str, str] = Field(default_factory=dict)
    uncertainty: str = "Low to moderate remaining variance."
    open_questions: List[str] = Field(default_factory=list)
    discourse_plan: Optional[DiscoursePlan] = None
    readiness_state: ArgumentReadinessState = ArgumentReadinessState.DRAFT
    issues: List[ReasoningIssue] = Field(default_factory=list)
    verification_requests: List[VerificationRequest] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
