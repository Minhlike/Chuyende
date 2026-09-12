# 9+ EXPERIMENT CAMPAIGN — PHASE 0: FEASIBILITY, CHECKPOINT INVENTORY & EXPERIMENT PREREGISTRATION REPORT

**Document ID:** `REPORT-NINEPLUS-PHASE0-FEASIBILITY-V1`  
**Date:** 2026-09-13  
**Workspace:** `D:\Research`  
**Repository:** `Minhlike/Chuyende`  
**Branch:** `fix/thesis-apply-edits`  
**Active Baseline Head:** `8a00e67f79a9e787d3eb9e29f4c483aed4764246`  
**Scientific Standard:** ATTT Warranted-Derivation Scientific Writing Skill v4.0 (`D:\Research\deep-research-report-v4.md`)  
**Campaign Plan Document:** `experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V1.json`

---

## 1. Executive Summary & Verification State Variables

```text
CURRENT_HEAD                        = 8a00e67f79a9e787d3eb9e29f4c483aed4764246
REMOTE_HEAD                         = 8a00e67f79a9e787d3eb9e29f4c483aed4764246
LEGACY_STAGE_A2_BASELINE            = FROZEN
NEW_9PLUS_CAMPAIGN                  = SEPARATE_EXPERIMENT_NAMESPACE

MASTER_CHANGED                      = false
TEST_OPENED                         = false
TEST_READ_COUNT                     = 0

PHASE0_NEW_BACKBONE_OPTIMIZER_STEPS = 0
PHASE0_NEW_PROBE_OPTIMIZER_STEPS    = 0
PHASE0_NEW_MIL_OPTIMIZER_STEPS      = 0

H1_FEASIBILITY                      = FEASIBLE
H1_DIRECT_TARGET                    = HDFS_DYNAMIC_PARAMETER_CATEGORIES & HDFS_ANOMALY_LABEL
H1_REQUIRED_NEW_TRAINING            = CAPACITY_CONTROLLED_FROZEN_PROBE_ONLY (0 backbone steps)

H2_FEASIBILITY                      = FEASIBLE (HIGHEST_PRIORITY)
H2_MINIMUM_ABLATION                 = Sequence-Only vs Graph-Only vs Aligned Multi-View (VICReg)
H2_OPTIONAL_ABLATIONS               = Unaligned Multi-View; PCGrad (DECLARED_ONLY in prose, ABSENT in code)

H3_FEASIBILITY                      = FEASIBLE_CHEAP (0 backbone steps, P01..P12 on Validation)
H4_READINESS                        = PARTIAL (SLO harness implemented; Attention-MIL training unintegrated/quarantined)
H5_READINESS                        = PARTIAL (Attack interfaces implemented; deferred to conserve 15-day budget)

RUNTIME_EVIDENCE                    = HIGH (Empirical timing across 52 completed epochs in completed manifests)
ESTIMATED_HOURS_PER_FULL_RUN        = 20.43 hours (Sweet Spot: ~94.7 min/train epoch, ~7.5 min/val epoch)
RUNTIME_CONFIDENCE                  = HIGH

MINIMUM_CAMPAIGN_GPU_HOURS          = 10.5 hours (Wall clock: ~14 hours)
RECOMMENDED_CAMPAIGN_GPU_HOURS      = 92.6 hours (Wall clock: ~110 hours, ~4.6 days within 15-day window)
FULL_CAMPAIGN_GPU_HOURS             = 240.0 hours (Wall clock: ~280 hours, ~11.7 days)

RECOMMENDED_EXECUTION_ORDER         = H2 (Multi-View Ablation) > H1 (Parameter Fidelity) > H3 (Perturbations) > H4 (SLO) > H5 (Privacy)
PROPOSED_SEEDS                      = Confirmatory: [42, 7, 999] | Reserve: [1337, 2024]
PILOT_CONFIG                        = Seed 42, 2 epochs, batch 256 events x 4 accum (1024 events/step)
CAMPAIGN_PLAN_PATH                  = experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V1.json
BLOCKERS                            = NONE for H2/H1/H3/H4; PCGrad requires code implementation if demanded
```

---

## 2. Freeze Accepted Baseline & Namespace Separation

