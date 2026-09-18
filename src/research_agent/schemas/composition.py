"""
Lược đồ Pydantic cho bố cục học thuật, trình bày tài liệu trung gian (IR) và kiểm tra luận án (Nhắc 7)
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
    """Neo liên kết một đoạn văn bản với nguồn sẵn sàng trích dẫn trong Bản đồ tham khảo."""
    anchor_id: str
    source_id: str
    citation_key: str
    locator: Optional[str] = None
    formatted_citation: str = ""


class EquationAnchor(BaseModel):
    """Neo liên kết công thức toán học với Sổ đăng ký phương trình."""
    anchor_id: str
    equation_id: str
    latex_code: str
    ownership: IntellectualOwnership = IntellectualOwnership.OURS
    is_inline: bool = False


class TableAnchor(BaseModel):
    """Neo liên kết dữ liệu dạng bảng với Đặc tả bảng trong sổ đăng ký."""
    anchor_id: str
    table_id: str
    caption: str
    output_markdown: str = ""
    output_latex: str = ""


class FigureAnchor(BaseModel):
    """Neo liên kết hình minh họa với Đặc tả hình trong sổ đăng ký."""
    anchor_id: str
    figure_id: str
    caption: str
    image_rel_path: str
    companion_csv_rel_path: str


class SentenceRecord(BaseModel):
    """Đề xuất chi tiết trong Tài liệu IR với đầy đủ siêu dữ liệu chống ảo giác."""
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
    """Tài liệu Đoạn IR chứa các câu có cấu trúc, các điểm neo và trạng thái đánh giá."""
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
    """Tiểu mục IR tài liệu biên soạn các đoạn văn cho một Nút Lộ trình cụ thể."""
    subsection_id: str
    node_code: str
    title: str
    discourse_plan_id: Optional[str] = None
    paragraphs: List[ParagraphRecord] = Field(default_factory=list)
    readiness: WritingReadiness = WritingReadiness.DRAFTED
    rendered_markdown: str = ""
    rendered_latex: str = ""


class SectionRecord(BaseModel):
    """Tài liệu IR Phần nhóm các tiểu mục."""
    section_code: str
    title: str
    subsections: List[SubsectionRecord] = Field(default_factory=list)
    intro_paragraph: Optional[ParagraphRecord] = None


class ChapterRecord(BaseModel):
    """Tài liệu Chương IR."""
    chapter_code: str
    title: str
    sections: List[SectionRecord] = Field(default_factory=list)


class ThesisDocument(BaseModel):
    """Hoàn thành cấu trúc luận án trình bày trung gian."""
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
    """Tổng quan về kiểm tra mức độ sẵn sàng và biên soạn cho Roadmap Node."""
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
    """Vấn đề kiểm tra có cấu trúc do ThesisAuditor phát ra."""
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
    """Báo cáo kiểm tra luận án đa chuyên mục."""
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
    """bản kê (manifest) mật mã và thủ tục để biên soạn luận án."""
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
    """bản kê (manifest) mô tả tất cả tài sản nghiên cứu đi kèm."""
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
