# -*- coding: utf-8 -*-
"""
Weak Evidence Attribution Evaluator (RQ4)
Evaluates Multiple Instance Learning (MIL) attention attribution without fabricated event labels.
Rules:
  - Strict prohibition of synthetic heuristic labels (e.g., assuming last 3 events are anomalies).
  - On HDFS: Explicitly returns NOT_EVALUABLE_ON_HDFS when only coarse block-level labels exist.
  - On Provenance / DARPA: Requires exact IOC / event-level match from verified ground truth map.
"""

from typing import Dict, Any, List, Optional, Set
import numpy as np

def evaluate_weak_attribution_accuracy(
    bag_attention_weights: List[np.ndarray],
    ground_truth_event_indices: List[Optional[Set[int]]],
    dataset_name: str
) -> Dict[str, Any]:
    """
    Evaluates Top-1, Top-3, Top-5 root-cause event hit rate on verified ground truth only.
    """
    if dataset_name.upper() == "HDFS":
        # HDFS provides only block-level anomaly labels, not per-log root cause labels
        has_real_event_annotations = any(gt is not None for gt in ground_truth_event_indices)
        if not has_real_event_annotations:
            return {
                "dataset": "HDFS",
                "evaluation_status": "NOT_EVALUABLE_ON_HDFS",
                "reason": "HDFS standard distribution provides only coarse block-level labels. Per-event attribution cannot be evaluated without independent event annotations.",
                "top1_hit_rate": None,
                "top3_hit_rate": None,
                "top5_hit_rate": None
            }

    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    total_evaluable = 0
    entropies = []

    for weights, gt_indices in zip(bag_attention_weights, ground_truth_event_indices):
        if gt_indices is None or len(gt_indices) == 0:
            continue

        total_evaluable += 1
        seq_len = len(weights)
        top_k_indices = np.argsort(weights)[::-1]

        # Top-1
        if top_k_indices[0] in gt_indices:
            top1_hits += 1
        # Top-3
        if any(idx in gt_indices for idx in top_k_indices[:min(3, seq_len)]):
            top3_hits += 1
        # Top-5
        if any(idx in gt_indices for idx in top_k_indices[:min(5, seq_len)]):
            top5_hits += 1

        # Attention Entropy
        p = np.clip(weights, 1e-12, 1.0)
        p = p / np.sum(p)
        entropy = -float(np.sum(p * np.log(p)))
        entropies.append(entropy)

    if total_evaluable == 0:
        return {
            "dataset": dataset_name,
            "evaluation_status": "NO_EVALUABLE_INSTANCES",
            "total_evaluable": 0
        }

    return {
        "dataset": dataset_name,
        "evaluation_status": "COMPLETED",
        "total_evaluable_bags": total_evaluable,
        "top1_hit_rate": float(top1_hits / total_evaluable),
        "top3_hit_rate": float(top3_hits / total_evaluable),
        "top5_hit_rate": float(top5_hits / total_evaluable),
        "mean_attention_entropy": float(np.mean(entropies))
    }
