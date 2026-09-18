"""
Bộ tổng hợp nhiều seed & Bộ bảo vệ hái anh đào (Nhắc 6 Phần 42)
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from research_agent.verification.statistics.descriptive import DescriptiveStatisticsEngine
from research_agent.verification.statistics.confidence_intervals import ConfidenceIntervalEngine


class MultiSeedAggregator:
    """
    Tổng hợp các số liệu thử nghiệm trên các seed riêng biệt (K >= 5).
    Thực thi báo cáo trung bình ± SD hoặc trung vị [IQR] và phát hiện việc chọn anh đào trong các lần chạy đơn lẻ tốt nhất.
    """

    def __init__(self):
        self.desc_engine = DescriptiveStatisticsEngine()
        self.ci_engine = ConfidenceIntervalEngine()

    def aggregate_seed_metrics(
        self,
        seed_runs: List[Dict[str, Any]],
        metric_key: str,
    ) -> Dict[str, Any]:
        """
        Tổng hợp các giá trị số liệu trên các lần chạy.
        Trả về bản tóm tắt đầy đủ với các cảnh báo trung bình, tiêu chuẩn, CI, tối thiểu, tối đa, trung bình và hái anh đào.
        """
        values = [float(r[metric_key]) for r in seed_runs if metric_key in r and r[metric_key] is not None]
        summary = self.desc_engine.compute_summary(values)
        mean, ci_low, ci_high = self.ci_engine.compute_parametric_ci(values)

        return {
            "metric_key": metric_key,
            "num_seeds": len(values),
            "mean": summary["mean"],
            "std": summary["std"],
            "median": summary["median"],
            "iqr": summary["iqr"],
            "ci_95_lower": ci_low,
            "ci_95_upper": ci_high,
            "min_run": summary["min"],
            "max_run": summary["max"],
            "all_seed_values": values,
        }

    def audit_cherry_picking(
        self,
        reported_value: float,
        seed_values: List[float],
        tolerance: float = 1e-4,
    ) -> Tuple[bool, Optional[str]]:
        """
        BestRunCherryPickingGuard:
        Kiểm tra xem đại lượng vô hướng đơn được báo cáo có khớp với ONLY lần chạy seed tối đa hay không
        thay vì tóm tắt giá trị trung bình/phân phối.
        """
        arr = np.array(seed_values, dtype=float)
        max_val = np.max(arr)
        mean_val = np.mean(arr)

        if abs(reported_value - max_val) < tolerance and abs(reported_value - mean_val) > tolerance:
            return False, (
                f"CHERRY_PICKING_DETECTED: Reported value {reported_value} matches the maximum single seed "
                f"({max_val}) rather than the seed mean ({mean_val:.4f} ± {np.std(arr, ddof=1):.4f})."
            )

        return True, None
