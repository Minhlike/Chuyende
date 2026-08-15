"""
Multi-Seed Aggregator & Cherry-Picking Guard (Prompt 6 Section 42)
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from research_agent.verification.statistics.descriptive import DescriptiveStatisticsEngine
from research_agent.verification.statistics.confidence_intervals import ConfidenceIntervalEngine


class MultiSeedAggregator:
    """
    Aggregates experiment metrics across distinct seeds (K >= 5).
    Enforces reporting mean ± SD or median [IQR], and detects cherry-picking of best single runs.
    """

    def __init__(self):
        self.desc_engine = DescriptiveStatisticsEngine()
        self.ci_engine = ConfidenceIntervalEngine()

    def aggregate_seed_metrics(
        self,
        seed_runs: List[Dict[str, Any]],
        metric_key: str,
    ) -> Dict[str, Any]:
        """
        Aggregates metric values across runs.
        Returns full summary with mean, std, CI, min, max, median, and cherry-picking warnings.
        """
        values = [float(r[metric_key]) for r in seed_runs if metric_key in r and r[metric_key] is not None]
        summary = self.desc_engine.compute_summary(values)
        mean, ci_low, ci_high = self.ci_engine.compute_parametric_ci(values)

        return {
            "metric_key": metric_key,
            "num_seeds": len(values),
            "mean": summary["mean"],
            "std": summary["std"],
            "median": summary["median"],
            "iqr": summary["iqr"],
            "ci_95_lower": ci_low,
            "ci_95_upper": ci_high,
            "min_run": summary["min"],
            "max_run": summary["max"],
            "all_seed_values": values,
        }

    def audit_cherry_picking(
        self,
        reported_value: float,
        seed_values: List[float],
        tolerance: float = 1e-4,
    ) -> Tuple[bool, Optional[str]]:
        """
        BestRunCherryPickingGuard:
        Checks if the reported single scalar matches ONLY the maximum seed run
        rather than the mean / distribution summary.
        """
        arr = np.array(seed_values, dtype=float)
        max_val = np.max(arr)
        mean_val = np.mean(arr)

        if abs(reported_value - max_val) < tolerance and abs(reported_value - mean_val) > tolerance:
            return False, (
                f"CHERRY_PICKING_DETECTED: Reported value {reported_value} matches the maximum single seed "
                f"({max_val}) rather than the seed mean ({mean_val:.4f} ± {np.std(arr, ddof=1):.4f})."
            )

        return True, None
