"""
Canonical Research Roadmap, Execution Graph, Axes, RQs, Hypotheses, and Contracts (Prompt 2)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class ResearchQuestion(BaseModel):
    """Canonical Research Question (RQ1..RQ5)."""
    rq_id: str = Field(description="Stable ID: RQ-000001..RQ-000005")
    code: str = Field(description="Human label e.g., 'RQ1', 'RQ2'")
    title: str = Field(description="Short title e.g., 'REPRESENTATION FIDELITY'")
    canonical_wording_en: str = Field(default="", description="Exact canonical wording in English")
    canonical_wording_vi: str = Field(default="", description="Exact canonical intent in Vietnamese")
    target_representation_aspect: str = Field(default="", description="Aspect of feature representation z addressed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Hypothesis(BaseModel):
    """Canonical Scientific Hypothesis (H1..H5)."""
    hyp_id: str = Field(description="Stable ID: HYP-000001..HYP-000005")
    code: str = Field(description="Human label e.g., 'H1', 'H2'")
    rq_id: str = Field(description="Associated Research Question ID")
    title: str = Field(default="", description="Hypothesis title e.g., 'FIDELITY'")
    statement: str = Field(description="Exact canonical hypothesis statement")
    falsification_criteria: str = Field(description="Explicit falsification criteria")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchAxis(BaseModel):
    """One of the five core Research Axes (A1..A5) modeling orthogonal research dimensions."""
    axis_id: str = Field(description="e.g. 'AXIS-A1'")
    code: str = Field(description="e.g. 'A1'")
    name: str = Field(description="e.g. 'REPRESENTATION FIDELITY'")
    problem_summary: str
    path_nodes: List[str] = Field(description="Ordered roadmap node codes e.g. ['1.3.1', '2.2.1', '2.3', '3.2.1', '3.3.1']")
    core_question: str
    core_risks: List[str] = Field(default_factory=list)


class RepresentationContractCategory(BaseModel):
    """Items within one category of the Representation Contract (Preserve / Invariant / Exclude)."""
    category: str = Field(description="'PRESERVE', 'INVARIANT', or 'EXCLUDE'")
    items: List[str] = Field(description="List of specific constraints / properties")


class RepresentationContract(BaseModel):
    """Canonical Three-Tier Representation Contract (Section 8)."""
    preserve: List[str] = Field(description="temporal order, security-relevant parameters, entity linkage, dependency context")
    invariant: List[str] = Field(description="benign formatting changes, template renaming, non-semantic identifiers")
    exclude: List[str] = Field(description="dataset IDs, campaign IDs, split-specific identifiers, leakage-derived info, shortcuts")


class NegativeControl(BaseModel):
    """Methodological Negative Control Requirement (Section 16)."""
    control_id: str = Field(description="e.g. 'CTRL-LEAK-001'")
    category: str = Field(description="e.g. 'LEAKAGE', 'SHORTCUT', 'PROBE', 'PRIVACY'")
    name: str
    description: str
    target_nodes: List[str] = Field(default_factory=list)


class ResearchBoundary(BaseModel):
    """Explicit Epistemic and Methodological Claim Boundary (Section 17)."""
    boundary_id: str = Field(description="e.g. 'BOUNDARY-01'")
    title: str
    statement: str
    rationale: str
    affected_sections: List[str] = Field(default_factory=list)


class DefensibilityQuestion(BaseModel):
    """One of the Ten Defensibility Questions (Section 12, DQ-01..DQ-10)."""
    question_id: str = Field(description="e.g. 'DQ-01'")
    question_text: str
    target_audit_scope: str


class TraceabilityEntry(BaseModel):
    """Machine-readable traceability entry linking RQ, Hypotheses, Gaps, Mechanisms, and Evaluations."""
    rq_id: str
    code: str
    chapter1_gap_nodes: List[str] = Field(default_factory=list)
    chapter2_mechanism_nodes: List[str] = Field(default_factory=list)
    chapter3_evaluation_nodes: List[str] = Field(default_factory=list)
    hypothesis_ids: List[str] = Field(default_factory=list)
    controls: List[str] = Field(default_factory=list)


class ResearchNode(BaseModel):
    """Hierarchical node in Research Roadmap (Chapter / Section / Subsection / Topic)."""
    node_id: str = Field(description="Stable ID: NOD-000001")
    parent_node_id: Optional[str] = None
    level: int = Field(ge=1, le=5, description="1=Chapter, 2=Section, 3=Subsection, 4=Paragraph/Topic, 5=Subtopic")
    order_index: int = Field(ge=0, description="Strict ordering within parent")
    code: str = Field(description="Canonical section code e.g. '1.0', '1.1', '2.3.1'")
    title: str = Field(description="Exact canonical title")
    canonical_text: Optional[str] = Field(default=None, description="Exact canonical body / notes from roadmap specification")
    expected_role: str = Field(default="SPECIFICATION", description="BACKGROUND, PROBLEM_DEFINITION, GAP, METHOD, MECHANISM, EXPERIMENT, EVALUATION, VALIDITY, APPLICATION, LIMITATION")
    research_axes: List[str] = Field(default_factory=list, description="Associated Research Axes e.g. ['A1', 'A3']")
    methodological_constraints: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    rq_ids: List[str] = Field(default_factory=list)
    hyp_ids: List[str] = Field(default_factory=list)
    status: str = Field(default="SPECIFIED", description="Current node progress status: SPECIFIED, SOURCED, etc.")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchRoadmap(BaseModel):
    """Canonical Versioned Research Specification Roadmap (Prompt 2 target)."""
    roadmap_id: str = Field(default_factory=lambda: format_stable_id(EntityPrefix.ROADMAP, 1))
    version: str = "1.0.0"
    title: str = "Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công"
    summary: str = "Canonical 3-Chapter Research Roadmap and Execution Graph for feature representation z."
    central_object: str = "feature representation z (f_theta: L_{1:t} -> z_t)"
    sha256_hash: Optional[str] = None
    nodes: List[ResearchNode] = Field(default_factory=list)
    questions: List[ResearchQuestion] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    axes: List[ResearchAxis] = Field(default_factory=list)
    representation_contract: Optional[RepresentationContract] = None
    controls: List[NegativeControl] = Field(default_factory=list)
    boundaries: List[ResearchBoundary] = Field(default_factory=list)
    defensibility_questions: List[DefensibilityQuestion] = Field(default_factory=list)
    traceability_matrix: List[TraceabilityEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
