"""
Intellectual Ownership & Candidate Contribution Schemas (Section 4, 5, 15, 16, 17)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from research_agent.core.enums import (
    IntellectualOwnership,
    NoveltyStatus,
    VerificationStatus,
)


class OwnershipMapping(BaseModel):
    """Explicit fine-grained ownership mapping for a roadmap node, component, or claim."""
    mapping_id: str = Field(description="Stable ID e.g. 'OWN-000001'")
    node_code: str = Field(description="Roadmap canonical code e.g. '1.1.1', '2.4.3'")
    node_id: Optional[str] = None
    claim_id: Optional[str] = None
    component_name: str = Field(description="Subcomponent or topic name within the node")
    ownership: IntellectualOwnership = Field(description="SOURCE, ADAPTED, OURS, or BASELINE")
    source_ids: List[str] = Field(default_factory=list, description="Primary external source IDs if SOURCE or BASELINE")
    motivation_source_ids: List[str] = Field(default_factory=list, description="Literature motivation source IDs if OURS or ADAPTED")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateContribution(BaseModel):
    """Canonical Candidate Contribution in Contribution Registry (Section 16, 17, 28)."""
    contribution_id: str = Field(description="Stable ID e.g. 'CAND-01'.. 'CAND-15'")
    name: str
    description: str
    roadmap_nodes: List[str] = Field(min_length=1, description="Associated roadmap section codes e.g. ['1.1.3.1', '2.1.1']")
    ownership: IntellectualOwnership = Field(default=IntellectualOwnership.OURS)
    novelty_status: NoveltyStatus = Field(default=NoveltyStatus.CANDIDATE, description="Lifecycle: CANDIDATE, PRIOR_ART_SEARCHED, etc. (Section 17)")
    literature_motivation: List[str] = Field(default_factory=list, description="Literature papers that motivate this contribution")
    nearest_prior_work: List[str] = Field(default_factory=list, description="Closest existing approaches/baselines")
    differentiation_notes: str = Field(description="Specific technical and operational distinctions from prior art")
    verification_status: VerificationStatus = Field(default=VerificationStatus.VERIFIED)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
