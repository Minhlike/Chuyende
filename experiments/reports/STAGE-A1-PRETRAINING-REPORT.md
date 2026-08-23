# CHAPTER 3 — REAL STAGE A1 SELF-SUPERVISED PRETRAINING COMPLETION REPORT

**Document ID:** `REPORT-CH3-STAGE-A1-001`  
**Date:** 2026-08-23  
**Status:** `STAGE A1 — FULL ACCEPTANCE / FROZEN`  
**Execution Branch:** `train/ch3-stage-a1-execution`  

---

## 1. Commit & Provenance Lineage

| Lifecycle Phase | Commit SHA | Description |
| :--- | :--- | :--- |
| **Protocol Lock Commit** | `ab15757d2fa2afaff499b23da753885c89487c51` | `protocol: finalize Stage A1 execution lock` on `train/ch3-stage-a1-preflight` |
| **Training Implementation Commit** | `929c4818081edb2b067b2fca86c599b67b21606c` / `70b68102204bc40f73fc02f18850b065562c574f` | Training engine, multi-slot extractor, and manifest caching runner |
| **Execution Results Commit** | `9cca545be8312417d8def6007047cc42ef5d8165` | Initial commit of all 10 manifests and dataset summaries |
| **Final Acceptance Commit** | *(Recorded at final commit of this session)* | Full acceptance gate PASS, deterministic resume regression, and evidence inventory |

**Protocol Lock & Contract Hash Distinction:**
- **Protocol Lock File Byte SHA-256 (`STAGE-A1-PREEXECUTION-LOCK.json`):** `b59ff02532443d9e21bb18f89f998770aa08f0e7002dfe43f38d5032f60ca026`
- **Internal `contract_sha256` (Hash of `STAGE-A1-TRAINING-CONTRACT.md`):** `151ddcca8d165cd50f3ee6258c002c5dab441ae8149235ec168bd471b654bfff`

---

## 2. Executive Summary & Objective

Stage A1 executes real self-supervised sequence pretraining for the Chapter 2 Sequence View Transformer across two canonical system log datasets:
1. **HDFS (Hadoop Distributed File System):** System-level event stream representation stress test.
2. **BGL (Blue Gene/L Supercomputer):** Multi-node temporal drift and alert log stress test.

This pretraining is **100% label-free** (no anomaly, alert, or attack labels were loaded or exposed to the model) and **strictly firewalled from the Test split** (`TEST_OPENED = false`, `TEST_FEATURE_READS = 0`, `TEST_LABEL_READS = 0`, `TEST_METRICS = 0`).

---

## 3. Model Architecture & Training Regime

### Architecture Specification
- **Base Architecture:** 4-layer Bidirectional Transformer Encoder (`SequenceViewTransformer`)
- **Hidden Dimension ($d_{\text{model}}$):** 128
- **Attention Heads ($H$):** 4 ($\text{head\_dim} = 32$)
- **Feedforward Dimension ($d_{\text{ffn}}$):** 512
- **Dropout:** 0.10
- **Maximum Sequence Length ($T_{\max}$):** 128
- **Parameter Representation:** `BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4` ($K=4$ slots/event)
- **Time Representation:** Continuous log-gap sinusoidal positional projection + scalar projection

### Self-Supervised Multi-Task Loss Formulation
$$L_{\text{seq}} = 1.0 \cdot L_{\text{MEP}} + 1.0 \cdot L_{\text{MPP}} + 0.1 \cdot L_{\text{time}}$$

Where:
- $L_{\text{MEP}}$ (**Masked Event Prediction**): 15% Bernoulli token masking with 80% `[MASK]`, 10% random token, 10% unchanged. Cross-entropy loss over vocabulary.
- $L_{\text{MPP}}$ (**Masked Parameter Prediction**): 15% Bernoulli masking per active parameter slot (excluding `<PAD_PARAM>` = 1 as target). Cross-entropy loss averaged across active masked slots.
- $L_{\text{time}}$ (**Continuous Log-Time Gap Prediction**): Smooth L1 loss ($\beta=1.0$) between predicted continuous log-gap and true log-gap.

