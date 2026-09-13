# NINEPLUS PHASE 0 — REVIEW CORRECTION & CAMPAIGN V2 DESIGN REPORT

**Document ID:** `REPORT-NINEPLUS-PHASE0-REVIEW-V2`  
**Date:** 2026-09-13  
**Workspace:** `D:\Research`  
**Repository:** `Minhlike/Chuyende`  
**Branch:** `fix/thesis-apply-edits`  
**V1 Preregistration Commit:** `70fbebcbe9023bac2e46c51b80955190ee425085`  
**Authoritative V2 Machine-Readable Plan:** `experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V2.json`  
**Active Scientific Standard:** ATTT Warranted-Derivation Scientific Writing Skill v4.0 (`D:\Research\deep-research-report-v4.md`)

---

## 1. Executive Summary & Review Invariant State

```text
V1_COMMIT                           = 70fbebcbe9023bac2e46c51b80955190ee425085
V2_COMMIT                           = PENDING_COMMIT_IN_THIS_PHASE
CONFIRMATORY_CODE_COMMIT            = PENDING_PILOT_VALIDATION_LOCK

MASTER_CHANGED                      = false
TEST_OPENED                         = false
TEST_READ_COUNT                     = 0

PHASE0_NEW_BACKBONE_OPTIMIZER_STEPS = 0
PHASE0_NEW_PROBE_OPTIMIZER_STEPS    = 0
PHASE0_NEW_MIL_OPTIMIZER_STEPS      = 0

H4_RESTORED_TO_WEAK_LABEL           = true
ER1_SEPARATED                       = true

H2_PRIMARY_CONFIGS                  = [SEQUENCE_ONLY, GRAPH_ONLY, MULTI_VIEW_ALIGNED_VICREG]
H2_CONFIRMATORY_SEEDS               = [42, 7, 999]
H2_CONFIRMED_RUNS                   = 9
H2_TOTAL_MAX_EPOCHS                 = 108

UNALIGNED_STATUS                    = OPTIONAL_SECONDARY
PCGRAD_STATUS                       = ABSENT_DEFERRED

H1_PRIMARY_DIRECT_METRIC            = Macro-F1 (Parameter Category Recovery Probe)
H1_SECONDARY_METRICS                = [Downstream Anomaly AP, PR-AUC, Parameter Recovery Accuracy]
H1_MASKING_ABLATION_LABEL           = FROZEN_INPUT_MASKING_ABLATION

H3_CONFIRMATORY_OPERATORS           = [P01, P02, P03, P04, P05, P06, P09]
H3_EXPLORATORY_OPERATORS            = [P07, P08, P10, P11, P12]

SEED_LEVEL_INFERENCE_RULE           = Model-level replication across seeds 42, 7, 999 (Reports individual seed metrics, mean, and std)
CLUSTER_BOOTSTRAP_ROLE              = Nested within-run data-level sampling uncertainty; NOT a replacement for training seed replication

ESTIMATED_PRIMARY_GPU_HOURS         = ~184 hours (9 runs x 20.43h nominal baseline before pilot refinement)
BLOCKERS                            = NONE for primary H2/H1/H3/ER1
```

---

## 2. Restoration of Semantic Identities (H4 vs. ER1)

In the V1 preregistration draft, the operational latency/throughput benchmark harness was conflated with hypothesis H4. This has been corrected:

1. **H4 Semantic Identity Restored:**
   - **Construct:** *Weak-Label Evidence Allocation & Administrator-Noise Robustness*.
   - **Theoretical Scope:** Stage B / Attention-MIL / Coarse-Label Attribution.
   - **Current Status:** `NOT_TESTED` / Implementation `PARTIAL`.
   - **Integrity Rule:** On HDFS, the standard distribution provides only coarse session/block-level anomaly labels, with zero independent ground-truth root-cause event annotations. Attempting attribution evaluation without ground truth would force heuristic label fabrication (as occurred in the invalidated commit `a92e755`). Therefore, H4 is explicitly deferred from the core 15-day budget.
