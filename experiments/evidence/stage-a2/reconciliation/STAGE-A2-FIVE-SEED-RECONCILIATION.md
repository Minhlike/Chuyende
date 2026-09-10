# Stage A2 Five-Seed Chronological Provenance & 12-Epoch Authority Reconciliation Report

**Audit Date:** 2026-09-10  
**Branch:** `fix/stage-a2-final-evidence-parity`  
**Base Commit:** `8cda77c5a1e13223c2ef100a9596ff2829a03280`  
**Authoritative Plan:** `experiments/plans/STAGE-A2-FINAL-12-EPOCH-AUTHORITY.json`  
**Auditor:** Senior Research Reproducibility Engineer + Scientific Auditor + Git Forensics Engineer  

---

## 1. Authoritative 12-Epoch Protocol Authority

The official authoritative Stage A2 configuration is locked to:
- **Authoritative Plan Document:** `experiments/plans/STAGE-A2-FINAL-12-EPOCH-AUTHORITY.json`
- **Execution Provider:** `LOCAL_WINDOWS_GPU`
- **Maximum Epochs:** `12`
- **Steps per Epoch:** `573`
- **Maximum Optimizer Steps:** `6,876` (`12 * 573 = 6,876`)
- **Warmup Ratio:** `0.05` (`int(6,876 * 0.05) = 343` steps)
- **Minimum Learning Rate:** `1e-5` (initial `5e-4`, AdamW betas `(0.9, 0.98)`, weight decay `0.01`)
- **Effective Batch Size:** `1,024` events (`4` windows x `256` events)
- **Dataset:** HDFS raw SHA `6ca6c5bc...`, Train membership SHA `65b76694...`, Val membership SHA `14cf689f...`
- **Test Firewall:** Cryptographically sealed (`test_opened = false`, `test_reads = 0`).

---

## 2. Executive Summary & Forensic Seed Classifications

| Seed | Classification | Status | Epochs Completed | Optimizer Steps | Stop Reason | Best Epoch | Best Val Loss | Final Train Loss | Execution Commit | Git Provenance & Protocol Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seed 999** | `CANONICAL` | COMPLETED | 12 | 6,876 | CEILING_REACHED | 12 | `0.609500` | `0.159004` | `e4d53b82...` | Fully compliant with 12-epoch authority; authorization committed in `244e81a5` before run launch; exact evidence parity; sealed test firewall. |
| **Seed 42** | `PROTOCOL_DEVIATION` | EARLY_STOPPED | 4 | 2,292 | EARLY_STOPPING | 1 | `6.081352` | `0.308279` | `33269cbe...` | Trajectory ran on legacy schedule (573 warmup steps); stopped early at epoch 4 by pre-registered patience=3. |
| **Seed 7** | `PROTOCOL_DEVIATION` | COMPLETED | 12 | 6,876 | CEILING_REACHED | 12 | `0.550259` | `0.160910` | `e4d53b82...` | Scheduler matched 12-epoch schedule; authorization artifact committed to Git ~34 hours after training launch. |
| **Seed 1337** | `NONCANONICAL` | HALTED | 12 | 6,876 | HALTED | 10 | `0.917827` | `0.184784` | `33269cbe...` | Trajectory ran on legacy schedule; halted at epoch 12 (`lr=0.000195`); missing run artifacts (METRICS, RUN-MANIFEST, TEST-FIREWALL). |
| **Seed 2024** | `NONCANONICAL` | COMPLETED | 12 | 6,876 | CEILING_REACHED | 12 | `0.553257` | `0.167085` | `e4d53b82...` | Completion record cites phantom commit `00ce524e`; mid-run schedule alteration produced hybrid LR trajectory. |

---

## 3. Chronological Git Provenance Timeline

1. **Seed 42 Launch (2026-08-28 10:25:53 +0700):**
   - Authorization committed in `c8879181` prior to launch (`10:26:33`). Scheduler configured for legacy schedule; early stopped at epoch 4 (`lr=0.0004705` vs `0.0003995` under 12-epoch schedule).
2. **Seed 1337 Launch (2026-08-29 23:20:24 +0700):**
   - Authorization committed in `84d1aa95`. Trajectory ran on legacy schedule, halted at epoch 12 (`lr=0.000195` vs `1e-5`).
3. **Seed 2024 Launch (2026-09-02 21:02:35 +0700):**
   - Hybrid schedule trajectory: epochs 1-4 ran on legacy schedule, epochs 5-12 adjusted. Completion cited nonexistent commit `00ce524e`.
4. **Seed 7 Launch (2026-09-05 22:17:43 +0700):**
   - Began training on 2026-09-05. Launch authorization was committed to Git in `b53b7264` on 2026-09-07 (~34 hours post-start).
5. **Seed 999 Launch (2026-09-08 23:12:43 +0700):**
   - Authorization committed on 2026-09-08 23:11:15 (`244e81a5`) strictly prior to launch (`23:12:43`). Exact 12-epoch schedule match across all 12 epochs (`lr=1e-5` at step 6,876). All required run artifacts present.

---

## 4. Strict Machine-Readable Aggregates

- **Canonical Subset ($N=1$, Seed 999):**
  - Best Val Loss: `0.609500`
  - Final Train Loss: `0.159004`
  - Sample standard deviation is undefined for $N=1$ (`N/A`).
- **Protocol Deviation Subset ($N=2$, Seed 42 & Seed 7):**
  - Mean Best Val Loss: `3.315805`
  - Sample Std Best Val Loss: `3.911074`
  - Mean Final Train Loss: `0.234594`
  - Kept strictly distinct as supporting observational runs.
