"""
Reference Map Specification Schema (Prompt 3 Target, Section 48)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.schemas.source import Source, SourceArtifact, SourceVersion
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.claim import Claim, ClaimRelation
from research_agent.schemas.ownership import OwnershipMapping, CandidateContribution
from research_agent.schemas.citation import CitationFirewallRule


class ReferenceMapSpecification(BaseModel):
    """Canonical Versioned Reference & Intellectual Ownership Map Specification."""
    reference_map_id: str = "REF-000001"
    version: str = "1.0.0"
    compatible_roadmap_version: str = "1.0.0"
    title: str = "Canonical Reference, Intellectual Ownership, and Evidence Provenance Map"
    summary: str = "Verified intellectual provenance mappings, claim-evidence linkages, candidate contributions, and citation firewall rules."
    sha256_hash: Optional[str] = None
    sources: List[Source] = Field(default_factory=list)
    evidences: List[Evidence] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    claim_relations: List[ClaimRelation] = Field(default_factory=list)
    ownership_mappings: List[OwnershipMapping] = Field(default_factory=list)
    contributions: List[CandidateContribution] = Field(default_factory=list)
    firewall_rules: List[CitationFirewallRule] = Field(default_factory=list)
    unresolved_references: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
