"""
Unit Tests for Datasets, Metrics, Tables & Figures (Prompt 6, TEST-DATA, TEST-METRIC, TEST-TBL, TEST-FIG)
"""

import os
import tempfile
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from research_agent.verification.datasets.data_validator import DataValidator
from research_agent.verification.datasets.data_profiler import DataProfiler
from research_agent.verification.datasets.split_validator import AntiLeakageSplitValidator
from research_agent.verification.metrics.recomputation import MetricRecomputationEngine
from research_agent.verification.metrics.thresholds import ThresholdAuditor
from research_agent.verification.tables.builder import TableBuilder
from research_agent.verification.tables.fairness import TableFairnessAuditor
from research_agent.verification.figures.builder import FigureBuilder
from research_agent.verification.figures.metadata import FigureMetadataManager


class TestDatasetsTablesFigures:
    def setup_method(self):
        self.validator = DataValidator()
        self.profiler = DataProfiler()
        self.split_val = AntiLeakageSplitValidator()
        self.metric_eng = MetricRecomputationEngine()
        self.threshold_auditor = ThresholdAuditor()
        self.table_builder = TableBuilder()
        self.table_fairness = TableFairnessAuditor()
        self.tmp_dir = tempfile.mkdtemp()
        self.figure_builder = FigureBuilder(output_dir=self.tmp_dir)
        self.fig_metadata = FigureMetadataManager()

    def test_data_01_hash_and_schema_validation(self):
        """TEST-DATA-01: Verifies file SHA-256 and schema checks."""
        tmp_file = Path(self.tmp_dir) / "test_data.csv"
        df = pd.DataFrame({
            "timestamp": ["2026-01-01 10:00:00", "2026-01-01 10:01:00"],
            "event_id": [1, 2],
            "label": [0, 1],
        })
        df.to_csv(tmp_file, index=False)

        sha = self.validator.calculate_file_sha256(tmp_file)
        valid, msg = self.validator.validate_file_hash(tmp_file, sha)
        assert valid is True

        schema_ok, issues = self.validator.validate_dataframe_schema(
            df, required_columns=["timestamp", "event_id", "label"], timestamp_col="timestamp", label_col="label"
        )
        assert schema_ok is True
        assert len(issues) == 0

    def test_data_02_temporal_leakage_detection(self):
        """TEST-DATA-02: Flags temporal leakage (train timestamp > test timestamp)."""
        train_df = pd.DataFrame({"timestamp": ["2026-01-05 12:00:00", "2026-01-06 12:00:00"]})
        test_df = pd.DataFrame({"timestamp": ["2026-01-02 12:00:00", "2026-01-03 12:00:00"]})
        valid, issues = self.split_val.audit_temporal_order(train_df, None, test_df, "timestamp")
        assert valid is False
        assert any("TEMPORAL_LEAKAGE" in i for i in issues)

    def test_data_03_entity_holdout_leakage(self):
        """TEST-DATA-03: Flags host/entity leakage across train and test."""
        train_df = pd.DataFrame({"host": ["host-01", "host-02", "host-03"]})
        test_df = pd.DataFrame({"host": ["host-03", "host-04"]})  # host-03 leaks
        valid, issues = self.split_val.audit_entity_holdout(train_df, test_df, "host")
        assert valid is False
        assert any("ENTITY_LEAKAGE" in i for i in issues)

    def test_metric_01_confusion_matrix_and_f1(self):
        """TEST-METRIC-01: Deterministic Precision, Recall, F1 calculation."""
        y_true = [1, 1, 1, 1, 0, 0, 0, 0]
        y_pred = [1, 1, 1, 0, 0, 0, 1, 0]  # TP=3, FN=1, FP=1, TN=3
        cm = self.metric_eng.compute_confusion_matrix(y_true, y_pred)
        assert cm.tp == 3
        assert cm.fn == 1
        assert cm.fp == 1
        assert cm.tn == 3
        assert cm.precision == 0.75
        assert cm.recall == 0.75
        assert cm.f1 == 0.75
        assert cm.fpr == 0.25

    def test_metric_02_trapezoidal_pr_auc(self):
        """TEST-METRIC-02: Deterministic PR-AUC integration."""
        y_true = [1, 0, 1, 0, 1]
        y_scores = [0.9, 0.8, 0.7, 0.2, 0.1]
        auc, r_curve, p_curve, thrs = self.metric_eng.compute_pr_curve_and_auc(y_true, y_scores)
        assert 0.0 < auc <= 1.0
        assert len(r_curve) == len(p_curve)

    def test_tbl_01_deterministic_table_export(self):
        """TEST-TBL-01: TableBuilder produces aligned CSV, Markdown, LaTeX with SHA-256."""
        df = pd.DataFrame({
            "Method": ["Baseline", "OURS"],
            "F1": [85.2, 98.4],
            "Recall@0.1%FPR": [72.1, 95.6],
        })
        spec = self.table_builder.build_table(
            table_id="TBL-000001",
            title="Detection Performance Comparison",
            caption="Performance comparison across benchmarks",
            df=df,
        )
        assert spec.table_id == "TBL-000001"
        assert len(spec.output_sha256) == 64
        assert "Baseline" in spec.output_markdown
        assert "tabular" in spec.output_latex

    def test_tbl_02_table_fairness_mismatch_audit(self):
        """TEST-TBL-02: Flags comparability mismatch when splits or granularities differ."""
        methods = [
            {"method_name": "PriorWork", "dataset_version": "v1.0", "split_strategy": "RANDOM", "granularity": "EVENT"},
            {"method_name": "OURS", "dataset_version": "v1.0", "split_strategy": "TEMPORAL", "granularity": "EVENT"},
        ]
        is_comp, reason = self.table_fairness.audit_comparison_fairness(methods)
        assert is_comp is False
        assert "SPLIT_STRATEGY_MISMATCH" in reason

    def test_fig_01_pr_curve_generation_and_companion_data(self):
        """TEST-FIG-01: Generates PR curve image, companion CSV data, and metadata JSON."""
        curves = [
            {"name": "Baseline", "recalls": [0.0, 0.5, 1.0], "precisions": [1.0, 0.8, 0.5], "pr_auc": 0.75},
            {"name": "OURS", "recalls": [0.0, 0.7, 1.0], "precisions": [1.0, 0.95, 0.9], "pr_auc": 0.95},
        ]
        spec = self.figure_builder.plot_pr_curve(
            figure_id="FIG-000001",
            title="Precision-Recall Tradeoff",
            caption="Comparison of PR trajectories",
            curves_data=curves,
        )
        assert Path(spec.output_file_rel_path).exists()
        assert Path(spec.companion_data_csv_rel_path).exists()
        assert len(spec.output_sha256) == 64
        assert len(spec.companion_data_sha256) == 64

        meta_file = Path(self.tmp_dir) / "fig-meta.json"
        self.fig_metadata.generate_metadata_file(spec, meta_file)
        assert meta_file.exists()
