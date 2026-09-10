# Stage A2 Five-Seed Chronological Provenance & 12-Epoch Authority Reconciliation Report

**Audit Date:** 2026-09-10  
**Branch:** `fix/stage-a2-prospective-contract-final`  
**Base Commit:** `e1d84db803d06ecff4ad4ad97c176ef28d9e6ffa`  
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

| Seed | Classification | Status | Epochs Completed | Optimizer Steps | Stop Reason | Best Epoch | Best Val Loss | Final Train Loss | Final Val Loss | Execution Commit | Git Provenance & Protocol Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seed 999** | `PROTOCOL_DEVIATION` | COMPLETED | 12 | 6,876 | CEILING_REACHED | 12 | `0.609500` | `0.159004` | `0.609500` | `e4d53b82...` | Pre-execution authorization in `244e81a5` bound historical plan containing `warmup_steps=573`, while actual execution trajectory used `warmup_steps=343`. |
| **Seed 42** | `PROTOCOL_DEVIATION` | EARLY_STOPPED | 4 | 2,292 | EARLY_STOPPING | 1 | `6.081352` | `0.308279` | `7.150944` | `33269cbe...` | Trajectory ran on legacy schedule (573 warmup steps); stopped early at epoch 4 by pre-registered patience=3. |
| **Seed 7** | `PROTOCOL_DEVIATION` | COMPLETED | 12 | 6,876 | CEILING_REACHED | 12 | `0.550259` | `0.160910` | `0.550259` | `e4d53b82...` | Scheduler matched 12-epoch schedule; authorization artifact committed to Git ~34 hours after training launch. |
| **Seed 1337** | `NONCANONICAL` | HALTED | 12 | 6,876 | HALTED | 10 | `0.917827` | `0.184784` | `1.205658` | `33269cbe...` | Trajectory ran on legacy schedule; halted at epoch 12 (`lr=0.000195`); incomplete output contract (missing METRICS, RUN-MANIFEST, TEST-FIREWALL). |
| **Seed 2024** | `NONCANONICAL` | COMPLETED | 12 | 6,876 | CEILING_REACHED | 12 | `0.553257` | `0.167085` | `0.553257` | `e4d53b82...` | Completion record cites phantom commit `00ce524e`; mid-run schedule alteration produced hybrid LR trajectory. |

### Classification Metadata
- `canonical_seeds`: `[]`
- `protocol_deviation_seeds`: `[7, 42, 999]`
- `noncanonical_seeds`: `[1337, 2024]`
- `output_contract_incomplete_seeds`: `[1337]`

---

## 3. Table 3.3 Semantic Contract: Final Validation Components

Table 3.3 strictly presents **Final Validation Components** ($L_{\text{rel}}$, $L_{\text{node}}$, $L_{\text{time}}$) measured at the final completed epoch:
$$\text{Final Val } L_{\text{graph}} = 1.0 \times L_{\text{rel}} + 1.0 \times L_{\text{node}} + 0.1 \times L_{\text{time}}$$

| Seed | Final Val $L_{\text{graph}}$ | Final Val $L_{\text{rel}}$ | Final Val $L_{\text{node}}$ | Final Val $L_{\text{time}}$ | Consistency Check ($\sum$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Seed 999** | `0.609500` | `0.194297` | `0.406335` | `0.088676` | `0.194297 + 0.406335 + 0.008868 = 0.609500` (Exact) |
| **Seed 42** | `7.150944` | `4.926572` | `2.180307` | `0.440652` | `4.926572 + 2.180307 + 0.044065 = 7.150944` (Exact) |
| **Seed 7** | `0.550259` | `0.183315` | `0.358369` | `0.085746` | `0.183315 + 0.358369 + 0.008575 = 0.550259` (Exact) |
| **Seed 1337** | `1.205658` | `0.306274` | `0.831675` | `0.677088` | `0.306274 + 0.831675 + 0.067709 = 1.205658` (Exact) |
| **Seed 2024** | `0.553257` | `0.197410` | `0.347181` | `0.086661` | `0.197410 + 0.347181 + 0.008666 = 0.553257` (Exact) |

---

## 4. Chronological Git Provenance Timeline

1. **Seed 42 Launch (2026-08-28 10:25:53 +0700):**
   - Authorization committed in `c8879181` prior to launch (`10:26:33`). Scheduler configured for legacy schedule; early stopped at epoch 4 (`lr=0.0004705` vs `0.0003995` under 12-epoch schedule).
2. **Seed 1337 Launch (2026-08-29 23:20:24 +0700):**
   - Authorization committed in `84d1aa95`. Trajectory ran on legacy schedule, halted at epoch 12 (`lr=0.000195` vs `1e-5`). Missing run artifacts (METRICS, RUN-MANIFEST, TEST-FIREWALL).
3. **Seed 2024 Launch (2026-09-02 21:02:35 +0700):**
   - Hybrid schedule trajectory: epochs 1-4 ran on legacy schedule, epochs 5-12 adjusted. Completion cited nonexistent commit `00ce524e`.
4. **Seed 7 Launch (2026-09-05 22:17:43 +0700):**
   - Began training on 2026-09-05. Launch authorization was committed to Git in `b53b7264` on 2026-09-07 (~34 hours post-start).
5. **Seed 999 Launch (2026-09-08 23:12:43 +0700):**
   - Authorization committed on 2026-09-08 23:11:15 (`244e81a5`) prior to launch (`23:12:43`). Bound historical plan containing `warmup_steps=573`, while actual code executed with `warmup_steps=343`. Classified as `PROTOCOL_DEVIATION`.

---

## 5. Strict Machine-Readable Aggregates

- **Canonical Subset ($N=0$):**
  - No runs strictly canonical under prospective contract.
- **Protocol Deviation Subset ($N=3$, Seeds 999, 42, 7):**
  - Mean Best Val Loss: `2.413703`
  - Sample Std Best Val Loss: `3.176465`
  - Mean Final Train Loss: `0.209398`
  - Mean Final Val Loss: `2.770234`
  - Mean Final Val $L_{\text{rel}}$: `1.768061`
  - Mean Final Val $L_{\text{node}}$: `0.981670`
  - Mean Final Val $L_{\text{time}}$: `0.205025`
  - Consistency Check: `1.768061 + 0.981670 + 0.1 * 0.205025 = 2.770234` (Exact)
