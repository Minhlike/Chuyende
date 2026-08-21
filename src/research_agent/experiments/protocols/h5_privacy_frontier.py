# -*- coding: utf-8 -*-
"""
H5 Canonical Test Contract: Controlled Linkability & Multi-Adversary Pareto Frontier
Implements Chapter 2 & Chapter 3 Frozen Protocol:
  - 4 Independent Adversarial Threat Models:
      1. Entity_ReIdentification_Attack (ReID Accuracy)
      2. Cross_Session_Linkage_Attack (Linkage AUC)
      3. Membership_Inference_Attack (MIA AUC)
      4. Representation_Inversion_Attack (Attribute Reconstruction or NOT_EVALUABLE with reason)
  - True Multi-Criteria Pareto Dominance:
      Point A dominates Point B (A > B) iff for all axes k, A_k >= B_k and at least one A_j > B_j.
  - Zero arbitrary scalar aggregate privacy scores.
  - Generates exact non-dominated Pareto frontier across the 4 tokenization regimes.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import numpy as np

CANONICAL_H5_REGIMES = [
    "RAW_IDENTIFIERS",
    "EXTREME_ANONYMIZATION",
    "CONTROLLED_LINKABILITY",
    "PRIVACY_AWARE_PARAMETERIZED"
]

CANONICAL_H5_ADVERSARIES = [
    "Entity_ReIdentification_Attack",
    "Cross_Session_Linkage_Attack",
    "Membership_Inference_Attack",
    "Representation_Inversion_Attack"
]

def check_pareto_dominance(point_a: Dict[str, float], point_b: Dict[str, float], metric_keys: List[str]) -> bool:
    """
    Returns True if point_a strictly Pareto-dominates point_b across all metric_keys.
    (Assumes all metric_keys are structured such that HIGHER IS BETTER).
    """
    all_ge = True
    any_gt = False
    for k in metric_keys:
        val_a = point_a.get(k, 0.0)
        val_b = point_b.get(k, 0.0)
        if val_a < val_b:
            all_ge = False
            break
        if val_a > val_b:
            any_gt = True
    return all_ge and any_gt

def compute_pareto_frontier(regime_evaluations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes exact Pareto non-dominated set and pairwise domination matrix.
    """
    # Transform raw risk metrics to utility/safety axes (higher is better)
    transformed_points = {}
    
    for regime, metrics in regime_evaluations.items():
        util = metrics.get("detection_pr_auc", 0.0)
        reid_acc = metrics.get("reid_accuracy", 1.0)
        linkage_auc = metrics.get("linkage_auc", 1.0)
        mia_auc = metrics.get("mia_auc", 1.0)
        
        # Privacy protection axes: 1 - risk
        transformed_points[regime] = {
            "utility_detection_pr_auc": util,
            "privacy_reid_defense": 1.0 - reid_acc,
            "privacy_linkage_defense": 1.0 - (linkage_auc - 0.5) * 2.0 if linkage_auc >= 0.5 else 1.0,
            "privacy_mia_defense": 1.0 - (mia_auc - 0.5) * 2.0 if mia_auc >= 0.5 else 1.0
        }

    axes = ["utility_detection_pr_auc", "privacy_reid_defense", "privacy_linkage_defense", "privacy_mia_defense"]
    
    # Check pairwise domination
    dominated_by: Dict[str, List[str]] = {r: [] for r in transformed_points}
    for r1 in transformed_points:
        for r2 in transformed_points:
            if r1 != r2:
                if check_pareto_dominance(transformed_points[r2], transformed_points[r1], axes):
                    dominated_by[r1].append(r2)

    nondominated_set = [r for r, doms in dominated_by.items() if len(doms) == 0]
    
    # Check if proposed method is in the non-dominated set
    proposed_in_frontier = "PRIVACY_AWARE_PARAMETERIZED" in nondominated_set

    return {
        "nondominated_pareto_set": nondominated_set,
        "domination_relations": dominated_by,
        "transformed_coordinates": transformed_points,
        "proposed_regime_is_pareto_optimal": proposed_in_frontier
    }

def evaluate_h5_privacy_utility_frontier(
    regime_evaluations: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executes pre-registered H5 hypothesis evaluation.
    """
    if regime_evaluations is None:
        # Pre-execution state: Strictly PENDING
        return {
            "hypothesis_id": "H5_Controlled_Linkability_Privacy_Frontier",
            "description": "Multi-Criteria Pareto Dominance across 4 Regimes and 4 Adversaries",
            "status": "PENDING",
            "falsification_status": "PENDING_EXECUTION",
            "canonical_regimes": CANONICAL_H5_REGIMES,
            "canonical_adversaries": CANONICAL_H5_ADVERSARIES
        }

    # Verify all 4 regimes are evaluated
    for r in CANONICAL_H5_REGIMES:
        if r not in regime_evaluations:
            raise ValueError(f"Missing evaluation results for canonical regime: {r}")

    pareto_res = compute_pareto_frontier(regime_evaluations)

    # Inversion feasibility check
    inversion_status = {}
    for r in CANONICAL_H5_REGIMES:
        inv_data = regime_evaluations[r].get("inversion_attack", {})
        if not inv_data or inv_data.get("status") == "NOT_EVALUABLE":
            inversion_status[r] = {
                "status": "NOT_EVALUABLE",
                "reason": inv_data.get("reason", "Inversion reconstruction infeasible without generative inversion model.")
            }
        else:
            inversion_status[r] = inv_data

    # H5 Falsification: Falsified if proposed regime is strictly Pareto-dominated
    is_falsified = not pareto_res["proposed_regime_is_pareto_optimal"]

    return {
        "hypothesis_id": "H5_Controlled_Linkability_Privacy_Frontier",
        "status": "COMPLETED",
        "pareto_analysis": pareto_res,
        "inversion_evaluations": inversion_status,
        "falsification_status": "FALSIFIED" if is_falsified else "NOT_FALSIFIED"
    }
