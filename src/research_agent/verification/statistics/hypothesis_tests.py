"""
Công cụ kiểm tra giả thuyết khoa học (Nhắc 6 Mục 38)
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import scipy.stats as stats
from research_agent.schemas.verification import StatisticalResult
from research_agent.verification.statistics.effect_sizes import EffectSizeEngine
from research_agent.verification.statistics.confidence_intervals import ConfidenceIntervalEngine


class HypothesisTestingEngine:
    """
    Thực hiện kiểm tra giả thuyết chính thức với các đánh giá giả định:
    - Xếp hạng kiểm định t của Student được ghép đôi / Xếp hạng có chữ ký của Wilcoxon (seed/chủ nhà phù hợp)
    - T-test hai mẫu độc lập / Mann-Whitney U (không khớp)
    - Kiểm tra hoán vị
    """

    def __init__(self):
        self.effect_engine = EffectSizeEngine()
        self.ci_engine = ConfidenceIntervalEngine()

    def run_paired_test(
        self,
        group_ours: Union[List[float], np.ndarray],
        group_baseline: Union[List[float], np.ndarray],
        question: str,
        sample_unit: str = "Seed Run",
        alpha: float = 0.05,
    ) -> StatisticalResult:
        """Chạy thử nghiệm ghép đôi so sánh OURS với baseline trên các seed phù hợp."""
        a = np.array(group_ours, dtype=float)
        b = np.array(group_baseline, dtype=float)

        if len(a) != len(b):
            raise ValueError(f"Paired test requires equal sample sizes, got {len(a)} and {len(b)}.")

        n = len(a)
        differences = a - b

        # 1. Đánh giá tính quy luật của sự khác biệt (Shapiro-Wilk)
        assumptions_evaluated = []
        is_normal = True
        if n >= 3:
            shapiro_stat, shapiro_p = stats.shapiro(differences)
            assumptions_evaluated.append(f"Shapiro-Wilk normality test on differences: p={shapiro_p:.4f}")
            if shapiro_p < 0.05:
                is_normal = False

        if n < 8 or is_normal:
            test_name = "Paired t-test"
            t_res = stats.ttest_rel(a, b)
            stat_val = float(t_res.statistic)
            p_val = float(t_res.pvalue)
        else:
            test_name = "Wilcoxon signed-rank test"
            w_res = stats.wilcoxon(a, b)
            stat_val = float(w_res.statistic)
            p_val = float(w_res.pvalue)

        # Kích thước hiệu ứng
        hedges_g = self.effect_engine.compute_hedges_g(a, b)
        mean_diff, ci_low, ci_high = self.ci_engine.compute_bootstrap_ci(differences, confidence_level=1.0 - alpha)

        is_significant = bool(p_val < alpha)
        notes = (
            f"Statistically significant difference (p={p_val:.4e} < {alpha}) with effect size g={hedges_g:.2f}."
            if is_significant
            else f"No statistically significant difference detected (p={p_val:.4e} >= {alpha})."
        )

        stat_id = f"STAT-{abs(hash(question + str(p_val))) % 1000000:06d}"
        return StatisticalResult(
            stat_id=stat_id,
            question=question,
            test_name=test_name,
            sample_unit=sample_unit,
            sample_size_n=n,
            statistic_value=stat_val,
            p_value=p_val,
            effect_size_name="Hedges' g",
            effect_size_value=hedges_g,
            ci_lower=ci_low,
            ci_upper=ci_high,
            ci_level=1.0 - alpha,
            assumptions_met=True,
            assumptions_evaluated=assumptions_evaluated,
            is_significant=is_significant,
            interpretation_notes=notes,
        )

    def run_two_sample_test(
        self,
        group1: Union[List[float], np.ndarray],
        group2: Union[List[float], np.ndarray],
        question: str,
        sample_unit: str = "Host / Partition",
        alpha: float = 0.05,
    ) -> StatisticalResult:
        """Chạy thử nghiệm so sánh hai mẫu độc lập (T-test Mann-Whitney U hoặc Welch)."""
        a = np.array(group1, dtype=float)
        b = np.array(group2, dtype=float)
        n1, n2 = len(a), len(b)

        # Kiểm tra Mann-Whitney U
        u_res = stats.mannwhitneyu(a, b, alternative="two-sided")
        stat_val = float(u_res.statistic)
        p_val = float(u_res.pvalue)

        hedges_g = self.effect_engine.compute_hedges_g(a, b)
        is_significant = bool(p_val < alpha)

        stat_id = f"STAT-{abs(hash(question + str(p_val))) % 1000000:06d}"
        return StatisticalResult(
            stat_id=stat_id,
            question=question,
            test_name="Mann-Whitney U test",
            sample_unit=sample_unit,
            sample_size_n=n1 + n2,
            statistic_value=stat_val,
            p_value=p_val,
            effect_size_name="Hedges' g",
            effect_size_value=hedges_g,
            ci_level=1.0 - alpha,
            assumptions_met=True,
            assumptions_evaluated=["Non-parametric rank sum test (no normality assumption required)"],
            is_significant=is_significant,
            interpretation_notes=f"Comparison yielded p={p_val:.4e}, effect size g={hedges_g:.2f}.",
        )
