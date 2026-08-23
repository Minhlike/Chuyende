# CHAPTER 3 PROTOCOL AMENDMENT RECORD (PRE-TEST LOCK)
**Timestamp:** 2026-08-22T03:30:00+07:00  
**Execution State:** ANY_MODEL_TRAINED = NO, ANY_TEST_OPENED = NO, RESULTS_SEEN = NO  

---

### Amendment 1: Statistical Decision Semantics (Replacing Binary Accept H0)
- **Previous Language:** Verdict returned binary "REJECT_H0" vs "ACCEPT_H0".
- **Amended Language:** Formally split into three epistemic states:
  1. `SUPPORTED`: Pre-registered effect direction/margin satisfied AND family-wise adjusted significance gate passes ($p \le \alpha_{\text{adj}}$ with positive CI lower bound).
  2. `INCONCLUSIVE`: Observed effect is statistically insufficient ($p > \alpha_{\text{adj}}$ or confidence interval spans zero), without crossing the falsification boundary.
  3. `FALSIFIED`: Observed effect crosses explicit opposite-direction falsification boundary, suffers variance collapse ($< 0.01$), or drops to positive prevalence chance level.
- **Rationale:** Avoids the standard fallacy of affirming the null ($ACCEPT\_H_0$) upon non-significance and establishes clear falsification criteria.

---

### Amendment 2: Primary Confirmatory Anomaly Metric — Average Precision (AP)
- **Previous Language:** Inconsistently used "PR-AUC" and "Average Precision" interchangeably.
- **Amended Language:** The primary confirmatory ranking metric for class-imbalanced log anomaly detection across H1, H2, and H3 is formally locked as **Average Precision (AP)**:
  $$\text{AP} = \sum_{n} (R_n - R_{n-1}) P_n$$
  matching `sklearn.metrics.average_precision_score`. Trapezoidal PR-AUC is retained only as an auxiliary descriptive statistic.
- **Prevalence Baseline:** The chance reference level for AP is locked to positive sample prevalence $\pi = \frac{N_{\text{pos}}}{N_{\text{total}}}$.

---

### Amendment 3: H2 Non-Oracle Multi-View Baseline Evaluation
- **Previous Language:** Unaligned baseline or single-view baseline allowed post-hoc max oracle.
- **Amended Language:** H2 evaluates three separate, pre-registered pairwise comparisons against the Aligned Multi-View model ($z_{\text{mv}}$):
  1. $z_{\text{mv}}$ vs $z^{(\text{seq})}$ (Sequence-Only)
  2. $z_{\text{mv}}$ vs $z^{(\text{graph})}$ (Graph-Only)
  3. $z_{\text{mv}}$ vs $z^{(\text{unaligned})}$ (Unaligned Fusion)
  Multiple testing correction applies Bonferroni adjustment with family size $m=3$ ($\alpha_{\text{adj}} = 0.0167$).

---

### Amendment 4: H5 Proposed Candidate and Adversary Advantage Metrics
- **Previous Language:** Informal reference to Controlled Linkability regime as H5 candidate.
- **Amended Language:** `PRIVACY_AWARE_PARAMETERIZED` is formally designated as the proposed representation candidate for H5 Pareto frontier evaluation, evaluated against `RAW_IDENTIFIERS`, `EXTREME_ANONYMIZATION`, and `CONTROLLED_LINKABILITY`.
- **Adversary Risk Metric:** For Linkage and Membership Inference (MIA), attack advantage is locked to:
  $$\text{Advantage}_{\text{AUC}} = 2 \cdot |\text{AUC} - 0.5| \in [0, 1]$$
  Defense score is locked to $1 - \text{Advantage}_{\text{AUC}}$, preventing inverted classifier evasion from masquerading as privacy defense.

---