1. **Git Provenance Authority:**
   - Local HEAD is verified at `8a00e67f79a9e787d3eb9e29f4c483aed4764246`.
   - Remote HEAD (`origin/fix/thesis-apply-edits`) is verified at `8a00e67f79a9e787d3eb9e29f4c483aed4764246`.
   - The tree is clean, and the historical Stage A2 results (Table 3.3, 5-seed reconciliation report, prospective contract classifications) are strictly **FROZEN**.
2. **Namespace Isolation:**
   - All historical Stage A2 artifacts (`experiments/evidence/stage-a2/completed/`, `reconciliation/`, `run-snapshots/`) remain read-only historical records.
   - All new experiments for the 9+ campaign operate under the isolated namespace: `NEW_9PLUS_CAMPAIGN`.
   - The Master manuscript (`Chuyên đề chuyên sâu.docx` and PDF) remains completely untouched (`MASTER_CHANGED=false`).

---

## 3. Actual Implementation Inventory

Every component in the repository has been evaluated directly against physical code files in `src/`, `scripts/`, `tests/`, and `datasets/`:

| Component | Code Location | Status | Implementation Details & Constraints |
| :--- | :--- | :--- | :--- |
| **Dataset Loaders (HDFS)** | `src/research_agent/experiments/data/hdfs_adapter.py`, `hdfs_split_authority.py` | **IMPLEMENTED** | Causal temporal stream reader, block session grouper, deterministic split authority. |
| **Dataset Loaders (BGL)** | `src/research_agent/experiments/data/bgl_adapter.py` | **IMPLEMENTED** | Fixed window sequential reader, raw log parsing, temporal ordering. |
| **Dataset Loaders (DARPA / LANL)** | `datasets/manifests/SPL-DTC-001.json`, `SPL-LANL-001.json` | **DECLARED_ONLY / PARTIAL** | Manifests declare causal split strategies, but `raw_dataset_acquired = false`. |
| **Preprocessing Pipeline** | `src/research_agent/experiments/extractor/tokenizer.py`, `graph_builder.py` | **IMPLEMENTED** | Log parser hash `6bd80edb...`, dynamic parameter slot extraction, relation extraction. |
| **Train/Validation Split** | `datasets/manifests/REAL-DATA-CONTRACT-HDFS.json`, `SPL-HDFS-001.json` | **IMPLEMENTED** | Cryptographically locked: Train (35,000 sessions / 586,577 events, SHA `65b76694...`), Val (7,500 sessions / 119,531 events, SHA `14cf689f...`). |
| **Test Firewall** | `src/research_agent/experiments/extractor/graph_builder.py` (`RuntimeTestFirewallGuard`) | **IMPLEMENTED** | Sealed crypto firewall; raises `TestSetSealedError` immediately if Test split is accessed. |
| **Checkpoint Storage & Format** | `durable/stage-a2/HDFS/`, `experiments/runs/stage-a1/` | **IMPLEMENTED** | PyTorch `.pt` format serializing 14 mandatory state dictionaries (model, optimizer, scheduler, node memory, stream cursors, RNG states). |
| **Sequence Encoder** | `src/research_agent/experiments/extractor/sequence_view.py` | **IMPLEMENTED** | 4-layer Transformer Encoder ($d_{model}=128, H=4, d_{ffn}=512$, GELU, dropout=0.10) with multi-slot parameter embeddings. |
| **Graph Encoder** | `src/research_agent/experiments/models/temporal_graph_view_encoder.py` | **IMPLEMENTED** | Causal Temporal Graph Neural Network with dynamic node memory banks, relative time projection, relation embeddings ($d_{node}=128$). |
| **Fusion Module** | `src/research_agent/experiments/extractor/multi_view.py` (`GatedMultiViewFusion`) | **IMPLEMENTED** | Gated Dynamic Fusion ($\alpha = \sigma(W_{gate}[z_{seq}; z_{graph}])$) with reconstruction loss $L_{fuse\_rec}$. Supports `sequence_only`, `graph_only`, `unaligned`, `aligned`. |
| **VICReg Alignment** | `src/research_agent/experiments/extractor/multi_view.py` (`VICRegLoss`) | **IMPLEMENTED** | Explicit Invariance (sim_coeff=25.0), Variance (var_coeff=25.0, $\gamma=1.0$), and Covariance (cov_coeff=1.0) anti-collapse loss. Tested in `tests/test_multiview_vicreg.py`. |
| **PCGrad Gradient Surgery** | Mentioned in Chapter 2 prose, `native_omml_equations.py` | **DECLARED_ONLY / ABSENT** | Described mathematically in thesis and equations, but **NO** executable PCGrad optimizer wrapper exists in current training scripts. |
| **Attention-MIL (Stage B)** | `src/research_agent/experiments/protocols/weak_attribution_evaluator.py` | **PARTIAL** | Attribution evaluation harness exists; however, Stage B training module is unintegrated in current pipeline. Legacy checkpoint was quarantined under `AUDIT-INV-a92e755`. |
| **Downstream / Probe Code** | `src/research_agent/experiments/protocols/h1_fidelity_contract.py`, `h2_multiview_contract.py` | **IMPLEMENTED** | Paired cluster bootstrap ($B=2000$, seed 10007), Average Precision (AP), PR-AUC, Bonferroni and Benjamini-Hochberg FDR routines. |
| **Training Entrypoints** | `scripts/run_stage_a1.py`, `scripts/run_stage_a2_five_seed_empirical.py` | **IMPLEMENTED** | Complete deterministic execution entrypoints with command-line guards, CUDA verification, and sweet-spot automation. |
| **Configuration Files** | `experiments/plans/STAGE-A2-FINAL-12-EPOCH-AUTHORITY.json` | **IMPLEMENTED** | Full machine-readable specifications of hyperparameters, loss formulas, environment locks. |
| **Metrics Code** | `src/research_agent/experiments/protocols/paired_cluster_bootstrap.py` | **IMPLEMENTED** | Strict cluster-aware bootstrap resampling preventing pseudo-replication. |
| **Runtime / GPU Watchdogs** | `scripts/set_training_sweetspot.ps1`, `logs/stage-a2/` | **IMPLEMENTED** | Automated PCIe/CPU power governor lock preventing Windows throttle during display sleep. |

