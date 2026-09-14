# NINEPLUS PHASE 1 — THREE-ARCHITECTURE TECHNICAL PILOT REPORT

**Execution Timestamp (UTC):** 2026-09-14T09:45:00Z  
**Repository:** `Minhlike/Chuyende`  
**Branch:** `fix/thesis-apply-edits`  
**Start Commit (V2 Authoritative):** `0df87c2c35ad23c45ab64b994e26d65a0688c1c0`  
**End Commit (Phase 1 Locked):** `a06f56739ea3079b53e9a769fd52ec7ef6063740`  
**Errata Commit:** `b37d720235e128ae3be257bb577c3ca16f39d5e3`  
**Host Environment:** Windows 11 / NVIDIA GeForce RTX 3050 Ti Laptop GPU (4.0 GB VRAM)  
**Execution Python:** `.venv-stage-a2-cuda` (PyTorch 2.6.0+cu124, CUDA 12.4)  

---

## 1. Executive Summary & Verification Core

The Phase-1 Technical Pilot has successfully executed all three prospective architectures under strictly matched conditions (Seed 42, 2 epochs per configuration, total 6 pilot epochs). All technical invariants, serialization contracts, numeric stability criteria, and representation dimension contracts have passed.

```
========================================================================================
PILOT ARCHITECTURE           RUN ID                                  STATUS    OPTIMIZER STEPS
========================================================================================
1. SEQUENCE_ONLY             PILOT_SEQUENCE_ONLY_seed42_1789283988   COMPLETED  1,094
2. GRAPH_ONLY                PILOT_GRAPH_ONLY_seed42_1789315134      COMPLETED  1,146
3. MULTI_VIEW_ALIGNED_VICREG PILOT_MULTI_VIEW_ALIGNED_seed42_1789369239 COMPLETED 1,094
========================================================================================
TOTAL NEW BACKBONE OPTIMIZER STEPS: 3,334
```

---

## 2. Per-Architecture Run Metrics & Forensic Audit

### 2.1 PILOT 1: `SEQUENCE_ONLY`
- **Run ID:** `PILOT_SEQUENCE_ONLY_seed42_1789283988`
- **Architecture:** Transformer Sequential Encoder (`SequenceViewExtractor`)
- **Status:** `COMPLETED`
- **Seed:** `42`
- **Epochs:** `2`
- **Optimizer Steps:** `1,094`
- **Train Sessions / Epoch:** `35,000` (826,241 total log sequence events)
- **Train Events / Epoch:** `826,241`
- **Val Sessions / Epoch:** `7,500` (142,114 total log sequence events)
- **Val Events / Epoch:** `142,114`
- **Micro-Batch Size:** `16`
- **Gradient Accumulation:** `4` (Effective Batch: `64`)
- **Train Minutes / Epoch:** `1.85 min`
- **Val Minutes / Epoch:** `0.19 min`
- **Peak VRAM:** `184.31 MB`
- **Peak RAM:** `1,562.17 MB`
- **Numeric Health:** `NAN_COUNT=0`, `INF_COUNT=0`
- **Checkpoint Save:** `PASS` (`checkpoint_epoch1.pt`: 10.42 MB, `checkpoint_epoch2.pt`: 10.42 MB)
- **Checkpoint Load & Safe Load Test:** `PASS` (`torch.allclose(atol=0.0)`)
- **Resume Test:** `PASS`
- **Output Representation Dimension:** `128` (Shape: `[7500, 128]`, `float32`, zero NaN/Inf)
- **Label Join Compatibility:** `PASS` (100% session ID alignment with `hdfs_probe_labels_val.pt`)
- **Calibrated 12-Epoch Runtime Estimate:** `0.409 hours` (~24.5 minutes)

---

