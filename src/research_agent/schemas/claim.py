"""
Khiếu nại và Lược đồ quan hệ yêu cầu bồi thường (RC-04, RC-05, RC-06, RC-07, RC-02)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
    ArgumentRelationType,
)
from research_agent.core.exceptions import ProvenanceError


class Claim(BaseModel):
    """Thực thể yêu cầu nguyên tử chuẩn (RC-04..RC-07)."""
    claim_id: str = Field(description="Stable ID: CLM-000001")
    statement: str = Field(min_length=5, description="Unambiguous atomic proposition")
    claim_type: ClaimType = Field(description="Taxonomy: SOURCE_FACT, OUR_DESIGN, etc. (RC-05)")
    ownership: IntellectualOwnership = Field(description="Ownership: SOURCE, ADAPTED, OURS, BASELINE (RC-06)")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.UNVERIFIED, description="Status matrix (RC-07)")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    assumptions: List[str] = Field(default_factory=list)
    scope: Optional[str] = Field(default=None, description="Boundary conditions and dataset contexts")
    evidence_ids: List[str] = Field(default_factory=list, description="Explicit EVD-xxxxxx bindings")
    experiment_run_id: Optional[str] = Field(default=None, description="Required for EXPERIMENT_RESULT claims (RC-02)")
    falsification_conditions: Optional[str] = Field(default=None)
    version: int = Field(default=1, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_invariants(self) -> "Claim":
        # RC-02 / TEST 4 Bất biến: EXPERIMENT_RESULT xác nhận liên kết MUST tới một ExperimentRun
        if self.claim_type == ClaimType.EXPERIMENT_RESULT:
            if not self.experiment_run_id or not self.experiment_run_id.strip():
                raise ProvenanceError(
                    rule_id="RC-02",
                    message=f"Claim '{self.claim_id}' of type EXPERIMENT_RESULT must specify a valid experiment_run_id."
                )

        # Bất biến: SOURCE_FACT hoặc SOURCE_CLAIM không được có quyền sở hữu OURS
        if self.claim_type in (ClaimType.SOURCE_FACT, ClaimType.SOURCE_CLAIM) and self.ownership == IntellectualOwnership.OURS:
            raise ValueError(f"Claim '{self.claim_id}' with type {self.claim_type} cannot have ownership OURS (RC-06).")

        return self


class ClaimRelation(BaseModel):
    """Mối quan hệ logic có định hướng rõ ràng giữa hai yêu cầu."""
    relation_id: str = Field(description="Stable ID: ARE-000001 or relation UUID")
    source_claim_id: str = Field(description="Subject Claim ID")
    target_claim_id: str = Field(description="Object Claim ID")
    relation_type: ArgumentRelationType = Field(description="SUPPORTS, CONTRADICTS, QUALIFIES, etc.")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
