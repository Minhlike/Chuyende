"""
Kiểm toán viên liêm chính khoa học & Tường lửa chống ảo giác (Nhắc 6 Mục 90..96, RC-08..18)
"""

from typing import Any, Dict, List, Optional, Tuple
from research_agent.core.enums import (
    AllowedWordingStrength,
    NumericalClaimType,
    VerificationStatus,
    VerificationRequestStatus,
)
from research_agent.schemas.verification import (
    NumericalClaim,
    TableSpecification,
    FigureSpecification,
    VerifiedClaimBundle,
    ResultBundle,
)
from research_agent.schemas.equation import Equation


class NumericalHallucinationAuditor:
    """
    Bảo vệ chống lại những tuyên bố bằng số vô căn cứ, bịa đặt hoặc được chọn lọc kỹ lưỡng (Nhắc 6 Mục 90).
    """

    def audit_numerical_claim(self, claim: NumericalClaim) -> Tuple[bool, List[str]]:
        issues = []

        # Quy tắc 1: Phải có xuất xứ
        if claim.source_type == NumericalClaimType.SOURCE_REPORTED:
            if not claim.source_id:
                issues.append(f"Numerical claim '{claim.numerical_claim_id}' is SOURCE_REPORTED but lacks source_id.")
            if not claim.source_locator:
                issues.append(f"Numerical claim '{claim.numerical_claim_id}' lacks source_locator.")
        elif claim.source_type in [NumericalClaimType.RECOMPUTED, NumericalClaimType.EXPERIMENT_RESULT]:
            if not claim.computation_id:
                issues.append(f"Numerical claim '{claim.numerical_claim_id}' is computed but lacks computation_id.")

        # Quy tắc 2: Câu lệnh và số lượng không trống
        if not claim.statement or len(claim.statement.strip()) < 5:
            issues.append(f"Numerical claim '{claim.numerical_claim_id}' has empty statement.")
        if not claim.quantity_name or len(claim.quantity_name.strip()) < 2:
            issues.append(f"Numerical claim '{claim.numerical_claim_id}' has empty quantity_name.")

        return len(issues) == 0, issues


class VerificationGateForWriting:
    """
    Cổng tường lửa cho Trình soạn thảo chương 7 (Nhắc 6 Mục 95, 139).
    Chặn các luận điểm (claim) chưa được xác minh, gói kết quả bị thiếu hoặc ngôn ngữ xác nhận phóng đại.
    """

    def audit_claim_for_thesis_composition(
        self,
        claim_bundle: VerifiedClaimBundle,
        result_bundle: Optional[ResultBundle] = None,
    ) -> Tuple[bool, List[str]]:
        issues = []

        # Kiểm tra các yêu cầu bằng số bên trong gói
        for num in claim_bundle.numerical_claims:
            if num.verification_status != VerificationStatus.VERIFIED:
                issues.append(
                    f"Claim contains unverified numerical quantity '{num.quantity_name}': status={num.verification_status}."
                )

        # Kiểm tra căn chỉnh cường độ từ ngữ được phép
        if claim_bundle.allowed_wording_strength == AllowedWordingStrength.STRONG_SUPPORT:
            if not claim_bundle.source_evidence_ids and not claim_bundle.result_bundle_id:
                issues.append("STRONG_SUPPORT requires multiple convergent empirical evidence sources.")

        if claim_bundle.allowed_wording_strength == AllowedWordingStrength.DESCRIPTIVE_ONLY:
            stmt_lower = claim_bundle.statement.lower()
            if any(w in stmt_lower for w in ["causes", "outperforms", "superior", "proves"]):
                issues.append(
                    "DESCRIPTIVE_ONLY claim uses comparative or causal language ('causes', 'outperforms', 'proves')."
                )

        return len(issues) == 0, issues
