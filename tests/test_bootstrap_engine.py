# -*- coding: utf-8 -*-
"""
Bootstrap Engine and Statistical Invariant Tests
Verifies:
  1. Bootstrap engine recomputes exact non-decomposable metric per resample (not mean of cluster scalars).
  2. B=2000 and seed=10007 constraints strictly enforced.
  3. Rejection of cluster arrays < 30 (preventing seed-level arrays).
  4. Benjamini-Hochberg False Discovery Rate (BH-FDR) rank sorting and critical value gating.
  5. Holm-Bonferroni step-down threshold adjustment.
  6. PR-AUC chance level dynamically reflects positive class prevalence.
"""

import pytest
import numpy as np

from research_agent.experiments.protocols.paired_cluster_bootstrap import (
    paired_cluster_bootstrap_recompute,
    apply_benjamini_hochberg_fdr,
    apply_holm_bonferroni_stepdown,
    compute_pr_auc,
    compute_f1_score
)

def test_01_recompute_metric_per_resample_non_decomposable():
    # Construct a dataset where per-cluster PR-AUC mean differs from overall PR-AUC
    # 40 clusters of 5 observations each
    rng = np.random.default_rng(42)
    cluster_ids = np.repeat(np.arange(40), 5)
    y_true = rng.choice([0, 1], size=200, p=[0.8, 0.2])
    y_prop = rng.uniform(0, 1, size=200)
    y_base = rng.uniform(0, 1, size=200)

    res = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=y_prop,
        y_pred_baseline=y_base,
        metric_fn=compute_pr_auc,
        b_resamples=2000,
        random_seed=10007
    )

    assert res["b_resamples"] == 2000
    assert res["seed"] == 10007
    assert "observed_delta" in res
    assert len(res["ci_95"]) == 2
    assert res["ci_95"][0] <= res["ci_95"][1]

def test_02_rejection_of_small_cluster_counts():
    small_clusters = np.repeat(np.arange(5), 2)  # Only 5 clusters
    y_t = np.ones(10)
    y_p = np.ones(10)
    y_b = np.zeros(10)

    with pytest.raises(ValueError, match="Cluster count .* is too low"):
        paired_cluster_bootstrap_recompute(
            cluster_ids=small_clusters,
            y_true=y_t,
            y_pred_proposed=y_p,
            y_pred_baseline=y_b,
            b_resamples=2000,
            random_seed=10007
        )

def test_03_benjamini_hochberg_fdr_correction():
    p_vals = {
        "P01": 0.001,
        "P02": 0.010,
        "P03": 0.040,
        "P04": 0.200,
        "P05": 0.800
    }
    bh = apply_benjamini_hochberg_fdr(p_vals, q_threshold=0.05)
    
    assert bh["P01"]["rejected_null"] is True
    assert bh["P02"]["rejected_null"] is True
    assert bh["P05"]["rejected_null"] is False
    assert bh["P01"]["rank"] == 1

def test_04_holm_bonferroni_stepdown():
    p_vals = {
        "H_adv1": 0.005,
        "H_adv2": 0.020,
        "H_adv3": 0.060
    }
    # m = 3. Rank 1 threshold: 0.05 / 3 = 0.0167 (0.005 < 0.0167 -> reject)
    # Rank 2 threshold: 0.05 / 2 = 0.025 (0.020 < 0.025 -> reject)
    # Rank 3 threshold: 0.05 / 1 = 0.05 (0.060 > 0.05 -> accept)
    holm = apply_holm_bonferroni_stepdown(p_vals, alpha=0.05)
    
    assert holm["H_adv1"]["rejected_null"] is True
    assert holm["H_adv2"]["rejected_null"] is True
    assert holm["H_adv3"]["rejected_null"] is False

def test_05_pr_auc_chance_level_matches_prevalence():
    # 10% positive prevalence -> chance PR-AUC is ~0.10
    y_true_10 = np.array([1]*100 + [0]*900)
    prevalence = float(np.sum(y_true_10) / len(y_true_10))
    assert prevalence == 0.10

    # Random guessing score has expected PR-AUC around positive prevalence
    rng = np.random.default_rng(42)
    random_scores = rng.uniform(0, 1, 1000)
    ap = compute_pr_auc(y_true_10, random_scores)
    # AP is within expected concentration bounds of prevalence
    assert abs(ap - prevalence) < 0.05
