"""
Deterministic Descriptive Statistics (Prompt 6 Section 35)
"""

from typing import Any, Dict, List, Union
import numpy as np
import scipy.stats as stats


class DescriptiveStatisticsEngine:
    """
    Computes deterministic descriptive statistics:
    mean, median, sample standard deviation (ddof=1), IQR, min, max, quantiles.
    """

    def compute_summary(self, values: Union[List[float], np.ndarray]) -> Dict[str, float]:
        """Calculates full descriptive summary of a sample array."""
        arr = np.array(values, dtype=float)
        arr = arr[~np.isnan(arr)]
        n = len(arr)

        if n == 0:
            return {"n": 0, "mean": 0.0, "std": 0.0, "median": 0.0, "iqr": 0.0, "min": 0.0, "max": 0.0}

        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0
        median_val = float(np.median(arr))
        q25 = float(np.percentile(arr, 25))
        q75 = float(np.percentile(arr, 75))
        iqr_val = q75 - q25
        min_val = float(np.min(arr))
        max_val = float(np.max(arr))

        return {
            "n": n,
            "mean": mean_val,
            "std": std_val,
            "median": median_val,
            "q25": q25,
            "q75": q75,
            "iqr": iqr_val,
            "min": min_val,
            "max": max_val,
        }
