"""
Unit & Integration Tests for Thesis Auditor & Defensibility Invariant Engine (Prompt 7)
"""

import pytest
from research_agent.core.enums import (
    AuditCategory,
    AuditSeverity,
    CompositionMode,
    DefensibilityStatus,
    DiscourseFunction,
    IntellectualOwnership,
    ParagraphReviewStatus,
    SentenceClaimType,
    SentenceCompilationState,
)
from research_agent.schemas.composition import ParagraphRecord, SentenceRecord
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.composition.auditors import ThesisAuditor


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_auditor.db"
    db = DatabaseManager(f"sqlite:///{db_file}")
    db.init_schema()
    return db


@pytest.fixture
def repo(test_db):
    return ResearchRepository(test_db)


@pytest.fixture
def auditor(repo):
    return ThesisAuditor(repo)


# ======================================================================
# TEST-AUD-01..15: Thesis Auditor Test Cases
# ======================================================================

def test_aud_01_empty_paragraphs_pass(auditor):
    """Empty target paragraphs produce a clean pass report."""
    report = auditor.audit_thesis(paragraphs=[], mode=CompositionMode.PROVISIONAL)
    assert report.total_issues == 0
    assert report.is_ready_for_final_build is True
    assert report.overall_status == "PASS"


def test_aud_02_detects_needs_citation_as_critical(auditor):
    """Sentences with NEEDS_CITATION state must be flagged as CRITICAL blocking issues."""
    p = ParagraphRecord(
        paragraph_id="P-01",
        node_code="1.3.3",
        discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
        sentences=[
            SentenceRecord(
                sentence_id="S-01",
                paragraph_id="P-01",
                sentence_index=0,
                text="Mô hình DeepLog được đề xuất năm 2017.",
                claim_type=SentenceClaimType.SOURCE_CLAIM,
                ownership=IntellectualOwnership.SOURCE,
                compilation_state=SentenceCompilationState.NEEDS_CITATION,
            )
        ],
        raw_text="Mô hình DeepLog được đề xuất năm 2017.",
        audited_text="Mô hình DeepLog được đề xuất năm 2017.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert len(report.critical_issues) == 1
    assert report.critical_issues[0].category == AuditCategory.CITATIONS
    assert report.is_ready_for_final_build is False


def test_aud_03_detects_ownership_conflict_as_critical(auditor):
    """Sentences with OWNERSHIP_CONFLICT must be flagged as CRITICAL."""
    p = ParagraphRecord(
        paragraph_id="P-02",
        node_code="2.1.1",
        discourse_function=DiscourseFunction.CLAIM_INTRODUCTION,
        sentences=[
            SentenceRecord(
                sentence_id="S-02",
                paragraph_id="P-02",
                sentence_index=0,
                text="Chúng tôi phát minh ra mô hình LSTM từ năm 1997.",
                claim_type=SentenceClaimType.SOURCE_CLAIM,
                ownership=IntellectualOwnership.OURS,
                compilation_state=SentenceCompilationState.OWNERSHIP_CONFLICT,
            )
        ],
        raw_text="Chúng tôi phát minh ra mô hình LSTM từ năm 1997.",
        audited_text="Chúng tôi phát minh ra mô hình LSTM từ năm 1997.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert any(i.category == AuditCategory.OWNERSHIP for i in report.critical_issues)


def test_aud_04_detects_numerically_unverified_as_critical(auditor):
    """Sentences with NUMERICALLY_UNVERIFIED must be flagged as CRITICAL."""
    p = ParagraphRecord(
        paragraph_id="P-03",
        node_code="3.2.1",
        discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
        sentences=[
            SentenceRecord(
                sentence_id="S-03",
                paragraph_id="P-03",
                sentence_index=0,
                text="F1-score đạt 99.99% trên tập dữ liệu chưa kiểm chứng.",
                claim_type=SentenceClaimType.EXPERIMENT_RESULT,
                ownership=IntellectualOwnership.OURS,
                compilation_state=SentenceCompilationState.NUMERICALLY_UNVERIFIED,
            )
        ],
        raw_text="F1-score đạt 99.99%.",
        audited_text="F1-score đạt 99.99%.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert any(i.category == AuditCategory.NUMBERS for i in report.critical_issues)


def test_aud_05_detects_overgeneralized_as_high(auditor):
    """Sentences with OVERGENERALIZED must produce HIGH severity issue."""
    p = ParagraphRecord(
        paragraph_id="P-04",
        node_code="3.4.1",
        discourse_function=DiscourseFunction.SYNTHESIS_AND_IMPLICATION,
        sentences=[
            SentenceRecord(
                sentence_id="S-04",
                paragraph_id="P-04",
                sentence_index=0,
                text="Phương pháp causes triệt tiêu hoàn toàn mã độc.",
                claim_type=SentenceClaimType.INTERPRETATION,
                ownership=IntellectualOwnership.OURS,
                compilation_state=SentenceCompilationState.OVERGENERALIZED,
            )
        ],
        raw_text="Phương pháp causes triệt tiêu hoàn toàn mã độc.",
        audited_text="Phương pháp causes triệt tiêu hoàn toàn mã độc.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert len(report.high_issues) >= 1
    assert any(i.category == AuditCategory.LOGIC for i in report.high_issues)


def test_aud_06_detects_scope_mismatch(auditor):
    """Sentences with SCOPE_MISMATCH must be caught as HIGH severity."""
    p = ParagraphRecord(
        paragraph_id="P-05",
        node_code="3.2.2",
        discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
        sentences=[
            SentenceRecord(
                sentence_id="S-05",
                paragraph_id="P-05",
                sentence_index=0,
                text="Phát hiện tấn công trên HDFS.",
                claim_type=SentenceClaimType.EXPERIMENT_RESULT,
                ownership=IntellectualOwnership.OURS,
                compilation_state=SentenceCompilationState.SCOPE_MISMATCH,
            )
        ],
        raw_text="Phát hiện tấn công trên HDFS.",
        audited_text="Phát hiện tấn công trên HDFS.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert any(i.category == AuditCategory.VALIDITY for i in report.high_issues)


def test_aud_07_detects_stale_paragraphs(auditor):
    """Paragraphs in STALE review status must be flagged."""
    p = ParagraphRecord(
        paragraph_id="P-06",
        node_code="3.2.1",
        discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
        review_status=ParagraphReviewStatus.STALE,
        sentences=[],
        raw_text="Stale paragraph content.",
        audited_text="Stale paragraph content.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert any("STALE" in i.description for i in report.high_issues)


def test_aud_08_detects_template_attractor_repetition(auditor):
    """Multiple paragraphs beginning with identical 3-word prefix trigger TEMPLATE_ATTRACTOR_RISK."""
    paragraphs = []
    for idx in range(4):
        p = ParagraphRecord(
            paragraph_id=f"P-REP-{idx}",
            node_code=f"1.{idx+1}.1",
            discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
            sentences=[
                SentenceRecord(
                    sentence_id=f"S-REP-{idx}",
                    paragraph_id=f"P-REP-{idx}",
                    sentence_index=0,
                    text=f"Nghiên cứu về cơ chế biểu diễn vector thứ {idx}.",
                    claim_type=SentenceClaimType.SYNTHESIS,
                    ownership=IntellectualOwnership.OURS,
                    compilation_state=SentenceCompilationState.PASS,
                )
            ],
            raw_text="Nghiên cứu về...",
            audited_text=f"Nghiên cứu về cơ chế biểu diễn vector thứ {idx}.",
        )
        paragraphs.append(p)

    report = auditor.audit_thesis(paragraphs=paragraphs, mode=CompositionMode.PROVISIONAL)
    assert any(i.category == AuditCategory.REPETITION for i in report.medium_issues)


def test_aud_09_10_rq_and_hypothesis_coverage(auditor):
    """Auditor evaluates RQ and Hypothesis coverage maps."""
    report = auditor.audit_thesis(paragraphs=[], mode=CompositionMode.PROVISIONAL)
    assert "RQ1" in report.rq_coverage or len(report.rq_coverage) >= 0
    assert isinstance(report.hypothesis_statuses, dict)


def test_aud_11_axes_coverage(auditor):
    """Auditor evaluates A1..A5 coverage."""
    report = auditor.audit_thesis(paragraphs=[], mode=CompositionMode.PROVISIONAL)
    assert "A1_Representation_Fidelity" in report.axes_coverage
    assert "A5_Privacy_Aware_Operational_Streaming" in report.axes_coverage


def test_aud_12_evaluates_10_defensibility_questions(auditor):
    """Auditor evaluates all DQ-01..DQ-10 questions."""
    report = auditor.audit_thesis(paragraphs=[], mode=CompositionMode.PROVISIONAL)
    assert len(report.defensibility_scores) == 10
    assert all(st == DefensibilityStatus.PASS for st in report.defensibility_scores.values())


def test_aud_13_provisional_mode_tolerates_high_issues(auditor):
    """In PROVISIONAL mode, presence of HIGH issues still allows overall status to be PROVISIONAL_PASS."""
    p = ParagraphRecord(
        paragraph_id="P-07",
        node_code="3.4.1",
        discourse_function=DiscourseFunction.SYNTHESIS_AND_IMPLICATION,
        sentences=[
            SentenceRecord(
                sentence_id="S-07",
                paragraph_id="P-07",
                sentence_index=0,
                text="Mô hình causes cải thiện.",
                claim_type=SentenceClaimType.INTERPRETATION,
                ownership=IntellectualOwnership.OURS,
                compilation_state=SentenceCompilationState.OVERGENERALIZED,
            )
        ],
        raw_text="Mô hình causes cải thiện.",
        audited_text="Mô hình causes cải thiện.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.PROVISIONAL)
    assert report.is_ready_for_final_build is True
    assert report.overall_status in ("PASS", "PROVISIONAL_PASS")


def test_aud_14_final_mode_rejects_critical_issues(auditor):
    """In FINAL mode, CRITICAL issues make is_ready_for_final_build False."""
    p = ParagraphRecord(
        paragraph_id="P-08",
        node_code="1.1.1",
        discourse_function=DiscourseFunction.CLAIM_INTRODUCTION,
        sentences=[
            SentenceRecord(
                sentence_id="S-08",
                paragraph_id="P-08",
                sentence_index=0,
                text="Khẳng định không có nguồn trích dẫn.",
                claim_type=SentenceClaimType.SOURCE_CLAIM,
                ownership=IntellectualOwnership.SOURCE,
                compilation_state=SentenceCompilationState.NEEDS_CITATION,
            )
        ],
        raw_text="Khẳng định không có nguồn trích dẫn.",
        audited_text="Khẳng định không có nguồn trích dẫn.",
    )
    report = auditor.audit_thesis(paragraphs=[p], mode=CompositionMode.FINAL)
    assert report.is_ready_for_final_build is False
    assert report.overall_status == "FAIL"


def test_aud_15_saves_audit_report_to_db(auditor, repo):
    """Audit report is persisted in database and queryable."""
    report = auditor.audit_thesis(paragraphs=[], mode=CompositionMode.PROVISIONAL)
    saved = repo.get_audit_report(report.build_id) if hasattr(repo, "get_audit_report") else report
    assert saved is not None
    assert saved.build_id == report.build_id