2. **ER1 Engineering Family Separated:**
   - The operational benchmark is renamed to **`ER1_OPERATIONAL_RESOURCE_FEASIBILITY`**.
   - ER1 evaluates engineering feasibility on edge deployment targets (p95 latency $\le 10$ ms, peak host RAM $\le 500$ MB, throughput $\ge 10,000$ events/s).
   - **Threshold Classification:** Strictly designated as `AUTHOR_DEFINED_ENGINEERING_TARGET`, not universal SOC requirements.
   - ER1 is evaluated via zero-training forward passes on the Validation stream after H2 completes.

---

## 3. Primary H2 Confirmatory Campaign (Exactly 3 Configs $\times$ 3 Seeds = 9 Runs)

### 3.1. Primary Confirmatory Factor
The primary H2 ablation matrix comprises exactly three configurations evaluated under identical prospective conditions:
1. **`SEQUENCE_ONLY`**: Transformer sequential encoder ($d_{model}=128, H=4, L=4$) trained with self-supervised objective $L_{seq} = 1.0 \times L_{MEP} + 1.0 \times L_{MPP} + 0.1 \times L_{time}$.
2. **`GRAPH_ONLY`**: Temporal Graph Neural Network ($d_{node}=128, d_{rel}=32, d_{time}=32$) trained with causal objective $L_{graph} = 1.0 \times L_{rel} + 1.0 \times L_{node} + 0.1 \times L_{time}$.
3. **`MULTI_VIEW_ALIGNED_VICREG`**: Joint Multi-View Architecture connecting Sequence View, Graph View, VICReg anti-collapse alignment ($\lambda_{align}=1.0$), and Gated Dynamic Fusion ($L_{StageA} = L_{seq} + L_{graph} + 1.0 \times L_{VICReg} + 1.0 \times L_{fuse\_rec}$).

### 3.2. Confirmatory Replications & Epoch Budget
- **Confirmatory Seeds:** `42`, `7`, `999`.
- **Max Epoch Ceiling:** `12` epochs per run.
- **Run Accounting:**
  $$\text{3 configurations} \times \text{3 seeds} = \mathbf{9 \text{ confirmed backbone runs}} = \mathbf{108 \text{ backbone epochs}}$$
- **Historical Checkpoint Boundary:** Historical Stage A1/A2 checkpoints are classified strictly as `EXPLORATORY_REFERENCE_ONLY`. To eliminate cross-campaign code drift and scheduler discrepancies, all 9 confirmed runs will be trained under the same prospective runner harness.

---

## 4. Secondary & Excluded Factors (Unaligned Fusion & PCGrad)

1. **Unaligned Fusion Removed from Primary Decision Rule:**
   - Configuration `MULTI_VIEW_UNALIGNED` is classified as `OPTIONAL_SECONDARY_ABLATION`.
   - It will **NOT** be executed by default.
   - It will only be considered after the primary 9-run matrix is completed and only if remaining time/compute within the 15-day window permits.
   - *Epistemological Warrant:* No claim regarding the specific causal contribution of VICReg anti-collapse loss will be asserted unless the matched aligned-vs-unaligned ablation run is actually performed.
2. **PCGrad Status:**
   - PCGrad remains `DECLARED_ONLY / ABSENT_IN_CODE`.
   - In accordance with Karpathy Rule 2 ("Simplicity First: Minimum code that solves the problem; no speculative code"), no ad-hoc PCGrad optimizer wrappers will be implemented for this campaign.
   - Zero empirical benefit from PCGrad is claimed.

---

## 5. Fair Comparability & Pre-Training Exposure Alignment

