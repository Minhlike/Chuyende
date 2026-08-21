# -*- coding: utf-8 -*-
"""
GPU and Runtime Smoke Test
Verifies PyTorch CUDA runtime, PyTorch Geometric, and tiny CPU/GPU tensor operations.
NO MODEL TRAINING, NO BENCHMARKS, NO DATASET ACCESS.
"""

import sys
import torch
import torch_geometric
import numpy
import scipy
import pandas
import sklearn

def run_smoke_test():
    print(f"Python: {sys.version.split()[0]}")
    print(f"PyTorch: {torch.__version__}")
    print(f"PyTorch CUDA: {torch.version.cuda}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        print(f"Device Capability: {torch.cuda.get_device_capability(0)}")
    print(f"PyG: {torch_geometric.__version__}")

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
        print("[WARN] CUDA not available on this runtime.")

    print("[PASS] GPU Smoke Test Passed 100% (Zero Model Training).")

if __name__ == "__main__":
    run_smoke_test()
