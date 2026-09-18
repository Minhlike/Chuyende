"""
Quy trình làm việc của con người trong vòng lặp, Trình quản lý vô hiệu hóa phiên bản và thượng nguồn (upstream) (Nhắc 7 phần 79..83)
"""

from datetime import datetime, timezone
from typing import List, Optional, Set
from research_agent.core.enums import (
    AuditCategory,
    AuditSeverity,
    ParagraphReviewStatus,
)
from research_agent.schemas.composition import AuditIssueRecord, ParagraphRecord
from research_agent.storage.repository import ResearchRepository


class HumanWorkflowManager:
    """
    Quản lý phiên bản đoạn văn, bảo quản các chỉnh sửa thủ công của con người,
    và lan truyền vô hiệu theo tầng từ những thay đổi nghiên cứu thượng nguồn (upstream).
    """

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def record_human_edit(
        self,
        paragraph_id: str,
        edited_text: str,
        edit_notes: Optional[str] = None,
    ) -> ParagraphRecord:
        """
        Ghi lại các sửa đổi thủ công của con người đối với một đoạn được chấp nhận.
        Đảm bảo rằng việc biên dịch lại tự động sẽ không bao giờ âm thầm ghi đè lên văn bản này.
        """
        p = self.repo.get_paragraph(paragraph_id)
        if not p:
            raise ValueError(f"Paragraph '{paragraph_id}' not found.")

        p.audited_text = edited_text
        p.raw_text = edited_text
        p.is_human_edited = True
        p.human_edit_notes = edit_notes or "Manual human revision applied."
        p.review_status = ParagraphReviewStatus.HUMAN_ACCEPTED
        p.version += 1
        p.updated_at = datetime.now(timezone.utc)

        return self.repo.save_paragraph(p)

    def propagate_upstream_invalidation(
        self,
        invalidated_entity_id: str,
        reason: str,
    ) -> List[str]:
        """
        Xác định tất cả các đoạn văn và phần luận án tùy thuộc vào một thực thể không hợp lệ
        (nguồn, khẳng định, kết quả bằng số, phương trình) và đánh dấu chúng là STALE / REVIEW_REQUIRED.
        """
        affected_paragraph_ids: List[str] = []
        all_paragraphs = self.repo.list_paragraphs()

        for p in all_paragraphs:
            is_affected = False

            # Kiểm tra câu để tham khảo
            for s in p.sentences:
                if (
                    invalidated_entity_id in s.citation_source_ids
                    or invalidated_entity_id in s.numerical_claim_ids
                    or invalidated_entity_id in s.equation_ids
                    or invalidated_entity_id == s.target_claim_id
                ):
                    is_affected = True
                    break

            if is_affected:
                self.repo.update_paragraph_review_status(
                    paragraph_id=p.paragraph_id,
                    status=ParagraphReviewStatus.STALE,
                    is_human_edited=p.is_human_edited,
                    notes=f"Upstream entity '{invalidated_entity_id}' invalidated: {reason}",
                )
                affected_paragraph_ids.append(p.paragraph_id)

                # Ghi lại một vấn đề kiểm toán
                self.repo.save_audit_issue(
                    AuditIssueRecord(
                        issue_id=f"ISS-INV-{p.paragraph_id}",
                        category=AuditCategory.REPRODUCIBILITY,
                        severity=AuditSeverity.HIGH,
                        location=f"Paragraph {p.paragraph_id}",
                        description=f"Upstream dependency '{invalidated_entity_id}' was invalidated: {reason}",
                        affected_entity_id=invalidated_entity_id,
                        recommended_action="Recompose or human-review this paragraph against updated empirical data.",
                        is_blocking=True,
                    )
                )

        return affected_paragraph_ids
