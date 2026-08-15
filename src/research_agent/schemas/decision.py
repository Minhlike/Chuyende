"""
Decision and Contradiction Record Schemas (Section 8, Section 23, Section 31, RC-13, RC-15)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import DecisionStatus


class DecisionRecord(BaseModel):
    """Architecture / Research Decision Record (ADR / RDR) (RC-15, Section 23, Section 31)."""
    decision_id: str = Field(description="Stable ID: DEC-000001")
    title: str = Field(min_length=5)
    status: DecisionStatus = Field(default=DecisionStatus.ACCEPTED)
    context: str = Field(min_length=10)
    decision: str = Field(min_length=10)
    rationale: str = Field(min_length=5)
    alternatives_considered: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    consequences: str = Field(min_length=5)
    target_affected_entities: List[str] = Field(default_factory=list)
    related_nodes: List[str] = Field(default_factory=list)
    related_claims: List[str] = Field(default_factory=list)
    related_experiments: List[str] = Field(default_factory=list)
    supersedes_id: Optional[str] = None
    superseded_by_id: Optional[str] = None
    diff_summary: Optional[str] = None
    actor: str = "HUMAN_ARCHITECT_OR_AGENT"
    made_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContradictionRecord(BaseModel):
    """Explicit Contradiction Unit between Conflicting Claims / Evidences (RC-13, Section 15)."""
    contradiction_id: str = Field(description="Stable ID: CTR-000001")
    claim_a_id: str = Field(description="Subject Claim ID")
    claim_b_id: str = Field(description="Conflicting Claim ID")
    description: str = Field(min_length=5)
    domain_or_scope_divergence: Optional[str] = None
    resolution_status: str = Field(default="OPEN", description="OPEN, RESOLVED, SYNTHESIZED_AS_TRADEOFF")
    resolution_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
