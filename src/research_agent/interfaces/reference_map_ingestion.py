"""
Reference and Ownership Map Ingestion Interface (Section 22, Prompt 3 Target)
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import IntellectualOwnership
from research_agent.core.exceptions import InvariantViolationError
from research_agent.storage.repository import ResearchRepository


class ReferenceMappingEntry(BaseModel):
    """Mapping between a research roadmap node and its literature / ownership provenance."""
    node_id: str = Field(description="Target Roadmap Node ID: NOD-xxxxxx")
    ownership: IntellectualOwnership = Field(description="SOURCE, ADAPTED, OURS, BASELINE")
    source_ids: List[str] = Field(default_factory=list, description="Associated external SRC-xxxxxx IDs")
    expected_evidence: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ReferenceMapSpecification(BaseModel):
    """Canonical Reference Map Specification."""
    map_id: str = "REF-000001"
    version: str = "1.0.0"
    title: str
    entries: List[ReferenceMappingEntry] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReferenceMapIngestionService:
    """Service to ingest and validate the Reference & Ownership Map in Prompt 3."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def ingest_reference_map(self, spec: ReferenceMapSpecification) -> ReferenceMapSpecification:
        """Validate ownership rules and persist reference map entries."""
        for entry in spec.entries:
            # If ownership is SOURCE or ADAPTED or BASELINE, source_ids must not be empty
            if entry.ownership in (IntellectualOwnership.SOURCE, IntellectualOwnership.ADAPTED, IntellectualOwnership.BASELINE):
                if not entry.source_ids:
                    raise InvariantViolationError(
                        f"Reference mapping for node '{entry.node_id}' with ownership '{entry.ownership}' "
                        "must specify at least one external source_id (RC-06)."
                    )
        return spec
