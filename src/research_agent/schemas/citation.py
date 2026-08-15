"""
Citation Firewall Rule and Verification Schemas (Section 10, Section 34, Prompt 3)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import (
    CitationFirewallStatus,
    SupportType,
)


class CitationFirewallRule(BaseModel):
    """Citation Firewall audit state for a specific citation key (Section 10)."""
    source_id: str = Field(description="Stable Source ID e.g. 'SRC-000001'")
    citation_key: str = Field(description="Stable citation key e.g. 'Arp2022DosDonts'")
    status: CitationFirewallStatus = Field(default=CitationFirewallStatus.BLOCKED)
    source_exists: bool = False
    metadata_verified: bool = False
    claim_evidence_link_exists: bool = False
    locator_exists: bool = False
    support_type: SupportType = SupportType.BACKGROUND
    blocking_reasons: List[str] = Field(default_factory=list)
    audit_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
