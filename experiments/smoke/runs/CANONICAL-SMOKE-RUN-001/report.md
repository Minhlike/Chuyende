# CH3 Implementation Smoke Test Report

> [!NOTE]
> **RESULT CLASS:** `IMPLEMENTATION_SMOKE_TEST`  
> **DATASET CLASSIFICATION:** `HYBRID_SMOKE_FIXTURE` (Real HDFS Sequences + Synthetic Proxies)  
> **THESIS ELIGIBLE:** `false`  
> **CONFIRMATORY EXPERIMENT:** `false`  
> **TEST SET OPENED:** `NO` (Records read: 0)

---

## 1. Execution Identity & Provenance
- **Smoke Run ID:** `CANONICAL-SMOKE-RUN-001`
- **Source Dataset:** `DATA-HDFS-001` (Status: `VALIDATED`)
- **Deterministic Seed:** `42`
- **Device:** `cuda` (CUDA Available: `True`)
- **GPU Model:** `NVIDIA GeForce RTX 3050 Ti Laptop GPU`
- **Config Hash:** `5c2bb460bec3a64cef7ec1af246e5257fe0a747c036cd3efd1387ea49a354d35`
- **Checkpoint SHA-256:** `4a4cd88a753431fdac300ff53e842f957cae916545c16913f87a51f836156e93`
- **Start UTC:** `2026-08-21T19:32:59.297124+00:00`
- **End UTC:** `2026-08-21T19:33:30.539749+00:00`

---

## 2. Data Subsets & Test Firewall
- **Train Partition Size:** `64` windows (Manifest ceiling: <= 256)
- **Validation Partition Size:** `16` windows (Manifest ceiling: <= 64)
- **Test Split Status:** `SEALED_UNTOUCHED`
- **Test Records Read:** `0`

---

## 3. Training Loop & Exact Stage A Loss Convergence
- **Epochs Executed:** `2`
- **Optimizer Steps:** `8` (Manifest ceiling: <= 50)
- **Final Total Loss (L_StageA):** `54.0096`
- **Loss Finiteness:**
  - L_MEP: `3.3409` (Finite: True)
  - L_MPP: `2.2242` (Finite: True)
  - L_time: `0.0952` (Finite: True)
  - L_mask_node: `1.9584` (Finite: True)
  - L_mask_edge: `0.7567` (Finite: True)
  - L_time_gap: `0.3106` (Finite: True)
  - L_VICReg: `44.8812` (Finite: True)
  - L_fuse_rec: `0.4424` (Finite: True)
  - Gate Alpha Mean: `0.4930`
  - NaN Losses Encountered: `0`
  - Inf Losses Encountered: `0`

---

## 4. Strict Zero-Grad & Optimization Health Audit
- **Unexpected Zero-Gradient Count:** `0` (Expected: 0)
- **NaN-Gradient Count:** `0` (Expected: 0)
- **Inf-Gradient Count:** `0` (Expected: 0)
- **Optimizer Modified Parameters:** `PASS`

---

## 5. Temporal State & Memory Lifecycle
- **Memory Scope Mode:** `independent`
- **Temporal State Isolation:** `PASS`
- **Active Entities:** `9`
- **Peak Active Entities:** `9`
- **Peak State Size Bytes:** `2376` bytes

---

## 6. True Checkpoint Resume (Training Step N+1 Match)
- **Checkpoint Saved:** `PASS` (`artifacts/smoke/CANONICAL-SMOKE-RUN-001/smoke_checkpoint.pt`)
- **Step N+1 Loss Difference:** `0.00000000` (Tolerance: < 1e-5) -> `PASS`
- **Step N+1 Max Parameter Difference:** `0.00000000` (Tolerance: < 1e-5) -> `PASS`

---

## 7. Resource Profiling
- **Peak RAM:** `1455.39 MB`
- **Peak VRAM:** `82.72 MB`
- **Total Duration:** `15.99 s`