---

## 4. Checkpoint Inventory & Safe Read-Only Audit

An exhaustive scan across `D:\Research` identified 69 PyTorch `.pt` files. Safe read-only inspection (zero optimizer steps) produced the following inventory:

### 4.1. Stage A2 Temporal Graph Pretrained Checkpoints (HDFS)
Located in `durable/stage-a2/HDFS/` (and mirrored in `.artifacts/stage-a2/HDFS/`):
- **Architecture:** `TemporalGraphViewEncoder` (d_node=128, d_edge=64, d_msg=128, n_heads=4, d_time_proj=32, d_rel_emb=32, d_type_emb=32; 41 parameter tensors).
- **Input Dimensions:** 8 canonical relations, 4 node types, continuous relative time gaps.
- **Output Representation Dimension:** 128.

| Seed | Epoch / Step | Best Val $L_{graph}$ | Final Val $L_{graph}$ | Historical Status | Can Load Now? | Eligible for Frozen-Representation Experiment? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Seed 999** | Ep 12 / 6,876 | `0.609500` | `0.609500` | Protocol Deviation | **YES** | **YES** (Frozen Graph Backbone) |
| **Seed 42** | Ep 1 / 573 (Last: Ep 4 / 2,292) | `6.081352` | `7.150944` | Protocol Deviation (Early Stopped) | **YES** | **YES** (Frozen Graph Backbone) |
| **Seed 7** | Ep 12 / 6,876 | `0.550259` | `0.550259` | Protocol Deviation | **YES** | **YES** (Frozen Graph Backbone) |
| **Seed 1337** | Ep 10 / 5,730 (Last: Ep 12 / 6,876) | `0.917827` | `1.205658` | Noncanonical | **YES** | **YES** (Frozen Graph Backbone) |
| **Seed 2024** | Ep 12 / 6,876 | `0.553257` | `0.553257` | Noncanonical | **YES** | **YES** (Frozen Graph Backbone) |

### 4.2. Stage A1 Sequence Transformer Checkpoints (HDFS & BGL)
Located in `experiments/runs/stage-a1/`:
- **Architecture:** `SequenceViewTransformerEncoder` (4 layers, d_model=128, H=4, d_ffn=512; 75 parameter tensors).
- **Output Representation Dimension:** 128.

