"""
Deterministic Confidence Intervals & Bootstrap Engine (Prompt 6 Section 36)
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import scipy.stats as stats


class ConfidenceIntervalEngine:
    """
    Computes parametric Student's t confidence intervals and non-parametric
    empirical bootstrap confidence intervals with reproducible random seeds.
    """

    def compute_parametric_ci(
        self,
        values: Union[List[float], np.ndarray],
        confidence_level: float = 0.95,
    ) -> Tuple[float, float, float]:
        """
        Computes parametric Student-t confidence interval:
        CI = mean ± t_{alpha/2, n-1} * (s / sqrt(n))
        Returns (mean, lower_bound, upper_bound).
        """
        arr = np.array(values, dtype=float)
        arr = arr[~np.isnan(arr)]
        n = len(arr)
        if n < 2:
            val = float(arr[0]) if n == 1 else 0.0
            return val, val, val

        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=1))
        se = std / np.sqrt(n)
        alpha = 1.0 - confidence_level
        t_crit = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
        margin = float(t_crit * se)

        return mean, mean - margin, mean + margin

    def compute_bootstrap_ci(
        self,
        values: Union[List[float], np.ndarray],
        confidence_level: float = 0.95,
        num_resamples: int = 2000,
        random_seed: int = 42,
    ) -> Tuple[float, float, float]:
        """
        Computes deterministic empirical bootstrap percentile confidence interval.
        Returns (mean, lower_bound, upper_bound).
        """
        arr = np.array(values, dtype=float)
        arr = arr[~np.isnan(arr)]
        n = len(arr)
        if n < 2:
            val = float(arr[0]) if n == 1 else 0.0
            return val, val, val

        rng = np.random.RandomState(random_seed)
        boot_means = np.empty(num_resamples)

        for i in range(num_resamples):
            sample = rng.choice(arr, size=n, replace=True)
            boot_means[i] = np.mean(sample)

        alpha = (1.0 - confidence_level) / 2.0
        lower = float(np.percentile(boot_means, alpha * 100))
        upper = float(np.percentile(boot_means, (1.0 - alpha) * 100))
        mean = float(np.mean(arr))

        return mean, lower, upper
