# -*- coding: utf-8 -*-
"""
Integration test for evaluate_downstream_linear_probe in scripts/run_nineplus_confirmatory.py.
Verifies that the probe evaluation returns a valid dictionary with finite probe_ap and probe_roc_auc in [0, 1].
Specifically catches the regression where evaluate_downstream_linear_probe ended without returning a dictionary (returning None).
"""

import math
import unittest
import torch
from scripts.run_nineplus_confirmatory import evaluate_downstream_linear_probe


class TestLinearProbeIntegration(unittest.TestCase):
    def test_evaluate_downstream_linear_probe_returns_valid_metrics(self):
        # Create a small synthetic dataset on CPU: 100 samples, dim 128
        torch.manual_seed(42)
        n_samples = 100
        z_dim = 128
        z_all = torch.randn(n_samples, z_dim, dtype=torch.float32)

        # Labels with both positive and negative classes (e.g. 20 positive, 80 negative)
        labels = [1] * 20 + [0] * 80

        # Call evaluate_downstream_linear_probe on CPU
        metrics = evaluate_downstream_linear_probe(
            z_all=z_all,
            labels=labels,
            seed=42,
            device="cpu"
        )

        # 1. Regression assertion: Must not be None
        self.assertIsNotNone(metrics, "Regression detected: evaluate_downstream_linear_probe returned None!")

        # 2. Must return a dict
        self.assertIsInstance(metrics, dict, "Expected evaluate_downstream_linear_probe to return a dict")

        # 3. Must contain required keys
        self.assertIn("probe_ap", metrics, "Missing 'probe_ap' in returned metrics dict")
        self.assertIn("probe_roc_auc", metrics, "Missing 'probe_roc_auc' in returned metrics dict")

        ap = metrics["probe_ap"]
        auc = metrics["probe_roc_auc"]

        # 4. Values must be finite and within [0.0, 1.0]
        self.assertTrue(math.isfinite(ap), f"probe_ap is not finite: {ap}")
        self.assertTrue(math.isfinite(auc), f"probe_roc_auc is not finite: {auc}")
        self.assertGreaterEqual(ap, 0.0, f"probe_ap out of bounds: {ap}")
        self.assertLessEqual(ap, 1.0, f"probe_ap out of bounds: {ap}")
        self.assertGreaterEqual(auc, 0.0, f"probe_roc_auc out of bounds: {auc}")
        self.assertLessEqual(auc, 1.0, f"probe_roc_auc out of bounds: {auc}")

    def test_regression_guard_catches_none(self):
        """Specifically verifies that returning None triggers the regression assertion error."""
        broken_output = None
        with self.assertRaises(AssertionError) as ctx:
            self.assertIsNotNone(broken_output, "Regression detected: evaluate_downstream_linear_probe returned None!")
        self.assertIn("Regression detected: evaluate_downstream_linear_probe returned None!", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