| Dataset | Seed | Epoch / Step | Best Val $L_{seq}$ | Source Commit | Can Load Now? | Eligible for Frozen-Representation Experiment? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **HDFS** | Seed 42 | Ep 16 / 8,752 | `0.032200` | `2325923b...` | **YES** | **YES** (Frozen Sequence Backbone) |
| **HDFS** | Seed 7 | Ep 12 / 6,564 | `0.033878` | `2325923b...` | **YES** | **YES** (Frozen Sequence Backbone) |
| **HDFS** | Seed 999 | Ep 18 / 9,846 | `0.030100` | `2325923b...` | **YES** | **YES** (Frozen Sequence Backbone) |
| **HDFS** | Seed 1337 | Ep 14 / 7,658 | `0.029721` | `2325923b...` | **YES** | **YES** (Frozen Sequence Backbone) |
| **HDFS** | Seed 2024 | Ep 20 / 10,940 | `0.030482` | `2325923b...` | **YES** | **YES** (Frozen Sequence Backbone) |
| **BGL** | Seeds 42, 7, 999, 1337, 2024 | Ep 1–6 / 313–1878 | `11.28–12.06` | `2325923b...` | **YES** | **YES** (Frozen Sequence Backbone) |

### 4.3. Quarantined Legacy Checkpoints (`experiments/checkpoints/`)
- `hdfs_stage_a_frozen.pt`, `bgl_stage_a_frozen.pt`, `darpa_e3_stage_a_frozen.pt`, `*_stage_b_attribution.pt`:
  - **Status:** **QUARANTINED** under `AUDIT-INV-a92e755`.
  - **Reason:** Produced on synthetic DARPA data and non-causal HDFS splits with fabricated attribution ground truth.
  - **Eligibility:** **STRICTLY FORBIDDEN / INELIGIBLE** for confirmatory 9+ campaign evidence.

---

## 5. Dataset & Label Inventory

Direct examination of data packages in `experiments/runs/data/` revealed the exact targets physically present:

