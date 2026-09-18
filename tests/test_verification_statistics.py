"""
Kiểm thử đơn vị cho Công cụ xác minh thống kê (Dấu nhắc 6, TEST-STAT-01..10)
"""

import pytest
import numpy as np
from research_agent.verification.statistics.descriptive import DescriptiveStatisticsEngine
from research_agent.verification.statistics.confidence_intervals import ConfidenceIntervalEngine
from research_agent.verification.statistics.effect_sizes import EffectSizeEngine
from research_agent.verification.statistics.hypothesis_tests import HypothesisTestingEngine
from research_agent.verification.statistics.multi_seed_aggregator import MultiSeedAggregator
from research_agent.verification.statistics.misuse_guards import StatisticalMisuseAuditor
from research_agent.schemas.verification import StatisticalResult


class TestStatisticalVerification:
    def setup_method(self):
        self.desc_engine = DescriptiveStatisticsEngine()
        self.ci_engine = ConfidenceIntervalEngine()
        self.effect_engine = EffectSizeEngine()
        self.hyp_engine = HypothesisTestingEngine()
        self.aggregator = MultiSeedAggregator()
        self.misuse_auditor = StatisticalMisuseAuditor()

    def test_stat_01_descriptive_summary(self):
        """TEST-STAT-01: Xác minh giá trị trung bình, độ lệch chuẩn mẫu, trung vị, IQR."""
        values = [10.0, 12.0, 14.0, 16.0, 18.0]
        res = self.desc_engine.compute_summary(values)
        assert res["n"] == 5
        assert res["mean"] == 14.0
        assert round(res["std"], 2) == 3.16
        assert res["median"] == 14.0
        assert res["iqr"] == 4.0

    def test_stat_02_parametric_confidence_interval(self):
        """TEST-STAT-02: Xác minh khoảng tin cậy 95% của Học sinh."""
        values = [10.0, 12.0, 14.0, 16.0, 18.0]
        mean, low, high = self.ci_engine.compute_parametric_ci(values, confidence_level=0.95)
        assert mean == 14.0
        assert low < 14.0 < high
        assert round(low, 2) == 10.07
        assert round(high, 2) == 17.93

    def test_stat_03_deterministic_bootstrap_ci(self):
        """TEST-STAT-03: Bootstrap CI với hạt giống cố định trả về các giới hạn giống hệt nhau."""
        values = [10.0, 12.0, 14.0, 16.0, 18.0]
        m1, low1, high1 = self.ci_engine.compute_bootstrap_ci(values, confidence_level=0.95, random_seed=42)
        m2, low2, high2 = self.ci_engine.compute_bootstrap_ci(values, confidence_level=0.95, random_seed=42)
        assert m1 == m2 == 14.0
        assert low1 == low2
        assert high1 == high2

    def test_stat_04_cohens_d_and_hedges_g(self):
        """TEST-STAT-04: Tính toán kích thước hiệu ứng được tiêu chuẩn hóa."""
        g1 = [95.0, 96.0, 97.0, 95.5, 96.5]
        g2 = [85.0, 86.0, 84.5, 85.5, 86.5]
        d = self.effect_engine.compute_cohens_d(g1, g2)
        g = self.effect_engine.compute_hedges_g(g1, g2)
        assert d > 0.0
        assert g > 0.0
        assert g < d  # Hedges' g nhỏ hơn một chút do hệ số hiệu chỉnh mẫu nhỏ

    def test_stat_05_paired_hypothesis_test(self):
        """TEST-STAT-05: Thử nghiệm ghép đôi phát hiện chính xác sự cải thiện đáng kể."""
        ours = [0.95, 0.96, 0.94, 0.97, 0.95]
        base = [0.85, 0.86, 0.84, 0.85, 0.83]
        res = self.hyp_engine.run_paired_test(ours, base, question="Test paired superiority")
        assert res.p_value < 0.001
        assert res.is_significant is True
        assert res.effect_size_name == "Hedges' g"
        assert res.effect_size_value > 3.0

    def test_stat_06_two_sample_unpaired_test(self):
        """TEST-STAT-06: Thử nghiệm Mann-Whitney U độc lập."""
        g1 = [10, 12, 14, 15, 16]
        g2 = [2, 4, 5, 6, 7]
        res = self.hyp_engine.run_two_sample_test(g1, g2, question="Test two sample comparison")
        assert res.p_value < 0.05
        assert res.is_significant is True

    def test_stat_07_multi_seed_aggregation(self):
        """TEST-STAT-07: Tổng hợp trên nhiều hạt giống ngẫu nhiên."""
        runs = [
            {"f1": 0.92, "seed": 1},
            {"f1": 0.94, "seed": 2},
            {"f1": 0.93, "seed": 3},
            {"f1": 0.95, "seed": 4},
            {"f1": 0.91, "seed": 5},
        ]
        summary = self.aggregator.aggregate_seed_metrics(runs, "f1")
        assert summary["num_seeds"] == 5
        assert round(summary["mean"], 2) == 0.93
        assert summary["min_run"] == 0.91
        assert summary["max_run"] == 0.95

    def test_stat_08_cherry_picking_guard(self):
        """TEST-STAT-08: Cờ BestRunCherryPickingGuard chỉ báo cáo một hạt giống tốt nhất."""
        seed_vals = [0.91, 0.92, 0.93, 0.94, 0.98]  # max = 0.98, mean = 0.936
        valid, warning = self.aggregator.audit_cherry_picking(0.98, seed_vals)
        assert valid is False
        assert "CHERRY_PICKING_DETECTED" in warning

    def test_stat_09_statistical_misuse_p_without_effect_size(self):
        """TEST-STAT-09: Cờ giá trị p được báo cáo không có kích thước hiệu ứng."""
        res = StatisticalResult(
            stat_id="STAT-TEST-01",
            question="Question",
            test_name="t-test",
            sample_unit="Seed",
            sample_size_n=10,
            p_value=0.01,
            effect_size_name=None,  # Thiếu kích thước hiệu ứng
            effect_size_value=None,
        )
        valid, issues = self.misuse_auditor.audit_statistical_result(res)
        assert valid is False
        assert any("without standardized effect size" in i for i in issues)

    def test_stat_10_statistical_misuse_absence_of_evidence_claim(self):
        """TEST-STAT-10: Cờ diễn giải p >= 0,05 là bằng chứng về sự tương đương."""
        res = StatisticalResult(
            stat_id="STAT-TEST-02",
            question="Question",
            test_name="t-test",
            sample_unit="Seed",
            sample_size_n=10,
            p_value=0.35,
            effect_size_name="Cohen's d",
            effect_size_value=0.1,
            interpretation_notes="The methods are completely identical and equivalent.",
        )
        valid, issues = self.misuse_auditor.audit_statistical_result(res)
        assert valid is False
        assert any("proof of equivalence" in i for i in issues)
