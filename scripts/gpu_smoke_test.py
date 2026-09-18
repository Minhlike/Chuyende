# -*- coding: utf-8 -*-
"""
GPU and Runtime Smoke Test
Verifies PyTorch CUDA runtime, PyTorch Geometric, and tiny CPU/GPU tensor operations
strictly against experiments/environment/ENVIRONMENT-LOCK.json.
NO MODEL TRAINING, NO BENCHMARKS, NO DATASET ACCESS.
STRICT PASS/FAIL GATING: Exits with non-zero code if ANY check fails.
"""

import os
import sys
import json
from pathlib import Path

# Auto-detect repository root
REPO_ROOT = Path(__file__).resolve().parent.parent

def run_smoke_test() -> bool:
    print("=" * 75)
    print("  GPU AND RUNTIME SMOKE TEST (STRICT PASS/FAIL GATE)")
    print("=" * 75)
    print(f"Repository Root: {REPO_ROOT}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version.split()[0]}")
    print("-" * 75)

    checks = []

    # Load environment lock
    lock_file = REPO_ROOT / "experiments" / "environment" / "ENVIRONMENT-LOCK.json"
    lock_data = {}
    if lock_file.exists():
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
        except Exception as e:
            print(f"[WARN] Could not parse ENVIRONMENT-LOCK.json: {e}")

    expected_torch = lock_data.get("runtime_stack", {}).get("pytorch_version", "2.6.0+cu124")
    expected_pyg = lock_data.get("runtime_stack", {}).get("pyg_version", "2.6.1")

    # Check 1: CUBLAS_WORKSPACE_CONFIG
    cublas_cfg = os.environ.get("CUBLAS_WORKSPACE_CONFIG", "NOT_SET")
    if cublas_cfg == ":4096:8":
        checks.append(("CUBLAS_WORKSPACE_CONFIG", ":4096:8", cublas_cfg, "PASS"))
    else:
        checks.append(("CUBLAS_WORKSPACE_CONFIG", ":4096:8", cublas_cfg, "FAIL"))

    # Check 2: PyTorch Import & CUDA Availability
    try:
        import torch
        torch_ver = torch.__version__
        cuda_avail = torch.cuda.is_available()
        cuda_ver = torch.version.cuda
    except Exception as e:
        torch = None
        torch_ver = f"ERROR: {e}"
        cuda_avail = False
        cuda_ver = "NONE"

    # Check 2a: CUDA Available
    if cuda_avail:
        dev_name = torch.cuda.get_device_name(0)
        total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
        vram_str = f"{dev_name} ({total_vram_mb:.1f} MB)"
        checks.append(("CUDA Availability", "True", f"True ({vram_str})", "PASS"))
    else:
        checks.append(("CUDA Availability", "True", "False (CUDA unavailable)", "FAIL"))

    # Check 3: PyTorch Version match
    if torch_ver == expected_torch:
        checks.append(("PyTorch Version", expected_torch, torch_ver, "PASS"))
    else:
        checks.append(("PyTorch Version", expected_torch, torch_ver, "FAIL"))

    # Check 4: PyTorch Geometric (PyG)
    try:
        import torch_geometric
        pyg_ver = torch_geometric.__version__
        if pyg_ver == expected_pyg:
            checks.append(("PyG (torch_geometric)", expected_pyg, pyg_ver, "PASS"))
        else:
            checks.append(("PyG (torch_geometric)", expected_pyg, pyg_ver, "FAIL"))
    except ImportError:
        checks.append(("PyG (torch_geometric)", expected_pyg, "NOT_INSTALLED", "FAIL"))
    except Exception as e:
        checks.append(("PyG (torch_geometric)", expected_pyg, f"ERROR: {e}", "FAIL"))

    # Check 5: Core Dependencies
    deps = [
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("psutil", "psutil")
    ]
    missing_deps = []
    for pkg_name, mod_name in deps:
        try:
            __import__(mod_name)
        except ImportError:
            missing_deps.append(pkg_name)
    if not missing_deps:
        checks.append(("Core Dependencies", "All installed", "numpy,scipy,pandas,sklearn,psutil", "PASS"))
    else:
        checks.append(("Core Dependencies", "All installed", f"Missing: {','.join(missing_deps)}", "FAIL"))

    # Check 6: GPU Tensor Transfer and Matrix Multiply
    if cuda_avail and torch is not None:
        try:
            a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
            b = torch.tensor([[5.0, 6.0], [7.0, 8.0]])
            c_cpu = torch.matmul(a, b)

            a_gpu = a.to("cuda:0")
            b_gpu = b.to("cuda:0")
            c_gpu = torch.matmul(a_gpu, b_gpu)
            c_from_gpu = c_gpu.to("cpu")

            if torch.allclose(c_cpu, c_from_gpu, atol=1e-4):
                checks.append(("GPU matmul & transfer", "allclose == True", "Verified on cuda:0", "PASS"))
            else:
                checks.append(("GPU matmul & transfer", "allclose == True", "Mismatch detected", "FAIL"))
        except Exception as e:
            checks.append(("GPU matmul & transfer", "allclose == True", f"ERROR: {e}", "FAIL"))
    else:
        checks.append(("GPU matmul & transfer", "allclose == True", "SKIPPED (CUDA unavailable)", "FAIL"))

    # Print Table
    print(f"{'CHECK ITEM':<26} | {'EXPECTED':<16} | {'OBSERVED':<20} | {'STATUS'}")
    print("-" * 75)
    all_passed = True
    for item, expected, observed, status in checks:
        if status != "PASS":
            all_passed = False
        # Truncate observed if too long
        obs_display = (observed[:18] + "..") if len(observed) > 20 else observed
        exp_display = (expected[:14] + "..") if len(expected) > 16 else expected
        print(f"{item:<26} | {exp_display:<16} | {obs_display:<20} | [{status}]")
    print("-" * 75)

    if all_passed:
        print("=" * 75)
        print("[PASS] GPU Smoke Test Passed 100% (Zero Model Training).")
        print("=" * 75)
        return True
    else:
        failed_count = sum(1 for c in checks if c[3] != "PASS")
        print("=" * 75)
        print(f"[FAIL] GPU Smoke Test FAILED ({failed_count} condition(s) unmet).")
        print("=" * 75)
        return False

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