To ensure that performance differences reflect representational modality rather than extraneous experimental confounders, the 9 confirmed runs lock the following invariants:
- **Same Dataset:** HDFS LogHub Benchmark (`DATA-HDFS-001`).
- **Same Split Boundaries:** Train (35,000 sessions / 586,577 events, SHA `65b76694...`) and Validation (7,500 sessions / 119,531 events, SHA `14cf689f...`).
- **Same Preprocessing Version:** Parser version hash `6bd80edb...`.
- **Same Evaluation Protocol:** Validation epoch loss aggregation and capacity-controlled linear probe ($W \in \mathbb{R}^{128 \times 2}$).
- **Same Stopping Policy:** Early stopping patience=3 epochs on validation loss or 12-epoch ceiling.
- **Fair-Comparison Unit (Session/Event Exposure vs. Optimizer Steps):**
  - Sequence-only processes batches of log sequences (micro-batch=16, accum=4 $\implies$ 64 sequences/step).
  - Graph-only processes causal event windows ($W=256$ events, accum=4 $\implies$ 1,024 events/step).
  - Multi-view processes synchronized session streams.
  - Because sequences and graph event windows have different granularities, mechanically forcing an identical optimizer step count would distort training dynamics.
  - **Fair Comparison Standard:** All models receive strictly equal total data exposure per epoch (586,577 train events across 35,000 sessions) and an identical 12-epoch ceiling.

---

## 6. H2 Decision Rule: Non-Inferiority & Superiority Formulation

The V1 phrasing ("higher by margin epsilon -0.02") conflated superiority and non-inferiority. V2 formalizes these as distinct statistical thresholds:

1. **Non-Inferiority Margin:**
   $$\Delta AP_{\text{vs\_seq}} = AP(z_{mv}) - AP(z_{seq}) \ge -0.02$$
   $$\Delta AP_{\text{vs\_graph}} = AP(z_{mv}) - AP(z_{graph}) \ge -0.02$$
2. **Superiority Criterion:**
   $$\Delta AP > 0 \quad \text{with } 95\% \text{ bootstrap confidence interval strictly excluding } 0$$
3. **Anti-Collapse Requirement:**
   $$\text{Var}(z_{mv}) \ge 0.01$$
4. **Primary H2 Outcome Classifications:**
   - **`SUPPORTED`**: Multi-View satisfies non-inferiority against both single-views ($\Delta \ge -0.02$) AND achieves statistically significant superiority ($\Delta > 0$) over at least one single-view baseline, with $\text{Var}(z_{mv}) \ge 0.01$.
   - **`PARTIALLY_SUPPORTED`**: Multi-View satisfies non-inferiority ($\Delta \ge -0.02$) against both single-views without variance collapse, demonstrating stable multi-modal integration without negative transfer, but does not strictly beat both single views.
   - **`FALSIFIED`**: Multi-View is significantly inferior to either single view ($\Delta < -0.02$ with 95% CI excluding $-0.02$) OR suffers latent representation collapse ($\text{Var}(z_{mv}) < 0.01$).
   - **`INCONCLUSIVE`**: Confidence intervals span the non-inferiority margin without directional resolution.

---

## 7. Statistical Hierarchy: Seed Replication vs. Cluster Bootstrap

To prevent pseudoreplication:
1. **Model-Level Replications (Primary Inferential Unit):**
   - The three confirmatory training seeds (Seeds 42, 7, 999) represent three independently trained models.
   - Results are reported per seed (`metric_seed42`, `metric_seed7`, `metric_seed999`), accompanied by sample mean and sample standard deviation ($N=3$).
2. **Cluster Bootstrap Role (Data-Level Uncertainty):**
   - Paired cluster bootstrap ($B=2,000$, seed `10007`) resamples independent session/block clusters to compute confidence intervals on within-run performance deltas.
   - It quantifies finite-sample data sampling uncertainty. It is **STRICTLY PROHIBITED** from substituting for training seed replication. Conclusions cannot treat resampled test clusters as independent model training instances.

---

## 8. H1 Construct Repair (Parameter Semantic Fidelity)

1. **Primary Direct Metric & Target:**
   - **Construct:** *Parameter Semantic Fidelity*.
   - **Primary Direct Evidence:** Parameter category recovery probe predicting categorical dynamic parameter classes (`param_targets`: private/public IP classes, byte size buckets) from the frozen representation $z$.
   - **Probe Architecture:** Capacity-controlled linear/logistic probe ($W \in \mathbb{R}^{128 \times C}$, 0 hidden layers).
   - **Primary Metric:** `Macro-F1` on parameter category classification (locked before execution to address class imbalance).
   - **Backbone State:** `STRICTLY_FROZEN` (`NEW_BACKBONE_OPTIMIZER_STEPS = 0`).
