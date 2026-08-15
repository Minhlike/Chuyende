"""
Unit & Integration Tests for Human-in-the-Loop & Invalidation Management (Prompt 7)
"""

import pytest
from research_agent.core.enums import (
    DiscourseFunction,
    IntellectualOwnership,
    ParagraphReviewStatus,
    SentenceClaimType,
    SentenceCompilationState,
)
from research_agent.schemas.composition import ParagraphRecord, SentenceRecord
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.composition.human_workflow import HumanWorkflowManager


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_human.db"
    db = DatabaseManager(f"sqlite:///{db_file}")
    db.init_schema()
    return db


@pytest.fixture
def repo(test_db):
    return ResearchRepository(test_db)


@pytest.fixture
def workflow(repo):
    return HumanWorkflowManager(repo)


def test_hum_01_manual_edit_preservation(workflow, repo):
    """Manual human revision sets is_human_edited=True, bumps version, and preserves text."""
    p = ParagraphRecord(
        paragraph_id="P-HUM-01",
        node_code="1.3.3",
        discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
        raw_text="Original automated draft text.",
        audited_text="Original automated draft text.",
        review_status=ParagraphReviewStatus.DRAFT,
        version=1,
    )
    repo.save_paragraph(p)

    edited_text = "Thực nghiệm chứng minh không gian biểu diễn đa chiều có tính bất biến cao."
    updated_p = workflow.record_human_edit(
        paragraph_id="P-HUM-01",
        edited_text=edited_text,
        edit_notes="Chỉnh sửa văn phong khoa học và chuẩn hóa thuật ngữ tiếng Việt.",
    )

    assert updated_p.audited_text == edited_text
    assert updated_p.is_human_edited is True
    assert updated_p.version == 2
    assert updated_p.review_status == ParagraphReviewStatus.HUMAN_ACCEPTED
    assert "tiếng Việt" in updated_p.human_edit_notes

    # Verify query from database returns human edited flags
    fetched = repo.get_paragraph("P-HUM-01")
    assert fetched.is_human_edited is True
    assert fetched.audited_text == edited_text


def test_hum_02_upstream_invalidation_cascades_to_stale(workflow, repo):
    """Invalidation of upstream source/claim marks referencing paragraphs STALE and logs audit issues."""
    p = ParagraphRecord(
        paragraph_id="P-INV-01",
        node_code="1.3.3",
        discourse_function=DiscourseFunction.EVIDENCE_INTEGRATION,
        sentences=[
            SentenceRecord(
                sentence_id="S-INV-01",
                paragraph_id="P-INV-01",
                sentence_index=0,
                text="Theo nghiên cứu cơ sở [SRC-DEP-01].",
                claim_type=SentenceClaimType.SOURCE_CLAIM,
                ownership=IntellectualOwnership.SOURCE,
                citation_source_ids=["SRC-DEP-01"],
            )
        ],
        raw_text="Theo nghiên cứu cơ sở [SRC-DEP-01].",
        audited_text="Theo nghiên cứu cơ sở [SRC-DEP-01].",
        review_status=ParagraphReviewStatus.MACHINE_AUDITED,
    )
    repo.save_paragraph(p)

    affected = workflow.propagate_upstream_invalidation(
        invalidated_entity_id="SRC-DEP-01",
        reason="Bài báo bị tác giả đính chính do lỗi phương pháp thu thập dữ liệu.",
    )

    assert "P-INV-01" in affected
    p_updated = repo.get_paragraph("P-INV-01")
    assert p_updated.review_status == ParagraphReviewStatus.STALE

    # Verify audit issue created
    issues = repo.list_audit_issues()
    assert any(i.affected_entity_id == "SRC-DEP-01" for i in issues)
