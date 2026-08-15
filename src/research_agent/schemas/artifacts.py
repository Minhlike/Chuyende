"""
Table and Figure Provenance Schemas (Section 13, RC-09)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from research_agent.core.enums import VerificationStatus
from research_agent.core.exceptions import ProvenanceError


class TableArtifact(BaseModel):
    """Canonical Table with verifiable cryptographic and computation lineage (RC-09)."""
    table_id: str = Field(description="Stable ID: TBL-000001")
    title: str = Field(min_length=3)
    caption: str
    content: str = Field(description="Markdown or LaTeX tabular string")
    is_numerical_result: bool = Field(default=True, description="True if contains empirical scores")
    dataset_id: Optional[str] = Field(default=None, description="Source dataset ID (RC-09)")
    experiment_run_ids: List[str] = Field(default_factory=list, description="Associated RUN-xxxxxx IDs")
    generation_script: Optional[str] = Field(default=None, description="Script generating the table")
    script_git_hash: Optional[str] = None
    input_hashes: List[str] = Field(default_factory=list)
    output_sha256: str = Field(min_length=8, description="SHA-256 hash of table content")
    is_synthetic_data: bool = False
    is_manually_edited: bool = False
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_numerical_provenance(self) -> "TableArtifact":
        if self.is_numerical_result:
            if not self.dataset_id or not self.experiment_run_ids:
                raise ProvenanceError(
                    rule_id="RC-09",
                    message=(
                        f"Table '{self.table_id}' contains numerical experiment output but lacks "
                        "mandatory dataset_id or experiment_run_ids provenance."
                    )
                )
        return self


class FigureArtifact(BaseModel):
    """Canonical Visual Figure with strict code and dataset lineage (RC-09)."""
    figure_id: str = Field(description="Stable ID: FIG-000001")
    title: str = Field(min_length=3)
    caption: str
    file_rel_path: str = Field(description="Path relative to workspace root e.g. artifacts/figures/f1.svg")
    is_numerical_result: bool = Field(default=True, description="True if plot depicts experimental metrics")
    dataset_id: Optional[str] = Field(default=None, description="Source dataset ID (RC-09)")
    experiment_run_ids: List[str] = Field(default_factory=list, description="Associated RUN-xxxxxx IDs")
    generation_script: Optional[str] = Field(default=None, description="Path to plotting python script")
    script_git_hash: Optional[str] = None
    input_hashes: List[str] = Field(default_factory=list)
    output_sha256: str = Field(min_length=8, description="SHA-256 hash of the generated image/vector file")
    is_synthetic_data: bool = False
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_figure_provenance(self) -> "FigureArtifact":
        if self.is_numerical_result:
            if not self.dataset_id or not self.experiment_run_ids:
                raise ProvenanceError(
                    rule_id="RC-09",
                    message=(
                        f"Figure '{self.figure_id}' contains numerical experiment output but lacks "
                        "mandatory dataset_id or experiment_run_ids provenance."
                    )
                )
        return self