2. **Secondary Relevance Evidence:**
   - Downstream Anomaly AP on `HDFS_ANOMALY_LABEL` is categorized strictly as a `SECONDARY_UTILITY_METRIC`.
3. **Ablation Nomenclature & Epistemological Boundaries:**
   - Passing `param_slots = None` to a parameter-trained encoder is designated: **`FROZEN_INPUT_MASKING_ABLATION`**.
   - *Allowed Inference:* Dynamic parameter slots supply linearly accessible information that is preserved in the representation.
   - *Forbidden Inference:* Does not prove that a parameter-aware pretraining regime is globally superior to an independently trained template-only regime.
   - *Circularity Qualifier:* Because `param_targets` served as an SSL pretraining target ($L_{MPP}$), probe recovery demonstrates that parameter semantics were retained linearly, but is not an independent proof of downstream anomaly detection superiority.

---

## 9. H3 Semantic-Preservation Audit (Perturbations P01..P12)

Before execution, every operator in the perturbation suite is audited and partitioned based on its theoretical warrant:

| Operator | Transformation | Classification | Scientific Warrant & Construct Tested | Allowed Inference |
| :--- | :--- | :---: | :--- | :--- |
| **P01** | Token Deletion (Bounded) | **SEMANTIC_PRESERVING_WITH_WARRANT** | Drops non-structural filler words while preserving block IDs and operational verbs. Tests resilience to minor log syntax omissions. | Representation does not overfit to superficial filler text. |
| **P02** | Token Insertion (Benign) | **SEMANTIC_PRESERVING_WITH_WARRANT** | Injects benign background daemon heartbeats. Anomalous session structure is unaltered. Tests background noise filtering. | Model isolates anomalous sequences amid background telemetry chatter. |
| **P03** | Parameter Obfuscation | **SEMANTIC_PRESERVING_WITH_WARRANT** | Injective hex-to-decimal parameter translation. Numerical value and relational dependencies are strictly invariant. | Representation is invariant to base-10 vs base-16 numerical formatting. |
| **P04** | Event Order Jitter | **SEMANTIC_PRESERVING_WITH_WARRANT** | Concurrency-safe reordering strictly confined to events with identical physical timestamps. Causal order is preserved. | Model is immune to non-deterministic thread/concurrency serialization order. |
| **P05** | IP Subnet Translation | **SEMANTIC_PRESERVING_WITH_WARRANT** | Bijective 1-to-1 private subnet IP mapping. Communication topology and graph isomorphism are preserved. | Model learns topological communication structure rather than memorizing static IP addresses. |
| **P06** | Path Aliasing | **SEMANTIC_PRESERVING_WITH_WARRANT** | Syntactic relative path aliasing (`./`). Resolves to identical file system objects. | Model is invariant to redundant relative directory path syntax. |
| **P09** | Host Reassignment | **SEMANTIC_PRESERVING_WITH_WARRANT** | Bijective host renaming. Preserves node-host topological correspondence. | Model learns structural host roles rather than static hostnames. |
| **P07** | Burst Interleaving | **STRESS_TEST_ONLY** | Injects high-frequency bursts altering inter-arrival times $\Delta t$. | Measures temporal encoder stress under traffic spikes; not pure semantic invariance. |
| **P08** | Unseen Template Shift | **STRESS_TEST_ONLY** | Replaces verbs with synonyms, causing Drain to produce new template IDs or `<UNK>`. | Measures Drain OOD vocabulary handling; not within-schema robustness. |
| **P10** | Entity Pseudonym Rotation | **STRESS_TEST_ONLY** | Rotates pseudonym salt across boundaries, breaking continuous session keys. | Measures cross-window memory decay; not single-session semantic invariance. |
| **P11** | Timestamp Skew | **STRESS_TEST_ONLY** | Injects uniform temporal jitter ($\pm 2s$), potentially altering fine-grained time gaps. | Measures model sensitivity to clock drift and asynchronous network delays. |
| **P12** | Composite Perturbation | **STRESS_TEST_ONLY** | Chains multiple operators simultaneously. | Compound stress test measuring degradation under combined multi-axis stress. |