### Amendment 5: Removal of Stale Split Bounds & Reconciled Raw Data Provenance (Pre-Test Amendment)
- **Previous Language:** Speculative split day ranges were listed for DARPA (Days 1..14 / 15..21) and LANL (Days 1..89), while HDFS manifest contained a stale line count (11,750,692).
- **Amended Language:**
  1. **DARPA TC E3:** Split boundaries are formally locked as **`PENDING_RAW_CDM18_ALIGNMENT`** until official DARPA TC E3 CDM18 raw artifacts and scenario timelines are materialized and verified.
  2. **LANL Cyber 1:** Split boundaries are formally locked as **`PENDING_ACQUISITION`** (the official LANL Cyber 1 dataset comprises 58 days total, removing the invalid 89-day specification).
  3. **HDFS Provenance & Causal Split:** Corrects official raw HDFS count to exact empirical value **`11,175,629`** lines (satisfying exact conservation $11175629 = 11175629 + 0 + 0$). Replaces random session shuffling with strictly deterministic causal sorting by `(session_start_time, block_id_tiebreak)` where $\max(\text{Train}) \le \min(\text{Val}) \le \min(\text{Test})$.
  4. **BGL Provenance:** Reconciles official raw record count **`4,747,963`** lines and observed minimum timestamp **`1117838570`** across temporal partitions (Days 1-150 Train, Days 151-180 Val, Days 181-215 Sealed Test).

---

### Amendment 6: Stage A1 Pre-Execution Final Consistency & Disambiguated MPP Masking Contract
- **Timestamp:** 2026-08-22T04:50:00+07:00
- **Execution State:** `TEST_OPENED = NO`, `RESULTS_SEEN = NO`, `OPTIMIZER_STEPS_BEFORE_AMENDMENT = 0`
- **Reason:** Consistency correction prior to the first optimizer step.
- **Amended Specifications:**
  1. **Tri-State Falsification Alignment:** Corrected `CH3-PRE-REGISTRATION.md` H1/H2 falsification text to align with canonical tri-state semantics (`SUPPORTED`, `INCONCLUSIVE`, `FALSIFIED`) where $p > \alpha$ or confidence intervals spanning zero indicate `INCONCLUSIVE`, not automatic falsification. Removed stale Hedges' $g$ criterion.
  2. **Disambiguated Masking Policies:** Formally separated Masked Event Prediction ($p_{\text{MEP}} = 0.15$, 80/10/10 rule) from Masked Parameter Prediction ($p_{\text{MPP}} = 0.15$ applied independently per active slot, `<PAD_PARAM>` excluded as target, loss computed strictly over active masked slots).
  3. **Batch & Optimization Regime:** Formally locked canonical batch parameters across all specifications: `micro_batch_size = 16`, `gradient_accumulation_steps = 4`, `effective_batch_size = 64`.
  4. **Five-Seed Stability Role:** Clarified that the $K=5$ canonical seeds evaluate stochastic training stability ($\text{Mean} \pm \text{SD}$) and do not serve as a bootstrap sampling population.

---

### Amendment 7: Stage A2 Pre-Execution Scientific Consistency & Raw-Grounded Graph Amendment V1.1
- **Timestamp:** 2026-08-23T21:05:00+07:00
- **Execution State:** `TEST_OPENED = NO`, `RESULTS_SEEN = NO`, `OPTIMIZER_STEPS_BEFORE_AMENDMENT = 0`, `MODELS_TRAINED_BEFORE_AMENDMENT = 0`
- **Reason:** Pre-execution scientific audit following Stage A2 initial registration to eliminate ungrounded topology assumptions and align graph contracts with verified raw audit schemas before the first optimizer step.
- **Amended Specifications:**
  1. **Dataset Grounding & BGL Ineligibility:** Formally designated **HDFS** as the authorized dataset for Stage A2 graph pretraining based on verified multi-entity raw interactions (DataBlocks, StorageNodes, Namesystem, Threads). Formally declared **BGL ineligible** for Stage A2 graph pretraining (`BGL_STAGE_A2_GRAPH_ELIGIBILITY = FAIL / INELIGIBLE`) because raw BGL telemetry comprises single-node localized alerts without extractable inter-entity interaction destinations, preventing fabricated graph topology.
  2. **Raw-to-Graph Mapping Contract:** Materialized and locked `experiments/schemas/STAGE-A2-RAW-TO-GRAPH-MAPPING.json` specifying deterministic regex-grounded extraction rules for all 8 canonical HDFS relations.
  3. **Removal of Unused Negative Destination Sampling:** Since the canonical multi-task objective $L_{\text{graph}} = 1.0 \cdot L_{\text{rel}} + 1.0 \cdot L_{\text{node}} + 0.1 \cdot L_{\text{time}}$ computes relation classification $L_{\text{rel}}$ on observed $(v, u)$ pairs, negative destination sampling is completely removed from all contracts and checkpoint state definitions.
  4. **Non-Learnable Fixed Node Target:** Defined $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$ as a fixed observable target (4-dim one-hot type + 2-dim log1p causal in/out degrees fit on Train only), eliminating learnable parameter leakage in the reconstruction target.
  5. **Exact Multi-Edge & Conservation Policy:** Enforced exact conservation $\text{raw\_scanned} = \text{materialized\_events} + \text{explicitly\_rejected\_events}$ and locked `PRESERVE_ALL_TEMPORAL_EVENTS_FIFO_CAUSAL` with `max_node_history = 64`.

