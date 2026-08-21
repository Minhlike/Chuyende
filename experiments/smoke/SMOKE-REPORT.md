# CH3 Implementation Smoke Test Report

> [!NOTE]
> **RESULT CLASS:** `IMPLEMENTATION_SMOKE_TEST`  
> **THESIS ELIGIBLE:** `false`  
> **CONFIRMATORY EXPERIMENT:** `false`  
> **TEST SET OPENED:** `NO` (Records read: 0)

---

## 1. Execution Identity & Provenance
- **Smoke Run ID:** `SMOKE-1787339433`
- **Source Dataset:** `DATA-HDFS-001` (Status: `VALIDATED`)
- **Deterministic Seed:** `42`
- **Device:** `cuda` (CUDA Available: `True`)
- **GPU Model:** `NVIDIA GeForce RTX 3050 Ti Laptop GPU`

---

## 2. Data Subsets & Test Firewall
- **Train Partition Size:** `16` windows (Manifest ceiling: <= 256)
- **Validation Partition Size:** `8` windows (Manifest ceiling: <= 64)
- **Test Split Status:** `SEALED_UNTOUCHED`
- **Test Records Read:** `0`

---

## 3. Training Loop & Loss Convergence Smoke
- **Epochs Executed:** `1`
- **Optimizer Steps:** `2` (Manifest ceiling: <= 50)
- **Final Total Loss (L_StageA):** `61.7666`
- **Loss Finiteness:**
  - L_MEP: `4.3690` (Finite: True)
  - L_MPP: `3.3485` (Finite: True)
  - L_time: `0.4866` (Finite: True)
  - L_mask_node: `2.9917` (Finite: True)
  - L_mask_edge: `1.0749` (Finite: True)
  - L_time_gap: `0.4971` (Finite: True)
  - L_VICReg: `48.9987` (Finite: True)
  - NaN Losses Encountered: `0`
  - Inf Losses Encountered: `0`

---

## 4. Gradient Health & Optimization Audit
- **Zero-Gradient Unexpected Count:** `0` (Expected: 0)
- **NaN-Gradient Count:** `0` (Expected: 0)
- **Inf-Gradient Count:** `0` (Expected: 0)
- **Optimizer Modified Parameters:** `PASS`

---

## 5. Temporal State & Memory Lifecycle
- **Memory Scope Mode:** `independent`
- **Temporal State Isolation:** `PASS`
- **Active Entities:** `10`
- **Peak Active Entities:** `10`
- **Peak State Size Bytes:** `2640` bytes

---

## 6. Checkpoint & Deterministic Reload Verification
- **Checkpoint Saved:** `PASS` (`artifacts/smoke/smoke_checkpoint.pt`)
- **Checkpoint Reloaded:** `PASS`
- **Deterministic Match:** `PASS`

---

## 7. Resource Profiling
- **Peak RAM:** `1436.81 MB`
- **Peak VRAM:** `26.17 MB`
- **Total Duration:** `2.79 s`