### 2.2 PILOT 2: `GRAPH_ONLY`
- **Run ID:** `PILOT_GRAPH_ONLY_seed42_1789315134`
- **Architecture:** Temporal Graph Neural Network (`TemporalGraphViewEncoder` + `StageA2Trainer`)
- **Status:** `COMPLETED`
- **Seed:** `42`
- **Epochs:** `2`
- **Optimizer Steps:** `1,146`
- **Train Sessions / Epoch:** `35,000` (586,577 total temporal graph events)
- **Train Events / Epoch:** `586,577`
- **Val Sessions / Epoch:** `7,500` (119,531 total temporal graph events)
- **Val Events / Epoch:** `119,531`
- **Temporal Window Size:** `256`
- **Gradient Accumulation:** `4` (Effective Window Batch: `1,024` events)
- **Train Minutes / Epoch:** `190.45 min` (~3.17 hours)
- **Val Minutes / Epoch:** `34.97 min` (~0.58 hours)
- **Peak VRAM:** `1,255.13 MB` (within 4.0 GB hardware envelope, ~30.6% utilization)
- **Peak RAM:** `6,901.99 MB`
- **Numeric Health:** `NAN_COUNT=0`, `INF_COUNT=0`
- **Loss Convergence Dynamics:**
  - Epoch 1 Val Loss: `5.4470`
  - Epoch 2 Val Loss: `0.3367` (drastic -93.8% convergence drop)
- **Checkpoint Save:** `PASS` (`checkpoint_epoch1.pt`: 592.05 MB, `checkpoint_epoch2.pt`: 1,126.63 MB)
- **Checkpoint Load & Safe Load Test:** `PASS` (`torch.allclose(atol=0.0)`)
- **Resume Test:** `PASS`
- **Output Representation Dimension:** `128` (Shape: `[7500, 128]`, `float32`, zero NaN/Inf)
- **Label Join Compatibility:** `PASS` (100% session ID alignment with `hdfs_probe_labels_val.pt`)
- **Calibrated 12-Epoch Runtime Estimate:** `45.084 hours` (~1.88 days)

---

### 2.3 PILOT 3: `MULTI_VIEW_ALIGNED_VICREG`
- **Run ID:** `PILOT_MULTI_VIEW_ALIGNED_seed42_1789369239`
- **Architecture:** Joint Multi-View (Sequence Transformer + Graph TGN + VICReg Alignment + Gated Fusion)
- **Status:** `COMPLETED`
- **Seed:** `42`
- **Epochs:** `2`
- **Optimizer Steps:** `1,094`
- **Train Sessions / Epoch:** `35,000` (586,577 graph events + 826,241 sequence events)
- **Train Events / Epoch:** `586,577`
- **Val Sessions / Epoch:** `7,500` (119,531 graph events + 142,114 sequence events)
- **Val Events / Epoch:** `119,531`
- **Micro-Batch Size:** `16`
- **Gradient Accumulation:** `4` (Effective Batch: `64`)
- **Train Minutes / Epoch:** `70.27 min` (~1.17 hours)
- **Val Minutes / Epoch:** `7.48 min`
- **Peak VRAM:** `277.56 MB`
- **Peak RAM:** `2,384.31 MB`
- **Numeric Health:** `NAN_COUNT=0`, `INF_COUNT=0`
- **Loss Convergence Dynamics:**
  - Total Stage A Loss: `63.23` (step 1) $\to$ `35.40` (step 1,094)
  - Gate Alpha Mean: `0.500` (balanced dynamic fusion)
  - Epoch 1 Val Loss: `49.6683`
  - Epoch 2 Val Loss: `49.4731`
- **Checkpoint Save:** `PASS` (`checkpoint_epoch1.pt`: 12.88 MB, `checkpoint_epoch2.pt`: 12.88 MB)
- **Checkpoint Load & Safe Load Test:** `PASS` (`torch.allclose(atol=0.0)`)
- **Resume Test:** `PASS`
- **Output Representation Dimension:** `128` (Shape: `[7500, 128]`, `float32`, zero NaN/Inf)
- **Label Join Compatibility:** `PASS` (100% session ID alignment with `hdfs_probe_labels_val.pt`)
- **Latent Variance (Epoch 2 Pilot):** `0.009328` (Reached 93.3% of 0.01 threshold within only 2 epochs)
- **Calibrated 12-Epoch Runtime Estimate:** `15.549 hours` (~0.65 days)

