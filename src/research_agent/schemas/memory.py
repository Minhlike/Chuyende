"""
Research Memory Hierarchy & Typed Entities (Prompt 4, Tiers M0..M5, ADR-0004, ADR-0008)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import (
    MemoryTier,
    MemoryRecordType,
    MemoryPromotionState,
    IntellectualOwnership,
    EpistemicStatus,
    EpisodeStatus,
    SkillStatus,
    OpenQuestionStatus,
    QueryIntentType,
    PrivacyClassification,
)


class EpisodeRecord(BaseModel):
    """M3 Episodic Research Memory: What happened in research execution (Section 5)."""
    episode_id: str = Field(description="Stable ID: EP-000001")
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str = "RESEARCH_AGENT"
    action: str = Field(description="e.g. 'RUN_EXPERIMENT', 'INGEST_SOURCE', 'EVALUATE_HYPOTHESIS'")
    object_reference: Optional[str] = None
    outcome: str = Field(description="Summary of result e.g. 'State memory exceeded budget'")
    status: EpisodeStatus = Field(default=EpisodeStatus.COMPLETED)
    related_node_code: Optional[str] = None
    related_rq_id: Optional[str] = None
    related_hyp_id: Optional[str] = None
    related_artifact_ids: List[str] = Field(default_factory=list)
    provenance_details: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    is_failure: bool = False
    failure_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OpenQuestion(BaseModel):
    """Persistent Open Research Question (Section 32)."""
    question_id: str = Field(description="Stable ID: OQ-000001")
    question: str = Field(min_length=5)
    related_rq_id: Optional[str] = None
    related_hyp_id: Optional[str] = None
    related_node_code: Optional[str] = None
    why_open: str = Field(description="Rationale for why this is unresolved")
    required_evidence: str = Field(description="What evidence/experiment is required to close this question")
    proposed_experiment: Optional[str] = None
    priority: str = "HIGH"
    status: OpenQuestionStatus = Field(default=OpenQuestionStatus.OPEN)
    resolution_notes: Optional[str] = None
    resolved_by_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LessonLearned(BaseModel):
    """Actionable scientific insight derived from experiment failures / attempts (Section 33)."""
    lesson_id: str = Field(description="Stable ID: LES-000001")
    title: str = Field(min_length=5)
    statement: str = Field(min_length=10)
    originating_episode_id: Optional[str] = None
    experiment_run_id: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    scope: Optional[str] = None
    actionable_recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionRecord(BaseModel):
    """Persistent Research Session Journal and Handoff State (Section 29, 30)."""
    session_id: str = Field(description="Stable ID: SES-000001")
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    objective: str = Field(description="Session primary goal")
    active_roadmap_nodes: List[str] = Field(default_factory=list)
    actions_summary: List[str] = Field(default_factory=list)
    decisions_made: List[str] = Field(default_factory=list)
    files_modified: List[str] = Field(default_factory=list)
    experiments_run: List[str] = Field(default_factory=list)
    sources_added: List[str] = Field(default_factory=list)
    claims_changed: List[str] = Field(default_factory=list)
    unresolved_items: List[str] = Field(default_factory=list)
    handoff_summary: Optional[str] = None
    git_commit_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SkillRecord(BaseModel):
    """M5 Procedural Memory Skill / Protocol / Rubric (Section 35)."""
    skill_id: str = Field(description="Stable ID: SKL-000001")
    name: str = Field(min_length=3)
    version: str = "1.0"
    status: SkillStatus = Field(default=SkillStatus.ACTIVE)
    category: str = Field(description="e.g. 'EVALUATION_PROTOCOL', 'FEATURE_EXTRACTION_RUBRIC'")
    description: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    preconditions: List[str] = Field(default_factory=list)
    invariants: List[str] = Field(default_factory=list)
    verification_procedure: str = Field(description="Methodological checks to verify skill execution")
    file_path: Optional[str] = Field(default=None, description="Path in memory/procedural/")
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StatusTransitionRecord(BaseModel):
    """Historical Status Transition Event preserving non-rewritable timeline (Section 8, Section 9)."""
    transition_id: str = Field(description="Stable ID: STR-000001")
    entity_type: str = Field(description="CLAIM, HYPOTHESIS, DECISION, QUESTION, CONTRIBUTION")
    entity_id: str
    from_status: str
    to_status: str
    cause: str
    evidence_id: Optional[str] = None
    decision_id: Optional[str] = None
    actor: str = "RESEARCH_AGENT"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryRecord(BaseModel):
    """Canonical Persistent Research Memory Record (Tiers M0..M5)."""
    memory_id: str = Field(description="Stable ID: MEM-000001")
    tier: MemoryTier = Field(description="M0_WORKING, M1_SOURCE, M2_SEMANTIC, M3_EPISODIC, M4_ARGUMENT, M5_PROCEDURAL")
    record_type: MemoryRecordType = Field(default=MemoryRecordType.OBSERVATION)
    promotion_state: MemoryPromotionState = Field(default=MemoryPromotionState.CONSOLIDATED)
    topic: str = Field(min_length=2)
    summary: str = Field(min_length=5)
    content: Optional[str] = None
    reference_type: Optional[str] = None  # SOURCE, CLAIM, EVIDENCE, DECISION, EXPERIMENT, EPISODE, HYPOTHESIS, QUESTION
    reference_id: Optional[str] = None
    associated_entity_ids: List[str] = Field(default_factory=list, description="Linked CLM, EVD, EXP, SRC, NOD IDs")
    ownership: IntellectualOwnership = Field(default=IntellectualOwnership.OURS)
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.SUPPORTED)
    is_generated_summary: bool = False
    supersedes_id: Optional[str] = None
    superseded_by_id: Optional[str] = None
    is_stale: bool = False
    review_required: bool = False
    last_verified_at: Optional[datetime] = None
    privacy: PrivacyClassification = Field(default=PrivacyClassification.INTERNAL)
    actor: str = "RESEARCH_AGENT"
    session_id: Optional[str] = None
    confidence_category: str = "HIGH"  # HIGH, MEDIUM, LOW
    confidence_basis: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextBundle(BaseModel):
    """Structured Context Bundle packaging hybrid retrieval results with provenance (Section 26)."""
    query: str
    resolved_intent: QueryIntentType
    canonical_entities: List[Dict[str, Any]] = Field(default_factory=list)
    verified_facts: List[Dict[str, Any]] = Field(default_factory=list)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    contradictory_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    qualifications: List[Dict[str, Any]] = Field(default_factory=list)
    our_inferences: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    experiment_results: List[Dict[str, Any]] = Field(default_factory=list)
    open_questions: List[Dict[str, Any]] = Field(default_factory=list)
    lessons: List[Dict[str, Any]] = Field(default_factory=list)
    provenance_chain: List[Dict[str, Any]] = Field(default_factory=list)
    retrieval_reasons: Dict[str, str] = Field(default_factory=dict)
    token_estimate: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryHealthReport(BaseModel):
    """Audit metric summary for research memory health (Section 54)."""
    total_memory_records: int
    total_episodes: int
    total_decisions: int
    total_failures: int
    total_lessons: int
    total_open_questions: int
    total_contradictions: int
    pending_consolidation: int
    stale_records: int
    orphan_records: int
    broken_references: int
    circular_support_count: int
    derived_index_status: str = "HEALTHY"
    audit_passed: bool = True
    issues: List[str] = Field(default_factory=list)
