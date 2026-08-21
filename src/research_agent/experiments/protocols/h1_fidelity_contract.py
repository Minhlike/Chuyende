# -*- coding: utf-8 -*-
"""
H1 Canonical Test Contract: Parameter Semantic Fidelity
Evaluates whether security-aware dynamic parameter representation preserves mutual information
I(z; Y_sec) compared to template-only abstraction under identical architecture, split, probe, and budget.
"""

from typing import Dict, Any
import numpy as np

def evaluate_h1_parameter_fidelity_contract(
    parameter_repr_cluster_scores: np.ndarray,
    template_only_cluster_scores: np.ndarray,
    b_resamples: int = 2000,
    seed: int = 10007
) -> Dict[str, Any]:
    """
    Executes pre-registered H1 hypothesis testing.
    """
    from research_agent.experiments.protocols.paired_cluster_bootstrap import paired_cluster_bootstrap_test
    
    bootstrap_result = paired_cluster_bootstrap_test(
        proposed_clusters=parameter_repr_cluster_scores,
        baseline_clusters=template_only_cluster_scores,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_method="bonferroni_h1"
    )

    # Falsification check: Falsified if delta <= 0 or p > 0.0125 or Cohen's d < 0.20
    is_falsified = (
        bootstrap_result["observed_mean_diff"] <= 0.0 or
        bootstrap_result["p_value"] > bootstrap_result["alpha_adjusted"] or
        bootstrap_result["cohens_d"] < 0.20
    )

    return {
        "hypothesis_id": "H1_Parameter_Semantic_Fidelity",
        "description": "Security-aware parameter representation vs Template-only abstraction",
        "primary_metric": "PR-AUC Difference over Clusters",
        "bootstrap_results": bootstrap_result,
        "falsification_status": "FALSIFIED" if is_falsified else "NOT_FALSIFIED",
        "verdict": "REJECT_H0" if not is_falsified else "ACCEPT_H0_OR_FALSIFIED"
    }
