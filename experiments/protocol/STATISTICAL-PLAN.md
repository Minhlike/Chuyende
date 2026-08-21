# STATISTICAL ANALYSIS PLAN & HYPOTHESIS TESTING CONTRACT

**Document Identifier:** `PLAN-STAT-20260822-V1.2`  
**Protocol Version:** 1.2.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-10`), Statistical Protocol (`docs/STATISTICAL-PROTOCOL.md`).  

---

## 1. Canonical Random Seed Stability Contract

- **Training Stability Runs:** Exactly $K = 5$ independent random seeds:
  $$\mathcal{K}_{\text{canonical}} = \{42, \; 1337, \; 2024, \; 7, \; 999\}$$
- **Role of $K=5$:** Evaluates stochastic training stability, parameter initialization sensitivity, and variance dispersion (reported as $\text{Mean} \pm \text{Standard Deviation}$ alongside individual-run dispersion).
- **Inferential Scope:** The $K=5$ seeds do **NOT** serve as the inferential sampling population for hypothesis testing. No bootstrap confidence interval is computed across the 5 seeds.
- **Additional Runs:** Any additional seeds are strictly designated as `EXTENDED_REPLICATION` and reported in appendix tables.

---

## 2. Removal of Shapiro-Wilk $K=5$ Decision Gate

> **Methodological Correction:** Testing normality via Shapiro-Wilk on a sample size of $N=5$ differences suffers from severe power deficiency and produces unstable inferential branching. Therefore, the preliminary Shapiro-Wilk decision gate on seed differences is **REMOVED** from the primary confirmatory inference pipeline. Seed-level inferential tests, if computed, are strictly designated as **`[EXPLORATORY]`**.

---

## 3. Primary Confirmatory Statistical Inference: Paired Cluster Bootstrap

All primary confirmatory hypothesis testing in Chapter 3 is conducted via **Paired Cluster Bootstrap**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRIMARY PAIRED CLUSTER BOOTSTRAP INFERENCE               │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Cluster Unit Definition: Resample independent units U_1 .. U_M          │
│  2. Bootstrap Resampling: B = 2000 iterations, Seed = 10007                 │
│  3. Paired Index Constraint: In iteration b, Proposed and Baseline          │
│     are evaluated on the EXACT SAME resampled cluster indices {i_1 .. i_M}  │
│  4. Compute Delta Metric for iteration b:                                   │
│     Delta^(b) = Metric(Proposed, S^(b)) - Metric(Baseline, S^(b))           │
│  5. Compute 95% Percentile Bootstrap Confidence Interval:                   │
│     CI_95 = [ Delta*_(0.025),  Delta*_(0.975) ]                             │
│  6. Confirmatory Decision (Tri-State):                                      │
│     - SUPPORTED: Lower bound > Delta_threshold and p < alpha_adjusted       │
│     - INCONCLUSIVE: CI_95 overlaps null threshold or direction uncertain    │
│     - FALSIFIED: Point estimate <= 0 with upper bound <= 0                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Cluster Resampling Unit Audit (EXP-01..EXP-06)

To prevent severe optimistic bias caused by treating dependent log events as independent samples, every experiment defines a strict cluster resampling unit:

| Exp ID | Hypothesis / Mapping | Cluster Resampling Unit | Non-Overlap Rule | Entity Leakage Rule | Temporal Boundary Rule | Independence Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-01** | **H1 (Fidelity)** | **Block Session ID / Process Execution Tree** | Each `blk_` ID or process tree is a disjoint cluster. | Parameters from one session cannot leak into another. | Bounded by session termination timestamp. | `PROVISIONAL` (Verified at acquisition) |
| **EXP-02** | **H2 (Multi-View)** | **15-Minute Provenance Subgraph Window** | Non-overlapping consecutive 15-min time chunks. | Edges crossing time chunk boundaries are handled via causal state snapshots. | Event-time watermark strictly enforced. | `PROVISIONAL` |
| **EXP-03** | **H3 (Robustness)** | **Perturbed Telemetry Session Chunk** ($L=128$) | Independent session chunks partitioned before perturbation. | Perturbation operators applied strictly within cluster. | No inter-chunk event reordering. | `PROVISIONAL` |
| **EXP-04** | **RQ4 (MIL Attribution)** | **Host-Day Authentication Bag** $\mathcal{B}_{h, d}$ | Disjoint host-day units ($h \in \mathcal{H}, d \in \mathcal{D}$). | User authentications across different days treated as distinct bags. | Daily 00:00:00–23:59:59 UTC boundary. | `PROVISIONAL` |
| **EXP-05** | **H4 (Operational Budget)** | **5-Minute Operational Streaming Segment** | Consecutive non-overlapping 5-minute operational stream segments. | Memory state measured independently per segment. | Segment boundaries strictly ordered in causal time. | `PROVISIONAL` |
| **EXP-06** | **H5 (Privacy)** | **User-Day Entity Subgraph** | Disjoint user-day interaction clusters. | Linkage adversary evaluated across disjoint session pairs. | Session rotation boundary enforced. | `PROVISIONAL` |

*Invariant:* Event rows within the same cluster are never resampled independently.

---

## 5. Effect-Size Specification Contract

Effect sizes are defined hierarchically based on metric characteristics:

| Metric Category | Target Metrics | Primary Effect Size | Secondary Effect Size |
| :--- | :--- | :--- | :--- |
| **Detection Performance** | Average Precision (AP), Macro-F1, Recall@0.1% FPR | **Absolute $\Delta$** ($\Delta = \text{Score}_{\text{proposed}} - \text{Score}_{\text{baseline}}$) | Relative $\Delta$ percentage ($\frac{\Delta}{\text{Score}_{\text{base}}} \times 100\%$) |
| **Operational Latency** | p50, p95, p99 Latency (ms) | **Absolute $\Delta\text{ ms}$** ($\Delta t = t_{\text{proposed}} - t_{\text{baseline}}$) | Latency Ratio ($\frac{t_{\text{proposed}}}{t_{\text{baseline}}}$) |
| **Memory / State Size** | Peak RAM, State Size (MiB) | **Absolute $\Delta\text{ MiB}$** ($\Delta M = M_{\text{proposed}} - M_{\text{baseline}}$) | Compression Ratio ($\frac{M_{\text{proposed}}}{M_{\text{baseline}}}$) |
| **Privacy Attack Resistance** | ReID Top-1 Acc, MIA Advantage, Linkage AUC | **Absolute Advantage Reduction** ($\Delta\text{Adv} = \text{Adv}_{\text{raw}} - \text{Adv}_{\text{priv}}$) | Relative Risk Reduction |

---

## 6. Pre-Registered Multiple Comparisons Policy

| Hypothesis Family | Scope | Mandatory Policy | Decision Rule |
| :--- | :--- | :--- | :--- |
| **Family 1 (H1 — Fidelity)** | 4 dynamic parameter attack subtypes (SQLi, Command Injection, Path Traversal, Port Scan). | **Bonferroni Adjustment** | Adjusted significance level $\alpha' = \frac{0.05}{4} = 0.0125$. |
| **Family 2 (H2 — Multi-View)** | 3 pairwise component tests (Multi-View vs Seq-only, Multi-View vs Graph-only, Multi-View vs Unaligned). | **Bonferroni Adjustment** | Adjusted significance level $\alpha' = \frac{0.05}{3} = 0.0167$. |
| **Family 3 (H3 — Robustness)** | 12 perturbation operators (P01..P12). | **Benjamini-Hochberg FDR** | Target False Discovery Rate $q^* = 0.05$. |
| **Family 4 (H4 — Operational)** | 3 conjunctive SLO targets (Latency $\le 10\text{ ms} \land \text{RAM} \le 500\text{ MB} \land \text{Throughput} \ge 10^4$). | **Intersection-Union Test (IUT)** | Strict conjunctive compliance (all must pass at $\alpha = 0.05$, no $p$-value hunting). |
| **Family 5 (H5 — Privacy)** | 4 adversary leakage models ($\mathcal{A}_{\text{ReID}}, \mathcal{A}_{\text{Link}}, \mathcal{A}_{\text{MIA}}, \mathcal{A}_{\text{Inv}}$). | **Holm-Bonferroni Step-Down** | Sequential step-down testing across 4 adversary models. |
| **Exploratory Analyses** | Sub-population slicing, parameter sweeps, post-hoc ablation. | **Benjamini-Yekutieli FDR** | Must be explicitly labeled **`[EXPLORATORY]`**. |