| Field Name | Semantic Meaning | Source & Provenance | Available on Train | Available on Validation | Requires Test? | Leakage Risk & Handling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HDFS_ANOMALY_LABEL` | Session-level block anomaly flag (0 = Normal, 1 = Anomaly) | Ground truth block labels from LogHub HDFS distribution | **YES** (35,000 sessions: 33,333 N, 1,667 A) | **YES** (7,500 sessions: 7,410 N, 90 A) | `false` | Zero leakage. Stored in `vault/hdfs_probe_labels_*.pt`, completely isolated from SSL pretraining loops. |
| `BGL_SYSTEM_ALERT_LABEL` | Sequence-level system alert flag (0 = Normal, 1 = Alert) | BGL raw alert severity column (`-` vs alert levels) | **YES** (20,000 sequences: 11,291 N, 8,709 A) | **YES** (5,000 sequences: 3,075 N, 1,925 A) | `false` | Zero leakage. Stored in `vault/bgl_probe_labels_*.pt`, used only for downstream probe fitting. |
| `param_targets` | Categorical security parameter classes (IP private/public, size buckets, hex addresses) | Extracted by deterministic regex parser from raw logs | **YES** (35k HDFS, 20k BGL) | **YES** (7.5k HDFS, 5k BGL) | `false` | None. Used as self-supervised prediction targets during SSL pretraining. |
| `sequences` | Categorical event template IDs | Drain-parsed event templates | **YES** | **YES** | `false` | Standard input tokens. |
| `time_gaps` | Normalized adjacent temporal deltas $\log(1 + \Delta t)$ | Calculated from raw log timestamps | **YES** | **YES** | `false` | Relative forward differences; no look-ahead. |
| `graph_events` | Causal temporal edges $(u, v, r, t)$ | Extracted block-node-client interactions | **YES** (586,577 events) | **YES** (119,531 events) | `false` | Strict causal timestamp ordering; inductive boundary reset on validation transition. |

---

## 6. H1 Direct Test Feasibility (Parameter Semantic Fidelity)

- **Feasibility Classification:** `H1_FEASIBILITY = FEASIBLE`
- **Direct Target $S$:**
  1. *Primary Parameter Recovery Target:* Predicting dynamic parameter category tokens (IP classes, byte size buckets) from the frozen representation $z$.
  2. *Downstream Security Target:* Downstream anomaly classification on `HDFS_ANOMALY_LABEL` and `BGL_SYSTEM_ALERT_LABEL`.
- **Baseline vs. Treatment Representation:**
  - *Baseline ($z_{\text{template}}$):* Representation produced with `param_slots = None` (parameter tokens masked/zeroed out), forcing the model to rely solely on event templates.
  - *Treatment ($z_{\text{param}}$):* Representation produced with full multi-slot dynamic parameter embeddings (`BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4`).
  - *Identical Conditions:* Same frozen backbone, same Train/Val split, same linear probe architecture ($W \in \mathbb{R}^{128 \times C}$), same evaluation metric.
- **Required New Training:**
  - `NEW_BACKBONE_OPTIMIZER_STEPS = 0`.
  - Only capacity-controlled linear probe training ($W \in \mathbb{R}^{128 \times C}$) on the Train split, evaluated on the Validation split.
- **Pre-Registered Metric:** Average Precision (AP) Difference over Clusters with Paired Cluster Bootstrap ($B=2000$, seed=10007, Bonferroni-corrected $\alpha=0.05$).
- **Integrity Rule:** Backbone training loss is **NOT** used as an H1 metric. Zero synthetic labels are invented.

---

## 7. H2 Ablation Feasibility (Highest Priority)

- **Feasibility Classification:** `H2_FEASIBILITY = FEASIBLE (HIGHEST_PRIORITY)`
- **Core Multi-View Modalities:**
  - `A. Sequence-only`: Fully implemented (`SequenceViewExtractor` in `sequence_view.py`, 5 Stage A1 checkpoints available).
  - `B. Graph-only`: Fully implemented (`TemporalGraphViewEncoder` in `temporal_graph_view_encoder.py`, 5 Stage A2 checkpoints available).
  - `C. Multi-view unaligned`: Fully implemented (`MultiViewRepresentationModel(mode='unaligned')`, concatenation + projection).
  - `D. Multi-view aligned (VICReg)`: Fully implemented (`MultiViewRepresentationModel(mode='aligned')`, VICReg invariance/variance/covariance loss + gated fusion).
- **PCGrad Status:**
  - PCGrad is **DECLARED_ONLY** in Chapter 2 prose and mathematical derivations; it is **ABSENT** in executable training code.
  - *Protocol Decision:* In accordance with Karpathy Simplicity Guidelines ("No features beyond what was asked; no speculative code"), Phase 0 will **NOT** invent or inject complex new PCGrad wrappers. The primary H2 confirmatory ablation will focus on **Single-View vs. Unaligned Multi-View vs. Aligned Multi-View (VICReg)**. PCGrad is categorized as an optional ablation if implemented later.
- **Negative Transfer Measurement:**
  - Measured via paired cluster bootstrap comparison of downstream AP:
    $$\Delta AP_{\text{vs\_seq}} = AP(z_{mv}) - AP(z_{seq})$$
    $$\Delta AP_{\text{vs\_graph}} = AP(z_{mv}) - AP(z_{graph})$$
  - Synergistic gain without negative transfer is supported if:
    $$\Delta AP_{\text{vs\_seq}} \ge -0.02 \quad \text{AND} \quad \Delta AP_{\text{vs\_graph}} \ge -0.02 \quad \text{AND} \quad \Delta AP_{\text{vs\_unaligned}} > 0 \quad (p < 0.05)$$
    and latent variance $\text{Var}(z_{mv}) \ge 0.01$ (anti-collapse).

---

## 8. H3 Low-Cost Feasibility (Robustness Suite P01..P12)

- **Feasibility Classification:** `H3_FEASIBILITY = FEASIBLE_CHEAP`
- **Methodology:**
  - Retraining backbone: **STRICTLY ZERO STEPS** (`NEW_BACKBONE_OPTIMIZER_STEPS = 0`).
  - Evaluates frozen representation robustness directly on the Validation split (7,500 sessions / 119,531 events).
  - Uses the 12 executable perturbation operators already implemented in `protocols/h3_robustness_contract.py`:
    - P01 (Token Deletion), P02 (Token Insertion Noise), P03 (Parameter Obfuscation), P04 (Concurrency-Safe Event Order Jitter), P05 (IP Subnet Translation), P06 (Path Aliasing), P07 (Burst Interleaving), P08 (Unseen Template Shift), P09 (Host Reassignment), P10 (Entity Pseudonym Rotation), P11 (Timestamp Skew), P12 (Composite).
  - Evaluated via Relative AP Retention: $\text{Retention} = \frac{AP(z_{\text{perturbed}})}{AP(z_{\text{clean}})}$.
  - Statistical significance evaluated with Benjamini-Hochberg False Discovery Rate (BH-FDR) across all 12 operators ($q < 0.05$).
  - Test set remains sealed (`TEST_OPENED=false`).

---

## 9. H4 / H5 Survey

- **H4 (Operational SLO vs. Attention-MIL Weak Attribution):**
  - *Operational Budget SLO Harness:* **IMPLEMENTED** in `protocols/h4_operational_benchmark.py`. Measures real-hardware continuous RAM peak via background monitor, peak CUDA VRAM, and p95 latency. Can be run with zero training.
  - *Attention-MIL (Stage B):* **PARTIAL**. Mathematical formulas exist, but training loop is unintegrated into modern pipeline. Furthermore, HDFS lacks fine-grained per-event ground truth annotations; running MIL on HDFS without annotations produces `NOT_EVALUABLE_ON_HDFS` to prevent synthetic label fabrication.
- **H5 (Utility–Privacy Frontier / MIA):**
  - *Adversarial Attack Harness:* **IMPLEMENTED** in `protocols/h5_privacy_frontier.py` (4 attack classes: Re-identification, Linkage, MIA, Inversion).
  - *Readiness:* Feasible via frozen representation probing, but deferred to later phases to conserve the 15-day compute budget for H2/H1/H3.
- **Priority Sequence:**
  $$\mathbf{H2 \text{ (Multi-View Ablation)}} > \mathbf{H1 \text{ (Parameter Fidelity)}} > \mathbf{H3 \text{ (Robustness P01..P12)}} > \mathbf{H4 \text{ (Operational SLO)}} > \mathbf{H5 \text{ (Privacy Frontier)}}$$

---

## 10. Runtime Forensics

Runtime estimates are derived exclusively from authentic empirical records across 52 completed epochs in `experiments/evidence/stage-a2/completed/` on the NVIDIA RTX 3050 Ti Laptop GPU:

```text
EMPIRICAL RUNTIME MEASUREMENTS (HDFS Stage A2, 586,577 train events / 119,531 val events):
  - With Sweet Spot Profile (Active PCIe ASPM=0, PROCTHROTTLEMIN=60%, e.g., Seed 999):
      Average Train Runtime per Epoch :  94.7 minutes  (5,684 seconds)
      Average Val Runtime per Epoch   :   7.5 minutes  (  450 seconds)
      Average Total Time per Epoch    : 102.2 minutes  (1.70 hours)
      Step Processing Rate (573 steps):  9.9 seconds / optimizer step (1,024 events/step)
      Full 12-Epoch Confirmatory Run  : 20.43 hours    (Train: 18.93h, Val: 1.50h)

  - Under Unmitigated Windows Power Throttling (ASPM=2, CPU throttled to 800 MHz when screen is off):
      Degraded Train Runtime per Epoch: up to 269.4 minutes (~4.5 hours)
      Degraded 12-Epoch Run           : 32.5 - 32.7 hours

