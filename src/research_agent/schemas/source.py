"""
Source, SourceVersion, and SourceArtifact Schemas (RC-01, RC-16)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import VerificationStatus
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class SourceArtifact(BaseModel):
    """Physical or digital file corresponding to a source (PDF, TXT, BibTeX)."""
    artifact_id: str = Field(description="Stable ID: SRA-000001")
    source_id: str = Field(description="Parent Source ID: SRC-000001")
    file_path: str = Field(description="Relative path inside sources/ directory")
    sha256_hash: str = Field(description="Cryptographic SHA-256 of the artifact")
    file_size_bytes: int = Field(ge=0)
    mime_type: str = "application/pdf"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SourceVersion(BaseModel):
    """Specific revision or edition of an external source."""
    version_id: str = Field(description="Stable ID: SRV-000001")
    source_id: str = Field(description="Parent Source ID: SRC-000001")
    version_label: str = "1.0"
    publication_date: Optional[str] = None
    changelog_or_edition: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Source(BaseModel):
    """Canonical Bibliographic Source Record (RC-01). No fabricated sources."""
    source_id: str = Field(description="Stable ID: SRC-000001")
    title: str = Field(min_length=3)
    authors: List[str] = Field(min_length=1)
    year: int = Field(ge=1900, le=2100)
    venue: str = Field(min_length=1, description="Conference, journal, or publisher")
    doi: Optional[str] = None
    url: Optional[str] = None
    bibtex: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    verification_method: str = "MANUAL_OR_CROSSREF"
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    artifacts: List[SourceArtifact] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
