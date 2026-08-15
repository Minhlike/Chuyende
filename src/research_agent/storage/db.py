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
    title TEXT NOT NULL,
    authors_json TEXT NOT NULL,
    year INTEGER NOT NULL,
    venue TEXT NOT NULL,
    doi TEXT,
    url TEXT,
    bibtex TEXT,
    verification_status TEXT NOT NULL,
    verification_method TEXT,
    abstract TEXT,
    keywords_json TEXT,
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
    context_notes TEXT,
    extraction_method TEXT,
    verification_status TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
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

-- Arguments
CREATE TABLE IF NOT EXISTS argument_nodes (
    node_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    role TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS argument_edges (
    edge_id TEXT PRIMARY KEY,
    from_node_id TEXT NOT NULL,
    to_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    rationale TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (from_node_id) REFERENCES argument_nodes(node_id) ON DELETE CASCADE,
    FOREIGN KEY (to_node_id) REFERENCES argument_nodes(node_id) ON DELETE CASCADE
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
    consequences TEXT NOT NULL,
    target_affected_entities_json TEXT,
    diff_summary TEXT,
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

-- Memory & Skills
CREATE TABLE IF NOT EXISTS memory_records (
    memory_id TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    associated_entity_ids_json TEXT,
    tags_json TEXT,
    importance REAL NOT NULL DEFAULT 0.5,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_records (
    skill_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    protocol_markdown_rel_path TEXT NOT NULL,
    description TEXT NOT NULL,
    checklist_json TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL
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
"""


class DatabaseManager:
    """Manages SQLite database connections and schema lifecycle."""

    def __init__(self, db_path: Path | str | None = None, config: WorkspaceConfig | None = None):
        cfg = config or get_default_config()
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