---

### Amendment 8: Stage A2 Pre-Execution Split Authority Binding & Millisecond Temporal Fidelity (V1.2)
- **Timestamp:** 2026-08-23T21:24:00+07:00
- **Execution State:** `TEST_OPENED = NO`, `RESULTS_SEEN = NO`, `OPTIMIZER_STEPS_BEFORE_AMENDMENT = 0`, `MODELS_TRAINED_BEFORE_AMENDMENT = 0`
- **Amends Commit:** `cc305041023acd855eacfd39d2befa6f2a30e322`
- **Reason:** Binds Stage A2 graph builder directly to canonical `SPL-HDFS-001` split authority, eliminates arbitrary line-offset partitioning in favor of causal block-session membership, restores exact millisecond precision to timestamps, re-audits all 8 relation triggers from raw Train logs, and locks empirical materialization and grounding evidence manifests prior to model training.
- **Amended Specifications:**
  1. **Canonical Split Authority Binding:** Shared `HDFSSplitAuthority` module binds graph materialization directly to `SPL-HDFS-001`. Guaranteed disjointness ($\text{Train} \cap \text{Val} = \emptyset, \text{Train} \cap \text{Test} = \emptyset, \text{Val} \cap \text{Test} = \emptyset$), boundary purges (45,406 T$\to$V sessions, 36,057 V$\to$T sessions purged), and causal time ordering ($\text{train\_max\_end} < \text{val\_min\_start} < \text{val\_max\_end} < \text{test\_min\_start}$).
  2. **Millisecond Timestamp Fidelity & Parity:** Parsed raw millisecond components into exact continuous fractional seconds (`epoch + ms/1000.0`). Verified exact parity between `HDFSRealDataAdapter` and `HDFSGraphBuilder` ($\Delta t = 0.0$).
  3. **Full Train/Val Conservation Manifests:** Materialized full empirical streaming audit manifests (`HDFS-GRAPH-MATERIALIZATION-AUDIT.json` with 5,998,764 Train events and 735,091 Val events with 100% conservation; `RELATION-GROUNDING-AUDIT.json` confirming non-zero Train matches for all 8 relations).
  4. **Strict Causal Node Target & Temporal Gap:** Locked $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$ (4-dim one-hot type + $\log(1 + d_{\text{in}}(v, t-))$ + $\log(1 + d_{\text{out}}(v, t-))$) and $\Delta t_{uv} = t_{\text{curr}} - t_{\text{last\_interaction}}(v, u)$ with boundary reset on Validation transition.

---

