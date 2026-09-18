# -*- coding: utf-8 -*-
"""
Unit tests for gpu_smoke_test.py
Tests both PASS path and FAIL path.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import scripts.gpu_smoke_test as smoke_mod

class TestGpuSmokeTest(unittest.TestCase):

    def test_fail_path_no_cublas(self):
        """FAIL path: CUBLAS_WORKSPACE_CONFIG not set must return False."""
        env_copy = os.environ.copy()
        env_copy.pop("CUBLAS_WORKSPACE_CONFIG", None)
        with patch.dict(os.environ, env_copy, clear=True):
            passed = smoke_mod.run_smoke_test()
            self.assertFalse(passed, "Smoke test must return False when CUBLAS_WORKSPACE_CONFIG is not set.")

    def test_fail_path_no_cuda(self):
        """FAIL path: When CUDA is unavailable, smoke test must return False."""
        with patch.dict(os.environ, {"CUBLAS_WORKSPACE_CONFIG": ":4096:8"}):
            with patch("torch.cuda.is_available", return_value=False):
                passed = smoke_mod.run_smoke_test()
                self.assertFalse(passed, "Smoke test must return False when CUDA is unavailable.")

    def test_pass_path_simulated(self):
        """PASS path: When all locked preconditions and GPU ops succeed, must return True."""
        mock_torch = MagicMock()
        mock_torch.__version__ = "2.6.0+cu124"
        mock_torch.version.cuda = "12.4"
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA GeForce RTX 3050 Ti Laptop GPU"
        mock_dev_props = MagicMock()
        mock_dev_props.total_memory = 4 * 1024 * 1024 * 1024
        mock_torch.cuda.get_device_properties.return_value = mock_dev_props
        mock_torch.allclose.return_value = True

        mock_pyg = MagicMock()
        mock_pyg.__version__ = "2.6.1"

        with patch.dict(os.environ, {"CUBLAS_WORKSPACE_CONFIG": ":4096:8"}):
            with patch.dict("sys.modules", {"torch": mock_torch, "torch_geometric": mock_pyg}):
                passed = smoke_mod.run_smoke_test()
                self.assertTrue(passed, "Smoke test must return True when all conditions are met.")

if __name__ == "__main__":
    unittest.main()
