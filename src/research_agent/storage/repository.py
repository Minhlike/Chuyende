"""
Canonical Repository Layer (ADR-0001, ADR-0002)
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
    EquationType,
    ArgumentRelationType,
    VerificationStatus,
    MemoryTier,
    ExperimentStatus,
)
from research_agent.core.identifiers import EntityPrefix, format_stable_id
from research_agent.core.exceptions import EntityNotFoundError, DuplicateEntityError
from research_agent.schemas import (
    ResearchProject,
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
    Source,
    SourceArtifact,
    Evidence,
    Claim,
    ClaimRelation,
    ArgumentNode,
    ArgumentEdge,
    Equation,
    SymbolDefinition,
    Dataset,
    DatasetVersion,
    Experiment,
    ExperimentRun,
    TableArtifact,
    FigureArtifact,
    DecisionRecord,
    ContradictionRecord,
    MemoryRecord,
    SkillRecord,
    VerificationRecord,
)
from research_agent.storage.db import DatabaseManager


class ResearchRepository:
    """Canonical Repository providing typed CRUD and transactional persistence."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def next_id(self, prefix: EntityPrefix) -> str:
        """Atomically increment and allocate the next stable identifier."""
        p_val = prefix.value
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_val FROM id_sequences WHERE prefix = ?", (p_val,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO id_sequences (prefix, current_val) VALUES (?, 1)", (p_val,))
                seq = 1
            else:
                seq = row["current_val"] + 1
                cursor.execute("UPDATE id_sequences SET current_val = ? WHERE prefix = ?", (seq, p_val))
            return format_stable_id(prefix, seq)

    # -------------------------------------------------------------
    # Project
    # -------------------------------------------------------------
    def save_project(self, project: ResearchProject) -> ResearchProject:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO projects (project_id, title, central_object, description, authors_json, constitution_version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    title=excluded.title,
                    central_object=excluded.central_object,
                    description=excluded.description,
                    authors_json=excluded.authors_json,
                    constitution_version=excluded.constitution_version,
                    updated_at=excluded.updated_at
                """,
                (
                    project.project_id,
                    project.title,
                    project.central_object,
                    project.description,
                    json.dumps(project.authors),
                    project.constitution_version,
                    project.created_at.isoformat(),
                    project.updated_at.isoformat(),
                )
            )
        return project

    def get_project(self, project_id: str) -> Optional[ResearchProject]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            if not row:
                return None
            return ResearchProject(
                project_id=row["project_id"],
                title=row["title"],
                central_object=row["central_object"],
                description=row["description"],
                authors=json.loads(row["authors_json"]),
                constitution_version=row["constitution_version"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    # -------------------------------------------------------------
    # Sources & Evidences
    # -------------------------------------------------------------
    def save_source(self, source: Source) -> Source:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO sources (source_id, title, authors_json, year, venue, doi, url, bibtex, verification_status, verification_method, abstract, keywords_json, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    title=excluded.title,
                    authors_json=excluded.authors_json,
                    year=excluded.year,
                    venue=excluded.venue,
                    doi=excluded.doi,
                    url=excluded.url,
                    bibtex=excluded.bibtex,
                    verification_status=excluded.verification_status,
                    verification_method=excluded.verification_method,
                    abstract=excluded.abstract,
                    keywords_json=excluded.keywords_json,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    source.source_id,
                    source.title,
                    json.dumps(source.authors),
                    source.year,
                    source.venue,
                    source.doi,
                    source.url,
                    source.bibtex,
                    source.verification_status.value,
                    source.verification_method,
                    source.abstract,
                    json.dumps(source.keywords),
                    json.dumps(source.metadata),
                    source.created_at.isoformat(),
                    source.updated_at.isoformat(),
                )
            )
        return source

    def get_source(self, source_id: str) -> Optional[Source]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM sources WHERE source_id = ?", (source_id,)).fetchone()
            if not row:
                return None
            return Source(
                source_id=row["source_id"],
                title=row["title"],
                authors=json.loads(row["authors_json"]),
                year=row["year"],
                venue=row["venue"],
                doi=row["doi"],
                url=row["url"],
                bibtex=row["bibtex"],
                verification_status=VerificationStatus(row["verification_status"]),
                verification_method=row["verification_method"],
                abstract=row["abstract"],
                keywords=json.loads(row["keywords_json"] or "[]"),
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def save_evidence(self, evidence: Evidence) -> Evidence:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO evidences (evidence_id, source_id, source_version_id, locator, page, section, exact_quote, paraphrase, context_notes, extraction_method, verification_status, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    locator=excluded.locator,
                    page=excluded.page,
                    section=excluded.section,
                    exact_quote=excluded.exact_quote,
                    paraphrase=excluded.paraphrase,
                    context_notes=excluded.context_notes,
                    verification_status=excluded.verification_status,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    evidence.evidence_id,
                    evidence.source_id,
                    evidence.source_version_id,
                    evidence.locator,
                    evidence.page,
                    evidence.section,
                    evidence.exact_quote,
                    evidence.paraphrase,
                    evidence.context_notes,
                    evidence.extraction_method,
                    evidence.verification_status.value,
                    json.dumps(evidence.metadata),
                    evidence.created_at.isoformat(),
                    evidence.updated_at.isoformat(),
                )
            )
        return evidence

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM evidences WHERE evidence_id = ?", (evidence_id,)).fetchone()
            if not row:
                return None
            return Evidence(
                evidence_id=row["evidence_id"],
                source_id=row["source_id"],
                source_version_id=row["source_version_id"],
                locator=row["locator"],
                page=row["page"],
                section=row["section"],
                exact_quote=row["exact_quote"],
                paraphrase=row["paraphrase"],
                context_notes=row["context_notes"],
                extraction_method=row["extraction_method"],
                verification_status=VerificationStatus(row["verification_status"]),
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    # -------------------------------------------------------------
    # Claims & Relations
    # -------------------------------------------------------------
    def save_claim(self, claim: Claim) -> Claim:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO claims (claim_id, statement, claim_type, ownership, epistemic_status, confidence, assumptions_json, scope, evidence_ids_json, experiment_run_id, falsification_conditions, version, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(claim_id) DO UPDATE SET
                    statement=excluded.statement,
                    claim_type=excluded.claim_type,
                    ownership=excluded.ownership,
                    epistemic_status=excluded.epistemic_status,
                    confidence=excluded.confidence,
                    assumptions_json=excluded.assumptions_json,
                    scope=excluded.scope,
                    evidence_ids_json=excluded.evidence_ids_json,
                    experiment_run_id=excluded.experiment_run_id,
                    falsification_conditions=excluded.falsification_conditions,
                    version=excluded.version,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    claim.claim_id,
                    claim.statement,
                    claim.claim_type.value,
                    claim.ownership.value,
                    claim.epistemic_status.value,
                    claim.confidence,
                    json.dumps(claim.assumptions),
                    claim.scope,
                    json.dumps(claim.evidence_ids),
                    claim.experiment_run_id,
                    claim.falsification_conditions,
                    claim.version,
                    json.dumps(claim.metadata),
                    claim.created_at.isoformat(),
                    claim.updated_at.isoformat(),
                )
            )
        return claim

    def get_claim(self, claim_id: str) -> Optional[Claim]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,)).fetchone()
            if not row:
                return None
            return Claim(
                claim_id=row["claim_id"],
                statement=row["statement"],
                claim_type=ClaimType(row["claim_type"]),
                ownership=IntellectualOwnership(row["ownership"]),
                epistemic_status=EpistemicStatus(row["epistemic_status"]),
                confidence=row["confidence"],
                assumptions=json.loads(row["assumptions_json"] or "[]"),
                scope=row["scope"],
                evidence_ids=json.loads(row["evidence_ids_json"] or "[]"),
                experiment_run_id=row["experiment_run_id"],
                falsification_conditions=row["falsification_conditions"],
                version=row["version"],
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_claims(self) -> List[Claim]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM claims ORDER BY claim_id").fetchall()
            return [
                Claim(
                    claim_id=r["claim_id"],
                    statement=r["statement"],
                    claim_type=ClaimType(r["claim_type"]),
                    ownership=IntellectualOwnership(r["ownership"]),
                    epistemic_status=EpistemicStatus(r["epistemic_status"]),
                    confidence=r["confidence"],
                    assumptions=json.loads(r["assumptions_json"] or "[]"),
                    scope=r["scope"],
                    evidence_ids=json.loads(r["evidence_ids_json"] or "[]"),
                    experiment_run_id=r["experiment_run_id"],
                    falsification_conditions=r["falsification_conditions"],
                    version=r["version"],
                    metadata=json.loads(r["metadata_json"] or "{}"),
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Equations
    # -------------------------------------------------------------
    def save_equation(self, eq: Equation) -> Equation:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO equations (equation_id, latex, normalized_representation, equation_type, source_id, source_locator, ownership, symbols_json, assumptions_json, derivation_json, verification_status, verification_method, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(equation_id) DO UPDATE SET
                    latex=excluded.latex,
                    normalized_representation=excluded.normalized_representation,
                    equation_type=excluded.equation_type,
                    source_id=excluded.source_id,
                    source_locator=excluded.source_locator,
                    ownership=excluded.ownership,
                    symbols_json=excluded.symbols_json,
                    assumptions_json=excluded.assumptions_json,
                    derivation_json=excluded.derivation_json,
                    verification_status=excluded.verification_status,
                    verification_method=excluded.verification_method,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    eq.equation_id,
                    eq.latex,
                    eq.normalized_representation,
                    eq.equation_type.value,
                    eq.source_id,
                    eq.source_locator,
                    eq.ownership.value,
                    json.dumps([s.model_dump() for s in eq.symbols]),
                    json.dumps(eq.assumptions),
                    json.dumps(eq.derivation.model_dump()) if eq.derivation else None,
                    eq.verification_status.value,
                    eq.verification_method,
                    json.dumps(eq.metadata),
                    eq.created_at.isoformat(),
                    eq.updated_at.isoformat(),
                )
            )
        return eq

    def get_equation(self, equation_id: str) -> Optional[Equation]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM equations WHERE equation_id = ?", (equation_id,)).fetchone()
            if not row:
                return None
            symbols = [SymbolDefinition(**s) for s in json.loads(row["symbols_json"] or "[]")]
            derivation = json.loads(row["derivation_json"]) if row["derivation_json"] else None
            return Equation(
                equation_id=row["equation_id"],
                latex=row["latex"],
                normalized_representation=row["normalized_representation"],
                equation_type=EquationType(row["equation_type"]),
                source_id=row["source_id"],
                source_locator=row["source_locator"],
                ownership=IntellectualOwnership(row["ownership"]),
                symbols=symbols,
                assumptions=json.loads(row["assumptions_json"] or "[]"),
                derivation=derivation,
                verification_status=VerificationStatus(row["verification_status"]),
                verification_method=row["verification_method"],
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    # -------------------------------------------------------------
    # Experiments & Runs
    # -------------------------------------------------------------
    def save_experiment(self, exp: Experiment) -> Experiment:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO experiments (experiment_id, rq_id, hyp_id, title, description, target_representation_aspect, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(experiment_id) DO UPDATE SET
                    rq_id=excluded.rq_id,
                    hyp_id=excluded.hyp_id,
                    title=excluded.title,
                    description=excluded.description,
                    target_representation_aspect=excluded.target_representation_aspect,
                    updated_at=excluded.updated_at
                """,
                (
                    exp.experiment_id,
                    exp.rq_id,
                    exp.hyp_id,
                    exp.title,
                    exp.description,
                    exp.target_representation_aspect,
                    exp.created_at.isoformat(),
                    exp.updated_at.isoformat(),
                )
            )
        return exp

    def save_experiment_run(self, run: ExperimentRun) -> ExperimentRun:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO experiment_runs (run_id, experiment_id, dataset_id, dataset_version_id, split_hash, model_config_json, extractor_config_json, random_seed, environment_spec_json, git_commit_hash, command, status, started_at, finished_at, metrics_json, error_message, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status=excluded.status,
                    finished_at=excluded.finished_at,
                    metrics_json=excluded.metrics_json,
                    error_message=excluded.error_message,
                    metadata_json=excluded.metadata_json
                """,
                (
                    run.run_id,
                    run.experiment_id,
                    run.dataset_id,
                    run.dataset_version_id,
                    run.split_hash,
                    json.dumps(run.model_parameters),
                    json.dumps(run.extractor_config),
                    run.random_seed,
                    json.dumps(run.environment_spec),
                    run.git_commit_hash,
                    run.command,
                    run.status.value,
                    run.started_at.isoformat(),
                    run.finished_at.isoformat() if run.finished_at else None,
                    json.dumps(run.metrics),
                    run.error_message,
                    json.dumps(run.metadata),
                )
            )
        return run

    def get_experiment_run(self, run_id: str) -> Optional[ExperimentRun]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM experiment_runs WHERE run_id = ?", (run_id,)).fetchone()
            if not row:
                return None
            return ExperimentRun(
                run_id=row["run_id"],
                experiment_id=row["experiment_id"],
                dataset_id=row["dataset_id"],
                dataset_version_id=row["dataset_version_id"],
                split_hash=row["split_hash"],
                model_parameters=json.loads(row["model_config_json"] or "{}"),
                extractor_config=json.loads(row["extractor_config_json"] or "{}"),
                random_seed=row["random_seed"],
                environment_spec=json.loads(row["environment_spec_json"] or "{}"),
                git_commit_hash=row["git_commit_hash"],
                command=row["command"],
                status=ExperimentStatus(row["status"]),
                started_at=datetime.fromisoformat(row["started_at"]),
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
                metrics=json.loads(row["metrics_json"] or "{}"),
                error_message=row["error_message"],
                metadata=json.loads(row["metadata_json"] or "{}"),
            )

    # -------------------------------------------------------------
    # Tables & Figures
    # -------------------------------------------------------------
    def save_table_artifact(self, tbl: TableArtifact) -> TableArtifact:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO table_artifacts (table_id, title, caption, content, is_numerical_result, dataset_id, experiment_run_ids_json, generation_script, script_git_hash, input_hashes_json, output_sha256, is_synthetic_data, is_manually_edited, verification_status, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(table_id) DO UPDATE SET
                    title=excluded.title,
                    caption=excluded.caption,
                    content=excluded.content,
                    output_sha256=excluded.output_sha256,
                    verification_status=excluded.verification_status,
                    metadata_json=excluded.metadata_json
                """,
                (
                    tbl.table_id,
                    tbl.title,
                    tbl.caption,
                    tbl.content,
                    1 if tbl.is_numerical_result else 0,
                    tbl.dataset_id,
                    json.dumps(tbl.experiment_run_ids),
                    tbl.generation_script,
                    tbl.script_git_hash,
                    json.dumps(tbl.input_hashes),
                    tbl.output_sha256,
                    1 if tbl.is_synthetic_data else 0,
                    1 if tbl.is_manually_edited else 0,
                    tbl.verification_status.value,
                    json.dumps(tbl.metadata),
                    tbl.created_at.isoformat(),
                )
            )
        return tbl

    def save_figure_artifact(self, fig: FigureArtifact) -> FigureArtifact:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO figure_artifacts (figure_id, title, caption, file_rel_path, is_numerical_result, dataset_id, experiment_run_ids_json, generation_script, script_git_hash, input_hashes_json, output_sha256, is_synthetic_data, verification_status, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(figure_id) DO UPDATE SET
                    title=excluded.title,
                    caption=excluded.caption,
                    file_rel_path=excluded.file_rel_path,
                    output_sha256=excluded.output_sha256,
                    verification_status=excluded.verification_status,
                    metadata_json=excluded.metadata_json
                """,
                (
                    fig.figure_id,
                    fig.title,
                    fig.caption,
                    fig.file_rel_path,
                    1 if fig.is_numerical_result else 0,
                    fig.dataset_id,
                    json.dumps(fig.experiment_run_ids),
                    fig.generation_script,
                    fig.script_git_hash,
                    json.dumps(fig.input_hashes),
                    fig.output_sha256,
                    1 if fig.is_synthetic_data else 0,
                    fig.verification_status.value,
                    json.dumps(fig.metadata),
                    fig.created_at.isoformat(),
                )
            )
        return fig

    # -------------------------------------------------------------
    # Contradictions & Decisions
    # -------------------------------------------------------------
    def save_contradiction(self, ctr: ContradictionRecord) -> ContradictionRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO contradiction_records (contradiction_id, claim_a_id, claim_b_id, description, domain_or_scope_divergence, resolution_status, resolution_notes, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contradiction_id) DO UPDATE SET
                    description=excluded.description,
                    domain_or_scope_divergence=excluded.domain_or_scope_divergence,
                    resolution_status=excluded.resolution_status,
                    resolution_notes=excluded.resolution_notes,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    ctr.contradiction_id,
                    ctr.claim_a_id,
                    ctr.claim_b_id,
                    ctr.description,
                    ctr.domain_or_scope_divergence,
                    ctr.resolution_status,
                    ctr.resolution_notes,
                    json.dumps(ctr.metadata),
                    ctr.created_at.isoformat(),
                    ctr.updated_at.isoformat(),
                )
            )
        return ctr

    def list_contradictions(self) -> List[ContradictionRecord]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM contradiction_records ORDER BY contradiction_id").fetchall()
            return [
                ContradictionRecord(
                    contradiction_id=r["contradiction_id"],
                    claim_a_id=r["claim_a_id"],
                    claim_b_id=r["claim_b_id"],
                    description=r["description"],
                    domain_or_scope_divergence=r["domain_or_scope_divergence"],
                    resolution_status=r["resolution_status"],
                    resolution_notes=r["resolution_notes"],
                    metadata=json.loads(r["metadata_json"] or "{}"),
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Memory Records
    # -------------------------------------------------------------
    def save_memory(self, mem: MemoryRecord) -> MemoryRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO memory_records (memory_id, tier, topic, content, associated_entity_ids_json, tags_json, importance, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    topic=excluded.topic,
                    content=excluded.content,
                    associated_entity_ids_json=excluded.associated_entity_ids_json,
                    tags_json=excluded.tags_json,
                    importance=excluded.importance,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    mem.memory_id,
                    mem.tier.value,
                    mem.topic,
                    mem.content,
                    json.dumps(mem.associated_entity_ids),
                    json.dumps(mem.tags),
                    mem.importance,
                    json.dumps(mem.metadata),
                    mem.created_at.isoformat(),
                    mem.updated_at.isoformat(),
                )
            )
        return mem
