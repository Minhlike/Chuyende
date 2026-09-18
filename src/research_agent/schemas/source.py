"""
Lược đồ nguồn, SourceVersion và SourceArtifact (RC-01, RC-16, Prompt 3)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import (
    VerificationStatus,
    SourceVerificationState,
    SourceRole,
    SourceQualityTier,
)
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class SourceArtifact(BaseModel):
    """Tệp vật lý hoặc kỹ thuật số tương ứng với một nguồn (PDF, TXT, BibTeX)."""
    artifact_id: str = Field(description="Stable ID: SRA-000001")
    source_id: str = Field(description="Parent Source ID: SRC-000001")
    file_path: str = Field(description="Relative path inside sources/ directory")
    sha256_hash: str = Field(description="Cryptographic SHA-256 of the artifact")
    file_size_bytes: int = Field(ge=0)
    mime_type: str = "application/pdf"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SourceVersion(BaseModel):
    """Bản sửa đổi hoặc ấn bản cụ thể của nguồn bên ngoài."""
    version_id: str = Field(description="Stable ID: SRV-000001")
    source_id: str = Field(description="Parent Source ID: SRC-000001")
    version_label: str = "1.0"
    publication_date: Optional[str] = None
    changelog_or_edition: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Source(BaseModel):
    """Bản ghi nguồn thư mục chuẩn (RC-01, Phần 8). Không có nguồn bịa đặt."""
    source_id: str = Field(description="Stable ID: SRC-000001")
    citation_key: str = Field(description="Stable human citation key e.g. 'Arp2022DosDonts'")
    title: str = Field(min_length=3)
    authors: List[str] = Field(min_length=1)
    year: int = Field(ge=1900, le=2100)
    venue: str = Field(min_length=1, description="Conference, journal, or official standard/owner")
    source_type: SourceQualityTier = Field(default=SourceQualityTier.PEER_REVIEWED)
    roles: List[SourceRole] = Field(default_factory=list)
    doi: Optional[str] = None
    publisher: Optional[str] = None
    canonical_url: Optional[str] = None
    access_url: Optional[str] = None
    access_date: Optional[str] = None
    bibtex: Optional[str] = None
    bibliographic_verification_state: SourceVerificationState = Field(default=SourceVerificationState.METADATA_VERIFIED)
    content_verification_state: SourceVerificationState = Field(default=SourceVerificationState.CONTENT_VERIFIED)
    verification_status: VerificationStatus = Field(default=VerificationStatus.VERIFIED)
    verification_method: str = "OFFICIAL_PUBLISHER_OR_CROSSREF"
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    license_or_access_notes: Optional[str] = None
    retraction_status: Optional[str] = None
    relevant_roadmap_nodes: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    sha256_hash: Optional[str] = None
    artifacts: List[SourceArtifact] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
