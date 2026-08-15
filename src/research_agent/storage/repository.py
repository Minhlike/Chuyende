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

    def list_claim_relations(self) -> List[ClaimRelation]:
        with self.db.session() as conn:
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
