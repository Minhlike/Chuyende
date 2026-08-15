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
    SourceVerificationState,
    SourceRole,
    SourceQualityTier,
    SupportType,
    EvidenceStrength,
    NoveltyStatus,
    CitationFirewallStatus,
    MemoryRecordType,
    MemoryPromotionState,
    DecisionStatus,
    OpenQuestionStatus,
    EpisodeStatus,
    SkillStatus,
    QueryIntentType,
    PrivacyClassification,
)
from research_agent.core.identifiers import EntityPrefix, format_stable_id
from research_agent.core.exceptions import EntityNotFoundError, DuplicateEntityError
from research_agent.schemas import (
    ResearchProject,
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
    ResearchAxis,
    RepresentationContract,
    NegativeControl,
    ResearchBoundary,
    DefensibilityQuestion,
    TraceabilityEntry,
    Source,
    SourceVersion,
    SourceArtifact,
    Evidence,
    Claim,
    ClaimRelation,
    OwnershipMapping,
    CandidateContribution,
    CitationFirewallRule,
    ReferenceMapSpecification,
    ArgumentNode,
    ArgumentEdge,
    SymbolDefinition,
    EquationDerivation,
    Equation,
    DatasetSplitManifest,
    DatasetVersion,
    Dataset,
    ExperimentArtifact,
    ExperimentRun,
    Experiment,
    TableArtifact,
    FigureArtifact,
    DecisionRecord,
    ContradictionRecord,
    MemoryRecord,
    SkillRecord,
    EpisodeRecord,
    OpenQuestion,
    LessonLearned,
    SessionRecord,
    StatusTransitionRecord,
    ContextBundle,
    VerificationRecord,
    ArgumentBundle,
    EvidenceGap,
    AssumptionRecord,
    VerificationRequest,
    ReasoningIssue,
    ArgumentGraph,
)
from research_agent.core.enums import (
    ArgumentReadinessState,
    ReasoningIssueType,
    VerificationRequestType,
    VerificationRequestStatus,
    ArgumentNodeType,
    ArgumentEdgeType,
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
                INSERT INTO sources (
                    source_id, citation_key, title, authors_json, year, venue,
                    source_type, roles_json, doi, publisher, canonical_url,
                    access_url, access_date, bibtex,
                    bibliographic_verification_state, content_verification_state,
                    verification_status, verification_method, abstract, keywords_json,
                    license_or_access_notes, retraction_status, relevant_roadmap_nodes_json,
                    notes, sha256_hash, metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    citation_key=excluded.citation_key,
                    title=excluded.title,
                    authors_json=excluded.authors_json,
                    year=excluded.year,
                    venue=excluded.venue,
                    source_type=excluded.source_type,
                    roles_json=excluded.roles_json,
                    doi=excluded.doi,
                    publisher=excluded.publisher,
                    canonical_url=excluded.canonical_url,
                    access_url=excluded.access_url,
                    access_date=excluded.access_date,
                    bibtex=excluded.bibtex,
                    bibliographic_verification_state=excluded.bibliographic_verification_state,
                    content_verification_state=excluded.content_verification_state,
                    verification_status=excluded.verification_status,
                    verification_method=excluded.verification_method,
                    abstract=excluded.abstract,
                    keywords_json=excluded.keywords_json,
                    license_or_access_notes=excluded.license_or_access_notes,
                    retraction_status=excluded.retraction_status,
                    relevant_roadmap_nodes_json=excluded.relevant_roadmap_nodes_json,
                    notes=excluded.notes,
                    sha256_hash=excluded.sha256_hash,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    source.source_id,
                    source.citation_key,
                    source.title,
                    json.dumps(source.authors),
                    source.year,
                    source.venue,
                    source.source_type.value,
                    json.dumps([r.value for r in source.roles]),
                    source.doi,
                    source.publisher,
                    source.canonical_url,
                    source.access_url,
                    source.access_date,
                    source.bibtex,
                    source.bibliographic_verification_state.value,
                    source.content_verification_state.value,
                    source.verification_status.value,
                    source.verification_method,
                    source.abstract,
                    json.dumps(source.keywords),
                    source.license_or_access_notes,
                    source.retraction_status,
                    json.dumps(source.relevant_roadmap_nodes),
                    source.notes,
                    source.sha256_hash,
                    json.dumps(source.metadata),
                    source.created_at.isoformat(),
                    source.updated_at.isoformat(),
                )
            )
            self._index_fts_on_conn(
                conn=conn,
                entity_id=source.source_id,
                entity_type="SOURCE",
                title=f"{source.citation_key}: {source.title}",
                body=f"{source.abstract or ''} {source.notes or ''} {' '.join(source.keywords)}",
                tags=" ".join(source.relevant_roadmap_nodes + source.authors),
            )
        return source

    def _row_to_source(self, row: Any) -> Source:
        roles_raw = json.loads(row["roles_json"] or "[]")
        roles = [SourceRole(r) for r in roles_raw if r in SourceRole.__members__.values()]
        return Source(
            source_id=row["source_id"],
            citation_key=row["citation_key"] or row["source_id"],
            title=row["title"],
            authors=json.loads(row["authors_json"]),
            year=row["year"],
            venue=row["venue"],
            source_type=SourceQualityTier(row["source_type"]) if row["source_type"] in SourceQualityTier.__members__.values() else SourceQualityTier.PEER_REVIEWED,
            roles=roles,
            doi=row["doi"],
            publisher=row["publisher"],
            canonical_url=row["canonical_url"],
            access_url=row["access_url"],
            access_date=row["access_date"],
            bibtex=row["bibtex"],
            bibliographic_verification_state=SourceVerificationState(row["bibliographic_verification_state"]) if row["bibliographic_verification_state"] in SourceVerificationState.__members__.values() else SourceVerificationState.METADATA_VERIFIED,
            content_verification_state=SourceVerificationState(row["content_verification_state"]) if row["content_verification_state"] in SourceVerificationState.__members__.values() else SourceVerificationState.CONTENT_VERIFIED,
            verification_status=VerificationStatus(row["verification_status"]),
            verification_method=row["verification_method"] or "OFFICIAL_PUBLISHER_OR_CROSSREF",
            abstract=row["abstract"],
            keywords=json.loads(row["keywords_json"] or "[]"),
            license_or_access_notes=row["license_or_access_notes"],
            retraction_status=row["retraction_status"],
            relevant_roadmap_nodes=json.loads(row["relevant_roadmap_nodes_json"] or "[]"),
            notes=row["notes"],
            sha256_hash=row["sha256_hash"],
            metadata=json.loads(row["metadata_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def get_source(self, source_id: str) -> Optional[Source]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM sources WHERE source_id = ?", (source_id,)).fetchone()
            if not row:
                return None
            return self._row_to_source(row)

    def get_source_by_citation_key(self, citation_key: str) -> Optional[Source]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM sources WHERE citation_key = ?", (citation_key,)).fetchone()
            if not row:
                return None
            return self._row_to_source(row)

    def get_source_by_doi(self, doi: str) -> Optional[Source]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM sources WHERE LOWER(doi) = LOWER(?)", (doi.strip(),)).fetchone()
            if not row:
                return None
            return self._row_to_source(row)

    def list_sources(self) -> List[Source]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM sources ORDER BY source_id ASC").fetchall()
            return [self._row_to_source(r) for r in rows]

    def save_evidence(self, evidence: Evidence) -> Evidence:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO evidences (
                    evidence_id, source_id, source_version_id, locator, page,
                    section, exact_quote, paraphrase, supports_claim_id,
                    support_type, strength, caveats, context_notes,
                    extraction_method, verification_status, verified_at,
                    metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    locator=excluded.locator,
                    page=excluded.page,
                    section=excluded.section,
                    exact_quote=excluded.exact_quote,
                    paraphrase=excluded.paraphrase,
                    supports_claim_id=excluded.supports_claim_id,
                    support_type=excluded.support_type,
                    strength=excluded.strength,
                    caveats=excluded.caveats,
                    context_notes=excluded.context_notes,
                    verification_status=excluded.verification_status,
                    verified_at=excluded.verified_at,
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
                    evidence.supports_claim_id,
                    evidence.support_type.value,
                    evidence.strength.value,
                    evidence.caveats,
                    evidence.context_notes,
                    evidence.extraction_method,
                    evidence.verification_status.value,
                    evidence.verified_at.isoformat() if evidence.verified_at else None,
                    json.dumps(evidence.metadata),
                    evidence.created_at.isoformat(),
                    evidence.updated_at.isoformat(),
                )
            )
        return evidence

    def _row_to_evidence(self, row: Any) -> Evidence:
        return Evidence(
            evidence_id=row["evidence_id"],
            source_id=row["source_id"],
            source_version_id=row["source_version_id"],
            locator=row["locator"],
            page=row["page"],
            section=row["section"],
            exact_quote=row["exact_quote"],
            paraphrase=row["paraphrase"],
            supports_claim_id=row["supports_claim_id"],
            support_type=SupportType(row["support_type"]) if row["support_type"] in SupportType.__members__.values() else SupportType.DIRECT_SUPPORT,
            strength=EvidenceStrength(row["strength"]) if row["strength"] in EvidenceStrength.__members__.values() else EvidenceStrength.STRONG,
            caveats=row["caveats"],
            context_notes=row["context_notes"],
            extraction_method=row["extraction_method"] or "MANUAL_EXTRACT",
            verification_status=VerificationStatus(row["verification_status"]),
            verified_at=datetime.fromisoformat(row["verified_at"]) if row["verified_at"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata_json"] or "{}"),
        )

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM evidences WHERE evidence_id = ?", (evidence_id,)).fetchone()
            if not row:
                return None
            return self._row_to_evidence(row)

    def list_evidences(self, source_id: Optional[str] = None) -> List[Evidence]:
        with self.db.session() as conn:
            if source_id:
                rows = conn.execute("SELECT * FROM evidences WHERE source_id = ? ORDER BY evidence_id ASC", (source_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM evidences ORDER BY evidence_id ASC").fetchall()
            return [self._row_to_evidence(r) for r in rows]

    def list_evidence_for_claim(self, claim_id: str) -> List[Evidence]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM evidences WHERE supports_claim_id = ? ORDER BY evidence_id ASC", (claim_id,)).fetchall()
            return [self._row_to_evidence(r) for r in rows]

    def get_rq(self, code_or_id: str) -> Optional[ResearchQuestion]:
        return self.get_research_question(code_or_id)

    # -------------------------------------------------------------
    # Ownership Mappings
    # -------------------------------------------------------------
    def save_ownership_mapping(self, mapping: OwnershipMapping) -> OwnershipMapping:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO ownership_mappings (
                    mapping_id, node_code, node_id, claim_id, component_name,
                    ownership, source_ids_json, motivation_source_ids_json, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(mapping_id) DO UPDATE SET
                    node_code=excluded.node_code,
                    node_id=excluded.node_id,
                    claim_id=excluded.claim_id,
                    component_name=excluded.component_name,
                    ownership=excluded.ownership,
                    source_ids_json=excluded.source_ids_json,
                    motivation_source_ids_json=excluded.motivation_source_ids_json,
                    notes=excluded.notes
                """,
                (
                    mapping.mapping_id,
                    mapping.node_code,
                    mapping.node_id,
                    mapping.claim_id,
                    mapping.component_name,
                    mapping.ownership.value,
                    json.dumps(mapping.source_ids),
                    json.dumps(mapping.motivation_source_ids),
                    mapping.notes,
                    mapping.created_at.isoformat(),
                )
            )
        return mapping

    def list_ownership_mappings(
        self,
        node_code: Optional[str] = None,
        ownership: Optional[IntellectualOwnership] = None,
    ) -> List[OwnershipMapping]:
        with self.db.session() as conn:
            query = "SELECT * FROM ownership_mappings WHERE 1=1"
            params: List[Any] = []
            if node_code:
                query += " AND (node_code = ? OR node_code LIKE ?)"
                params.extend([node_code, f"{node_code}.%"])
            if ownership:
                query += " AND ownership = ?"
                params.append(ownership.value)
            query += " ORDER BY node_code ASC, mapping_id ASC"
            rows = conn.execute(query, tuple(params)).fetchall()
            return [
                OwnershipMapping(
                    mapping_id=r["mapping_id"],
                    node_code=r["node_code"],
                    node_id=r["node_id"],
                    claim_id=r["claim_id"],
                    component_name=r["component_name"],
                    ownership=IntellectualOwnership(r["ownership"]),
                    source_ids=json.loads(r["source_ids_json"] or "[]"),
                    motivation_source_ids=json.loads(r["motivation_source_ids_json"] or "[]"),
                    notes=r["notes"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Candidate Contributions
    # -------------------------------------------------------------
    def save_candidate_contribution(self, contrib: CandidateContribution) -> CandidateContribution:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO candidate_contributions (
                    contribution_id, name, description, roadmap_nodes_json,
                    ownership, novelty_status, literature_motivation_json,
                    nearest_prior_work_json, differentiation_notes,
                    verification_status, metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contribution_id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    roadmap_nodes_json=excluded.roadmap_nodes_json,
                    ownership=excluded.ownership,
                    novelty_status=excluded.novelty_status,
                    literature_motivation_json=excluded.literature_motivation_json,
                    nearest_prior_work_json=excluded.nearest_prior_work_json,
                    differentiation_notes=excluded.differentiation_notes,
                    verification_status=excluded.verification_status,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    contrib.contribution_id,
                    contrib.name,
                    contrib.description,
                    json.dumps(contrib.roadmap_nodes),
                    contrib.ownership.value,
                    contrib.novelty_status.value,
                    json.dumps(contrib.literature_motivation),
                    json.dumps(contrib.nearest_prior_work),
                    contrib.differentiation_notes,
                    contrib.verification_status.value,
                    json.dumps(contrib.metadata),
                    contrib.created_at.isoformat(),
                    contrib.updated_at.isoformat(),
                )
            )
        return contrib

    def get_candidate_contribution(self, contribution_id: str) -> Optional[CandidateContribution]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM candidate_contributions WHERE contribution_id = ?", (contribution_id,)).fetchone()
            if not row:
                return None
            return CandidateContribution(
                contribution_id=row["contribution_id"],
                name=row["name"],
                description=row["description"],
                roadmap_nodes=json.loads(row["roadmap_nodes_json"] or "[]"),
                ownership=IntellectualOwnership(row["ownership"]),
                novelty_status=NoveltyStatus(row["novelty_status"]),
                literature_motivation=json.loads(row["literature_motivation_json"] or "[]"),
                nearest_prior_work=json.loads(row["nearest_prior_work_json"] or "[]"),
                differentiation_notes=row["differentiation_notes"],
                verification_status=VerificationStatus(row["verification_status"]),
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_candidate_contributions(self) -> List[CandidateContribution]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM candidate_contributions ORDER BY contribution_id ASC").fetchall()
            return [
                CandidateContribution(
                    contribution_id=r["contribution_id"],
                    name=r["name"],
                    description=r["description"],
                    roadmap_nodes=json.loads(r["roadmap_nodes_json"] or "[]"),
                    ownership=IntellectualOwnership(r["ownership"]),
                    novelty_status=NoveltyStatus(r["novelty_status"]),
                    literature_motivation=json.loads(r["literature_motivation_json"] or "[]"),
                    nearest_prior_work=json.loads(r["nearest_prior_work_json"] or "[]"),
                    differentiation_notes=r["differentiation_notes"],
                    verification_status=VerificationStatus(r["verification_status"]),
                    metadata=json.loads(r["metadata_json"] or "{}"),
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Citation Firewall Rules
    # -------------------------------------------------------------
    def save_citation_firewall_rule(self, rule: CitationFirewallRule) -> CitationFirewallRule:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO citation_firewall_rules (
                    source_id, citation_key, status, source_exists,
                    metadata_verified, claim_evidence_link_exists,
                    locator_exists, support_type, blocking_reasons_json,
                    audit_notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    citation_key=excluded.citation_key,
                    status=excluded.status,
                    source_exists=excluded.source_exists,
                    metadata_verified=excluded.metadata_verified,
                    claim_evidence_link_exists=excluded.claim_evidence_link_exists,
                    locator_exists=excluded.locator_exists,
                    support_type=excluded.support_type,
                    blocking_reasons_json=excluded.blocking_reasons_json,
                    audit_notes=excluded.audit_notes,
                    updated_at=excluded.updated_at
                """,
                (
                    rule.source_id,
                    rule.citation_key,
                    rule.status.value,
                    1 if rule.source_exists else 0,
                    1 if rule.metadata_verified else 0,
                    1 if rule.claim_evidence_link_exists else 0,
                    1 if rule.locator_exists else 0,
                    rule.support_type.value,
                    json.dumps(rule.blocking_reasons),
                    rule.audit_notes,
                    rule.created_at.isoformat(),
                    rule.updated_at.isoformat(),
                )
            )
        return rule

    def get_citation_firewall_rule(self, source_id_or_key: str) -> Optional[CitationFirewallRule]:
        with self.db.session() as conn:
            row = conn.execute(
                "SELECT * FROM citation_firewall_rules WHERE source_id = ? OR citation_key = ?",
                (source_id_or_key, source_id_or_key)
            ).fetchone()
            if not row:
                return None
            return CitationFirewallRule(
                source_id=row["source_id"],
                citation_key=row["citation_key"],
                status=CitationFirewallStatus(row["status"]),
                source_exists=bool(row["source_exists"]),
                metadata_verified=bool(row["metadata_verified"]),
                claim_evidence_link_exists=bool(row["claim_evidence_link_exists"]),
                locator_exists=bool(row["locator_exists"]),
                support_type=SupportType(row["support_type"]),
                blocking_reasons=json.loads(row["blocking_reasons_json"] or "[]"),
                audit_notes=row["audit_notes"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_citation_firewall_rules(self, status: Optional[CitationFirewallStatus] = None) -> List[CitationFirewallRule]:
        with self.db.session() as conn:
            if status:
                rows = conn.execute("SELECT * FROM citation_firewall_rules WHERE status = ? ORDER BY source_id ASC", (status.value,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM citation_firewall_rules ORDER BY source_id ASC").fetchall()
            return [
                CitationFirewallRule(
                    source_id=r["source_id"],
                    citation_key=r["citation_key"],
                    status=CitationFirewallStatus(r["status"]),
                    source_exists=bool(r["source_exists"]),
                    metadata_verified=bool(r["metadata_verified"]),
                    claim_evidence_link_exists=bool(r["claim_evidence_link_exists"]),
                    locator_exists=bool(r["locator_exists"]),
                    support_type=SupportType(r["support_type"]),
                    blocking_reasons=json.loads(r["blocking_reasons_json"] or "[]"),
                    audit_notes=r["audit_notes"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Reference Map Specification
    # -------------------------------------------------------------
    def save_reference_map(self, spec: ReferenceMapSpecification) -> ReferenceMapSpecification:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO reference_maps (reference_map_id, version, compatible_roadmap_version, title, summary, sha256_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(reference_map_id) DO UPDATE SET
                    version=excluded.version,
                    compatible_roadmap_version=excluded.compatible_roadmap_version,
                    title=excluded.title,
                    summary=excluded.summary,
                    sha256_hash=excluded.sha256_hash,
                    updated_at=excluded.updated_at
                """,
                (
                    spec.reference_map_id,
                    spec.version,
                    spec.compatible_roadmap_version,
                    spec.title,
                    spec.summary,
                    spec.sha256_hash,
                    spec.created_at.isoformat(),
                    spec.updated_at.isoformat(),
                )
            )

        # Ingest child entities
        for src in spec.sources:
            self.save_source(src)
        for evd in spec.evidences:
            self.save_evidence(evd)
        for clm in spec.claims:
            self.save_claim(clm)
        for rel in spec.claim_relations:
            self.save_claim_relation(rel)
        for own in spec.ownership_mappings:
            self.save_ownership_mapping(own)
        for cand in spec.contributions:
            self.save_candidate_contribution(cand)
        for fw in spec.firewall_rules:
            self.save_citation_firewall_rule(fw)

        return spec

    def get_reference_map(self, reference_map_id: str = "REF-000001") -> Optional[ReferenceMapSpecification]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM reference_maps WHERE reference_map_id = ?", (reference_map_id,)).fetchone()
            if not row:
                return None
            return ReferenceMapSpecification(
                reference_map_id=row["reference_map_id"],
                version=row["version"],
                compatible_roadmap_version=row["compatible_roadmap_version"],
                title=row["title"],
                summary=row["summary"] or "",
                sha256_hash=row["sha256_hash"],
                sources=self.list_sources(),
                evidences=self.list_evidences(),
                claims=self.list_claims(),
                claim_relations=self.list_claim_relations(),
                ownership_mappings=self.list_ownership_mappings(),
                contributions=self.list_candidate_contributions(),
                firewall_rules=self.list_citation_firewall_rules(),
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
            self._index_fts_on_conn(
                conn=conn,
                entity_id=claim.claim_id,
                entity_type="CLAIM",
                title=f"Claim: {claim.statement[:60]}...",
                body=f"{claim.statement} {claim.scope or ''} {claim.falsification_conditions or ''}",
                tags=f"{claim.ownership.value} {claim.claim_type.value}",
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

    def save_claim_relation(self, relation: ClaimRelation) -> ClaimRelation:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO claim_relations (relation_id, source_claim_id, target_claim_id, relation_type, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(relation_id) DO UPDATE SET
                    source_claim_id=excluded.source_claim_id,
                    target_claim_id=excluded.target_claim_id,
                    relation_type=excluded.relation_type,
                    notes=excluded.notes
                """,
                (
                    relation.relation_id,
                    relation.source_claim_id,
                    relation.target_claim_id,
                    relation.relation_type.value,
                    relation.notes,
                    relation.created_at.isoformat(),
                )
            )
        return relation

    def get_claim_relation(self, relation_id: str) -> Optional[ClaimRelation]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM claim_relations WHERE relation_id = ?", (relation_id,)).fetchone()
            if not row:
                return None
            return ClaimRelation(
                relation_id=row["relation_id"],
                source_claim_id=row["source_claim_id"],
                target_claim_id=row["target_claim_id"],
                relation_type=ArgumentRelationType(row["relation_type"]),
                notes=row["notes"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_claim_relations(self, claim_id: Optional[str] = None) -> List[ClaimRelation]:
        with self.db.session() as conn:
            if claim_id:
                rows = conn.execute(
                    "SELECT * FROM claim_relations WHERE source_claim_id = ? OR target_claim_id = ? ORDER BY relation_id ASC",
                    (claim_id, claim_id)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM claim_relations ORDER BY relation_id ASC").fetchall()
            return [
                ClaimRelation(
                    relation_id=r["relation_id"],
                    source_claim_id=r["source_claim_id"],
                    target_claim_id=r["target_claim_id"],
                    relation_type=ArgumentRelationType(r["relation_type"]),
                    notes=r["notes"],
                    created_at=datetime.fromisoformat(r["created_at"]),
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
    # Decisions & Contradictions (Prompt 4, Section 31)
    # -------------------------------------------------------------
    def save_decision(self, dec: DecisionRecord) -> DecisionRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO decision_records (
                    decision_id, title, status, context, decision, rationale,
                    alternatives_considered_json, evidence_ids_json, consequences,
                    target_affected_entities_json, related_nodes_json,
                    related_claims_json, related_experiments_json, supersedes_id,
                    superseded_by_id, diff_summary, actor, made_at, metadata_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET
                    title=excluded.title,
                    status=excluded.status,
                    context=excluded.context,
                    decision=excluded.decision,
                    rationale=excluded.rationale,
                    alternatives_considered_json=excluded.alternatives_considered_json,
                    evidence_ids_json=excluded.evidence_ids_json,
                    consequences=excluded.consequences,
                    target_affected_entities_json=excluded.target_affected_entities_json,
                    related_nodes_json=excluded.related_nodes_json,
                    related_claims_json=excluded.related_claims_json,
                    related_experiments_json=excluded.related_experiments_json,
                    supersedes_id=excluded.supersedes_id,
                    superseded_by_id=excluded.superseded_by_id,
                    diff_summary=excluded.diff_summary,
                    actor=excluded.actor,
                    made_at=excluded.made_at,
                    metadata_json=excluded.metadata_json
                """,
                (
                    dec.decision_id,
                    dec.title,
                    dec.status.value if hasattr(dec.status, "value") else str(dec.status),
                    dec.context,
                    dec.decision,
                    dec.rationale,
                    json.dumps(dec.alternatives_considered),
                    json.dumps(dec.evidence_ids),
                    dec.consequences,
                    json.dumps(dec.target_affected_entities),
                    json.dumps(dec.related_nodes),
                    json.dumps(dec.related_claims),
                    json.dumps(dec.related_experiments),
                    dec.supersedes_id,
                    dec.superseded_by_id,
                    dec.diff_summary,
                    dec.actor,
                    dec.made_at.isoformat(),
                    json.dumps(dec.metadata),
                    dec.created_at.isoformat(),
                )
            )
            # Index into FTS using active connection
            self._index_fts_on_conn(
                conn=conn,
                entity_id=dec.decision_id,
                entity_type="DECISION",
                title=dec.title,
                body=f"{dec.decision} {dec.rationale} {dec.context}",
                tags=" ".join(dec.target_affected_entities + dec.related_nodes),
            )
        return dec

    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM decision_records WHERE decision_id = ?", (decision_id,)).fetchone()
            if not row:
                return None
            return self._row_to_decision(row)

    def _row_to_decision(self, row: Any) -> DecisionRecord:
        status_val = row["status"]
        status_enum = DecisionStatus(status_val) if status_val in DecisionStatus.__members__.values() else DecisionStatus.ACCEPTED
        return DecisionRecord(
            decision_id=row["decision_id"],
            title=row["title"],
            status=status_enum,
            context=row["context"],
            decision=row["decision"],
            rationale=row["rationale"] or "",
            alternatives_considered=json.loads(row["alternatives_considered_json"] or "[]"),
            evidence_ids=json.loads(row["evidence_ids_json"] or "[]"),
            consequences=row["consequences"],
            target_affected_entities=json.loads(row["target_affected_entities_json"] or "[]"),
            related_nodes=json.loads(row["related_nodes_json"] or "[]"),
            related_claims=json.loads(row["related_claims_json"] or "[]"),
            related_experiments=json.loads(row["related_experiments_json"] or "[]"),
            supersedes_id=row["supersedes_id"],
            superseded_by_id=row["superseded_by_id"],
            diff_summary=row["diff_summary"],
            actor=row["actor"] or "HUMAN_ARCHITECT_OR_AGENT",
            made_at=datetime.fromisoformat(row["made_at"]) if row["made_at"] else datetime.fromisoformat(row["created_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            metadata=json.loads(row["metadata_json"] or "{}"),
        )

    def list_decisions(self, status: Optional[DecisionStatus] = None) -> List[DecisionRecord]:
        with self.db.session() as conn:
            if status:
                rows = conn.execute("SELECT * FROM decision_records WHERE status = ? ORDER BY made_at DESC", (status.value,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM decision_records ORDER BY made_at DESC").fetchall()
            return [self._row_to_decision(r) for r in rows]

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

    def get_contradiction(self, contradiction_id: str) -> Optional[ContradictionRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM contradiction_records WHERE contradiction_id = ?", (contradiction_id,)).fetchone()
            if not row:
                return None
            return ContradictionRecord(
                contradiction_id=row["contradiction_id"],
                claim_a_id=row["claim_a_id"],
                claim_b_id=row["claim_b_id"],
                description=row["description"],
                domain_or_scope_divergence=row["domain_or_scope_divergence"],
                resolution_status=row["resolution_status"],
                resolution_notes=row["resolution_notes"],
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_contradictions(self) -> List[ContradictionRecord]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM contradiction_records ORDER BY contradiction_id ASC").fetchall()
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
    # Memory Records (M0..M5)
    # -------------------------------------------------------------
    def save_memory(self, mem: MemoryRecord) -> MemoryRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO memory_records (
                    memory_id, tier, record_type, promotion_state, topic, summary,
                    content, reference_type, reference_id, associated_entity_ids_json,
                    ownership, epistemic_status, is_generated_summary, supersedes_id,
                    superseded_by_id, is_stale, review_required, last_verified_at,
                    privacy, actor, session_id, confidence_category, confidence_basis,
                    tags_json, importance, metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    tier=excluded.tier,
                    record_type=excluded.record_type,
                    promotion_state=excluded.promotion_state,
                    topic=excluded.topic,
                    summary=excluded.summary,
                    content=excluded.content,
                    reference_type=excluded.reference_type,
                    reference_id=excluded.reference_id,
                    associated_entity_ids_json=excluded.associated_entity_ids_json,
                    ownership=excluded.ownership,
                    epistemic_status=excluded.epistemic_status,
                    is_generated_summary=excluded.is_generated_summary,
                    supersedes_id=excluded.supersedes_id,
                    superseded_by_id=excluded.superseded_by_id,
                    is_stale=excluded.is_stale,
                    review_required=excluded.review_required,
                    last_verified_at=excluded.last_verified_at,
                    privacy=excluded.privacy,
                    actor=excluded.actor,
                    session_id=excluded.session_id,
                    confidence_category=excluded.confidence_category,
                    confidence_basis=excluded.confidence_basis,
                    tags_json=excluded.tags_json,
                    importance=excluded.importance,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    mem.memory_id,
                    mem.tier.value,
                    mem.record_type.value if hasattr(mem.record_type, "value") else str(mem.record_type),
                    mem.promotion_state.value if hasattr(mem.promotion_state, "value") else str(mem.promotion_state),
                    mem.topic,
                    mem.summary,
                    mem.content,
                    mem.reference_type,
                    mem.reference_id,
                    json.dumps(mem.associated_entity_ids),
                    mem.ownership.value if hasattr(mem.ownership, "value") else str(mem.ownership),
                    mem.epistemic_status.value if hasattr(mem.epistemic_status, "value") else str(mem.epistemic_status),
                    1 if mem.is_generated_summary else 0,
                    mem.supersedes_id,
                    mem.superseded_by_id,
                    1 if mem.is_stale else 0,
                    1 if mem.review_required else 0,
                    mem.last_verified_at.isoformat() if mem.last_verified_at else None,
                    mem.privacy.value if hasattr(mem.privacy, "value") else str(mem.privacy),
                    mem.actor,
                    mem.session_id,
                    mem.confidence_category,
                    mem.confidence_basis,
                    json.dumps(mem.tags),
                    mem.importance,
                    json.dumps(mem.metadata),
                    mem.created_at.isoformat(),
                    mem.updated_at.isoformat(),
                )
            )
            # Index into FTS using active connection
            self._index_fts_on_conn(
                conn=conn,
                entity_id=mem.memory_id,
                entity_type=mem.record_type.value if hasattr(mem.record_type, "value") else "MEMORY",
                title=mem.topic,
                body=f"{mem.summary} {mem.content or ''}",
                tags=" ".join(mem.tags + mem.associated_entity_ids),
            )
        return mem

    def _row_to_memory(self, row: Any) -> MemoryRecord:
        tier_val = row["tier"]
        tier_enum = MemoryTier(tier_val) if tier_val in MemoryTier.__members__.values() else MemoryTier.M2_SEMANTIC
        rec_type_val = row["record_type"] or "OBSERVATION"
        rec_type_enum = MemoryRecordType(rec_type_val) if rec_type_val in MemoryRecordType.__members__.values() else MemoryRecordType.OBSERVATION
        promo_val = row["promotion_state"] or "CONSOLIDATED"
        promo_enum = MemoryPromotionState(promo_val) if promo_val in MemoryPromotionState.__members__.values() else MemoryPromotionState.CONSOLIDATED
        ownership_val = row["ownership"] or "OURS"
        ownership_enum = IntellectualOwnership(ownership_val) if ownership_val in IntellectualOwnership.__members__.values() else IntellectualOwnership.OURS
        epistemic_val = row["epistemic_status"] or "SUPPORTED"
        epistemic_enum = EpistemicStatus(epistemic_val) if epistemic_val in EpistemicStatus.__members__.values() else EpistemicStatus.SUPPORTED

        return MemoryRecord(
            memory_id=row["memory_id"],
            tier=tier_enum,
            record_type=rec_type_enum,
            promotion_state=promo_enum,
            topic=row["topic"],
            summary=row["summary"] or row["content"] or "",
            content=row["content"],
            reference_type=row["reference_type"],
            reference_id=row["reference_id"],
            associated_entity_ids=json.loads(row["associated_entity_ids_json"] or "[]"),
            ownership=ownership_enum,
            epistemic_status=epistemic_enum,
            is_generated_summary=bool(row["is_generated_summary"]),
            supersedes_id=row["supersedes_id"],
            superseded_by_id=row["superseded_by_id"],
            is_stale=bool(row["is_stale"]),
            review_required=bool(row["review_required"]),
            last_verified_at=datetime.fromisoformat(row["last_verified_at"]) if row["last_verified_at"] else None,
            privacy=PrivacyClassification(row["privacy"]) if row["privacy"] in PrivacyClassification.__members__.values() else PrivacyClassification.INTERNAL,
            actor=row["actor"] or "RESEARCH_AGENT",
            session_id=row["session_id"],
            confidence_category=row["confidence_category"] or "HIGH",
            confidence_basis=row["confidence_basis"],
            tags=json.loads(row["tags_json"] or "[]"),
            importance=row["importance"],
            metadata=json.loads(row["metadata_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM memory_records WHERE memory_id = ?", (memory_id,)).fetchone()
            if not row:
                return None
            return self._row_to_memory(row)

    def list_memories(
        self,
        tier: Optional[MemoryTier] = None,
        record_type: Optional[MemoryRecordType] = None,
        promotion_state: Optional[MemoryPromotionState] = None,
    ) -> List[MemoryRecord]:
        with self.db.session() as conn:
            query = "SELECT * FROM memory_records WHERE 1=1"
            params: List[Any] = []
            if tier:
                query += " AND tier = ?"
                params.append(tier.value)
            if record_type:
                query += " AND record_type = ?"
                params.append(record_type.value)
            if promotion_state:
                query += " AND promotion_state = ?"
                params.append(promotion_state.value)
            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            return [self._row_to_memory(r) for r in rows]

    # -------------------------------------------------------------
    # Episodes (M3)
    # -------------------------------------------------------------
    def save_episode(self, ep: EpisodeRecord) -> EpisodeRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO episodes (
                    episode_id, session_id, timestamp, actor, action, object_reference,
                    outcome, status, related_node_code, related_rq_id, related_hyp_id,
                    related_artifact_ids_json, provenance_details_json, tags_json,
                    is_failure, failure_reason, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(episode_id) DO UPDATE SET
                    session_id=excluded.session_id,
                    timestamp=excluded.timestamp,
                    actor=excluded.actor,
                    action=excluded.action,
                    object_reference=excluded.object_reference,
                    outcome=excluded.outcome,
                    status=excluded.status,
                    related_node_code=excluded.related_node_code,
                    related_rq_id=excluded.related_rq_id,
                    related_hyp_id=excluded.related_hyp_id,
                    related_artifact_ids_json=excluded.related_artifact_ids_json,
                    provenance_details_json=excluded.provenance_details_json,
                    tags_json=excluded.tags_json,
                    is_failure=excluded.is_failure,
                    failure_reason=excluded.failure_reason
                """,
                (
                    ep.episode_id,
                    ep.session_id,
                    ep.timestamp.isoformat(),
                    ep.actor,
                    ep.action,
                    ep.object_reference,
                    ep.outcome,
                    ep.status.value if hasattr(ep.status, "value") else str(ep.status),
                    ep.related_node_code,
                    ep.related_rq_id,
                    ep.related_hyp_id,
                    json.dumps(ep.related_artifact_ids),
                    json.dumps(ep.provenance_details),
                    json.dumps(ep.tags),
                    1 if ep.is_failure else 0,
                    ep.failure_reason,
                    ep.created_at.isoformat(),
                )
            )
            # Index into FTS using active connection
            self._index_fts_on_conn(
                conn=conn,
                entity_id=ep.episode_id,
                entity_type="EPISODE",
                title=f"Episode: {ep.action} on {ep.object_reference or 'general'}",
                body=f"{ep.outcome} {ep.failure_reason or ''}",
                tags=" ".join(ep.tags + ([ep.related_node_code] if ep.related_node_code else [])),
            )
        return ep

    def get_episode(self, episode_id: str) -> Optional[EpisodeRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM episodes WHERE episode_id = ?", (episode_id,)).fetchone()
            if not row:
                return None
            return self._row_to_episode(row)

    def _row_to_episode(self, row: Any) -> EpisodeRecord:
        st_val = row["status"]
        st_enum = EpisodeStatus(st_val) if st_val in EpisodeStatus.__members__.values() else EpisodeStatus.COMPLETED
        return EpisodeRecord(
            episode_id=row["episode_id"],
            session_id=row["session_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            actor=row["actor"],
            action=row["action"],
            object_reference=row["object_reference"],
            outcome=row["outcome"],
            status=st_enum,
            related_node_code=row["related_node_code"],
            related_rq_id=row["related_rq_id"],
            related_hyp_id=row["related_hyp_id"],
            related_artifact_ids=json.loads(row["related_artifact_ids_json"] or "[]"),
            provenance_details=json.loads(row["provenance_details_json"] or "{}"),
            tags=json.loads(row["tags_json"] or "[]"),
            is_failure=bool(row["is_failure"]),
            failure_reason=row["failure_reason"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_episodes(self, session_id: Optional[str] = None, only_failures: bool = False) -> List[EpisodeRecord]:
        with self.db.session() as conn:
            query = "SELECT * FROM episodes WHERE 1=1"
            params: List[Any] = []
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            if only_failures:
                query += " AND is_failure = 1"
            query += " ORDER BY timestamp DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            return [self._row_to_episode(r) for r in rows]

    # -------------------------------------------------------------
    # Open Questions
    # -------------------------------------------------------------
    def save_open_question(self, oq: OpenQuestion) -> OpenQuestion:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO open_questions (
                    question_id, question, related_rq_id, related_hyp_id, related_node_code,
                    why_open, required_evidence, proposed_experiment, priority, status,
                    resolution_notes, resolved_by_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(question_id) DO UPDATE SET
                    question=excluded.question,
                    related_rq_id=excluded.related_rq_id,
                    related_hyp_id=excluded.related_hyp_id,
                    related_node_code=excluded.related_node_code,
                    why_open=excluded.why_open,
                    required_evidence=excluded.required_evidence,
                    proposed_experiment=excluded.proposed_experiment,
                    priority=excluded.priority,
                    status=excluded.status,
                    resolution_notes=excluded.resolution_notes,
                    resolved_by_id=excluded.resolved_by_id,
                    updated_at=excluded.updated_at
                """,
                (
                    oq.question_id,
                    oq.question,
                    oq.related_rq_id,
                    oq.related_hyp_id,
                    oq.related_node_code,
                    oq.why_open,
                    oq.required_evidence,
                    oq.proposed_experiment,
                    oq.priority,
                    oq.status.value if hasattr(oq.status, "value") else str(oq.status),
                    oq.resolution_notes,
                    oq.resolved_by_id,
                    oq.created_at.isoformat(),
                    oq.updated_at.isoformat(),
                )
            )
            # Index into FTS using active connection
            self._index_fts_on_conn(
                conn=conn,
                entity_id=oq.question_id,
                entity_type="OPEN_QUESTION",
                title=f"Open Question: {oq.question[:60]}...",
                body=f"{oq.question} {oq.why_open} {oq.required_evidence}",
                tags=f"{oq.priority} {oq.status.value}",
            )
        return oq

    def get_open_question(self, question_id: str) -> Optional[OpenQuestion]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM open_questions WHERE question_id = ?", (question_id,)).fetchone()
            if not row:
                return None
            st_val = row["status"]
            st_enum = OpenQuestionStatus(st_val) if st_val in OpenQuestionStatus.__members__.values() else OpenQuestionStatus.OPEN
            return OpenQuestion(
                question_id=row["question_id"],
                question=row["question"],
                related_rq_id=row["related_rq_id"],
                related_hyp_id=row["related_hyp_id"],
                related_node_code=row["related_node_code"],
                why_open=row["why_open"],
                required_evidence=row["required_evidence"],
                proposed_experiment=row["proposed_experiment"],
                priority=row["priority"] or "HIGH",
                status=st_enum,
                resolution_notes=row["resolution_notes"],
                resolved_by_id=row["resolved_by_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_open_questions(self, status: Optional[OpenQuestionStatus] = None) -> List[OpenQuestion]:
        with self.db.session() as conn:
            if status:
                rows = conn.execute("SELECT * FROM open_questions WHERE status = ? ORDER BY created_at DESC", (status.value,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM open_questions ORDER BY created_at DESC").fetchall()
            results = []
            for r in rows:
                st_val = r["status"]
                st_enum = OpenQuestionStatus(st_val) if st_val in OpenQuestionStatus.__members__.values() else OpenQuestionStatus.OPEN
                results.append(
                    OpenQuestion(
                        question_id=r["question_id"],
                        question=r["question"],
                        related_rq_id=r["related_rq_id"],
                        related_hyp_id=r["related_hyp_id"],
                        related_node_code=r["related_node_code"],
                        why_open=r["why_open"],
                        required_evidence=r["required_evidence"],
                        proposed_experiment=r["proposed_experiment"],
                        priority=r["priority"] or "HIGH",
                        status=st_enum,
                        resolution_notes=r["resolution_notes"],
                        resolved_by_id=r["resolved_by_id"],
                        created_at=datetime.fromisoformat(r["created_at"]),
                        updated_at=datetime.fromisoformat(r["updated_at"]),
                    )
                )
            return results

    # -------------------------------------------------------------
    # Lessons Learned
    # -------------------------------------------------------------
    def save_lesson_learned(self, les: LessonLearned) -> LessonLearned:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO lessons_learned (
                    lesson_id, title, statement, originating_episode_id, experiment_run_id,
                    evidence_ids_json, scope, actionable_recommendations_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(lesson_id) DO UPDATE SET
                    title=excluded.title,
                    statement=excluded.statement,
                    originating_episode_id=excluded.originating_episode_id,
                    experiment_run_id=excluded.experiment_run_id,
                    evidence_ids_json=excluded.evidence_ids_json,
                    scope=excluded.scope,
                    actionable_recommendations_json=excluded.actionable_recommendations_json
                """,
                (
                    les.lesson_id,
                    les.title,
                    les.statement,
                    les.originating_episode_id,
                    les.experiment_run_id,
                    json.dumps(les.evidence_ids),
                    les.scope,
                    json.dumps(les.actionable_recommendations),
                    les.created_at.isoformat(),
                )
            )
            # Index into FTS using active connection
            self._index_fts_on_conn(
                conn=conn,
                entity_id=les.lesson_id,
                entity_type="LESSON",
                title=les.title,
                body=f"{les.statement} {' '.join(les.actionable_recommendations)}",
                tags=" ".join(les.evidence_ids),
            )
        return les

    def get_lesson_learned(self, lesson_id: str) -> Optional[LessonLearned]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM lessons_learned WHERE lesson_id = ?", (lesson_id,)).fetchone()
            if not row:
                return None
            return LessonLearned(
                lesson_id=row["lesson_id"],
                title=row["title"],
                statement=row["statement"],
                originating_episode_id=row["originating_episode_id"],
                experiment_run_id=row["experiment_run_id"],
                evidence_ids=json.loads(row["evidence_ids_json"] or "[]"),
                scope=row["scope"],
                actionable_recommendations=json.loads(row["actionable_recommendations_json"] or "[]"),
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_lessons_learned(self) -> List[LessonLearned]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM lessons_learned ORDER BY created_at DESC").fetchall()
            return [
                LessonLearned(
                    lesson_id=r["lesson_id"],
                    title=r["title"],
                    statement=r["statement"],
                    originating_episode_id=r["originating_episode_id"],
                    experiment_run_id=r["experiment_run_id"],
                    evidence_ids=json.loads(r["evidence_ids_json"] or "[]"),
                    scope=r["scope"],
                    actionable_recommendations=json.loads(r["actionable_recommendations_json"] or "[]"),
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Research Sessions
    # -------------------------------------------------------------
    def save_research_session(self, sess: SessionRecord) -> SessionRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO research_sessions (
                    session_id, start_time, end_time, objective, active_roadmap_nodes_json,
                    actions_summary_json, decisions_made_json, files_modified_json,
                    experiments_run_json, sources_added_json, claims_changed_json,
                    unresolved_items_json, handoff_summary, git_commit_hash, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    objective=excluded.objective,
                    active_roadmap_nodes_json=excluded.active_roadmap_nodes_json,
                    actions_summary_json=excluded.actions_summary_json,
                    decisions_made_json=excluded.decisions_made_json,
                    files_modified_json=excluded.files_modified_json,
                    experiments_run_json=excluded.experiments_run_json,
                    sources_added_json=excluded.sources_added_json,
                    claims_changed_json=excluded.claims_changed_json,
                    unresolved_items_json=excluded.unresolved_items_json,
                    handoff_summary=excluded.handoff_summary,
                    git_commit_hash=excluded.git_commit_hash,
                    updated_at=excluded.updated_at
                """,
                (
                    sess.session_id,
                    sess.start_time.isoformat(),
                    sess.end_time.isoformat() if sess.end_time else None,
                    sess.objective,
                    json.dumps(sess.active_roadmap_nodes),
                    json.dumps(sess.actions_summary),
                    json.dumps(sess.decisions_made),
                    json.dumps(sess.files_modified),
                    json.dumps(sess.experiments_run),
                    json.dumps(sess.sources_added),
                    json.dumps(sess.claims_changed),
                    json.dumps(sess.unresolved_items),
                    sess.handoff_summary,
                    sess.git_commit_hash,
                    sess.created_at.isoformat(),
                    sess.updated_at.isoformat(),
                )
            )
        return sess

    def get_research_session(self, session_id: str) -> Optional[SessionRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM research_sessions WHERE session_id = ?", (session_id,)).fetchone()
            if not row:
                return None
            return SessionRecord(
                session_id=row["session_id"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                objective=row["objective"],
                active_roadmap_nodes=json.loads(row["active_roadmap_nodes_json"] or "[]"),
                actions_summary=json.loads(row["actions_summary_json"] or "[]"),
                decisions_made=json.loads(row["decisions_made_json"] or "[]"),
                files_modified=json.loads(row["files_modified_json"] or "[]"),
                experiments_run=json.loads(row["experiments_run_json"] or "[]"),
                sources_added=json.loads(row["sources_added_json"] or "[]"),
                claims_changed=json.loads(row["claims_changed_json"] or "[]"),
                unresolved_items=json.loads(row["unresolved_items_json"] or "[]"),
                handoff_summary=row["handoff_summary"],
                git_commit_hash=row["git_commit_hash"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_research_sessions(self) -> List[SessionRecord]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM research_sessions ORDER BY start_time DESC").fetchall()
            return [
                SessionRecord(
                    session_id=r["session_id"],
                    start_time=datetime.fromisoformat(r["start_time"]),
                    end_time=datetime.fromisoformat(r["end_time"]) if r["end_time"] else None,
                    objective=r["objective"],
                    active_roadmap_nodes=json.loads(r["active_roadmap_nodes_json"] or "[]"),
                    actions_summary=json.loads(r["actions_summary_json"] or "[]"),
                    decisions_made=json.loads(r["decisions_made_json"] or "[]"),
                    files_modified=json.loads(r["files_modified_json"] or "[]"),
                    experiments_run=json.loads(r["experiments_run_json"] or "[]"),
                    sources_added=json.loads(r["sources_added_json"] or "[]"),
                    claims_changed=json.loads(r["claims_changed_json"] or "[]"),
                    unresolved_items=json.loads(r["unresolved_items_json"] or "[]"),
                    handoff_summary=r["handoff_summary"],
                    git_commit_hash=r["git_commit_hash"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Skills (M5 Procedural)
    # -------------------------------------------------------------
    def save_skill(self, sk: SkillRecord) -> SkillRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO skills (
                    skill_id, name, version, status, category, description,
                    inputs_json, outputs_json, preconditions_json, invariants_json,
                    verification_procedure, file_path, dependencies_json,
                    metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(skill_id) DO UPDATE SET
                    name=excluded.name,
                    version=excluded.version,
                    status=excluded.status,
                    category=excluded.category,
                    description=excluded.description,
                    inputs_json=excluded.inputs_json,
                    outputs_json=excluded.outputs_json,
                    preconditions_json=excluded.preconditions_json,
                    invariants_json=excluded.invariants_json,
                    verification_procedure=excluded.verification_procedure,
                    file_path=excluded.file_path,
                    dependencies_json=excluded.dependencies_json,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    sk.skill_id,
                    sk.name,
                    sk.version,
                    sk.status.value if hasattr(sk.status, "value") else str(sk.status),
                    sk.category,
                    sk.description,
                    json.dumps(sk.inputs),
                    json.dumps(sk.outputs),
                    json.dumps(sk.preconditions),
                    json.dumps(sk.invariants),
                    sk.verification_procedure,
                    sk.file_path,
                    json.dumps(sk.dependencies),
                    json.dumps(sk.metadata),
                    sk.created_at.isoformat(),
                    sk.updated_at.isoformat(),
                )
            )
        return sk

    def get_skill(self, skill_id: str) -> Optional[SkillRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM skills WHERE skill_id = ?", (skill_id,)).fetchone()
            if not row:
                return None
            st_val = row["status"]
            st_enum = SkillStatus(st_val) if st_val in SkillStatus.__members__.values() else SkillStatus.ACTIVE
            return SkillRecord(
                skill_id=row["skill_id"],
                name=row["name"],
                version=row["version"] or "1.0",
                status=st_enum,
                category=row["category"],
                description=row["description"],
                inputs=json.loads(row["inputs_json"] or "[]"),
                outputs=json.loads(row["outputs_json"] or "[]"),
                preconditions=json.loads(row["preconditions_json"] or "[]"),
                invariants=json.loads(row["invariants_json"] or "[]"),
                verification_procedure=row["verification_procedure"],
                file_path=row["file_path"],
                dependencies=json.loads(row["dependencies_json"] or "[]"),
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_skills(self) -> List[SkillRecord]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM skills ORDER BY skill_id ASC").fetchall()
            results = []
            for r in rows:
                st_val = r["status"]
                st_enum = SkillStatus(st_val) if st_val in SkillStatus.__members__.values() else SkillStatus.ACTIVE
                results.append(
                    SkillRecord(
                        skill_id=r["skill_id"],
                        name=r["name"],
                        version=r["version"] or "1.0",
                        status=st_enum,
                        category=r["category"],
                        description=r["description"],
                        inputs=json.loads(r["inputs_json"] or "[]"),
                        outputs=json.loads(r["outputs_json"] or "[]"),
                        preconditions=json.loads(r["preconditions_json"] or "[]"),
                        invariants=json.loads(r["invariants_json"] or "[]"),
                        verification_procedure=r["verification_procedure"],
                        file_path=r["file_path"],
                        dependencies=json.loads(r["dependencies_json"] or "[]"),
                        metadata=json.loads(r["metadata_json"] or "{}"),
                        created_at=datetime.fromisoformat(r["created_at"]),
                        updated_at=datetime.fromisoformat(r["updated_at"]),
                    )
                )
            return results

    # -------------------------------------------------------------
    # Status Transitions (Section 8, Section 9)
    # -------------------------------------------------------------
    def save_status_transition(self, trans: StatusTransitionRecord) -> StatusTransitionRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO status_transitions (
                    transition_id, entity_type, entity_id, from_status, to_status,
                    cause, evidence_id, decision_id, actor, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transition_id) DO UPDATE SET
                    entity_type=excluded.entity_type,
                    entity_id=excluded.entity_id,
                    from_status=excluded.from_status,
                    to_status=excluded.to_status,
                    cause=excluded.cause,
                    evidence_id=excluded.evidence_id,
                    decision_id=excluded.decision_id,
                    actor=excluded.actor,
                    timestamp=excluded.timestamp
                """,
                (
                    trans.transition_id,
                    trans.entity_type,
                    trans.entity_id,
                    trans.from_status,
                    trans.to_status,
                    trans.cause,
                    trans.evidence_id,
                    trans.decision_id,
                    trans.actor,
                    trans.timestamp.isoformat(),
                )
            )
        return trans

    def list_status_transitions(self, entity_id: Optional[str] = None) -> List[StatusTransitionRecord]:
        with self.db.session() as conn:
            if entity_id:
                rows = conn.execute(
                    "SELECT * FROM status_transitions WHERE entity_id = ? ORDER BY timestamp ASC",
                    (entity_id,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM status_transitions ORDER BY timestamp ASC").fetchall()
            return [
                StatusTransitionRecord(
                    transition_id=r["transition_id"],
                    entity_type=r["entity_type"],
                    entity_id=r["entity_id"],
                    from_status=r["from_status"],
                    to_status=r["to_status"],
                    cause=r["cause"],
                    evidence_id=r["evidence_id"],
                    decision_id=r["decision_id"],
                    actor=r["actor"],
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Full-Text Search (FTS5) Indexing & Query
    # -------------------------------------------------------------
    def _index_fts_on_conn(self, conn: Any, entity_id: str, entity_type: str, title: str, body: str, tags: str = "") -> None:
        try:
            conn.execute("DELETE FROM memory_fts WHERE entity_id = ?", (entity_id,))
            conn.execute(
                "INSERT INTO memory_fts (entity_id, entity_type, title, body, tags) VALUES (?, ?, ?, ?, ?)",
                (entity_id, entity_type, title, body, tags)
            )
        except Exception:
            pass

    def index_fts_entity(self, entity_id: str, entity_type: str, title: str, body: str, tags: str = "") -> None:
        try:
            with self.db.session() as conn:
                self._index_fts_on_conn(conn, entity_id, entity_type, title, body, tags)
        except Exception:
            pass

    def search_fts(self, query_str: str, entity_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.db.session() as conn:
            # Clean search query for FTS5 syntax
            safe_terms = [f'"{t.replace('"', '')}"' for t in query_str.split() if t.strip()]
            if not safe_terms:
                return []
            match_query = " OR ".join(safe_terms)
            try:
                if entity_type:
                    rows = conn.execute(
                        "SELECT entity_id, entity_type, title, body, tags, rank FROM memory_fts WHERE memory_fts MATCH ? AND entity_type = ? ORDER BY rank LIMIT ?",
                        (match_query, entity_type, limit)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT entity_id, entity_type, title, body, tags, rank FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
                        (match_query, limit)
                    ).fetchall()
                return [dict(r) for r in rows]
            except Exception:
                # Fallback substring search
                fallback_query = "%" + query_str.strip() + "%"
                rows = conn.execute(
                    "SELECT entity_id, entity_type, title, body, tags, 0.0 as rank FROM memory_fts WHERE title LIKE ? OR body LIKE ? OR tags LIKE ? LIMIT ?",
                    (fallback_query, fallback_query, fallback_query, limit)
                ).fetchall()
                return [dict(r) for r in rows]

    def rebuild_fts_index(self) -> int:
        """Rebuild entire FTS5 index from canonical sources, claims, decisions, episodes, lessons, and questions."""
        count = 0
        with self.db.session() as conn:
            try:
                conn.execute("DELETE FROM memory_fts")
            except Exception:
                pass

        # Index Sources
        for s in self.list_sources():
            self.index_fts_entity(
                entity_id=s.source_id,
                entity_type="SOURCE",
                title=s.title,
                body=f"{s.citation_key} {s.venue} {s.notes or ''} {' '.join(s.authors)}",
                tags=" ".join(s.keywords + [r.value for r in s.roles]),
            )
            count += 1

        # Index Claims
        for c in self.list_claims():
            self.index_fts_entity(
                entity_id=c.claim_id,
                entity_type="CLAIM",
                title=f"Claim: {c.statement[:60]}...",
                body=f"{c.statement} {c.scope or ''} {' '.join(c.assumptions)}",
                tags=f"{c.claim_type.value} {c.ownership.value} {c.epistemic_status.value}",
            )
            count += 1

        # Index Decisions
        for d in self.list_decisions():
            self.index_fts_entity(
                entity_id=d.decision_id,
                entity_type="DECISION",
                title=d.title,
                body=f"{d.decision} {d.rationale} {d.context}",
                tags=" ".join(d.target_affected_entities + d.related_nodes),
            )
            count += 1

        # Index Episodes
        for e in self.list_episodes():
            self.index_fts_entity(
                entity_id=e.episode_id,
                entity_type="EPISODE",
                title=f"Episode: {e.action} on {e.object_reference or 'general'}",
                body=f"{e.outcome} {e.failure_reason or ''}",
                tags=" ".join(e.tags + ([e.related_node_code] if e.related_node_code else [])),
            )
            count += 1

        # Index Lessons
        for l in self.list_lessons_learned():
            self.index_fts_entity(
                entity_id=l.lesson_id,
                entity_type="LESSON",
                title=l.title,
                body=f"{l.statement} {' '.join(l.actionable_recommendations)}",
                tags=" ".join(l.evidence_ids),
            )
            count += 1

        # Index Open Questions
        for o in self.list_open_questions():
            self.index_fts_entity(
                entity_id=o.question_id,
                entity_type="OPEN_QUESTION",
                title=f"Open Question: {o.question[:60]}...",
                body=f"{o.question} {o.why_open} {o.required_evidence}",
                tags=f"{o.priority} {o.status.value}",
            )
            count += 1

        # Index Memory Records
        for m in self.list_memories():
            self.index_fts_entity(
                entity_id=m.memory_id,
                entity_type=m.record_type.value if hasattr(m.record_type, "value") else "MEMORY",
                title=m.topic,
                body=f"{m.summary} {m.content or ''}",
                tags=" ".join(m.tags + m.associated_entity_ids),
            )
            count += 1

        return count

    # -------------------------------------------------------------
    # Canonical Roadmap & Execution Graph
    # -------------------------------------------------------------
    def save_roadmap(self, roadmap: ResearchRoadmap) -> ResearchRoadmap:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO roadmaps (roadmap_id, version, title, summary, central_object, sha256_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(roadmap_id) DO UPDATE SET
                    version=excluded.version,
                    title=excluded.title,
                    summary=excluded.summary,
                    central_object=excluded.central_object,
                    sha256_hash=excluded.sha256_hash,
                    updated_at=excluded.updated_at
                """,
                (
                    roadmap.roadmap_id,
                    roadmap.version,
                    roadmap.title,
                    roadmap.summary,
                    roadmap.central_object,
                    roadmap.sha256_hash,
                    roadmap.created_at.isoformat(),
                    roadmap.updated_at.isoformat(),
                )
            )

            # Insert/Update Nodes
            for node in roadmap.nodes:
                conn.execute(
                    """
                    INSERT INTO roadmap_nodes (node_id, roadmap_id, parent_node_id, level, order_index, code, title, canonical_text, expected_role, research_axes_json, methodological_constraints_json, expected_outputs_json, rq_ids_json, hyp_ids_json, status, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(node_id) DO UPDATE SET
                        parent_node_id=excluded.parent_node_id,
                        level=excluded.level,
                        order_index=excluded.order_index,
                        code=excluded.code,
                        title=excluded.title,
                        canonical_text=excluded.canonical_text,
                        expected_role=excluded.expected_role,
                        research_axes_json=excluded.research_axes_json,
                        methodological_constraints_json=excluded.methodological_constraints_json,
                        expected_outputs_json=excluded.expected_outputs_json,
                        rq_ids_json=excluded.rq_ids_json,
                        hyp_ids_json=excluded.hyp_ids_json,
                        status=excluded.status,
                        metadata_json=excluded.metadata_json
                    """,
                    (
                        node.node_id,
                        roadmap.roadmap_id,
                        node.parent_node_id,
                        node.level,
                        node.order_index,
                        node.code,
                        node.title,
                        node.canonical_text,
                        node.expected_role,
                        json.dumps(node.research_axes),
                        json.dumps(node.methodological_constraints),
                        json.dumps(node.expected_outputs),
                        json.dumps(node.rq_ids),
                        json.dumps(node.hyp_ids),
                        node.status,
                        json.dumps(node.metadata),
                    )
                )

            # Insert/Update Questions
            for q in roadmap.questions:
                conn.execute(
                    """
                    INSERT INTO research_questions (rq_id, code, title, canonical_wording_en, canonical_wording_vi, target_aspect, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(rq_id) DO UPDATE SET
                        code=excluded.code,
                        title=excluded.title,
                        canonical_wording_en=excluded.canonical_wording_en,
                        canonical_wording_vi=excluded.canonical_wording_vi,
                        target_aspect=excluded.target_aspect
                    """,
                    (q.rq_id, q.code, q.title, q.canonical_wording_en, q.canonical_wording_vi, q.target_representation_aspect, q.created_at.isoformat())
                )

            # Insert/Update Hypotheses
            for h in roadmap.hypotheses:
                conn.execute(
                    """
                    INSERT INTO hypotheses (hyp_id, code, rq_id, title, statement, falsification_criteria, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(hyp_id) DO UPDATE SET
                        code=excluded.code,
                        rq_id=excluded.rq_id,
                        title=excluded.title,
                        statement=excluded.statement,
                        falsification_criteria=excluded.falsification_criteria
                    """,
                    (h.hyp_id, h.code, h.rq_id, h.title, h.statement, h.falsification_criteria, h.created_at.isoformat())
                )

            # Insert/Update Axes
            for ax in roadmap.axes:
                conn.execute(
                    """
                    INSERT INTO research_axes (axis_id, code, name, problem_summary, path_nodes_json, core_question, core_risks_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(axis_id) DO UPDATE SET
                        code=excluded.code,
                        name=excluded.name,
                        problem_summary=excluded.problem_summary,
                        path_nodes_json=excluded.path_nodes_json,
                        core_question=excluded.core_question,
                        core_risks_json=excluded.core_risks_json
                    """,
                    (ax.axis_id, ax.code, ax.name, ax.problem_summary, json.dumps(ax.path_nodes), ax.core_question, json.dumps(ax.core_risks))
                )

            # Insert/Update Representation Contract
            if roadmap.representation_contract:
                conn.execute(
                    """
                    INSERT INTO representation_contracts (contract_id, preserve_json, invariant_json, exclude_json, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(contract_id) DO UPDATE SET
                        preserve_json=excluded.preserve_json,
                        invariant_json=excluded.invariant_json,
                        exclude_json=excluded.exclude_json
                    """,
                    (
                        "REP-CONTRACT-1.0",
                        json.dumps(roadmap.representation_contract.preserve),
                        json.dumps(roadmap.representation_contract.invariant),
                        json.dumps(roadmap.representation_contract.exclude),
                        datetime.now(timezone.utc).isoformat(),
                    )
                )

            # Insert/Update Negative Controls
            for ctrl in roadmap.controls:
                conn.execute(
                    """
                    INSERT INTO negative_controls (control_id, category, name, description, target_nodes_json)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(control_id) DO UPDATE SET
                        category=excluded.category,
                        name=excluded.name,
                        description=excluded.description,
                        target_nodes_json=excluded.target_nodes_json
                    """,
                    (ctrl.control_id, ctrl.category, ctrl.name, ctrl.description, json.dumps(ctrl.target_nodes))
                )

            # Insert/Update Research Boundaries
            for b in roadmap.boundaries:
                conn.execute(
                    """
                    INSERT INTO research_boundaries (boundary_id, title, statement, rationale, affected_sections_json)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(boundary_id) DO UPDATE SET
                        title=excluded.title,
                        statement=excluded.statement,
                        rationale=excluded.rationale,
                        affected_sections_json=excluded.affected_sections_json
                    """,
                    (b.boundary_id, b.title, b.statement, b.rationale, json.dumps(b.affected_sections))
                )

            # Insert/Update Defensibility Questions
            for dq in roadmap.defensibility_questions:
                conn.execute(
                    """
                    INSERT INTO defensibility_questions (question_id, question_text, target_audit_scope)
                    VALUES (?, ?, ?)
                    ON CONFLICT(question_id) DO UPDATE SET
                        question_text=excluded.question_text,
                        target_audit_scope=excluded.target_audit_scope
                    """,
                    (dq.question_id, dq.question_text, dq.target_audit_scope)
                )

            # Insert/Update Traceability Entries
            for tr in roadmap.traceability_matrix:
                conn.execute(
                    """
                    INSERT INTO traceability_entries (rq_id, code, gap_nodes_json, mechanism_nodes_json, evaluation_nodes_json, hypothesis_ids_json, controls_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(rq_id) DO UPDATE SET
                        code=excluded.code,
                        gap_nodes_json=excluded.gap_nodes_json,
                        mechanism_nodes_json=excluded.mechanism_nodes_json,
                        evaluation_nodes_json=excluded.evaluation_nodes_json,
                        hypothesis_ids_json=excluded.hypothesis_ids_json,
                        controls_json=excluded.controls_json
                    """,
                    (
                        tr.rq_id,
                        tr.code,
                        json.dumps(tr.chapter1_gap_nodes),
                        json.dumps(tr.chapter2_mechanism_nodes),
                        json.dumps(tr.chapter3_evaluation_nodes),
                        json.dumps(tr.hypothesis_ids),
                        json.dumps(tr.controls),
                    )
                )

        return roadmap

    def get_roadmap(self, roadmap_id: str = "ROD-000001") -> Optional[ResearchRoadmap]:
        with self.db.session() as conn:
            r_row = conn.execute("SELECT * FROM roadmaps WHERE roadmap_id = ?", (roadmap_id,)).fetchone()
            if not r_row:
                return None

            nodes = self.list_roadmap_nodes(roadmap_id)
            questions = self.list_research_questions()
            hypotheses = self.list_hypotheses()
            axes = self.list_research_axes()
            contract = self.get_representation_contract()
            controls = self.list_negative_controls()
            boundaries = self.list_research_boundaries()
            dqs = self.list_defensibility_questions()
            traceability = self.get_traceability_matrix()

            return ResearchRoadmap(
                roadmap_id=r_row["roadmap_id"],
                version=r_row["version"],
                title=r_row["title"],
                summary=r_row["summary"] or "",
                central_object=r_row["central_object"] or "feature representation z",
                sha256_hash=r_row["sha256_hash"],
                nodes=nodes,
                questions=questions,
                hypotheses=hypotheses,
                axes=axes,
                representation_contract=contract,
                controls=controls,
                boundaries=boundaries,
                defensibility_questions=dqs,
                traceability_matrix=traceability,
                created_at=datetime.fromisoformat(r_row["created_at"]),
                updated_at=datetime.fromisoformat(r_row["updated_at"]),
            )

    def list_roadmap_nodes(self, roadmap_id: str = "ROD-000001") -> List[ResearchNode]:
        with self.db.session() as conn:
            rows = conn.execute(
                "SELECT * FROM roadmap_nodes WHERE roadmap_id = ? ORDER BY level ASC, order_index ASC",
                (roadmap_id,)
            ).fetchall()
            return [
                ResearchNode(
                    node_id=r["node_id"],
                    parent_node_id=r["parent_node_id"],
                    level=r["level"],
                    order_index=r["order_index"],
                    code=r["code"],
                    title=r["title"],
                    canonical_text=r["canonical_text"],
                    expected_role=r["expected_role"] or "SPECIFICATION",
                    research_axes=json.loads(r["research_axes_json"] or "[]"),
                    methodological_constraints=json.loads(r["methodological_constraints_json"] or "[]"),
                    expected_outputs=json.loads(r["expected_outputs_json"] or "[]"),
                    rq_ids=json.loads(r["rq_ids_json"] or "[]"),
                    hyp_ids=json.loads(r["hyp_ids_json"] or "[]"),
                    status=r["status"] or "SPECIFIED",
                    metadata=json.loads(r["metadata_json"] or "{}"),
                )
                for r in rows
            ]

    def get_roadmap_node_by_code(self, code: str) -> Optional[ResearchNode]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM roadmap_nodes WHERE code = ?", (code,)).fetchone()
            if not row:
                return None
            return ResearchNode(
                node_id=row["node_id"],
                parent_node_id=row["parent_node_id"],
                level=row["level"],
                order_index=row["order_index"],
                code=row["code"],
                title=row["title"],
                canonical_text=row["canonical_text"],
                expected_role=row["expected_role"] or "SPECIFICATION",
                research_axes=json.loads(row["research_axes_json"] or "[]"),
                methodological_constraints=json.loads(row["methodological_constraints_json"] or "[]"),
                expected_outputs=json.loads(row["expected_outputs_json"] or "[]"),
                rq_ids=json.loads(row["rq_ids_json"] or "[]"),
                hyp_ids=json.loads(row["hyp_ids_json"] or "[]"),
                status=row["status"] or "SPECIFIED",
                metadata=json.loads(row["metadata_json"] or "{}"),
            )

    def list_research_questions(self) -> List[ResearchQuestion]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM research_questions ORDER BY rq_id ASC").fetchall()
            return [
                ResearchQuestion(
                    rq_id=r["rq_id"],
                    code=r["code"],
                    title=r["title"],
                    canonical_wording_en=r["canonical_wording_en"],
                    canonical_wording_vi=r["canonical_wording_vi"],
                    target_representation_aspect=r["target_aspect"] or "",
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    def get_research_question(self, rq_id_or_code: str) -> Optional[ResearchQuestion]:
        with self.db.session() as conn:
            row = conn.execute(
                "SELECT * FROM research_questions WHERE rq_id = ? OR code = ?",
                (rq_id_or_code, rq_id_or_code)
            ).fetchone()
            if not row:
                return None
            return ResearchQuestion(
                rq_id=row["rq_id"],
                code=row["code"],
                title=row["title"],
                canonical_wording_en=row["canonical_wording_en"],
                canonical_wording_vi=row["canonical_wording_vi"],
                target_representation_aspect=row["target_aspect"] or "",
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_hypotheses(self) -> List[Hypothesis]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM hypotheses ORDER BY hyp_id ASC").fetchall()
            return [
                Hypothesis(
                    hyp_id=r["hyp_id"],
                    code=r["code"],
                    rq_id=r["rq_id"],
                    title=r["title"] or "",
                    statement=r["statement"],
                    falsification_criteria=r["falsification_criteria"] or "",
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    def list_hypotheses_for_rq(self, rq_id: str) -> List[Hypothesis]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM hypotheses WHERE rq_id = ? ORDER BY hyp_id ASC", (rq_id,)).fetchall()
            return [
                Hypothesis(
                    hyp_id=r["hyp_id"],
                    code=r["code"],
                    rq_id=r["rq_id"],
                    title=r["title"] or "",
                    statement=r["statement"],
                    falsification_criteria=r["falsification_criteria"] or "",
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    def get_hypothesis(self, hyp_id_or_code: str) -> Optional[Hypothesis]:
        with self.db.session() as conn:
            row = conn.execute(
                "SELECT * FROM hypotheses WHERE hyp_id = ? OR code = ?",
                (hyp_id_or_code, hyp_id_or_code)
            ).fetchone()
            if not row:
                return None
            return Hypothesis(
                hyp_id=row["hyp_id"],
                code=row["code"],
                rq_id=row["rq_id"],
                title=row["title"] or "",
                statement=row["statement"],
                falsification_criteria=row["falsification_criteria"] or "",
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_research_axes(self) -> List[ResearchAxis]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM research_axes ORDER BY axis_id ASC").fetchall()
            return [
                ResearchAxis(
                    axis_id=r["axis_id"],
                    code=r["code"],
                    name=r["name"],
                    problem_summary=r["problem_summary"],
                    path_nodes=json.loads(r["path_nodes_json"] or "[]"),
                    core_question=r["core_question"],
                    core_risks=json.loads(r["core_risks_json"] or "[]"),
                )
                for r in rows
            ]

    def get_representation_contract(self) -> Optional[RepresentationContract]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM representation_contracts LIMIT 1").fetchone()
            if not row:
                return None
            return RepresentationContract(
                preserve=json.loads(row["preserve_json"] or "[]"),
                invariant=json.loads(row["invariant_json"] or "[]"),
                exclude=json.loads(row["exclude_json"] or "[]"),
            )

    def list_negative_controls(self) -> List[NegativeControl]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM negative_controls ORDER BY control_id ASC").fetchall()
            return [
                NegativeControl(
                    control_id=r["control_id"],
                    category=r["category"],
                    name=r["name"],
                    description=r["description"],
                    target_nodes=json.loads(r["target_nodes_json"] or "[]"),
                )
                for r in rows
            ]

    def list_research_boundaries(self) -> List[ResearchBoundary]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM research_boundaries ORDER BY boundary_id ASC").fetchall()
            return [
                ResearchBoundary(
                    boundary_id=r["boundary_id"],
                    title=r["title"],
                    statement=r["statement"],
                    rationale=r["rationale"],
                    affected_sections=json.loads(r["affected_sections_json"] or "[]"),
                )
                for r in rows
            ]

    def list_defensibility_questions(self) -> List[DefensibilityQuestion]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM defensibility_questions ORDER BY question_id ASC").fetchall()
            return [
                DefensibilityQuestion(
                    question_id=r["question_id"],
                    question_text=r["question_text"],
                    target_audit_scope=r["target_audit_scope"],
                )
                for r in rows
            ]

    def get_traceability_matrix(self) -> List[TraceabilityEntry]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM traceability_entries ORDER BY rq_id ASC").fetchall()
            return [
                TraceabilityEntry(
                    rq_id=r["rq_id"],
                    code=r["code"],
                    chapter1_gap_nodes=json.loads(r["gap_nodes_json"] or "[]"),
                    chapter2_mechanism_nodes=json.loads(r["mechanism_nodes_json"] or "[]"),
                    chapter3_evaluation_nodes=json.loads(r["evaluation_nodes_json"] or "[]"),
                    hypothesis_ids=json.loads(r["hypothesis_ids_json"] or "[]"),
                    controls=json.loads(r["controls_json"] or "[]"),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Argument Bundles (Prompt 5 Section 57)
    # -------------------------------------------------------------
    def save_argument_bundle(self, bundle: ArgumentBundle) -> ArgumentBundle:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO argument_bundles (
                    bundle_id, roadmap_node, objective, research_questions_json, hypotheses_json,
                    claims_json, evidence_json, contradicting_evidence_json, assumptions_json,
                    counterarguments_json, candidate_inferences_json, falsification_plans_json,
                    ownership_summary_json, uncertainty, open_questions_json, discourse_plan_json,
                    readiness_state, issues_json, verification_requests_json, generated_at, version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bundle_id) DO UPDATE SET
                    roadmap_node=excluded.roadmap_node,
                    objective=excluded.objective,
                    research_questions_json=excluded.research_questions_json,
                    hypotheses_json=excluded.hypotheses_json,
                    claims_json=excluded.claims_json,
                    evidence_json=excluded.evidence_json,
                    contradicting_evidence_json=excluded.contradicting_evidence_json,
                    assumptions_json=excluded.assumptions_json,
                    counterarguments_json=excluded.counterarguments_json,
                    candidate_inferences_json=excluded.candidate_inferences_json,
                    falsification_plans_json=excluded.falsification_plans_json,
                    ownership_summary_json=excluded.ownership_summary_json,
                    uncertainty=excluded.uncertainty,
                    open_questions_json=excluded.open_questions_json,
                    discourse_plan_json=excluded.discourse_plan_json,
                    readiness_state=excluded.readiness_state,
                    issues_json=excluded.issues_json,
                    verification_requests_json=excluded.verification_requests_json,
                    generated_at=excluded.generated_at,
                    version=excluded.version
                """,
                (
                    bundle.bundle_id,
                    bundle.roadmap_node,
                    bundle.objective,
                    json.dumps(bundle.research_questions),
                    json.dumps(bundle.hypotheses),
                    json.dumps(bundle.claims),
                    json.dumps(bundle.evidence),
                    json.dumps(bundle.contradicting_evidence),
                    json.dumps([a.model_dump(mode="json") for a in bundle.assumptions]),
                    json.dumps([c.model_dump(mode="json") for c in bundle.counterarguments]),
                    json.dumps([i.model_dump(mode="json") for i in bundle.candidate_inferences]),
                    json.dumps([f.model_dump(mode="json") for f in bundle.falsification_plans]),
                    json.dumps(bundle.ownership_summary),
                    bundle.uncertainty,
                    json.dumps(bundle.open_questions),
                    json.dumps(bundle.discourse_plan.model_dump(mode="json") if bundle.discourse_plan else {}),
                    bundle.readiness_state.value if hasattr(bundle.readiness_state, "value") else str(bundle.readiness_state),
                    json.dumps([iss.model_dump(mode="json") for iss in bundle.issues]),
                    json.dumps([v.model_dump(mode="json") for v in bundle.verification_requests]),
                    bundle.generated_at.isoformat(),
                    bundle.version,
                )
            )
            # Index into FTS
            self._index_fts_on_conn(
                conn=conn,
                entity_id=bundle.bundle_id,
                entity_type="ARGUMENT_BUNDLE",
                title=f"Argument Bundle: {bundle.roadmap_node} — {bundle.objective[:60]}",
                body=f"{bundle.objective} {bundle.uncertainty}",
                tags=f"{bundle.roadmap_node} {bundle.readiness_state.value}",
            )
        return bundle

    def get_argument_bundle(self, bundle_id: str) -> Optional[ArgumentBundle]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM argument_bundles WHERE bundle_id = ?", (bundle_id,)).fetchone()
            if not row:
                return None
            return self._row_to_argument_bundle(row)

    def list_argument_bundles(self, roadmap_node: Optional[str] = None) -> List[ArgumentBundle]:
        with self.db.session() as conn:
            if roadmap_node:
                rows = conn.execute("SELECT * FROM argument_bundles WHERE roadmap_node = ? ORDER BY generated_at DESC", (roadmap_node,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM argument_bundles ORDER BY generated_at DESC").fetchall()
            return [self._row_to_argument_bundle(r) for r in rows]

    def _row_to_argument_bundle(self, row: Any) -> ArgumentBundle:
        from research_agent.schemas.reasoning import (
            AssumptionRecord,
            CounterargumentRecord,
            InferenceRecord,
            FalsificationPlan,
            ReasoningIssue,
            VerificationRequest,
            DiscoursePlan,
        )
        dp_data = json.loads(row["discourse_plan_json"] or "{}")
        discourse_plan = DiscoursePlan.model_validate(dp_data) if dp_data else None
        return ArgumentBundle(
            bundle_id=row["bundle_id"],
            roadmap_node=row["roadmap_node"],
            objective=row["objective"],
            research_questions=json.loads(row["research_questions_json"] or "[]"),
            hypotheses=json.loads(row["hypotheses_json"] or "[]"),
            claims=json.loads(row["claims_json"] or "[]"),
            evidence=json.loads(row["evidence_json"] or "[]"),
            contradicting_evidence=json.loads(row["contradicting_evidence_json"] or "[]"),
            assumptions=[AssumptionRecord.model_validate(a) for a in json.loads(row["assumptions_json"] or "[]")],
            counterarguments=[CounterargumentRecord.model_validate(c) for c in json.loads(row["counterarguments_json"] or "[]")],
            candidate_inferences=[InferenceRecord.model_validate(i) for i in json.loads(row["candidate_inferences_json"] or "[]")],
            falsification_plans=[FalsificationPlan.model_validate(f) for f in json.loads(row["falsification_plans_json"] or "[]")],
            ownership_summary=json.loads(row["ownership_summary_json"] or "{}"),
            uncertainty=row["uncertainty"] or "",
            open_questions=json.loads(row["open_questions_json"] or "[]"),
            discourse_plan=discourse_plan,
            readiness_state=ArgumentReadinessState(row["readiness_state"]) if row["readiness_state"] in ArgumentReadinessState.__members__.values() else ArgumentReadinessState.DRAFT,
            issues=[ReasoningIssue.model_validate(iss) for iss in json.loads(row["issues_json"] or "[]")],
            verification_requests=[VerificationRequest.model_validate(v) for v in json.loads(row["verification_requests_json"] or "[]")],
            generated_at=datetime.fromisoformat(row["generated_at"]),
            version=row["version"] or "1.0.0",
        )

    # -------------------------------------------------------------
    # Evidence Gaps (Prompt 5 Section 11)
    # -------------------------------------------------------------
    def save_evidence_gap(self, gap: EvidenceGap) -> EvidenceGap:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO evidence_gaps (
                    gap_id, claim_id, missing_evidence, why_required,
                    possible_source_search, suggested_experiment, severity,
                    related_node_code, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(gap_id) DO UPDATE SET
                    claim_id=excluded.claim_id,
                    missing_evidence=excluded.missing_evidence,
                    why_required=excluded.why_required,
                    possible_source_search=excluded.possible_source_search,
                    suggested_experiment=excluded.suggested_experiment,
                    severity=excluded.severity,
                    related_node_code=excluded.related_node_code,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    gap.gap_id,
                    gap.claim_id,
                    gap.missing_evidence,
                    gap.why_required,
                    gap.possible_source_search,
                    gap.suggested_experiment,
                    gap.severity,
                    gap.related_node_code,
                    gap.status,
                    gap.created_at.isoformat(),
                    gap.updated_at.isoformat(),
                )
            )
            # Index into FTS
            self._index_fts_on_conn(
                conn=conn,
                entity_id=gap.gap_id,
                entity_type="EVIDENCE_GAP",
                title=f"Evidence Gap: {gap.claim_id} — {gap.missing_evidence[:60]}",
                body=f"{gap.why_required} {gap.suggested_experiment or ''}",
                tags=f"{gap.severity} {gap.status} {gap.related_node_code or ''}",
            )
        return gap

    def get_evidence_gap(self, gap_id: str) -> Optional[EvidenceGap]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM evidence_gaps WHERE gap_id = ?", (gap_id,)).fetchone()
            if not row:
                return None
            return EvidenceGap(
                gap_id=row["gap_id"],
                claim_id=row["claim_id"],
                missing_evidence=row["missing_evidence"],
                why_required=row["why_required"],
                possible_source_search=row["possible_source_search"],
                suggested_experiment=row["suggested_experiment"],
                severity=row["severity"],
                related_node_code=row["related_node_code"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def list_evidence_gaps(self, status: Optional[str] = None) -> List[EvidenceGap]:
        with self.db.session() as conn:
            if status:
                rows = conn.execute("SELECT * FROM evidence_gaps WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM evidence_gaps ORDER BY created_at DESC").fetchall()
            return [
                EvidenceGap(
                    gap_id=r["gap_id"],
                    claim_id=r["claim_id"],
                    missing_evidence=r["missing_evidence"],
                    why_required=r["why_required"],
                    possible_source_search=r["possible_source_search"],
                    suggested_experiment=r["suggested_experiment"],
                    severity=r["severity"],
                    related_node_code=r["related_node_code"],
                    status=r["status"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Assumptions (Prompt 5 Section 16)
    # -------------------------------------------------------------
    def save_assumption(self, ass: AssumptionRecord) -> AssumptionRecord:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO assumptions (
                    assumption_id, statement, is_explicit, required_by_json,
                    evidence_or_basis, testability, violation_consequence, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(assumption_id) DO UPDATE SET
                    statement=excluded.statement,
                    is_explicit=excluded.is_explicit,
                    required_by_json=excluded.required_by_json,
                    evidence_or_basis=excluded.evidence_or_basis,
                    testability=excluded.testability,
                    violation_consequence=excluded.violation_consequence,
                    status=excluded.status
                """,
                (
                    ass.assumption_id,
                    ass.statement,
                    1 if ass.is_explicit else 0,
                    json.dumps(ass.required_by),
                    ass.evidence_or_basis,
                    ass.testability,
                    ass.violation_consequence,
                    ass.status,
                    ass.created_at.isoformat(),
                )
            )
            # Index into FTS
            self._index_fts_on_conn(
                conn=conn,
                entity_id=ass.assumption_id,
                entity_type="ASSUMPTION",
                title=f"Assumption: {ass.statement[:60]}...",
                body=f"{ass.statement} {ass.violation_consequence}",
                tags=f"{ass.testability} {ass.status}",
            )
        return ass

    def get_assumption(self, assumption_id: str) -> Optional[AssumptionRecord]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM assumptions WHERE assumption_id = ?", (assumption_id,)).fetchone()
            if not row:
                return None
            return AssumptionRecord(
                assumption_id=row["assumption_id"],
                statement=row["statement"],
                is_explicit=bool(row["is_explicit"]),
                required_by=json.loads(row["required_by_json"] or "[]"),
                evidence_or_basis=row["evidence_or_basis"],
                testability=row["testability"],
                violation_consequence=row["violation_consequence"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_assumptions(self) -> List[AssumptionRecord]:
        with self.db.session() as conn:
            rows = conn.execute("SELECT * FROM assumptions ORDER BY assumption_id ASC").fetchall()
            return [
                AssumptionRecord(
                    assumption_id=r["assumption_id"],
                    statement=r["statement"],
                    is_explicit=bool(r["is_explicit"]),
                    required_by=json.loads(r["required_by_json"] or "[]"),
                    evidence_or_basis=r["evidence_or_basis"],
                    testability=r["testability"],
                    violation_consequence=r["violation_consequence"],
                    status=r["status"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Verification Requests (Prompt 5 Section 102, Prompt 6 Interface)
    # -------------------------------------------------------------
    def save_verification_request(self, req: VerificationRequest) -> VerificationRequest:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO verification_requests (
                    request_id, request_type, target_claim_id, target_equation_id,
                    target_table_or_figure_id, description, input_payload_json,
                    status, verification_result_json, requested_at, completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    status=excluded.status,
                    verification_result_json=excluded.verification_result_json,
                    completed_at=excluded.completed_at
                """,
                (
                    req.request_id,
                    req.request_type.value if hasattr(req.request_type, "value") else str(req.request_type),
                    req.target_claim_id,
                    req.target_equation_id,
                    req.target_table_or_figure_id,
                    req.description,
                    json.dumps(req.input_payload),
                    req.status.value if hasattr(req.status, "value") else str(req.status),
                    json.dumps(req.verification_result) if req.verification_result else None,
                    req.requested_at.isoformat(),
                    req.completed_at.isoformat() if req.completed_at else None,
                )
            )
        return req

    def get_verification_request(self, request_id: str) -> Optional[VerificationRequest]:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM verification_requests WHERE request_id = ?", (request_id,)).fetchone()
            if not row:
                return None
            return VerificationRequest(
                request_id=row["request_id"],
                request_type=VerificationRequestType(row["request_type"]),
                target_claim_id=row["target_claim_id"],
                target_equation_id=row["target_equation_id"],
                target_table_or_figure_id=row["target_table_or_figure_id"],
                description=row["description"],
                input_payload=json.loads(row["input_payload_json"] or "{}"),
                status=VerificationRequestStatus(row["status"]),
                verification_result=json.loads(row["verification_result_json"]) if row["verification_result_json"] else None,
                requested_at=datetime.fromisoformat(row["requested_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            )

    def list_verification_requests(self, status: Optional[VerificationRequestStatus] = None) -> List[VerificationRequest]:
        with self.db.session() as conn:
            if status:
                rows = conn.execute("SELECT * FROM verification_requests WHERE status = ? ORDER BY requested_at DESC", (status.value,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM verification_requests ORDER BY requested_at DESC").fetchall()
            return [
                VerificationRequest(
                    request_id=r["request_id"],
                    request_type=VerificationRequestType(r["request_type"]),
                    target_claim_id=r["target_claim_id"],
                    target_equation_id=r["target_equation_id"],
                    target_table_or_figure_id=r["target_table_or_figure_id"],
                    description=r["description"],
                    input_payload=json.loads(r["input_payload_json"] or "{}"),
                    status=VerificationRequestStatus(r["status"]),
                    verification_result=json.loads(r["verification_result_json"]) if r["verification_result_json"] else None,
                    requested_at=datetime.fromisoformat(r["requested_at"]),
                    completed_at=datetime.fromisoformat(r["completed_at"]) if r["completed_at"] else None,
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Reasoning Issues (Prompt 5 Section 63)
    # -------------------------------------------------------------
    def save_reasoning_issue(self, issue: ReasoningIssue) -> ReasoningIssue:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO reasoning_issues (
                    issue_id, issue_type, affected_entity_id, message, severity, mitigation, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(issue_id) DO UPDATE SET
                    message=excluded.message,
                    severity=excluded.severity,
                    mitigation=excluded.mitigation
                """,
                (
                    issue.issue_id,
                    issue.issue_type.value if hasattr(issue.issue_type, "value") else str(issue.issue_type),
                    issue.affected_entity_id,
                    issue.message,
                    issue.severity,
                    issue.mitigation,
                    datetime.now(timezone.utc).isoformat(),
                )
            )
        return issue

    def list_reasoning_issues(self, affected_entity_id: Optional[str] = None) -> List[ReasoningIssue]:
        with self.db.session() as conn:
            if affected_entity_id:
                rows = conn.execute("SELECT * FROM reasoning_issues WHERE affected_entity_id = ? ORDER BY issue_id ASC", (affected_entity_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM reasoning_issues ORDER BY issue_id ASC").fetchall()
            return [
                ReasoningIssue(
                    issue_id=r["issue_id"],
                    issue_type=ReasoningIssueType(r["issue_type"]),
                    affected_entity_id=r["affected_entity_id"],
                    message=r["message"],
                    severity=r["severity"],
                    mitigation=r["mitigation"],
                )
                for r in rows
            ]

    # -------------------------------------------------------------
    # Argument Graph Nodes & Edges (Prompt 5 Section 40)
    # -------------------------------------------------------------
    def save_argument_node(self, node: ArgumentNode) -> ArgumentNode:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO argument_nodes (node_id, node_type, title, statement, entity_ref_id, ownership, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    node_type=excluded.node_type,
                    title=excluded.title,
                    statement=excluded.statement,
                    entity_ref_id=excluded.entity_ref_id,
                    ownership=excluded.ownership,
                    metadata_json=excluded.metadata_json
                """,
                (
                    node.node_id,
                    node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type),
                    node.title,
                    node.statement,
                    node.entity_ref_id,
                    node.ownership.value if hasattr(node.ownership, "value") else str(node.ownership),
                    json.dumps(node.metadata),
                    datetime.now(timezone.utc).isoformat(),
                )
            )
        return node

    def save_argument_edge(self, edge: ArgumentEdge) -> ArgumentEdge:
        with self.db.session() as conn:
            conn.execute(
                """
                INSERT INTO argument_edges (edge_id, source_node_id, target_node_id, relation_type, weight, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(edge_id) DO UPDATE SET
                    relation_type=excluded.relation_type,
                    weight=excluded.weight,
                    notes=excluded.notes
                """,
                (
                    edge.edge_id,
                    edge.source_node_id,
                    edge.target_node_id,
                    edge.relation_type.value if hasattr(edge.relation_type, "value") else str(edge.relation_type),
                    edge.weight,
                    edge.notes,
                    datetime.now(timezone.utc).isoformat(),
                )
            )
        return edge

    def get_argument_graph(self, graph_id: str = "MAIN_ARGUMENT_GRAPH") -> ArgumentGraph:
        with self.db.session() as conn:
            n_rows = conn.execute("SELECT * FROM argument_nodes ORDER BY node_id ASC").fetchall()
            e_rows = conn.execute("SELECT * FROM argument_edges ORDER BY edge_id ASC").fetchall()
            nodes = [
                ArgumentNode(
                    node_id=r["node_id"],
                    node_type=ArgumentNodeType(r["node_type"]),
                    title=r["title"],
                    statement=r["statement"],
                    entity_ref_id=r["entity_ref_id"],
                    ownership=IntellectualOwnership(r["ownership"]),
                    metadata=json.loads(r["metadata_json"] or "{}"),
                )
                for r in n_rows
            ]
            edges = [
                ArgumentEdge(
                    edge_id=r["edge_id"],
                    source_node_id=r["source_node_id"],
                    target_node_id=r["target_node_id"],
                    relation_type=ArgumentEdgeType(r["relation_type"]),
                    weight=r["weight"],
                    notes=r["notes"],
                )
                for r in e_rows
            ]
            root_claims = [n.node_id for n in nodes if n.node_type == ArgumentNodeType.CLAIM]
            return ArgumentGraph(
                graph_id=graph_id,
                nodes=nodes,
                edges=edges,
                completeness_score=1.0 if nodes else 0.0,
                is_cyclic=False,
                root_claims=root_claims,
            )
