"""
Kiểm toán viên chứng minh phương trình & bất biến (Nhắc 6 Phần 6..12, RC-08)
"""

from typing import Any, Dict, List, Optional, Tuple
from research_agent.core.enums import EquationType, IntellectualOwnership, VerificationStatus
from research_agent.schemas.equation import Equation
from research_agent.core.exceptions import ProvenanceError


class EquationProvenanceAuditor:
    """
    Thực thi các bất biến về nhập và xuất xứ nghiêm ngặt đối với các phương trình toán học.
    Đảm bảo cách ly các phương trình SOURCE, DERIVED và PROPOSED.
    """

    def audit_equation(self, eq: Equation) -> Tuple[bool, List[str]]:
        """Kiểm tra một phương trình cho các bất biến xuất xứ hợp pháp (RC-08)."""
        issues: List[str] = []

        # Bất biến 1: SOURCE_EQUATION yêu cầu source_id bên ngoài và bộ định vị
        if eq.equation_type == EquationType.SOURCE_EQUATION:
            if not eq.source_id or not eq.source_id.strip():
                issues.append(f"SOURCE_EQUATION '{eq.equation_id}' lacks mandatory source_id.")
            if not eq.source_locator or not eq.source_locator.strip():
                issues.append(f"SOURCE_EQUATION '{eq.equation_id}' lacks mandatory source_locator (page/equation number).")
            if eq.ownership != IntellectualOwnership.SOURCE:
                issues.append(f"SOURCE_EQUATION '{eq.equation_id}' must have ownership=SOURCE, got {eq.ownership}.")

        # Bất biến 2: DERIVED_EQUATION yêu cầu các phương trình gốc và các bước đạo hàm
        elif eq.equation_type == EquationType.DERIVED_EQUATION:
            if not eq.derivation:
                issues.append(f"DERIVED_EQUATION '{eq.equation_id}' lacks mandatory derivation record.")
            else:
                if not eq.derivation.parent_equation_ids:
                    issues.append(f"DERIVED_EQUATION '{eq.equation_id}' has empty parent_equation_ids.")
                if not eq.derivation.derivation_steps:
                    issues.append(f"DERIVED_EQUATION '{eq.equation_id}' has empty derivation_steps.")

        # Bất biến 3: PROPOSED_EQUATION phải có quyền sở hữu OURS với tính năng theo dõi thành phần
        elif eq.equation_type == EquationType.PROPOSED_EQUATION:
            if eq.ownership != IntellectualOwnership.OURS:
                issues.append(f"PROPOSED_EQUATION '{eq.equation_id}' should have ownership=OURS.")

        # Bất biến 4: Không có LaTeX trống
        if not eq.latex or not eq.latex.strip():
            issues.append(f"Equation '{eq.equation_id}' has empty LaTeX content.")

        return len(issues) == 0, issues
