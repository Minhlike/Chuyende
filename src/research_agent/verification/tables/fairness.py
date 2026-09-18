"""
Kiểm toán viên về tính công bằng và khả năng so sánh của bảng (Nhắc 6 Mục 56)
"""

from typing import Any, Dict, List, Optional, Tuple


class TableFairnessAuditor:
    """
    Kiểm tra các bảng so sánh để ngăn chặn việc so sánh giữa các giấy tờ gây hiểu lầm:
    - Phân chia tập dữ liệu khác nhau (e.g. 80/20 so với 60/40)
    - Mức độ chi tiết đánh giá khác nhau (e.g. sự kiện so với thực thể và máy chủ)
    - Các phương pháp nội suy số liệu khác nhau
    """

    def audit_comparison_fairness(
        self,
        method_metadata: List[Dict[str, Any]],
    ) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra danh sách {method_name, dataset_version, split_strategy, mức độ chi tiết, source_type}.
        Trả về (is_directly_comparable, incomparability_reason).
        """
        if len(method_metadata) <= 1:
            return True, None

        first = method_metadata[0]
        dataset_ver = first.get("dataset_version")
        split_strat = first.get("split_strategy")
        granularity = first.get("granularity")

        for m in method_metadata[1:]:
            if m.get("dataset_version") != dataset_ver:
                return False, (
                    f"DATASET_VERSION_MISMATCH: '{first.get('method_name')}' evaluated on {dataset_ver} "
                    f"while '{m.get('method_name')}' evaluated on {m.get('dataset_version')}."
                )
            if m.get("split_strategy") != split_strat:
                return False, (
                    f"SPLIT_STRATEGY_MISMATCH: '{first.get('method_name')}' evaluated on {split_strat} "
                    f"while '{m.get('method_name')}' evaluated on {m.get('split_strategy')}."
                )
            if m.get("granularity") != granularity:
                return False, (
                    f"GRANULARITY_MISMATCH: '{first.get('method_name')}' computed at {granularity} "
                    f"while '{m.get('method_name')}' computed at {m.get('granularity')}."
                )

        return True, None
