"""
Kiểm toán viên kiểm tra ngưỡng chứng minh và chống điều chỉnh (Nhắc 6 Mục 30)
"""

from typing import Any, Dict, List, Optional, Tuple


class ThresholdAuditor:
    """
    Đảm bảo quyết định lựa chọn ngưỡng xuất xứ.
    Thực thi các ngưỡng được chọn theo tiêu chí phân tách xác thực hoặc đặt trước,
    không bao giờ điều chỉnh sau phần kiểm tra.
    """

    def audit_threshold_selection(
        self,
        threshold_value: float,
        split_used_for_selection: str,
        selection_criterion: str,
    ) -> Tuple[bool, Optional[str]]:
        """Kiểm tra xem ngưỡng có được chọn hợp pháp trên phân vùng xác thực hay không."""
        split_clean = split_used_for_selection.strip().upper()
        if split_clean in ["TEST", "TEST_SET", "EVAL_TEST"]:
            return False, f"TEST_SET_TUNING_LEAKAGE: Threshold {threshold_value} was tuned directly on '{split_used_for_selection}'."

        if not selection_criterion or len(selection_criterion.strip()) < 3:
            return False, "Threshold lacks an explicit optimization criterion (e.g. 'Max F1 on Validation', 'FPR <= 0.1%')."

        return True, None