### Optimization Regime
- **Optimizer:** `AdamW` (peak $\text{lr} = 5.0 \times 10^{-4}, \text{weight\_decay} = 0.01, \beta = (0.9, 0.98), \epsilon = 10^{-8}$)
- **Batching:** `micro_batch_size = 16`, `gradient_accumulation_steps = 4`, `effective_batch_size = 64`
- **Learning Rate Schedule:** Linear warmup for first 5% of total optimizer steps, followed by Cosine Decay down to $\text{lr}_{\min} = 1.0 \times 10^{-5}$
- **Gradient Clipping:** Max gradient norm = $1.0$
- **Validation Cadence:** Evaluated once per completed epoch on the full validation split.
- **Early Stopping:** Patience = 3 completed epochs without improvement on validation $L_{\text{seq}}$.
- **Checkpoint Selection:** Checkpoint corresponding to minimum validation $L_{\text{seq}}$ (`best_val_loss.pt`).

---

## 4. Deterministic Checkpoint/Resume Continuation

Deterministic continuation has been verified through a multi-step trajectory test comparing:
1. **Continuous Run A:** Uninterrupted training through Epoch 1 and Epoch 2.
2. **Resumed Run B:** Epoch 1 $\to$ Save Checkpoint $\to$ Destroy and instantiate fresh Trainer $\to$ Load Checkpoint $\to$ Execute Epoch 2.

**Verification Results (`tests/test_stage_a1_deterministic_resume.py`):**
- **Next Minibatch Data Order:** Exactly identical (`torch.equal` == True)
- **Loss Value Trajectory:** Exactly identical ($\Delta L < 10^{-12}$)
- **Optimizer State (`exp_avg`, `exp_avg_sq`, `step`):** Exactly identical ($\Delta \text{opt} = 0.0$)
- **Scheduler Learning Rate & Step:** Exactly identical
- **Max Model Parameter Divergence:** **`0.00000000e+00`**

---

## 5. Five-Seed Pretraining Results (Unmodified Historical Runs)

### A. HDFS Dataset ($K=5$ Canonical Seeds)

| Seed | Run ID | Best Val Loss ($L_{\text{seq}}$) | Stopped Epoch | Optimizer Steps | Duration (s) | Peak VRAM | Checkpoint SHA-256 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | `STAGE_A1_HDFS_SEED_42_1787349673` | `0.03220` | 19 | 10,393 | 1250.8s | 170.6 MB | `9df4df87c280005d0f6eee1d69f88bbc379dc5438b96596af50184bd268809b9` |
| **1337** | `STAGE_A1_HDFS_SEED_1337_1787350945` | `0.02972` | 17 | 9,299 | 1212.3s | 180.9 MB | `c2347457d1c29b6b162cb76894fe660fd25249e3112aed42a618ac4e29cd1083` |
| **2024** | `STAGE_A1_HDFS_SEED_2024_1787361630` | `0.03048` | 20 | 10,940 | 1688.7s | 170.6 MB | `9802d9570dfb0b0372e56621e301bc553e95e9fea83a51b906a7b324be761ea0` |
| **7** | `STAGE_A1_HDFS_SEED_7_1787363345` | `0.03388` | 15 | 8,205 | 1222.5s | 180.9 MB | `4737d60ef95bea3a8f532d1cf8c24952cacdefe5e3db267bf8f1c6ef43c8c74f` |
| **999** | `STAGE_A1_HDFS_SEED_999_1787487334` | `0.03010` | 20 | 10,940 | 1463.9s | 170.6 MB | `5b93970b78a4dec5bcc5160de29fbe4ab5c220f0fba4a13b9e3f0bfed47f20e5` |

**HDFS Aggregate Metrics ($\text{Mean} \pm \text{SD}$):**
- **Validation Loss ($L_{\text{seq}}$):** $0.03128 \pm 0.00174$
- **Stopped Epoch:** $18.2 \pm 2.2$
- **Optimizer Steps:** $9955.4 \pm 1185.9$
- **Duration:** $1367.7\text{s} \pm 206.9\text{s}$
- **Peak VRAM:** $174.7\text{ MB} \pm 5.7\text{ MB}$
- **Peak Host RAM:** $2066.0\text{ MB} \pm 6.8\text{ MB}$

---

### B. BGL Dataset ($K=5$ Canonical Seeds)

