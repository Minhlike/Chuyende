"""
Dataset and DatasetVersion Schemas (Section 8, Section 15, RC-10, RC-16)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import VerificationStatus
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class DatasetSplitManifest(BaseModel):
    """Manifest describing train/val/test data split and indices/hashes."""
    split_id: str = Field(description="e.g. SPL-000001")
    train_hash: str
    val_hash: str
    test_hash: str
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    random_seed: int = 42
    temporal_split: bool = True
    split_notes: Optional[str] = None


class DatasetVersion(BaseModel):
    """Specific immutable version/snapshot of a log dataset (RC-16)."""
    version_id: str = Field(description="Stable ID: DSV-000001")
    dataset_id: str = Field(description="Parent Dataset ID: DATA-000001")
    version_tag: str = "v1.0"
    raw_file_rel_path: str = Field(description="Relative path inside datasets/raw/")
    raw_sha256: str = Field(description="SHA-256 hash of immutable raw log data (RC-16)")
    processed_rel_path: Optional[str] = None
    processed_sha256: Optional[str] = None
    total_records: int = Field(ge=0)
    normal_records: Optional[int] = Field(default=None, ge=0)
    attack_records: Optional[int] = Field(default=None, ge=0)
    split_manifest: Optional[DatasetSplitManifest] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Dataset(BaseModel):
    """Canonical Dataset Entity for Log Feature Extraction (RC-10, RC-16)."""
    dataset_id: str = Field(description="Stable ID: DATA-000001")
    name: str = Field(min_length=2, description="e.g. BGL, HDFS, Thunderbird, CIC-IDS2017")
    modality: str = Field(description="e.g. 'Unstructured syslog', 'Structured JSON audit', 'Flow logs'")
    description: str
    source_url: Optional[str] = None
    license: Optional[str] = None
    versions: List[DatasetVersion] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
