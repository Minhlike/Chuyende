"""
Giao diện sổ cái yêu cầu bồi thường (RC-04..RC-07, RC-13)
"""

from typing import List, Optional
from research_agent.schemas.claim import Claim, ClaimRelation
from research_agent.schemas.decision import ContradictionRecord
from research_agent.core.enums import ClaimType, IntellectualOwnership, EpistemicStatus, ArgumentRelationType
from research_agent.core.identifiers import EntityPrefix
from research_agent.core.exceptions import InvariantViolationError, EntityNotFoundError
from research_agent.storage.repository import ResearchRepository


class ClaimLedger:
    """Quản lý vòng đời, trạng thái dịch bệnh và xác minh các tuyên bố khoa học."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def register_claim(
        self,
        statement: str,
        claim_type: ClaimType,
        ownership: IntellectualOwnership,
        epistemic_status: EpistemicStatus = EpistemicStatus.UNVERIFIED,
        confidence: Optional[float] = None,
        assumptions: Optional[List[str]] = None,
        scope: Optional[str] = None,
        evidence_ids: Optional[List[str]] = None,
        experiment_run_id: Optional[str] = None,
        falsification_conditions: Optional[str] = None,
    ) -> Claim:
        """Đăng ký yêu cầu nguyên tử mới với ID ổn định xác định."""
        claim_id = self.repo.next_id(EntityPrefix.CLAIM)
        claim = Claim(
            claim_id=claim_id,
            statement=statement,
            claim_type=claim_type,
            ownership=ownership,
            epistemic_status=epistemic_status,
            confidence=confidence,
            assumptions=assumptions or [],
            scope=scope,
            evidence_ids=evidence_ids or [],
            experiment_run_id=experiment_run_id,
            falsification_conditions=falsification_conditions,
        )
        return self.repo.save_claim(claim)

    def link_evidence(self, claim_id: str, evidence_id: str) -> Claim:
        """Đính kèm một mục bằng chứng đã được xác thực vào yêu cầu bồi thường."""
        claim = self.repo.get_claim(claim_id)
        if not claim:
            raise EntityNotFoundError(f"Claim '{claim_id}' not found.")
        evidence = self.repo.get_evidence(evidence_id)
        if not evidence:
            raise EntityNotFoundError(f"Evidence '{evidence_id}' not found.")

        if evidence_id not in claim.evidence_ids:
            claim.evidence_ids.append(evidence_id)
            self.repo.save_claim(claim)
        return claim

    def register_contradiction(
        self,
        claim_a_id: str,
        claim_b_id: str,
        description: str,
        divergence_notes: Optional[str] = None,
    ) -> ContradictionRecord:
        """Ghi lại sự mâu thuẫn rõ ràng giữa hai tuyên bố (RC-13) và cập nhật các trạng thái nhận thức."""
        claim_a = self.repo.get_claim(claim_a_id)
        claim_b = self.repo.get_claim(claim_b_id)
        if not claim_a or not claim_b:
            raise EntityNotFoundError("Both conflicting claims must exist in the Claim Ledger.")

        # Cập nhật trạng thái dịch bệnh thành CONTESTED nếu trước đó là SUPPORTED hoặc UNVERIFIED
        if claim_a.epistemic_status in (EpistemicStatus.SUPPORTED, EpistemicStatus.UNVERIFIED):
            claim_a.epistemic_status = EpistemicStatus.CONTESTED
            self.repo.save_claim(claim_a)

        if claim_b.epistemic_status in (EpistemicStatus.SUPPORTED, EpistemicStatus.UNVERIFIED):
            claim_b.epistemic_status = EpistemicStatus.CONTESTED
            self.repo.save_claim(claim_b)

        ctr_id = self.repo.next_id(EntityPrefix.CONTRADICTION)
        ctr = ContradictionRecord(
            contradiction_id=ctr_id,
            claim_a_id=claim_a_id,
            claim_b_id=claim_b_id,
            description=description,
            domain_or_scope_divergence=divergence_notes,
            resolution_status="OPEN",
        )
        return self.repo.save_contradiction(ctr)
