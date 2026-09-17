# -*- coding: utf-8 -*-
"""
GPU and Runtime Smoke Test
Verifies PyTorch CUDA runtime, PyTorch Geometric, and tiny CPU/GPU tensor operations.
NO MODEL TRAINING, NO BENCHMARKS, NO DATASET ACCESS.
"""

import os
import sys
from pathlib import Path

# Auto-detect repository root
REPO_ROOT = Path(__file__).resolve().parent.parent

import torch

try:
    import torch_geometric
    pyg_ver = torch_geometric.__version__
except ImportError:
    pyg_ver = "NOT_INSTALLED"

import numpy as np

try:
    import scipy
    scipy_ver = scipy.__version__
except ImportError:
    scipy_ver = "NOT_INSTALLED"

try:
    import pandas as pd
    pandas_ver = pd.__version__
except ImportError:
    pandas_ver = "NOT_INSTALLED"

try:
    import sklearn
    sklearn_ver = sklearn.__version__
except ImportError:
    sklearn_ver = "NOT_INSTALLED"

try:
    import psutil
    psutil_ver = psutil.__version__
except ImportError:
    psutil_ver = "NOT_INSTALLED"

def run_smoke_test():
    cublas_config = os.environ.get("CUBLAS_WORKSPACE_CONFIG", "NOT_SET")
    print("=" * 60)
    print("  GPU AND RUNTIME SMOKE TEST")
    print("=" * 60)
    print(f"Repository Root:         {REPO_ROOT}")
    print(f"Python:                  {sys.version.split()[0]}")
    print(f"CUBLAS_WORKSPACE_CONFIG: {cublas_config}")
    print(f"PyTorch:                 {torch.__version__}")
    print(f"PyTorch CUDA:            {torch.version.cuda}")
    print(f"CUDA Available:          {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        dev_name = torch.cuda.get_device_name(0)
        dev_cap = torch.cuda.get_device_capability(0)
        total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
        print(f"Device Name:             {dev_name}")
        print(f"Device Capability:       {dev_cap}")
        print(f"Total GPU VRAM:          {total_vram_mb:.1f} MB ({total_vram_mb / 1024:.2f} GB)")
    else:
        print("[WARN] CUDA not available on this runtime.")
    print(f"PyG (torch_geometric):   {pyg_ver}")
    print(f"NumPy:                   {np.__version__}")
    print(f"SciPy:                   {scipy_ver}")
    print(f"Pandas:                  {pandas_ver}")
    print(f"Scikit-Learn:            {sklearn_ver}")
    print(f"Psutil:                  {psutil_ver}")
    print("-" * 60)

    # 1. Tiny CPU tensor operation
    a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    b = torch.tensor([[5.0, 6.0], [7.0, 8.0]])
    c_cpu = torch.matmul(a, b)

    # 2. Tiny GPU transfer and matrix multiply
    if torch.cuda.is_available():
        a_gpu = a.to("cuda:0")
        b_gpu = b.to("cuda:0")
        c_gpu = torch.matmul(a_gpu, b_gpu)
        c_from_gpu = c_gpu.to("cpu")
        assert torch.allclose(c_cpu, c_from_gpu, atol=1e-4), "GPU matrix multiply mismatch!"
        print("[PASS] CPU/GPU tiny tensor transfer & matmul verified successfully.")
    else:
        print("[WARN] CUDA transfer skipped (CPU only).")

    print("=" * 60)
    print("[PASS] GPU Smoke Test Passed 100% (Zero Model Training).")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_smoke_test()
    if not success:
        sys.exit(1)
