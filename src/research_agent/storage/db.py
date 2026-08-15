"""
SQLite Database Schema and Connection Manager (ADR-0001, ADR-0002)
"""

import sqlite3
from pathlib import Path
from typing import Generator
from contextlib import contextmanager
from research_agent.config import WorkspaceConfig, get_default_config


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Stable ID Sequences
CREATE TABLE IF NOT EXISTS id_sequences (
    prefix TEXT PRIMARY KEY,
    current_val INTEGER NOT NULL DEFAULT 0
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    central_object TEXT NOT NULL,
    description TEXT,
    authors_json TEXT NOT NULL,
    constitution_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Roadmaps & Nodes
CREATE TABLE IF NOT EXISTS roadmaps (
    roadmap_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    central_object TEXT,
    sha256_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roadmap_nodes (
    node_id TEXT PRIMARY KEY,
    roadmap_id TEXT NOT NULL,
    parent_node_id TEXT,
    level INTEGER NOT NULL,
    order_index INTEGER NOT NULL,
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    canonical_text TEXT,
    expected_role TEXT DEFAULT 'SPECIFICATION',
    research_axes_json TEXT,
    methodological_constraints_json TEXT,
    expected_outputs_json TEXT,
    rq_ids_json TEXT,
    hyp_ids_json TEXT,
    status TEXT DEFAULT 'SPECIFIED',
    metadata_json TEXT,
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_questions (
    rq_id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    canonical_wording_en TEXT NOT NULL,
    canonical_wording_vi TEXT NOT NULL,
    target_aspect TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hypotheses (
    hyp_id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    rq_id TEXT NOT NULL,
    title TEXT,
    statement TEXT NOT NULL,
    falsification_criteria TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (rq_id) REFERENCES research_questions(rq_id)
);

CREATE TABLE IF NOT EXISTS research_axes (
    axis_id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    problem_summary TEXT NOT NULL,
    path_nodes_json TEXT NOT NULL,
    core_question TEXT NOT NULL,
    core_risks_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS representation_contracts (
    contract_id TEXT PRIMARY KEY,
    preserve_json TEXT NOT NULL,
    invariant_json TEXT NOT NULL,
    exclude_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS negative_controls (
    control_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    target_nodes_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_boundaries (
    boundary_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    statement TEXT NOT NULL,
    rationale TEXT NOT NULL,
    affected_sections_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS defensibility_questions (
    question_id TEXT PRIMARY KEY,
    question_text TEXT NOT NULL,
    target_audit_scope TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS traceability_entries (
    rq_id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    gap_nodes_json TEXT NOT NULL,
    mechanism_nodes_json TEXT NOT NULL,
    evaluation_nodes_json TEXT NOT NULL,
    hypothesis_ids_json TEXT NOT NULL,
    controls_json TEXT NOT NULL,
    FOREIGN KEY (rq_id) REFERENCES research_questions(rq_id)
);

-- Sources
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    citation_key TEXT NOT NULL,
    title TEXT NOT NULL,
    authors_json TEXT NOT NULL,
    year INTEGER NOT NULL,
    venue TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'PEER_REVIEWED',
    roles_json TEXT NOT NULL DEFAULT '[]',
    doi TEXT,
    publisher TEXT,
    canonical_url TEXT,
    access_url TEXT,
    access_date TEXT,
    bibtex TEXT,
    bibliographic_verification_state TEXT NOT NULL DEFAULT 'METADATA_VERIFIED',
    content_verification_state TEXT NOT NULL DEFAULT 'CONTENT_VERIFIED',
    verification_status TEXT NOT NULL,
    verification_method TEXT,
    abstract TEXT,
    keywords_json TEXT,
    license_or_access_notes TEXT,
    retraction_status TEXT,
    relevant_roadmap_nodes_json TEXT DEFAULT '[]',
    notes TEXT,
    sha256_hash TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_artifacts (
    artifact_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
);

-- Evidence
CREATE TABLE IF NOT EXISTS evidences (
    evidence_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_version_id TEXT,
    locator TEXT NOT NULL,
    page INTEGER,
    section TEXT,
    exact_quote TEXT,
    paraphrase TEXT,
    supports_claim_id TEXT,
    support_type TEXT NOT NULL DEFAULT 'DIRECT_SUPPORT',
    strength TEXT NOT NULL DEFAULT 'STRONG',
    caveats TEXT,
    context_notes TEXT,
    extraction_method TEXT,
    verification_status TEXT NOT NULL,
    verified_at TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
);

-- Reference Maps & Intellectual Ownership
CREATE TABLE IF NOT EXISTS reference_maps (
    reference_map_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    compatible_roadmap_version TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    sha256_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ownership_mappings (
    mapping_id TEXT PRIMARY KEY,
    node_code TEXT NOT NULL,
    node_id TEXT,
    claim_id TEXT,
    component_name TEXT NOT NULL,
    ownership TEXT NOT NULL,
    source_ids_json TEXT NOT NULL,
    motivation_source_ids_json TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidate_contributions (
    contribution_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    roadmap_nodes_json TEXT NOT NULL,
    ownership TEXT NOT NULL DEFAULT 'OURS',
    novelty_status TEXT NOT NULL DEFAULT 'CANDIDATE',
    literature_motivation_json TEXT NOT NULL,
    nearest_prior_work_json TEXT NOT NULL,
    differentiation_notes TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citation_firewall_rules (
    source_id TEXT PRIMARY KEY,
    citation_key TEXT NOT NULL,
    status TEXT NOT NULL,
    source_exists INTEGER NOT NULL,
    metadata_verified INTEGER NOT NULL,
    claim_evidence_link_exists INTEGER NOT NULL,
    locator_exists INTEGER NOT NULL,
    support_type TEXT NOT NULL,
    blocking_reasons_json TEXT NOT NULL,
    audit_notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Claims
CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    ownership TEXT NOT NULL,
    epistemic_status TEXT NOT NULL,
    confidence REAL,
    assumptions_json TEXT,
    scope TEXT,
    evidence_ids_json TEXT,
    experiment_run_id TEXT,
    falsification_conditions TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claim_relations (
    relation_id TEXT PRIMARY KEY,
    source_claim_id TEXT NOT NULL,
    target_claim_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_claim_id) REFERENCES claims(claim_id) ON DELETE CASCADE,
    FOREIGN KEY (target_claim_id) REFERENCES claims(claim_id) ON DELETE CASCADE
);

-- Arguments & M4 Argument Graph (Prompt 1 Section 11, Prompt 5 Section 40)
CREATE TABLE IF NOT EXISTS argument_nodes (
    node_id TEXT PRIMARY KEY,
    claim_id TEXT,
    role TEXT,
    node_type TEXT NOT NULL DEFAULT 'CLAIM',
    title TEXT,
    statement TEXT,
    summary TEXT,
    entity_ref_id TEXT,
    ownership TEXT NOT NULL DEFAULT 'OURS',
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS argument_edges (
    edge_id TEXT PRIMARY KEY,
    from_node_id TEXT,
    to_node_id TEXT,
    source_node_id TEXT,
    target_node_id TEXT,
    relation_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    rationale TEXT,
    notes TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

-- Equations & Symbols
CREATE TABLE IF NOT EXISTS equations (
    equation_id TEXT PRIMARY KEY,
    latex TEXT NOT NULL,
    normalized_representation TEXT,
    equation_type TEXT NOT NULL,
    source_id TEXT,
    source_locator TEXT,
    ownership TEXT NOT NULL,
    symbols_json TEXT,
    assumptions_json TEXT,
    derivation_json TEXT,
    verification_status TEXT NOT NULL,
    verification_method TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS symbol_definitions (
    symbol_id TEXT PRIMARY KEY,
    symbol_latex TEXT NOT NULL,
    name TEXT NOT NULL,
    dimension TEXT,
    domain TEXT,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Datasets
CREATE TABLE IF NOT EXISTS datasets (
    dataset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    modality TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    license TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dataset_versions (
    version_id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    version_tag TEXT NOT NULL,
    raw_file_rel_path TEXT NOT NULL,
    raw_sha256 TEXT NOT NULL,
    processed_rel_path TEXT,
    processed_sha256 TEXT,
    total_records INTEGER NOT NULL,
    normal_records INTEGER,
    attack_records INTEGER,
    split_manifest_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id) ON DELETE CASCADE
);

-- Experiments & Runs
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    rq_id TEXT NOT NULL,
    hyp_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    target_representation_aspect TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiment_runs (
    run_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    dataset_version_id TEXT NOT NULL,
    split_hash TEXT NOT NULL,
    model_config_json TEXT,
    extractor_config_json TEXT,
    random_seed INTEGER NOT NULL,
    environment_spec_json TEXT,
    git_commit_hash TEXT NOT NULL,
    command TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    metrics_json TEXT,
    error_message TEXT,
    metadata_json TEXT,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiment_artifacts (
    artifact_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES experiment_runs(run_id) ON DELETE CASCADE
);

-- Tables & Figures
CREATE TABLE IF NOT EXISTS table_artifacts (
    table_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    caption TEXT,
    content TEXT NOT NULL,
    is_numerical_result INTEGER NOT NULL DEFAULT 1,
    dataset_id TEXT,
    experiment_run_ids_json TEXT,
    generation_script TEXT,
    script_git_hash TEXT,
    input_hashes_json TEXT,
    output_sha256 TEXT NOT NULL,
    is_synthetic_data INTEGER NOT NULL DEFAULT 0,
    is_manually_edited INTEGER NOT NULL DEFAULT 0,
    verification_status TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS figure_artifacts (
    figure_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    caption TEXT,
    file_rel_path TEXT NOT NULL,
    is_numerical_result INTEGER NOT NULL DEFAULT 1,
    dataset_id TEXT,
    experiment_run_ids_json TEXT,
    generation_script TEXT,
    script_git_hash TEXT,
    input_hashes_json TEXT,
    output_sha256 TEXT NOT NULL,
    is_synthetic_data INTEGER NOT NULL DEFAULT 0,
    verification_status TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

-- Decisions & Contradictions
CREATE TABLE IF NOT EXISTS decision_records (
    decision_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    context TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    alternatives_considered_json TEXT NOT NULL DEFAULT '[]',
    evidence_ids_json TEXT NOT NULL DEFAULT '[]',
    consequences TEXT NOT NULL,
    target_affected_entities_json TEXT DEFAULT '[]',
    related_nodes_json TEXT DEFAULT '[]',
    related_claims_json TEXT DEFAULT '[]',
    related_experiments_json TEXT DEFAULT '[]',
    supersedes_id TEXT,
    superseded_by_id TEXT,
    diff_summary TEXT,
    actor TEXT NOT NULL DEFAULT 'HUMAN_ARCHITECT_OR_AGENT',
    made_at TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contradiction_records (
    contradiction_id TEXT PRIMARY KEY,
    claim_a_id TEXT NOT NULL,
    claim_b_id TEXT NOT NULL,
    description TEXT NOT NULL,
    domain_or_scope_divergence TEXT,
    resolution_status TEXT NOT NULL,
    resolution_notes TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Memory (M0..M5)
CREATE TABLE IF NOT EXISTS memory_records (
    memory_id TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    record_type TEXT NOT NULL DEFAULT 'OBSERVATION',
    promotion_state TEXT NOT NULL DEFAULT 'CONSOLIDATED',
    topic TEXT NOT NULL,
    summary TEXT NOT NULL,
    content TEXT,
    reference_type TEXT,
    reference_id TEXT,
    associated_entity_ids_json TEXT,
    ownership TEXT NOT NULL DEFAULT 'OURS',
    epistemic_status TEXT NOT NULL DEFAULT 'SUPPORTED',
    is_generated_summary INTEGER NOT NULL DEFAULT 0,
    supersedes_id TEXT,
    superseded_by_id TEXT,
    is_stale INTEGER NOT NULL DEFAULT 0,
    review_required INTEGER NOT NULL DEFAULT 0,
    last_verified_at TEXT,
    privacy TEXT NOT NULL DEFAULT 'INTERNAL',
    actor TEXT NOT NULL DEFAULT 'RESEARCH_AGENT',
    session_id TEXT,
    confidence_category TEXT NOT NULL DEFAULT 'HIGH',
    confidence_basis TEXT,
    tags_json TEXT,
    importance REAL NOT NULL DEFAULT 0.5,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episodes (
    episode_id TEXT PRIMARY KEY,
    session_id TEXT,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    object_reference TEXT,
    outcome TEXT NOT NULL,
    status TEXT NOT NULL,
    related_node_code TEXT,
    related_rq_id TEXT,
    related_hyp_id TEXT,
    related_artifact_ids_json TEXT,
    provenance_details_json TEXT,
    tags_json TEXT,
    is_failure INTEGER NOT NULL DEFAULT 0,
    failure_reason TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS open_questions (
    question_id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    related_rq_id TEXT,
    related_hyp_id TEXT,
    related_node_code TEXT,
    why_open TEXT NOT NULL,
    required_evidence TEXT NOT NULL,
    proposed_experiment TEXT,
    priority TEXT NOT NULL DEFAULT 'HIGH',
    status TEXT NOT NULL DEFAULT 'OPEN',
    resolution_notes TEXT,
    resolved_by_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons_learned (
    lesson_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    statement TEXT NOT NULL,
    originating_episode_id TEXT,
    experiment_run_id TEXT,
    evidence_ids_json TEXT,
    scope TEXT,
    actionable_recommendations_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT,
    objective TEXT NOT NULL,
    active_roadmap_nodes_json TEXT,
    actions_summary_json TEXT,
    decisions_made_json TEXT,
    files_modified_json TEXT,
    experiments_run_json TEXT,
    sources_added_json TEXT,
    claims_changed_json TEXT,
    unresolved_items_json TEXT,
    handoff_summary TEXT,
    git_commit_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    inputs_json TEXT,
    outputs_json TEXT,
    preconditions_json TEXT,
    invariants_json TEXT,
    verification_procedure TEXT NOT NULL,
    file_path TEXT,
    dependencies_json TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS status_transitions (
    transition_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    cause TEXT NOT NULL,
    evidence_id TEXT,
    decision_id TEXT,
    actor TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Verification Audit Log
CREATE TABLE IF NOT EXISTS verification_records (
    verification_id TEXT PRIMARY KEY,
    target_entity_id TEXT NOT NULL,
    rule_code TEXT NOT NULL,
    status TEXT NOT NULL,
    passed INTEGER NOT NULL,
    checker_name TEXT NOT NULL,
    details TEXT NOT NULL,
    evidence_trail_json TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

-- Argument Bundles (Prompt 5 Section 57)
CREATE TABLE IF NOT EXISTS argument_bundles (
    bundle_id TEXT PRIMARY KEY,
    roadmap_node TEXT NOT NULL,
    objective TEXT NOT NULL,
    research_questions_json TEXT,
    hypotheses_json TEXT,
    claims_json TEXT,
    evidence_json TEXT,
    contradicting_evidence_json TEXT,
    assumptions_json TEXT,
    counterarguments_json TEXT,
    candidate_inferences_json TEXT,
    falsification_plans_json TEXT,
    ownership_summary_json TEXT,
    uncertainty TEXT,
    open_questions_json TEXT,
    discourse_plan_json TEXT,
    readiness_state TEXT NOT NULL,
    issues_json TEXT,
    verification_requests_json TEXT,
    generated_at TEXT NOT NULL,
    version TEXT NOT NULL
);

-- Evidence Gaps (Prompt 5 Section 11)
CREATE TABLE IF NOT EXISTS evidence_gaps (
    gap_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    missing_evidence TEXT NOT NULL,
    why_required TEXT NOT NULL,
    possible_source_search TEXT,
    suggested_experiment TEXT,
    severity TEXT NOT NULL,
    related_node_code TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Assumptions (Prompt 5 Section 16)
CREATE TABLE IF NOT EXISTS assumptions (
    assumption_id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    is_explicit INTEGER NOT NULL DEFAULT 0,
    required_by_json TEXT,
    evidence_or_basis TEXT,
    testability TEXT NOT NULL,
    violation_consequence TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Verification Requests (Prompt 5 Section 102)
CREATE TABLE IF NOT EXISTS verification_requests (
    request_id TEXT PRIMARY KEY,
    request_type TEXT NOT NULL,
    target_claim_id TEXT,
    target_equation_id TEXT,
    target_table_or_figure_id TEXT,
    description TEXT NOT NULL,
    input_payload_json TEXT,
    status TEXT NOT NULL,
    verification_result_json TEXT,
    requested_at TEXT NOT NULL,
    completed_at TEXT
);

-- Reasoning Issues Log (Prompt 5 Section 63)
CREATE TABLE IF NOT EXISTS reasoning_issues (
    issue_id TEXT PRIMARY KEY,
    issue_type TEXT NOT NULL,
    affected_entity_id TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT NOT NULL,
    mitigation TEXT,
    created_at TEXT NOT NULL
);

-- Numerical Claims (Prompt 6 Section 50)
CREATE TABLE IF NOT EXISTS numerical_claims (
    numerical_claim_id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    quantity_name TEXT NOT NULL,
    raw_value REAL NOT NULL,
    display_value TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'dimensionless',
    uncertainty TEXT,
    source_type TEXT NOT NULL,
    source_id TEXT,
    source_locator TEXT,
    computation_id TEXT,
    metric_name TEXT,
    granularity TEXT DEFAULT 'EVENT',
    scope_dataset TEXT,
    verification_status TEXT NOT NULL DEFAULT 'PENDING',
    related_claim_id TEXT,
    is_estimate INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Mathematical Equations (Prompt 6, Prompt 7)
CREATE TABLE IF NOT EXISTS equations (
    equation_id TEXT PRIMARY KEY,
    latex TEXT NOT NULL,
    description TEXT,
    equation_type TEXT NOT NULL DEFAULT 'OBJECTIVE_FUNCTION',
    ownership TEXT NOT NULL DEFAULT 'OURS',
    is_verified INTEGER NOT NULL DEFAULT 1,
    roadmap_nodes_json TEXT NOT NULL DEFAULT '[]',
    symbols_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

-- Metric Definitions (Prompt 6 Section 28)
CREATE TABLE IF NOT EXISTS metric_definitions (
    metric_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    formula_latex TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'dimensionless',
    aggregation TEXT NOT NULL DEFAULT 'MEAN',
    granularity TEXT NOT NULL DEFAULT 'EVENT',
    positive_class TEXT DEFAULT 'ATTACK / ANOMALY',
    interpolation_method TEXT DEFAULT 'LINEAR',
    assumptions_json TEXT NOT NULL DEFAULT '[]',
    version TEXT NOT NULL DEFAULT 'v1.0',
    created_at TEXT NOT NULL
);

-- Statistical Results (Prompt 6 Section 34..43)
CREATE TABLE IF NOT EXISTS statistical_results (
    stat_id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    test_name TEXT NOT NULL,
    sample_unit TEXT NOT NULL,
    sample_size_n INTEGER NOT NULL,
    statistic_value REAL,
    p_value REAL,
    effect_size_name TEXT,
    effect_size_value REAL,
    ci_lower REAL,
    ci_upper REAL,
    ci_level REAL NOT NULL DEFAULT 0.95,
    bootstrap_resamples INTEGER,
    random_seed INTEGER,
    assumptions_met INTEGER NOT NULL DEFAULT 1,
    assumptions_evaluated_json TEXT NOT NULL DEFAULT '[]',
    is_significant INTEGER,
    multiple_comparisons_context TEXT,
    interpretation_notes TEXT,
    created_at TEXT NOT NULL
);

-- Dataset Manifests & Profiles (Prompt 6 Section 21, 23)
CREATE TABLE IF NOT EXISTS dataset_manifests (
    manifest_id TEXT PRIMARY KEY,
    dataset_version_id TEXT NOT NULL,
    files_json TEXT NOT NULL DEFAULT '[]',
    total_files INTEGER NOT NULL DEFAULT 0,
    total_bytes INTEGER NOT NULL DEFAULT 0,
    total_events INTEGER NOT NULL DEFAULT 0,
    manifest_sha256 TEXT NOT NULL,
    schema_fields_json TEXT NOT NULL DEFAULT '[]',
    timestamp_start TEXT,
    timestamp_end TEXT,
    label_field TEXT,
    entity_fields_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dataset_profiles (
    profile_id TEXT PRIMARY KEY,
    dataset_version_id TEXT NOT NULL,
    total_events INTEGER NOT NULL DEFAULT 0,
    total_entities INTEGER NOT NULL DEFAULT 0,
    label_counts_json TEXT NOT NULL DEFAULT '{}',
    class_ratios_json TEXT NOT NULL DEFAULT '{}',
    missing_rates_json TEXT NOT NULL DEFAULT '{}',
    template_count INTEGER,
    host_count INTEGER,
    timestamp_range TEXT,
    script_path TEXT NOT NULL,
    code_commit_hash TEXT NOT NULL,
    profile_sha256 TEXT NOT NULL,
    computed_at TEXT NOT NULL
);

-- Split Manifests & Preprocessing Lineage (Prompt 6 Section 24, 26)
CREATE TABLE IF NOT EXISTS split_manifests (
    split_id TEXT PRIMARY KEY,
    dataset_version_id TEXT NOT NULL,
    strategy TEXT NOT NULL,
    train_hashes_json TEXT NOT NULL DEFAULT '[]',
    val_hashes_json TEXT NOT NULL DEFAULT '[]',
    test_hashes_json TEXT NOT NULL DEFAULT '[]',
    train_count INTEGER NOT NULL DEFAULT 0,
    val_count INTEGER NOT NULL DEFAULT 0,
    test_count INTEGER NOT NULL DEFAULT 0,
    temporal_boundaries_json TEXT NOT NULL DEFAULT '{}',
    host_holdout_json TEXT NOT NULL DEFAULT '[]',
    campaign_holdout_json TEXT NOT NULL DEFAULT '[]',
    seed INTEGER NOT NULL DEFAULT 42,
    manifest_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS preprocessing_transformations (
    transformation_id TEXT PRIMARY KEY,
    input_dataset_version_id TEXT NOT NULL,
    output_dataset_version_id TEXT NOT NULL,
    transformation_type TEXT NOT NULL,
    script_path TEXT NOT NULL,
    parameters_json TEXT NOT NULL DEFAULT '{}',
    fitted_on_subset TEXT NOT NULL DEFAULT 'TRAIN_ONLY',
    execution_time_sec REAL NOT NULL DEFAULT 0.0,
    code_commit_hash TEXT NOT NULL,
    output_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS protocol_deviations (
    deviation_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    original_protocol TEXT NOT NULL,
    deviated_protocol TEXT NOT NULL,
    reason TEXT NOT NULL,
    timing TEXT NOT NULL,
    impact_assessment TEXT NOT NULL,
    approved_by TEXT NOT NULL DEFAULT 'RESEARCH_ARCHITECT',
    created_at TEXT NOT NULL
);

-- Result Bundles & Verified Claim Bundles (Prompt 6 Section 98, 138)
CREATE TABLE IF NOT EXISTS result_bundles (
    bundle_id TEXT PRIMARY KEY,
    roadmap_node_code TEXT NOT NULL,
    rq_id TEXT NOT NULL,
    hyp_id TEXT NOT NULL,
    experiment_run_ids_json TEXT NOT NULL DEFAULT '[]',
    verified_metrics_json TEXT NOT NULL DEFAULT '{}',
    numerical_claims_json TEXT NOT NULL DEFAULT '[]',
    statistical_results_json TEXT NOT NULL DEFAULT '[]',
    table_ids_json TEXT NOT NULL DEFAULT '[]',
    figure_ids_json TEXT NOT NULL DEFAULT '[]',
    data_provenance_summary TEXT NOT NULL,
    limitations_json TEXT NOT NULL DEFAULT '[]',
    comparability_constraints_json TEXT NOT NULL DEFAULT '[]',
    invalidated_run_ids_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verified_claim_bundles (
    claim_id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    ownership TEXT NOT NULL DEFAULT 'OURS',
    source_evidence_ids_json TEXT NOT NULL DEFAULT '[]',
    numerical_claims_json TEXT NOT NULL DEFAULT '[]',
    equation_ids_json TEXT NOT NULL DEFAULT '[]',
    result_bundle_id TEXT,
    uncertainty_description TEXT,
    allowed_wording_strength TEXT NOT NULL DEFAULT 'SUPPORTIVE',
    citation_keys_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reproducibility_logs (
    log_id TEXT PRIMARY KEY,
    target_artifact_id TEXT NOT NULL,
    reproducibility_level TEXT NOT NULL,
    reproduction_command TEXT NOT NULL,
    success INTEGER NOT NULL,
    divergence_details TEXT,
    executed_at TEXT NOT NULL
);

-- ======================================================================
-- PROMPT 7 TABLES: PARAGRAPHS, SENTENCES, AUDITS, MANIFESTS
-- ======================================================================

CREATE TABLE IF NOT EXISTS thesis_paragraphs (
    paragraph_id TEXT PRIMARY KEY,
    node_code TEXT NOT NULL,
    section_code TEXT NOT NULL,
    chapter_code TEXT NOT NULL,
    discourse_function TEXT NOT NULL,
    argument_bundle_id TEXT,
    raw_text TEXT NOT NULL,
    audited_text TEXT NOT NULL,
    review_status TEXT NOT NULL,
    is_human_edited INTEGER NOT NULL DEFAULT 0,
    human_edit_notes TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS thesis_sentences (
    sentence_id TEXT PRIMARY KEY,
    paragraph_id TEXT NOT NULL,
    sentence_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    ownership TEXT NOT NULL,
    target_claim_id TEXT,
    citation_source_ids_json TEXT NOT NULL DEFAULT '[]',
    numerical_claim_ids_json TEXT NOT NULL DEFAULT '[]',
    equation_ids_json TEXT NOT NULL DEFAULT '[]',
    table_ids_json TEXT NOT NULL DEFAULT '[]',
    figure_ids_json TEXT NOT NULL DEFAULT '[]',
    compilation_state TEXT NOT NULL,
    issues_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS thesis_audit_reports (
    build_id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    total_sentences INTEGER NOT NULL,
    total_paragraphs INTEGER NOT NULL,
    total_issues INTEGER NOT NULL,
    report_json TEXT NOT NULL,
    overall_status TEXT NOT NULL,
    is_ready_for_final_build INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS thesis_audit_issues (
    issue_id TEXT PRIMARY KEY,
    build_id TEXT,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    affected_entity_id TEXT,
    recommended_action TEXT,
    is_blocking INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    waiver_rationale TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS thesis_build_manifests (
    build_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    mode TEXT NOT NULL,
    git_commit TEXT NOT NULL,
    roadmap_version TEXT NOT NULL,
    reference_map_version TEXT NOT NULL,
    memory_schema_version TEXT NOT NULL,
    reasoning_version TEXT NOT NULL,
    verification_version TEXT NOT NULL,
    total_nodes_compiled INTEGER NOT NULL,
    unresolved_critical_count INTEGER NOT NULL,
    unresolved_high_count INTEGER NOT NULL,
    output_file_path TEXT NOT NULL,
    output_sha256 TEXT NOT NULL
);
"""


class DatabaseManager:
    """Manages SQLite database connections and schema lifecycle."""

    def __init__(self, db_path: Path | str | None = None, config: WorkspaceConfig | None = None):
        cfg = config or get_default_config()
        if isinstance(db_path, str) and db_path.startswith("sqlite:///"):
            db_path = db_path[len("sqlite:///"):]
        self.db_path = Path(db_path) if db_path else cfg.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Execute full schema migration and upgrade tables if needed."""
        with self.session() as conn:
            conn.executescript(SCHEMA_SQL)
            
            # Helper to safely add column if missing
            def ensure_column(table: str, column: str, col_type: str, default: str = ""):
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [row["name"] for row in cursor.fetchall()]
                if column not in cols:
                    default_clause = f" DEFAULT {default}" if default else ""
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}{default_clause}")

            # Migrations for existing roadmaps tables
            ensure_column("roadmaps", "central_object", "TEXT", "'feature representation z'")
            ensure_column("roadmap_nodes", "canonical_text", "TEXT")
            ensure_column("roadmap_nodes", "expected_role", "TEXT", "'SPECIFICATION'")
            ensure_column("roadmap_nodes", "research_axes_json", "TEXT", "'[]'")
            ensure_column("roadmap_nodes", "methodological_constraints_json", "TEXT", "'[]'")
            ensure_column("roadmap_nodes", "status", "TEXT", "'SPECIFIED'")
            ensure_column("research_questions", "canonical_wording_en", "TEXT", "''")
            ensure_column("research_questions", "canonical_wording_vi", "TEXT", "''")
            ensure_column("hypotheses", "title", "TEXT", "''")

            # Migrations for sources and evidences
            ensure_column("sources", "citation_key", "TEXT", "''")
            ensure_column("sources", "source_type", "TEXT", "'PEER_REVIEWED'")
            ensure_column("sources", "roles_json", "TEXT", "'[]'")
            ensure_column("sources", "publisher", "TEXT", "''")
            ensure_column("sources", "canonical_url", "TEXT", "''")
            ensure_column("sources", "access_url", "TEXT", "''")
            ensure_column("sources", "access_date", "TEXT", "''")
            ensure_column("sources", "bibliographic_verification_state", "TEXT", "'METADATA_VERIFIED'")
            ensure_column("sources", "content_verification_state", "TEXT", "'CONTENT_VERIFIED'")
            ensure_column("sources", "license_or_access_notes", "TEXT", "''")
            ensure_column("sources", "retraction_status", "TEXT", "''")
            ensure_column("sources", "relevant_roadmap_nodes_json", "TEXT", "'[]'")
            ensure_column("sources", "notes", "TEXT", "''")
            ensure_column("sources", "sha256_hash", "TEXT", "''")
            ensure_column("evidences", "supports_claim_id", "TEXT", "''")
            ensure_column("evidences", "support_type", "TEXT", "'DIRECT_SUPPORT'")
            ensure_column("evidences", "strength", "TEXT", "'STRONG'")
            ensure_column("evidences", "caveats", "TEXT", "''")
            ensure_column("evidences", "verified_at", "TEXT", "''")

            # Migrations for decision_records
            ensure_column("decision_records", "rationale", "TEXT", "''")
            ensure_column("decision_records", "alternatives_considered_json", "TEXT", "'[]'")
            ensure_column("decision_records", "evidence_ids_json", "TEXT", "'[]'")
            ensure_column("decision_records", "target_affected_entities_json", "TEXT", "'[]'")
            ensure_column("decision_records", "related_nodes_json", "TEXT", "'[]'")
            ensure_column("decision_records", "related_claims_json", "TEXT", "'[]'")
            ensure_column("decision_records", "related_experiments_json", "TEXT", "'[]'")
            ensure_column("decision_records", "supersedes_id", "TEXT", "''")
            ensure_column("decision_records", "superseded_by_id", "TEXT", "''")
            ensure_column("decision_records", "actor", "TEXT", "'HUMAN_ARCHITECT_OR_AGENT'")
            ensure_column("decision_records", "made_at", "TEXT", "''")

            # Migrations for memory_records
            ensure_column("memory_records", "record_type", "TEXT", "'OBSERVATION'")
            ensure_column("memory_records", "promotion_state", "TEXT", "'CONSOLIDATED'")
            ensure_column("memory_records", "summary", "TEXT", "''")
            ensure_column("memory_records", "reference_type", "TEXT", "''")
            ensure_column("memory_records", "reference_id", "TEXT", "''")
            ensure_column("memory_records", "ownership", "TEXT", "'OURS'")
            ensure_column("memory_records", "epistemic_status", "TEXT", "'SUPPORTED'")
            ensure_column("memory_records", "is_generated_summary", "INTEGER", "0")
            ensure_column("memory_records", "supersedes_id", "TEXT", "''")
            ensure_column("memory_records", "superseded_by_id", "TEXT", "''")
            ensure_column("memory_records", "is_stale", "INTEGER", "0")
            ensure_column("memory_records", "review_required", "INTEGER", "0")
            ensure_column("memory_records", "last_verified_at", "TEXT", "''")
            ensure_column("memory_records", "privacy", "TEXT", "'INTERNAL'")
            ensure_column("memory_records", "actor", "TEXT", "'RESEARCH_AGENT'")
            ensure_column("memory_records", "session_id", "TEXT", "''")
            ensure_column("memory_records", "confidence_category", "TEXT", "'HIGH'")
            ensure_column("memory_records", "confidence_basis", "TEXT", "''")

            # Initialize FTS5 table if supported
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                        entity_id UNINDEXED,
                        entity_type,
                        title,
                        body,
                        tags,
                        tokenize='porter unicode61'
                    );
                    """
                )
            except Exception:
                # Fallback standard FTS5 without extra params
                try:
                    conn.execute(
                        """
                        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                            entity_id UNINDEXED,
                            entity_type,
                            title,
                            body,
                            tags
                        );
                        """
                    )
                except Exception:
                    pass