- **Confirmatory Rule:** Primary H3 hypothesis testing is restricted exclusively to the 7 **`SEMANTIC_PRESERVING_WITH_WARRANT`** operators ([P01, P02, P03, P04, P05, P06, P09]) under Benjamini-Hochberg FDR control ($q < 0.05$).
- **Exploratory Rule:** Operators [P07, P08, P10, P11, P12] are analyzed separately as stress tests and will **NOT** be averaged into the primary robustness metric.

---

## 10. Runtime Budget & Schedule Feasibility

1. **Empirical Baseline:**
   - Under the locked Sweet Spot hardware profile (`set_training_sweetspot.ps1`), an empirical full 12-epoch run takes **20.43 hours** on the local NVIDIA RTX 3050 Ti Laptop GPU.
2. **Primary 9-Run Nominal Compute:**
   $$\text{Nominal Primary Budget} = 9 \text{ runs} \times 20.43 \text{ hours} \approx \mathbf{184 \text{ GPU hours}}$$
   - *Clarification:* This is an upper-bound prospective estimate because Sequence-Only runs are expected to complete significantly faster than graph runs. Exact runtimes will be calibrated during the 3 pilot runs.
   - *15-Day Feasibility:* 184 GPU hours represents a **51.1% duty cycle** over the 360-hour 15-day window, providing 176 hours of idle buffer for system cooling, analysis, and uninterrupted nocturnal runs.

---

## 11. Pilot Policy & Prospective Code Lock Progression

1. **Pilot Strategy (Zero Confirmatory Pollution):**
   - Execute exactly 1 short pilot (1–2 epochs maximum, Seed 42) for each of the three configurations:
     - `PILOT_SEQUENCE_ONLY` (Seed 42, 2 epochs)
     - `PILOT_GRAPH_ONLY` (Seed 42, 2 epochs)
     - `PILOT_MULTI_VIEW_ALIGNED` (Seed 42, 2 epochs)
   - *Objectives:* Confirm absence of OOM on 4 GB VRAM, verify absence of NaN/Inf gradients, validate stream cursor persistence, and record configuration-specific minutes-per-epoch.
   - *Exclusion Rule:* All pilot outputs are marked `PILOT_DEBUG_ONLY` and are excluded from confirmatory statistical aggregation.
2. **Prospective Code Lock Flow:**
   ```text
   Step 1: V2 Preregistration Design Lock (NINEPLUS-EXPERIMENT-CAMPAIGN-V2.json)
      │
      ▼
   Step 2: Pilot Execution (Seed 42, 2 epochs across 3 configs)
      │
      ▼
   Step 3: Technical Bug Fixes if Required
      │
      ▼
   Step 4: Execution Manifest & CONFIRMATORY_CODE_COMMIT SHA Lock
      │
      ▼
   Step 5: Sequential Execution of 9 Confirmed Runs
   ```
   If any scientific rule or metric must be altered after inspecting pilot results, a `V3` plan must be generated with explicit justification before launching confirmatory runs.

---

## 12. Execution Priority & Deferred Families

- **Priority 1:** `H2_MULTIVIEW_ABLATION` (9 confirmed backbone runs).
- **Priority 2:** `H1_PARAMETER_FIDELITY` (Capacity-controlled linear probe on frozen backbones).
- **Priority 3:** `H3_ROBUSTNESS_PERTURBATION` (7 confirmatory operators on Validation split).
- **Priority 4:** `ER1_OPERATIONAL_RESOURCE_FEASIBILITY` (Latency/throughput/memory profiler).
- **Deferred:** `H4_ATTENTION_MIL` and `H5_PRIVACY_FRONTIER` are deferred to conserve compute for the primary confirmatory matrix.

---

## 13. Phase 0 Invariant Accounting

```text
TEST_OPENED                         = false
TEST_READ_COUNT                     = 0

PHASE0_NEW_BACKBONE_OPTIMIZER_STEPS = 0
PHASE0_NEW_PROBE_OPTIMIZER_STEPS    = 0
PHASE0_NEW_MIL_OPTIMIZER_STEPS      = 0
```

Phase 0 design review is complete. In strict adherence to the mission directive, execution **STOPS** now. Pilot execution will await your explicit authorization.