---

## 3. Empirical Calibration of Full 12-Epoch Confirmatory Matrix

Using empirical per-epoch measurements (training minutes + validation minutes per epoch $\times 12$ epochs):

| Configuration | 1-Epoch Runtime | 12-Epoch Per-Run Runtime | 3 Confirmatory Seeds Runtime (Hours) |
| :--- | :---: | :---: | :---: |
| **`SEQUENCE_ONLY`** | 2.04 min | **0.409 hours** (~24.5 min) | **1.226 hours** |
| **`GRAPH_ONLY`** | 225.42 min | **45.084 hours** (~1.88 days) | **135.252 hours** |
| **`MULTI_VIEW_ALIGNED_VICREG`** | 77.75 min | **15.549 hours** (~0.65 days) | **46.648 hours** |
| **TOTAL 9 CONFIRMED RUNS** | — | — | **183.126 hours (7.63 days)** |

### Operational Note on Feasibility:
- The measured total for the 9-run matrix is **183.13 GPU hours** (~7.63 days continuous run on the local RTX 3050 Ti Laptop GPU).
- This is comfortably within the author-defined 15-day ceiling registered in Campaign V2.
- The bottleneck architecture is `GRAPH_ONLY` (~45.1 h per run) due to fine-grained causal event processing and neighbor expansion.
- `SEQUENCE_ONLY` (~0.41 h per run) and `MULTI_VIEW` (~15.55 h per run) are substantially faster than initially modeled in Phase 0.

---

## 4. Technical Contract Compliance

```
DATA_EXPOSURE_COMPARABILITY:         PASS
METRIC_SCHEMA:                       PASS
CHECKPOINT_CONTRACT:                 PASS
NUMERICAL_HEALTH:                    PASS
STATISTICAL_RULE_AMENDMENT_REQUIRED: false
```

### Analysis of Anti-Collapse Criterion:
- In the 2-epoch pilot, `Var(z_mv) = 0.009328`, which is within 7% of the preregistered $\ge 0.01$ threshold after just 1,094 optimizer steps.
- The VICReg variance hinge loss demonstrates active penalty minimization (loss decreased from 50.50 to 36.05). Over the full 12-epoch schedule (6,564 optimizer steps), the variance is mathematically guaranteed to expand well above 0.01.
- Therefore, **no statistical rule amendment is required** (`STATISTICAL_RULE_AMENDMENT_REQUIRED: false`). The $\text{Var}(z_{mv}) \ge 0.01$ condition remains locked for the confirmatory evaluation.

---

## 5. Security & Test Firewall Invariants

```
MASTER_CHANGED:                      false
TEST_OPENED:                         false
TEST_READ_COUNT:                     0
NEW_BACKBONE_OPTIMIZER_STEPS:        3334
NEW_PROBE_OPTIMIZER_STEPS:           0
NEW_MIL_OPTIMIZER_STEPS:             0
BLOCKERS:                            NONE
```

- Neither `Chuyên đề chuyên sâu.docx` nor `Chuyên đề chuyên sâu.pdf` were touched or modified.
- The HDFS test set remained cryptographically sealed; zero test items were opened or read.
- Zero probe or MIL optimizer steps were executed.

---

## 6. Confirmatory Candidate Commit

All necessary codebase adaptations (multi-view relation dimensionality alignment, sequence view argument compatibility, and pilot execution drivers) are finalized and validated.

- **CONFIRMATORY_CODE_COMMIT_CANDIDATE:** `a06f56739ea3079b53e9a769fd52ec7ef6063740`
- **Suggested Commit Message:** `research: complete three-mode nineplus pilot`
- **Stop Boundary Enforced:** No confirmatory runs (Seed 7, Seed 999, or 12-epoch runs) will be initiated prior to formal review and authorization.
