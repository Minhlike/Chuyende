"""
Evidence Schema (Section 10, RC-01, RC-11, RC-12)
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator
from research_agent.core.enums import VerificationStatus
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class Evidence(BaseModel):
    """Canonical Evidence Unit tied explicitly to a Source."""
    evidence_id: str = Field(description="Stable ID: EVD-000001")
    source_id: str = Field(description="Parent Source ID: SRC-000001")
    source_version_id: Optional[str] = None
    locator: str = Field(min_length=1, description="Exact locator e.g. 'Page 4, Table 2' or 'Sec 3.1'")
    page: Optional[int] = Field(default=None, ge=1)
    section: Optional[str] = None
    exact_quote: Optional[str] = Field(default=None, description="Verbatim text span from source (RC-12)")
    paraphrase: Optional[str] = Field(default=None, description="Faithful paraphrase/summary")
    context_notes: Optional[str] = None
    extraction_method: str = "MANUAL_EXTRACT"
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_content_presence(self) -> "Evidence":
        if not self.exact_quote and not self.paraphrase:
            raise ValueError("Evidence must contain either an exact_quote or a paraphrase.")
        return self