### Amendment 9: Stage A2 Execution Scope Disambiguation & Experimental Source Contract (V1.3)
- **Timestamp:** 2026-08-23T21:38:00+07:00
- **Execution State:** `TEST_OPENED = NO`, `RESULTS_SEEN = NO`, `OPTIMIZER_STEPS_BEFORE_AMENDMENT = 0`, `MODELS_TRAINED_BEFORE_AMENDMENT = 0`
- **Amends Commit:** `82d6f7ed37a94efbee80352a907ee38acbe3390a`
- **Reason:** Disambiguates eligible population (357,133 Train / 50,204 Val) from the authorized execution budget (35,000 Train / 7,500 Val), formalizes exact target-leakage masking semantics for $L_{\text{rel}}$ and $L_{\text{node}}$, locks full mutable checkpoint state contracts at optimizer-step boundaries, and establishes the mandatory Chapter 3 Experimental Source Contract.
- **Amended Specifications:**
  1. **Execution Scope Disambiguation:** Formalized separate audits for Full Eligible Population (`HDFS-GRAPH-MATERIALIZATION-AUDIT.json`) and Authorized Execution Budget Subset (`HDFS-EXECUTION-SUBSET-AUDIT.json` with 586,577 Train graph events across 35,000 sessions and 119,531 Val graph events across 7,500 sessions). Materialized deterministic session membership in `HDFS-EXECUTION-MEMBERSHIP.json`.
  2. **Target-Leakage Masking Formalism:** Formalized that when edge relation $r$ is masked for $L_{\text{rel}}$, the prediction input is strictly $[h_v(t-) \parallel h_u(t-) \parallel \phi(\Delta t_{uv})]$ with ground-truth relation embedding withheld until memory update. For $L_{\text{node}}$, reconstruction predicts $x_v^{\text{fixed\_priv}}$ strictly from $h_v(t-)$ without direct target pass-through.
  3. **Complete Mutable Checkpoint State:** Enforced that checkpoints occur strictly at optimizer boundaries (`CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY = true`) and atomically serialize all 14 execution state elements including causal in/out degrees, last interaction timestamps, and temporal history buffers.
  4. **Experimental Source Contract:** Established mandatory provenance standard (`EXPERIMENTAL-SOURCE-CONTRACT.md` and `EXPERIMENTAL-SOURCE-SCHEMA.json`) requiring machine-readable source manifests for every empirical claim.

---

### Amendment 10: Stage A2 Validation Semantics, Global Metric Aggregation & CUDA Execution Lock (V1.4)
- **Timestamp:** 2026-08-23T23:05:00+07:00
- **Execution State:** `TEST_OPENED = NO`, `RESULTS_SEEN = NO`, `OPTIMIZER_STEPS_BEFORE_AMENDMENT = 0`, `MODELS_TRAINED_BEFORE_AMENDMENT = 0`
- **Amends Commit:** `7b3992be792e3b1e2fa48a724562d56c5eeed774`
- **Reason:** Locks validation masking semantics, replaces window-averaged metrics with exact global epoch metric aggregation, formalizes partial final window gradient weighting for the 849-event accumulation group, and locks the empirical execution environment to dedicated CUDA GPU execution without CPU fallback.
- **Amended Specifications:**
  1. **Validation Masking (15% Fixed Deterministic Mask):** Validation evaluation strictly preserves the pre-registered SSL objective ($p_{\text{rel\_mask}} = 0.15$, $p_{\text{node\_mask}} = 0.15$) rather than masking 100% of targets. Validation masks are deterministically fixed across all validation epochs and training seeds via `VALIDATION_MASK_POLICY = "FIXED_DETERMINISTIC_RNG_GENERATOR"` with `VALIDATION_MASK_SEED = 20260823`, completely decoupled from the stochastic training RNG trajectory.
  2. **Global Metric Aggregation:** All reported metrics ($\text{L}_{\text{rel}}$, $\text{L}_{\text{node}}$, $\text{L}_{\text{time}}$, and composite $\text{L}_{\text{graph}}$) are computed by global epoch summation over exact numerators and denominators (not mean-of-window-means):
     $$\text{L}_{\text{rel}} = \frac{\sum \text{rel\_loss\_sum}}{\sum \text{rel\_target\_count}}, \quad \text{L}_{\text{node}} = \frac{\sum \text{node\_sq\_err\_sum}}{6 \times \sum \text{node\_target\_count}}, \quad \text{L}_{\text{time}} = \frac{\sum \text{time\_loss\_sum}}{\sum \text{time\_target\_count}}$$
     $$\text{L}_{\text{graph}} = 1.0 \times \text{L}_{\text{rel}} + 1.0 \times \text{L}_{\text{node}} + 0.1 \times \text{L}_{\text{time}}$$
     Minimum validation $\text{L}_{\text{graph}}$ is the sole criterion for early stopping and best checkpoint selection.
  3. **Partial Window & Gradient Weighting Semantics:** For the 586,577 Train events with window size 256, the 2,292 windows partition into 2,291 full windows (256 events) and 1 final partial window (81 events). Over 573 optimizer steps ($\text{grad\_accum} = 4$), Steps 1..572 have $\text{NOMINAL\_EFFECTIVE\_BATCH\_EVENTS} = 1024$, while Step 573 has $\text{FINAL\_OPTIMIZER\_STEP_EFFECTIVE_EVENTS} = 849$. Gradient scaling weights each window $k$ within an accumulation group by $N_k / N_{\text{group}}$, preventing statistical overweighting of the 81-event window while preserving mathematical consistency.
  4. **CUDA Execution Environment Lock:** Formally locks empirical execution to dedicated NVIDIA CUDA GPU hardware (`EXECUTION_DEVICE = "cuda"` on RTX 3050 Ti Laptop GPU). All Python virtual environments, pip caches, and temporary download buffers reside exclusively on drive `D:\Research`. The empirical runner enforces a fail-closed check that halts execution immediately if CUDA is unavailable or mismatched, with zero automatic CPU fallback.

