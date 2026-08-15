"""
Deterministic Metric Recomputation Engine (Prompt 6 Sections 28..32, 73..77)
"""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from research_agent.core.enums import MetricGranularity
from research_agent.schemas.verification import ConfusionMatrixRecord


class MetricRecomputationEngine:
    """
    Deterministic metric calculation from machine predictions and ground truth labels.
    Never relies on log text or LLM memory; recalculates from raw arrays.
    """

    def compute_confusion_matrix(
        self,
        y_true: Union[List[int], np.ndarray],
        y_pred: Union[List[int], np.ndarray],
        threshold: Optional[float] = None,
        granularity: MetricGranularity = MetricGranularity.EVENT,
    ) -> ConfusionMatrixRecord:
        """Calculates deterministic TP, FP, TN, FN and basic classification metrics."""
        y_t = np.array(y_true, dtype=int)
        y_p = np.array(y_pred, dtype=int)

        if len(y_t) != len(y_p):
            raise ValueError(f"Length mismatch: {len(y_t)} ground truth labels vs {len(y_p)} predictions.")

        tp = int(np.sum((y_t == 1) & (y_p == 1)))
        fp = int(np.sum((y_t == 0) & (y_p == 1)))
        tn = int(np.sum((y_t == 0) & (y_p == 0)))
        fn = int(np.sum((y_t == 1) & (y_p == 0)))
        total = len(y_t)

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        matrix_id = f"CMX-{abs(hash(str((tp, fp, tn, fn, threshold)))) % 1000000:06d}"
        return ConfusionMatrixRecord(
            matrix_id=matrix_id,
            tp=tp,
            fp=fp,
            tn=tn,
            fn=fn,
            precision=precision,
            recall=recall,
            f1=f1,
            fpr=fpr,
            total_samples=total,
            threshold=threshold,
            granularity=granularity,
            calculated_at=datetime.now(timezone.utc),
        )

    def compute_pr_curve_and_auc(
        self,
        y_true: Union[List[int], np.ndarray],
        y_scores: Union[List[float], np.ndarray],
    ) -> Tuple[float, List[float], List[float], List[float]]:
        """
        Computes PR curve (Precision, Recall) across all unique score thresholds
        and calculates Area Under PR Curve (PR-AUC) via trapezoidal integration.
        """
        y_t = np.array(y_true, dtype=int)
        scores = np.array(y_scores, dtype=float)

        sorted_indices = np.argsort(-scores)
        y_t_sorted = y_t[sorted_indices]
        scores_sorted = scores[sorted_indices]

        distinct_indices = np.where(np.diff(scores_sorted))[0]
        threshold_indices = np.r_[distinct_indices, len(scores_sorted) - 1]

        tps = np.cumsum(y_t_sorted)[threshold_indices]
        fps = (1 + threshold_indices) - tps
        total_positives = int(np.sum(y_t == 1))

        if total_positives == 0:
            return 0.0, [0.0], [0.0], [0.0]

        recalls = tps / total_positives
        precisions = tps / (tps + fps)

        # Prepend boundary (Recall 0, Precision 1)
        r_curve = np.r_[0.0, recalls]
        p_curve = np.r_[1.0, precisions]
        thresholds = scores_sorted[threshold_indices]

        # Calculate PR-AUC using trapezoidal integration
        pr_auc = float(np.sum((r_curve[1:] - r_curve[:-1]) * p_curve[1:]))

        return pr_auc, list(r_curve), list(p_curve), list(thresholds)

    def compute_latency_and_throughput(
        self,
        latencies_ms: List[float],
        warmup_samples: int = 10,
    ) -> Dict[str, float]:
        """
        Computes latency percentiles and event throughput.
        Automatically excludes warmup iterations.
        """
        if len(latencies_ms) <= warmup_samples:
            valid_latencies = latencies_ms
        else:
            valid_latencies = latencies_ms[warmup_samples:]

        arr = np.array(valid_latencies, dtype=float)
        mean_lat = float(np.mean(arr))
        p50 = float(np.percentile(arr, 50))
        p95 = float(np.percentile(arr, 95))
        p99 = float(np.percentile(arr, 99))
        throughput_eps = float(1000.0 / mean_lat) if mean_lat > 0 else 0.0

        return {
            "mean_latency_ms": mean_lat,
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "p99_latency_ms": p99,
            "throughput_eps": throughput_eps,
            "sample_count": len(valid_latencies),
            "warmup_excluded": warmup_samples,
        }
