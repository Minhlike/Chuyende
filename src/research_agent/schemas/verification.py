"""
Verification and Integrity Audit Schemas (RC-18)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import VerificationStatus
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class VerificationRecord(BaseModel):
    """Audit record capturing the automated or manual invariant verification result."""
    verification_id: str = Field(description="Stable ID: VRF-000001")
    target_entity_id: str = Field(description="ID of audited Claim, Equation, Run, Figure, Table")
    rule_code: str = Field(description="Constitution rule or invariant e.g. 'RC-01', 'RC-09'")
    status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    passed: bool
    checker_name: str
    details: str
    evidence_trail: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