---

### Amendment 11: Stage A2 Exact Multi-Task Group Objective & Canonical Training Accumulation Fix (V1.4.1)
- **Timestamp:** 2026-08-24T01:55:00+07:00
- **Execution State:** `TEST_OPENED = NO`, `RESULTS_SEEN = NO`, `REAL_HDFS_RUNS = 0`, `REAL_HDFS_OPTIMIZER_STEPS = 0`, `MODELS_TRAINED_BEFORE_AMENDMENT = 0`
- **Amends Commit:** `41d9e9eb4b2b7795f60d65d73404001c2ebeab75`
- **Reason:** Corrects canonical training accumulation in `train_one_epoch()` prior to empirical execution so that micro-batch windows are explicitly processed as accumulation groups and normalized by exact multi-task target counts rather than simple event-count proxies, ensuring that the 81-event partial window receives the exact $81/849$ temporal weight and all components ($L_{\text{rel}}$, $L_{\text{node}}$, $L_{\text{time}}$) are mathematically identical to the group objective.
- **Amended Specifications:**
  1. **Canonical Accumulation Group Structure:** In `train_one_epoch()`, chronological windows are explicitly batched into accumulation groups of up to 4 windows ($W \le 4$). Steps 1..572 accumulate 4 full windows of 256 events ($1024$ events). Step 573 accumulates 3 full windows of 256 events $+ 1$ partial window of 81 events ($849$ events).
  2. **Exact Multi-Task Group Objective:**
     Because Bernoulli relation ($p=0.15$) and node ($p=0.15$) masking generates stochastic target counts per window, event count alone is an imperfect proxy for multi-task loss normalization. The exact group objective is defined over the union of targets within the accumulation group:
     $$L_{\text{rel\_group}} = \frac{\sum_{k \in \text{group}} \text{rel\_loss\_sum}_k}{\max(1, \sum_{k \in \text{group}} \text{rel\_target\_count}_k)}$$
     $$L_{\text{node\_group}} = \frac{\sum_{k \in \text{group}} \text{node\_sq\_err\_sum}_k}{\max(1, \sum_{k \in \text{group}} \text{node\_element\_count}_k)}$$
     $$L_{\text{time\_group}} = \frac{\sum_{k \in \text{group}} \text{time\_loss\_sum}_k}{\max(1, \sum_{k \in \text{group}} \text{time\_target\_count}_k)}$$
     $$L_{\text{graph\_group}} = 1.0 \times L_{\text{rel\_group}} + 1.0 \times L_{\text{node\_group}} + 0.1 \times L_{\text{time\_group}}$$
  3. **Sequential Truncated-BPTT & Exact Group Backpropagation:**
     Windows within an accumulation group are executed sequentially to advance dynamic node memory causally ($h_v(t-)$ updates and detached memory buffers at window boundaries). Unnormalized differentiable loss sums from each window are collected, combined into $L_{\text{graph\_group}}$ using the exact group denominators, and backpropagated in a single backward pass per optimizer step, guaranteeing exact gradient alignment with zero memory leakage.
  4. **Scheduler and Data Invariants Preserved:**
     Total Train events: 586,577; Train windows: 2,292; Optimizer steps/epoch: 573; Warmup steps: 573; Max epochs: 20; Total optimizer steps: 11,460. No events dropped, padded, duplicated, or reordered.




