"""
Giao diện sổ cái bằng chứng (RC-01, RC-11, RC-12)
"""

from typing import Optional
from research_agent.schemas.evidence import Evidence
from research_agent.core.enums import VerificationStatus
from research_agent.core.identifiers import EntityPrefix
from research_agent.core.exceptions import EntityNotFoundError
from research_agent.storage.repository import ResearchRepository


class EvidenceLedger:
    """Quản lý việc đăng ký và xác nhận bằng chứng thực nghiệm và văn bản."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def register_evidence(
        self,
        source_id: str,
        locator: str,
        exact_quote: Optional[str] = None,
        paraphrase: Optional[str] = None,
        page: Optional[int] = None,
        section: Optional[str] = None,
        context_notes: Optional[str] = None,
        extraction_method: str = "MANUAL_EXTRACT",
    ) -> Evidence:
        """Đăng ký một mục bằng chứng mới với xác nhận nguồn bắt buộc."""
        source = self.repo.get_source(source_id)
        if not source:
            raise EntityNotFoundError(f"Source '{source_id}' does not exist in Source Store (RC-01).")

        evidence_id = self.repo.next_id(EntityPrefix.EVIDENCE)
        evidence = Evidence(
            evidence_id=evidence_id,
            source_id=source_id,
            locator=locator,
            exact_quote=exact_quote,
            paraphrase=paraphrase,
            page=page,
            section=section,
            context_notes=context_notes,
            extraction_method=extraction_method,
            verification_status=VerificationStatus.VERIFIED,
        )
        return self.repo.save_evidence(evidence)
