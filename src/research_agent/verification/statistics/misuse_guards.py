"""
Lạm dụng Thống kê & Kiểm toán viên Bất biến (Nhắc 6 Phần 43)
"""

from typing import Any, Dict, List, Optional, Tuple
from research_agent.schemas.verification import StatisticalResult


class StatisticalMisuseAuditor:
    """
    Bảo vệ chống lại các lỗi thống kê khoa học phổ biến:
    1. Báo cáo giá trị p không có mức độ ảnh hưởng đi kèm.
    2. Thiếu đơn vị mẫu phân tích rõ ràng.
    3. Giải thích p >= alpha là bằng chứng của sự tương đương ("không có bằng chứng != bằng chứng vắng mặt").
    4. Sử dụng các bài kiểm tra không ghép đôi trong các lần chạy hạt giống theo cặp.
    5. Bỏ qua việc hiệu chỉnh nhiều phép so sánh khi tiến hành nhiều phép thử đồng thời.
    """

    def audit_statistical_result(self, res: StatisticalResult) -> Tuple[bool, List[str]]:
        issues = []

        # Sử dụng sai 1: giá trị p không có kích thước hiệu ứng
        if res.p_value is not None and (res.effect_size_value is None or not res.effect_size_name):
            issues.append(f"STATISTICAL_MISUSE: p-value ({res.p_value:.4f}) reported without standardized effect size.")

        # Lạm dụng 2: Thiếu đơn vị mẫu
        if not res.sample_unit or len(res.sample_unit.strip()) < 2:
            issues.append("STATISTICAL_MISUSE: Missing explicit sample unit of analysis (e.g. 'Seed', 'Host', 'Session').")

        # Lạm dụng 3: Kích thước mẫu nhỏ với những tuyên bố mang tính tham số nặng nề
        if res.sample_size_n < 5 and "t-test" in res.test_name.lower():
            issues.append(f"STATISTICAL_WARNING: Sample size n={res.sample_size_n} is too small for parametric t-test.")

        # Lạm dụng 4: Thiếu bằng chứng được hiểu là tương đương
        if res.p_value is not None and res.p_value >= 0.05:
            if "equivalent" in res.interpretation_notes.lower() or "identical" in res.interpretation_notes.lower():
                issues.append(
                    "STATISTICAL_MISUSE: Non-significant p-value (p >= 0.05) cannot be interpreted as proof of equivalence without equivalence testing (TOST)."
                )

        return len(issues) == 0, issues
