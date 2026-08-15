"""
Pydantic Schemas for Academic Composition, Document Intermediate Representation (IR) & Thesis Auditing (Prompt 7)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from research_agent.core.enums import (
    AuditCategory,
    AuditIssueStatus,
    AuditSeverity,
    CompositionMode,
    DefensibilityStatus,
    DiscourseFunction,
    IntellectualOwnership,
    ParagraphReviewStatus,
    SentenceClaimType,
    SentenceCompilationState,
    WritingReadiness,
)


class CitationAnchor(BaseModel):
    """Anchor linking a text span to a citation-ready source in Reference Map."""
    anchor_id: str
    source_id: str
    citation_key: str
    locator: Optional[str] = None
    formatted_citation: str = ""


class EquationAnchor(BaseModel):
    """Anchor linking mathematical formula to Equation Registry."""
    anchor_id: str
    equation_id: str
    latex_code: str
    ownership: IntellectualOwnership = IntellectualOwnership.OURS
    is_inline: bool = False


class TableAnchor(BaseModel):
    """Anchor linking tabular data to Table Specification in registry."""
    anchor_id: str
    table_id: str
    caption: str
    output_markdown: str = ""
    output_latex: str = ""


class FigureAnchor(BaseModel):
    """Anchor linking figure illustration to Figure Specification in registry."""
    anchor_id: str
    figure_id: str
    caption: str
    image_rel_path: str
    companion_csv_rel_path: str


class SentenceRecord(BaseModel):
    """Granular proposition within Document IR with full anti-hallucination metadata."""
    sentence_id: str
    paragraph_id: str
    sentence_index: int = 0
    text: str
    claim_type: SentenceClaimType = SentenceClaimType.SYNTHESIS
    ownership: IntellectualOwnership = IntellectualOwnership.OURS
    target_claim_id: Optional[str] = None
    citation_source_ids: List[str] = Field(default_factory=list)
    numerical_claim_ids: List[str] = Field(default_factory=list)
    equation_ids: List[str] = Field(default_factory=list)
    table_ids: List[str] = Field(default_factory=list)
    figure_ids: List[str] = Field(default_factory=list)
    compilation_state: SentenceCompilationState = SentenceCompilationState.DRAFT
    issues: List[str] = Field(default_factory=list)


class ParagraphRecord(BaseModel):
    """Document IR Paragraph containing structured sentences, anchors, and review status."""
    paragraph_id: str
    node_code: str
    section_code: str = ""
    chapter_code: str = ""
    discourse_function: DiscourseFunction = DiscourseFunction.EVIDENCE_INTEGRATION
    argument_bundle_id: Optional[str] = None
    sentences: List[SentenceRecord] = Field(default_factory=list)
    citations: List[CitationAnchor] = Field(default_factory=list)
    equations: List[EquationAnchor] = Field(default_factory=list)
    tables: List[TableAnchor] = Field(default_factory=list)
    figures: List[FigureAnchor] = Field(default_factory=list)
    raw_text: str = ""
    audited_text: str = ""
    review_status: ParagraphReviewStatus = ParagraphReviewStatus.GENERATED
    is_human_edited: bool = False
    human_edit_notes: Optional[str] = None
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SubsectionRecord(BaseModel):
    """Document IR Subsection compiling paragraphs for a specific Roadmap Node."""
    subsection_id: str
    node_code: str
    title: str
    discourse_plan_id: Optional[str] = None
    paragraphs: List[ParagraphRecord] = Field(default_factory=list)
    readiness: WritingReadiness = WritingReadiness.DRAFTED
    rendered_markdown: str = ""
    rendered_latex: str = ""


class SectionRecord(BaseModel):
    """Document IR Section grouping subsections."""
    section_code: str
    title: str
    subsections: List[SubsectionRecord] = Field(default_factory=list)
    intro_paragraph: Optional[ParagraphRecord] = None


class ChapterRecord(BaseModel):
    """Document IR Chapter."""
    chapter_code: str
    title: str
    sections: List[SectionRecord] = Field(default_factory=list)


class ThesisDocument(BaseModel):
    """Complete structured thesis intermediate representation."""
    document_id: str
    title: str
    author: str = "Nguyen Van A"
    institution: str = "Vietnam National University"
    year: int = 2026
    chapters: List[ChapterRecord] = Field(default_factory=list)
    bibliography_bibtex: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NodeWritingStatus(BaseModel):
    """Readiness and compilation audit overview for a Roadmap Node."""
    node_code: str
    title: str
    readiness: WritingReadiness = WritingReadiness.NOT_READY
    argument_bundle_id: Optional[str] = None
    total_sources: int = 0
    total_claims: int = 0
    total_evidences: int = 0
    total_contradictions: int = 0
    total_numerical_claims: int = 0
    total_equations: int = 0
    is_blocked: bool = False
    blocking_reasons: List[str] = Field(default_factory=list)
    paragraph_count: int = 0
    review_status: ParagraphReviewStatus = ParagraphReviewStatus.GENERATED


class AuditIssueRecord(BaseModel):
    """Structured audit issue emitted by ThesisAuditor."""
    issue_id: str
    category: AuditCategory
    severity: AuditSeverity
    location: str
    description: str
    affected_entity_id: Optional[str] = None
    recommended_action: str = ""
    is_blocking: bool = False
    status: AuditIssueStatus = AuditIssueStatus.OPEN
    waiver_rationale: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ThesisAuditReport(BaseModel):
    """Multi-category thesis audit report."""
    build_id: str
    mode: CompositionMode = CompositionMode.PROVISIONAL
    total_sentences: int = 0
    total_paragraphs: int = 0
    total_issues: int = 0
    issues_by_category: Dict[str, int] = Field(default_factory=dict)
    issues_by_severity: Dict[str, int] = Field(default_factory=dict)
    critical_issues: List[AuditIssueRecord] = Field(default_factory=list)
    high_issues: List[AuditIssueRecord] = Field(default_factory=list)
    medium_issues: List[AuditIssueRecord] = Field(default_factory=list)
    low_issues: List[AuditIssueRecord] = Field(default_factory=list)
    rq_coverage: Dict[str, str] = Field(default_factory=dict)
    hypothesis_statuses: Dict[str, str] = Field(default_factory=dict)
    axes_coverage: Dict[str, str] = Field(default_factory=dict)
    defensibility_scores: Dict[str, DefensibilityStatus] = Field(default_factory=dict)
    is_ready_for_final_build: bool = False
    overall_status: str = "AUDITED"


class ThesisBuildManifest(BaseModel):
    """Cryptographic and procedural manifest for thesis compilation."""
    build_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mode: CompositionMode = CompositionMode.PROVISIONAL
    git_commit: str = "UNKNOWN"
    roadmap_version: str = "1.0.0"
    reference_map_version: str = "1.0.0"
    memory_schema_version: str = "1.0.0"
    reasoning_version: str = "1.0.0"
    verification_version: str = "1.0.0"
    total_nodes_compiled: int = 0
    unresolved_critical_count: int = 0
    unresolved_high_count: int = 0
    output_file_path: str = ""
    output_sha256: str = ""


class ResearchArtifactPackage(BaseModel):
    """Manifest describing all bundled research assets."""
    package_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    git_commit: str = ""
    roadmap_file: str = "roadmap.json"
    reference_map_file: str = "references.json"
    claim_ledger_count: int = 0
    argument_bundles_count: int = 0
    numerical_claims_count: int = 0
    equations_count: int = 0
    tables_count: int = 0
    figures_count: int = 0
    package_sha256: str = ""
