"""
Scientific Verification Schemas & Contracts (Prompt 6, RC-08, RC-09, RC-10, RC-14, RC-16, RC-18)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, model_validator

from research_agent.core.enums import (
    VerificationStatus,
    VerificationRequestType,
    VerificationRequestStatus,
    SymbolicEqualityState,
    NumericalClaimType,
    TableType,
    FigureType,
    ReproducibilityLevel,
    AllowedWordingStrength,
    MetricGranularity,
    ProtocolLockState,
    UnitOfMeasurement,
    TransformationOp,
    IntellectualOwnership,
    EquationType,
)


class ScopedSymbol(BaseModel):
    """Canonical mathematical symbol definition with explicit scope (Prompt 6 Section 10)."""
    symbol_id: str = Field(description="Stable ID: SYM-000001")
    symbol_latex: str = Field(description="LaTeX string, e.g. '\\mathbf{z}_t', '\\lambda_1'")
    equation_id: Optional[str] = Field(default=None, description="Associated Equation ID or namespace")
    name: str = Field(description="Human readable name")
    symbol_type: str = Field(default="VARIABLE", description="VARIABLE, PARAMETER, HYPERPARAMETER, OPERATOR, CONSTANT")
    shape_or_dimension: Optional[str] = Field(default=None, description="e.g. 'R^d', 'R^{N x d}', 'Scalar'")
    unit: Optional[str] = Field(default=None, description="e.g. 'ms', 'dimensionless'")
    domain: Optional[str] = Field(default=None, description="e.g. 'Continuous latent space', '[0, 1]'")
    assumptions: List[str] = Field(default_factory=list)
    source_citation: Optional[str] = Field(default=None, description="Source where symbol was defined")
    ambiguity_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TransformationStep(BaseModel):
    """Single structured derivation operation step (Prompt 6 Section 11)."""
    step_index: int = Field(ge=1)
    operation: TransformationOp = Field(description="Structured algebraic operation")
    input_expression: str = Field(description="Starting expression in LaTeX / SymPy")
    output_expression: str = Field(description="Resulting expression in LaTeX / SymPy")
    rationale: str = Field(description="Mathematical explanation of the transformation")
    approximation_assumptions: List[str] = Field(default_factory=list)
    error_bound: Optional[str] = None


class NumericalClaim(BaseModel):
    """Explicitly verified numerical claim (Prompt 6 Section 50)."""
    numerical_claim_id: str = Field(description="Stable ID: NUM-000001")
    statement: str = Field(description="Factual claim containing the quantity")
    quantity_name: str = Field(description="e.g. 'Recall@0.1%FPR', 'Inference Latency'")
    raw_value: float = Field(description="Full precision machine value")
    display_value: str = Field(description="Formatted presentation string, e.g. '98.4%'")
    unit: str = Field(default="dimensionless", description="Unit of measurement")
    uncertainty: Optional[str] = Field(default=None, description="e.g. '±0.3% (95% CI)'")
    source_type: NumericalClaimType = Field(description="SOURCE_REPORTED, RECOMPUTED, EXPERIMENT_RESULT, DERIVED, ESTIMATE")
    source_id: Optional[str] = Field(default=None, description="Source ID if SOURCE_REPORTED")
    source_locator: Optional[str] = Field(default=None, description="Page / Table / Figure locator")
    computation_id: Optional[str] = Field(default=None, description="ExperimentRun or StatisticalResult ID")
    metric_name: Optional[str] = None
    granularity: Optional[MetricGranularity] = MetricGranularity.EVENT
    scope_dataset: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    related_claim_id: Optional[str] = None
    is_estimate: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricDefinition(BaseModel):
    """Standardized Metric Definition with explicit granularity (Prompt 6 Section 28, 29)."""
    metric_id: str = Field(description="Stable ID: MET-000001")
    name: str = Field(description="e.g. 'Recall@Fixed_FPR', 'P95_Latency'")
    formula_latex: str = Field(description="Mathematical formula")
    unit: str = Field(default="dimensionless")
    aggregation: str = Field(default="MEAN", description="MEAN, MEDIAN, MACRO_AVG, MICRO_AVG, P95")
    granularity: MetricGranularity = Field(default=MetricGranularity.EVENT)
    positive_class: Optional[str] = Field(default="ATTACK / ANOMALY")
    interpolation_method: Optional[str] = Field(default="LINEAR", description="For ROC/PR AUC curves")
    assumptions: List[str] = Field(default_factory=list)
    version: str = "v1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConfusionMatrixRecord(BaseModel):
    """Deterministic confusion matrix metrics (Prompt 6 Section 31)."""
    matrix_id: str = Field(description="Stable ID: CMX-000001")
    tp: int = Field(ge=0)
    fp: int = Field(ge=0)
    tn: int = Field(ge=0)
    fn: int = Field(ge=0)
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    f1: float = Field(ge=0.0, le=1.0)
    fpr: float = Field(ge=0.0, le=1.0)
    total_samples: int = Field(ge=0)
    threshold: Optional[float] = None
    granularity: MetricGranularity = MetricGranularity.EVENT
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatisticalResult(BaseModel):
    """Computed statistical analysis result (Prompt 6 Section 34..43)."""
    stat_id: str = Field(description="Stable ID: STAT-000001")
    question: str = Field(description="Empirical or comparative question tested")
    test_name: str = Field(description="e.g. 'Paired t-test', 'Wilcoxon signed-rank', 'Bootstrap CI'")
    sample_unit: str = Field(description="Mandatory unit of analysis (e.g. 'Session', 'Run Seed', 'Host')")
    sample_size_n: int = Field(ge=1)
    statistic_value: Optional[float] = None
    p_value: Optional[float] = None
    effect_size_name: Optional[str] = Field(default=None, description="e.g. 'Cohen\\'s d', 'Relative Difference'")
    effect_size_value: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    ci_level: float = Field(default=0.95, ge=0.5, le=0.999)
    bootstrap_resamples: Optional[int] = None
    random_seed: Optional[int] = None
    assumptions_met: bool = True
    assumptions_evaluated: List[str] = Field(default_factory=list)
    is_significant: Optional[bool] = None
    multiple_comparisons_context: Optional[str] = None
    interpretation_notes: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetManifest(BaseModel):
    """Cryptographic file manifest for a dataset version (Prompt 6 Section 21)."""
    manifest_id: str = Field(description="Stable ID: MAN-000001")
    dataset_version_id: str
    files: List[Dict[str, Any]] = Field(default_factory=list, description="List of {rel_path, sha256, size_bytes}")
    total_files: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    total_events: int = Field(ge=0)
    manifest_sha256: str = Field(description="SHA-256 of the combined manifest content")
    schema_fields: List[str] = Field(default_factory=list)
    timestamp_start: Optional[str] = None
    timestamp_end: Optional[str] = None
    label_field: Optional[str] = None
    entity_fields: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataProfile(BaseModel):
    """Deterministic profile summary computed on dataset (Prompt 6 Section 23)."""
    profile_id: str = Field(description="Stable ID: DPF-000001")
    dataset_version_id: str
    total_events: int = Field(ge=0)
    total_entities: int = Field(ge=0)
    label_counts: Dict[str, int] = Field(default_factory=dict)
    class_ratios: Dict[str, float] = Field(default_factory=dict)
    missing_rates: Dict[str, float] = Field(default_factory=dict)
    template_count: Optional[int] = None
    host_count: Optional[int] = None
    timestamp_range: Optional[str] = None
    script_path: str = Field(description="Script that computed this profile")
    code_commit_hash: str
    profile_sha256: str = Field(description="SHA-256 hash of the generated profile")
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PreprocessingTransformation(BaseModel):
    """Lineage tracking of data transformations (Prompt 6 Section 26)."""
    transformation_id: str = Field(description="Stable ID: TRF-000001")
    input_dataset_version_id: str
    output_dataset_version_id: str
    transformation_type: str = Field(description="CLEANING, NORMALIZATION, PARSING, TEMPLATE_MASKING, PERTURBATION")
    script_path: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    fitted_on_subset: str = Field(default="TRAIN_ONLY", description="TRAIN_ONLY, FULL_DATASET (flagged)")
    execution_time_sec: float = Field(ge=0.0)
    code_commit_hash: str
    output_sha256: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProtocolDeviationRecord(BaseModel):
    """Formal audit record of post-registration protocol changes (Prompt 6 Section 84)."""
    deviation_id: str = Field(description="Stable ID: DEV-000001")
    experiment_id: str
    original_protocol: str
    deviated_protocol: str
    reason: str
    timing: str = Field(description="BEFORE_RESULTS, AFTER_RESULTS (flagged)")
    impact_assessment: str
    approved_by: str = "RESEARCH_ARCHITECT"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TableSpecification(BaseModel):
    """Deterministic scientific table specification and output (Prompt 6 Section 53..56)."""
    table_id: str = Field(description="Stable ID: TBL-000001")
    table_type: TableType = TableType.COMPUTED_TABLE
    title: str = Field(min_length=3)
    caption: str
    columns: List[str] = Field(min_length=1)
    rows_data: List[List[Any]] = Field(default_factory=list)
    cell_provenance: Dict[str, str] = Field(default_factory=dict, description="row_col key to Source or Run ID")
    is_directly_comparable: bool = True
    incomparability_reason: Optional[str] = None
    output_csv: Optional[str] = None
    output_markdown: Optional[str] = None
    output_latex: Optional[str] = None
    output_sha256: str = Field(min_length=8)
    dataset_ids: List[str] = Field(default_factory=list)
    experiment_run_ids: List[str] = Field(default_factory=list)
    generation_script: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FigureSpecification(BaseModel):
    """Deterministic scientific figure specification and companion data (Prompt 6 Section 57..62)."""
    figure_id: str = Field(description="Stable ID: FIG-000001")
    figure_type: FigureType = FigureType.LINE_PLOT
    title: str = Field(min_length=3)
    caption: str
    plot_script_path: str = Field(description="Path to python plotting script")
    output_file_rel_path: str = Field(description="Path to SVG/PNG artifact")
    companion_data_csv_rel_path: str = Field(description="Companion figure-data.csv path")
    dataset_ids: List[str] = Field(default_factory=list)
    source_result_ids: List[str] = Field(default_factory=list)
    uncertainty_represented: str = Field(default="NONE", description="CI_95, ERROR_BARS_SD, BOX_PLOT, NONE")
    manually_edited: bool = False
    manual_edit_reason: Optional[str] = None
    output_sha256: str = Field(min_length=8)
    companion_data_sha256: str = Field(min_length=8)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerificationResult(BaseModel):
    """Full execution outcome returned to Prompt 5 Reasoning Engine (Prompt 6 Section 99)."""
    result_id: str = Field(description="Stable ID: VRS-000001")
    request_id: str = Field(description="Target VerificationRequest ID")
    status: VerificationRequestStatus = Field(description="PASS, FAIL, INCONCLUSIVE, BLOCKED")
    verified_artifact_ids: List[str] = Field(default_factory=list)
    computed_result: Dict[str, Any] = Field(default_factory=dict)
    method_used: str = Field(description="Deterministic method or tool executed")
    provenance_trail: List[str] = Field(default_factory=list)
    assumptions_applied: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    reproducibility_level: ReproducibilityLevel = ReproducibilityLevel.LEVEL_2_METRIC
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResultBundle(BaseModel):
    """Packaged verified experimental outcome for thesis composition (Prompt 6 Section 98)."""
    bundle_id: str = Field(description="Stable ID: RSB-000001")
    roadmap_node_code: str = Field(description="e.g. 'CH3.SEC2'")
    rq_id: str = Field(description="RQ1..RQ5")
    hyp_id: str = Field(description="H1..H5")
    experiment_run_ids: List[str] = Field(default_factory=list)
    verified_metrics: Dict[str, float] = Field(default_factory=dict)
    numerical_claims: List[NumericalClaim] = Field(default_factory=list)
    statistical_results: List[StatisticalResult] = Field(default_factory=list)
    table_ids: List[str] = Field(default_factory=list)
    figure_ids: List[str] = Field(default_factory=list)
    data_provenance_summary: str = Field(description="Summary of dataset versions and splits used")
    limitations: List[str] = Field(default_factory=list)
    comparability_constraints: List[str] = Field(default_factory=list)
    invalidated_run_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerifiedClaimBundle(BaseModel):
    """Guarded claim package for Prompt 7 Chapter Composer (Prompt 6 Section 138)."""
    claim_id: str = Field(description="CLM-000001")
    statement: str = Field(description="Normalized claim statement")
    ownership: IntellectualOwnership = IntellectualOwnership.OURS
    source_evidence_ids: List[str] = Field(default_factory=list)
    numerical_claims: List[NumericalClaim] = Field(default_factory=list)
    equation_ids: List[str] = Field(default_factory=list)
    result_bundle_id: Optional[str] = None
    uncertainty_description: Optional[str] = None
    allowed_wording_strength: AllowedWordingStrength = AllowedWordingStrength.SUPPORTIVE
    citation_keys: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