| Seed | Run ID | Best Val Loss ($L_{\text{seq}}$) | Stopped Epoch | Optimizer Steps | Duration (s) | Peak VRAM | Checkpoint SHA-256 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | `STAGE_A1_BGL_SEED_42_1787488818` | `11.90822` | 9 | 2,817 | 530.4s | 470.2 MB | `bfb278ae1da9dc7aa8e7aa27482fe1ba151e0f864cc0191dfee2f1e846470e65` |
| **1337** | `STAGE_A1_BGL_SEED_1337_1787489374` | `12.05965` | 4 | 1,252 | 238.1s | 591.8 MB | `a3135ec1e5cf5aad9f9f266cc0e6bc43ed53a35f4f3aa588f0ac6e13b4973853` |
| **2024** | `STAGE_A1_BGL_SEED_2024_1787489632` | `11.27919` | 8 | 2,504 | 485.5s | 591.8 MB | `9903d1f2d0d21bdcd7f9064be011b9b0aa893c59418b748bb1f0bed30bff73f7` |
| **7** | `STAGE_A1_BGL_SEED_7_1787490139` | `11.77521` | 9 | 2,817 | 542.8s | 591.8 MB | `e59622617964bd764e33a20e29c69e56395f762eed76ace217074977664efc73` |
| **999** | `STAGE_A1_BGL_SEED_999_1787490707` | `11.99088` | 5 | 1,565 | 301.4s | 591.8 MB | `3d32d9ba9d95beb73c6b5f45a69b7714b848564868ca6b585e91d4f64908edbf` |

**BGL Aggregate Metrics ($\text{Mean} \pm \text{SD}$):**
- **Validation Loss ($L_{\text{seq}}$):** $11.80263 \pm 0.31120$
- **Stopped Epoch:** $7.0 \pm 2.3$
- **Optimizer Steps:** $2191.0 \pm 734.1$
- **Duration:** $419.6\text{s} \pm 140.3\text{s}$
- **Peak VRAM:** $567.5\text{ MB} \pm 54.4\text{ MB}$
- **Peak Host RAM:** $2071.6\text{ MB} \pm 6.0\text{ MB}$

---

## 6. Provenance Attestation & Known Limitations

1. **Attestation Status:** Recorded in `experiments/reports/STAGE-A1-PROVENANCE-AUDIT.json`.
2. **Historical Attestation Limitations:**
   - The 10 historical Stage A1 runs were executed across two sequential sessions on `train/ch3-stage-a1-execution`.
   - Git commits and environment specs (`Python 3.12.3`, `PyTorch 2.6.0+cu124`, `CUDA 12.4`, `RTX 3050 Ti Laptop GPU`, `WSL2 Ubuntu 24.04`) are formally derived and attested from repository history and verified logs.
   - For all future runs (Stage A2 onwards), runtime telemetry (`git_commit_sha`, `git_branch`, `git_dirty`, environment fingerprint) will be captured directly by the runner at invocation time.

---

## 7. Integrity & Acceptance Gate Checklist

| Acceptance Check | Contract Requirement | Realized Status | Verdict |
| :--- | :---: | :---: | :---: |
| **10 Historical Manifests Present** | Exactly 10 (5 HDFS + 5 BGL) | 10 verified | **PASS** |
| **Test Set Sealed (`test_opened`)** | `false` | `false` across all 10 manifests | **PASS** |
| **Test Feature Read Count** | `0` | `0` across all 10 manifests | **PASS** |
| **Test Label Read Count** | `0` | `0` across all 10 manifests | **PASS** |
| **Test Metric Count** | `0` | `0` across all 10 manifests | **PASS** |
| **Confirmatory Hypotheses Sealed** | No confirmatory metrics | `confirmatory_hypothesis_result = false` | **PASS** |
| **Label-Free SSL Purity** | 100% label-free | 0 anomaly/alert/attack labels loaded | **PASS** |
| **NaN / Inf Loss Anomalies** | `0` | `0` across all 10 runs | **PASS** |
| **NaN / Inf Gradient Anomalies** | `0` | `0` across all 10 runs | **PASS** |
| **Deterministic Resume Divergence** | $< 10^{-6}$ | `0.00000000e+00` | **PASS** |
| **Windows Unit Test Suite** | 100% Passed | 192 passed, 8 skipped | **PASS** |
| **WSL Ubuntu Test Suite** | 100% Passed | 9 passed (7 adapter + 2 resume) | **PASS** |
| **Secret Scan Audit** | 0 secrets | 0 secrets found | **PASS** |
| **Database Canonical Invariants** | 100% Valid | Verified | **PASS** |
| **Evidence Manifest & SHA256SUMS** | Valid inventory | 8 evidence artifacts verified | **PASS** |

---

## 8. Final Verdict

$$\text{STAGE\_A1\_ACCEPTANCE} = \mathbf{PASS}$$
$$\text{STATUS} = \mathbf{STAGE\ A1\ —\ FULL\ ACCEPTANCE\ /\ FROZEN}$$
