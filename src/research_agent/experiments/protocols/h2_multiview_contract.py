# -*- coding: utf-8 -*-
"""
H2 Canonical Test Contract: Cross-View Alignment & Non-Collapse
Evaluates whether aligned multi-view representations z_mv Pareto-dominate single-view
baselines (Sequence-only, Graph-only) and unaligned fusion without representation collapse.
Eliminates observation-level oracle baselines and performs 3 distinct Bonferroni comparisons.
"""

from typing import Dict, Any
import numpy as np

def evaluate_h2_multiview_alignment_contract(
    cluster_ids: np.ndarray,
    y_true: np.ndarray,
    aligned_mv_scores: np.ndarray,
    seq_only_scores: np.ndarray,
    graph_only_scores: np.ndarray,
    unaligned_mv_scores: np.ndarray,
    latent_variance: float,
    b_resamples: int = 2000,
    seed: int = 10007,
    margin_epsilon: float = 0.02
) -> Dict[str, Any]:
    """
    Executes pre-registered H2 hypothesis testing using Average Precision (AP) across 3 distinct comparisons.
    """
    from research_agent.experiments.protocols.paired_cluster_bootstrap import (
        paired_cluster_bootstrap_recompute,
        compute_average_precision
    )
    
    # Comparison 1: Aligned Multi-View vs Sequence-Only
    boot_vs_seq = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=aligned_mv_scores,
        y_pred_baseline=seq_only_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h2"
    )

    # Comparison 2: Aligned Multi-View vs Graph-Only
    boot_vs_graph = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=aligned_mv_scores,
        y_pred_baseline=graph_only_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h2"
    )

    # Comparison 3: Aligned Multi-View vs Unaligned Fusion
    boot_vs_unaligned = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=aligned_mv_scores,
        y_pred_baseline=unaligned_mv_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h2"
    )

    variance_collapsed = bool(latent_variance < 0.01)

    # All single-view comparisons must not significantly beat aligned
    # Aligned must be supported against at least unaligned and not worse than single views
    is_falsified = (
        boot_vs_seq["verdict"] == "FALSIFIED" or
        boot_vs_graph["verdict"] == "FALSIFIED" or
        variance_collapsed
    )
    is_supported = (
        (boot_vs_seq["verdict"] == "SUPPORTED" or boot_vs_seq["observed_delta"] >= -margin_epsilon) and
        (boot_vs_graph["verdict"] == "SUPPORTED" or boot_vs_graph["observed_delta"] >= -margin_epsilon) and
        (boot_vs_unaligned["verdict"] == "SUPPORTED") and
        not variance_collapsed
    )

    if is_falsified:
        final_verdict = "FALSIFIED"
    elif is_supported:
        final_verdict = "SUPPORTED"
    else:
        final_verdict = "INCONCLUSIVE"

    return {
        "hypothesis_id": "H2_Multi_View_Alignment",
        "description": "Aligned Multi-View vs Sequence-Only, Graph-Only, and Unaligned Fusion",
        "latent_representation_variance": latent_variance,
        "variance_collapse_detected": variance_collapsed,
        "comparisons": {
            "vs_sequence_only": boot_vs_seq,
            "vs_graph_only": boot_vs_graph,
            "vs_unaligned_fusion": boot_vs_unaligned
        },
        "falsification_status": "FALSIFIED" if final_verdict == "FALSIFIED" else ("NOT_FALSIFIED" if final_verdict == "SUPPORTED" else "INCONCLUSIVE"),
        "verdict": final_verdict
    }
