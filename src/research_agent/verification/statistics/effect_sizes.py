"""
Số liệu kích thước hiệu ứng được tiêu chuẩn hóa (Nhắc 6 Phần 37)
"""

from typing import Any, Dict, List, Tuple, Union
import numpy as np


class EffectSizeEngine:
    """
    Tính toán kích thước hiệu ứng thống kê được tiêu chuẩn hóa:
    Cohen's d, Hedges' g (hiệu chỉnh mẫu nhỏ), tương quan cấp bậc-lưỡng chuỗi,
    và thay đổi phần trăm tuyệt đối/tương đối.
    """

    def compute_cohens_d(
        self,
        group1: Union[List[float], np.ndarray],
        group2: Union[List[float], np.ndarray],
    ) -> float:
        """
        Tính Cohen's d:
        d = (mean1 - mean2) / s_pooled
        """
        a = np.array(group1, dtype=float)
        b = np.array(group2, dtype=float)
        n1, n2 = len(a), len(b)
        if n1 < 2 or n2 < 2:
            return 0.0

        mean1, mean2 = np.mean(a), np.mean(b)
        var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return 0.0
        return float((mean1 - mean2) / pooled_std)

    def compute_hedges_g(
        self,
        group1: Union[List[float], np.ndarray],
        group2: Union[List[float], np.ndarray],
    ) -> float:
        """
        Tính g Hedges' với hệ số hiệu chỉnh mẫu nhỏ chính xác:
        g = d * (1 - 3 / (4 * (n1 + n2) - 9))
        """
        n1, n2 = len(group1), len(group2)
        d = self.compute_cohens_d(group1, group2)
        if (n1 + n2) <= 3:
            return float(d)
        correction = 1.0 - (3.0 / (4.0 * (n1 + n2) - 9.0))
        return float(d * correction)

    def compute_absolute_and_relative_diff(
        self,
        baseline_mean: float,
        proposed_mean: float,
    ) -> Dict[str, float]:
        """Tính toán sự khác biệt tuyệt đối (delta) và tỷ lệ phần trăm thay đổi tương đối."""
        abs_diff = proposed_mean - baseline_mean
        rel_diff_pct = (abs_diff / baseline_mean * 100.0) if baseline_mean != 0 else 0.0
        return {
            "absolute_difference": float(abs_diff),
            "relative_difference_pct": float(rel_diff_pct),
        }