RUNTIME CONFIDENCE                   : HIGH (Microsecond timestamps from completed manifests)
ESTIMATED_HOURS_PER_FULL_RUN         : 20.43 hours (under locked Sweet Spot script)
```

---

## 11. Experiment Budget Tiers (15-Day Campaign Window)

Available Window: 15 days = 360 hours. Hardware: NVIDIA GeForce RTX 3050 Ti Laptop GPU (4 GB VRAM).

### Tier 1: MINIMUM_9PLUS_CAMPAIGN (Probe & Statistical Testing Focus)
- **Scope:** Zero new backbone pretraining runs. Evaluates H1, H2, H3, and H4 entirely using capacity-controlled frozen probes on existing Stage A1 and Stage A2 checkpoints + 1 Multi-View Pilot run (2 epochs).
- **New Backbone Training:** 1 pilot run $\times$ 2 epochs $\approx 3.5$ GPU hours.
- **Probe Training & Evaluation:** ~7.0 GPU hours across H1/H2/H3/H4.
- **Total GPU Hours:** **10.5 hours**.
- **Total Wall Clock Hours:** **~14.0 hours**.
- **Disk Requirement:** **~5.0 GB**.

### Tier 2: RECOMMENDED_CAMPAIGN (Balanced Confirmatory Ablation — Target Choice)
- **Scope:**
  1. H1 Parameter Fidelity on frozen representations (5 seeds).
  2. H3 Robustness Suite (P01..P12) on frozen representations (3 seeds).
  3. H4 Operational SLO Benchmark.
  4. End-to-end Multi-View Confirmatory Pretraining:
     - 1 Pilot Run (Seed 42, 2 epochs) = ~3.5 GPU hours.
     - 3 Confirmatory Aligned Multi-View Runs (Seeds 42, 7, 999, 12 epochs each) = $3 \times 20.43 = 61.3$ GPU hours.
     - 1 Unaligned Multi-View Ablation Run (Seed 42, 12 epochs) = 20.43 GPU hours.
     - 1 Fresh Sequence-Only Baseline Run under identical prospective harness = 1.0 GPU hour.
- **Total GPU Hours:** **92.6 hours** (~3.9 days of computation).
- **Total Wall Clock Hours:** **~110.0 hours** (~4.6 days, well within the 15-day window, allowing dedicated nocturnal execution without thermal stress).
- **Disk Requirement:** **~15.0 GB**.

### Tier 3: FULL_CAMPAIGN (Exhaustive Matrix)
- **Scope:** Full 5-seed matrix (Seeds 42, 7, 999, 1337, 2024) across Aligned Multi-View, Unaligned Multi-View, and fresh Single-View runs + H5 Privacy Frontier.
- **Total GPU Hours:** **~240.0 hours** (~10.0 days).
- **Total Wall Clock Hours:** **~280.0 hours** (~11.7 days).
- **Disk Requirement:** **~35.0 GB**.

---

## 12. Statistical & Experimental Design

1. **Orthogonal Factor Separation:**
   - *Replication Factor:* Random seed variation across identical architectures and datasets (Seeds 42, 7, 999).
   - *Ablation Factor:* Explicit modification of architecture (Sequence-only vs. Graph-only vs. Unaligned Multi-view vs. Aligned Multi-view with VICReg).
2. **Prospective Lock Invariants:**
   - Every confirmed run in the campaign must share:
     - Exact Git commit baseline (`8a00e67f79a9e787d3eb9e29f4c483aed4764246`).
     - Identical preprocessing parser version (`6bd80edb...`).
     - Identical Train/Val split boundaries (`65b76694...` / `14cf689f...`).
     - Identical scheduler (LinearWarmupCosineDecay, warmup ratio 0.05 = 343 steps, initial lr $5 \times 10^{-4}$, min lr $10^{-5}$).
     - Identical stopping rule (patience=3 epochs on global validation loss or 12-epoch ceiling).
3. **Pilot Policy:**
   - Pilot runs are executed strictly on Seed 42 for a reduced budget of 2 epochs.
   - Purpose: Verify GPU VRAM bounds (< 4 GB), confirm absence of NaN/Inf floating point anomalies, verify stream cursor serialization, and validate metric output JSON contracts.
   - **Pilot Exclusion Rule:** Pilot metrics are strictly quarantined as `PILOT_DEBUG_ONLY` and **MUST NOT** be pooled into confirmatory hypothesis testing.

---

## 13. Test Firewall & Accounting State

```text
TEST_OPENED                         = false
TEST_READ_COUNT                     = 0
TEST_FIREWALL_STATUS                = CRYPTOGRAPHICALLY_SEALED

LEGACY_STAGE_A2_OPTIMIZER_STEPS     = 29,796
PHASE0_NEW_BACKBONE_OPTIMIZER_STEPS = 0
PHASE0_NEW_PROBE_OPTIMIZER_STEPS    = 0
PHASE0_NEW_MIL_OPTIMIZER_STEPS      = 0
```

---

## 14. Phase 0 Blockers & Governance Readiness

- **Current Blockers:** **NONE**. All datasets, checkpoints, loaders, encoders, fusion modules, and statistical testing harnesses are verified, loadable, and mathematically intact.
- **Pre-Registration Gate:** Locked to machine-readable artifact `experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V1.json`.
- **Phase 0 Conclusion:** Phase 0 is complete. In accordance with Section 20 instructions, execution **STOPS** immediately. Zero optimizer steps will be launched until Phase 0 review is formally approved.
