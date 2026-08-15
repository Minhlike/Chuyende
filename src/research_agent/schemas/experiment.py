"""
Experiment and ExperimentRun Schemas (Section 14, RC-10, RC-14)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import ExperimentStatus
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class ExperimentArtifact(BaseModel):
    """Output artifact produced by an ExperimentRun."""
    artifact_id: str = Field(description="Stable ID: e.g. SRA-000001 or ART-000001")
    run_id: str = Field(description="Parent Experiment Run ID: RUN-000001")
    file_path: str = Field(description="Relative path within experiments/runs/")
    sha256_hash: str = Field(description="SHA-256 hash of output artifact (RC-10)")
    artifact_type: str = Field(description="e.g. 'METRIC_SUMMARY', 'EMBEDDINGS_NPZ', 'MODEL_CHECKPOINT'")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExperimentRun(BaseModel):
    """Deterministic Execution Run of an Experiment (RC-10, RC-14)."""
    run_id: str = Field(description="Stable ID: RUN-000001")
    experiment_id: str = Field(description="Parent Experiment ID: EXP-000001")
    dataset_id: str = Field(description="DATA-000001")
    dataset_version_id: str = Field(description="DSV-000001")
    split_hash: str = Field(description="SHA-256 hash of the exact split manifest")
    model_parameters: Dict[str, Any] = Field(default_factory=dict, description="Model architecture hyperparameters")
    extractor_config: Dict[str, Any] = Field(default_factory=dict, description="Feature extractor hyperparameters")
    random_seed: int = Field(default=42)
    environment_spec: Dict[str, Any] = Field(default_factory=dict)
    git_commit_hash: str = Field(default="bootstrap-initial", min_length=4)
    command: str = Field(default="python -m research_agent.run", min_length=1)
    status: ExperimentStatus = Field(default=ExperimentStatus.COMPLETED)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    error_message: Optional[str] = Field(default=None, description="Preserved on failure (RC-14)")
    artifacts: List[ExperimentArtifact] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Experiment(BaseModel):
    """Canonical Scientific Experiment Specification."""
    experiment_id: str = Field(description="Stable ID: EXP-000001")
    rq_id: str = Field(description="Target Research Question: RQ-000001")
    hyp_id: str = Field(description="Target Hypothesis: HYP-000001")
    title: str = Field(min_length=5)
    description: str
    target_representation_aspect: str = Field(description="e.g. Robustness to out-of-vocabulary log templates")
    runs: List[ExperimentRun] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
