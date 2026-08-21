# CANONICAL EXPERIMENT MATRIX & FALSIFICATION PROTOCOL

**Document Identifier:** `MAT-EXP-20260822-V1.2`  
**Protocol Version:** 1.2.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-07`, `RC-10`, `RC-14`), Boundaries (`BOUNDARY-04`, `BOUNDARY-05`, `BOUNDARY-10`).  

---

## 1. Master Experiment Matrix & Tri-State Falsification Framework

All confirmatory hypothesis tests adhere strictly to tri-state decision semantics:
- **SUPPORTED:** Point estimate meets or exceeds pre-registered effect threshold $\Delta_{\text{target}}$ AND the 95% bootstrap confidence interval strictly excludes the null value in the pre-registered direction ($p < \alpha_{\text{adjusted}}$).
- **INCONCLUSIVE:** The 95% bootstrap confidence interval spans the null boundary or uncertainty precludes confident directionality, despite non-negative point estimates.
- **FALSIFIED:** The point estimate lies in the counter-hypothesized direction with 95% CI upper bound $\le 0$, or pre-registered catastrophic degradation thresholds are crossed.

---

### Experiment EXP-01: Parameter Semantic Fidelity Test (Mapping: RQ1, H1, Axis A1)
- **Claim:** Parameter-aware representation ($X_{\text{param}}$) preserves significantly higher security semantics than template-only abstraction.
- **Independent Variable:** Parameter representation mode (`BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4` vs `PRIMARY_PARAM_ONLY` vs `TEMPLATE_ONLY`).
- **Controlled Variables:** Sequence length ($L=128$), Model capacity (4-layer Transformer, $d=128, H=4, d_{\text{ffn}}=512$), Frozen linear probe capacity, Training split (`SPL-HDFS-001`, `SPL-DTC-001`), Canonical seeds ($K=5$).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over Block Session clusters.
- **Primary Effect Size:** Absolute $\Delta \text{Average Precision}$ ($\Delta \text{AP}$).
- **Multiple Comparisons:** Bonferroni adjustment across 4 attack subtypes ($\alpha' = 0.0125$).
- **Tri-State Decision Criteria:**
  - **Supported:** $\Delta \text{AP} \ge +0.05$ with lower 95% CI bound $> 0$.
  - **Inconclusive:** 95% CI overlaps $0$ or lower 95% CI bound $< +0.05$ while upper bound $> 0$.
  - **Falsified:** $\Delta \text{AP} \le 0$ with upper 95% CI bound $\le 0$.

---

### Experiment EXP-02: Multi-View Alignment & Negative Transfer Test (Mapping: RQ2, H2, Axis A2)
- **Claim:** Controlled cross-view alignment ($\mathbf{z}^{(\text{seq})} \leftrightarrow \mathbf{z}^{(\text{graph})}$) improves representation quality without variance collapse or negative transfer.
- **Independent Variable:** Alignment mechanism (VICReg vs InfoNCE vs Barlow Twins vs Unaligned Concat vs Single-view components).
- **Controlled Variables:** Event window ($\Delta t=15\text{m}$), Feature dimension ($d=128$), Frozen probe capacity, Test split (`SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over 15-minute provenance subgraph windows.
- **Primary Effect Size:** Absolute $\Delta \text{AP}$ and Dimensional Variance $\text{Var}(\mathbf{z})$.
- **Multiple Comparisons:** Bonferroni adjustment across 3 component comparisons ($\alpha' = 0.0167$).
- **Tri-State Decision Criteria:**
  - **Supported:** $\Delta \text{AP} \ge +0.03$ over best single-view with $\text{Var}(\mathbf{z}) \ge 0.05$ and lower 95% CI bound $> 0$.
  - **Inconclusive:** 95% CI overlaps $0$ or variance $\text{Var}(\mathbf{z}) \in [0.01, 0.05)$.
  - **Falsified:** $\text{AP}(\mathbf{z}_{\text{mv}}) < \max(\text{AP}_{\text{seq}}, \text{AP}_{\text{graph}})$ with upper 95% CI bound $\le 0$, or dimensional collapse $\text{Var}(\mathbf{z}) < 0.01$.

---

### Experiment EXP-03: Robustness Under Shortcut Removal & Distribution Shift (Mapping: RQ3, H3, Axis A3)
- **Claim:** Feature representation preserves discriminative utility after removing dataset shortcuts and under 12 perturbation attacks.
- **Independent Variable:** Telemetry condition (Clean vs Shortcut-masked vs OOV Template Holdout vs 12 Perturbations P01..P12).
- **Controlled Variables:** Pre-trained frozen extractor weights, Downstream probe capacity, Test splits (`SPL-BGL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over session chunks.
- **Primary Effect Size:** Performance retention ratio $\text{AP}_{\text{perturbed}} / \text{AP}_{\text{clean}}$ and geometric invariance distance $\|\mathbf{z}(T(X)) - \mathbf{z}(X)\|_2$.
- **Multiple Comparisons:** Benjamini-Hochberg FDR at $q^* = 0.05$ across 12 perturbations.
- **Tri-State Decision Criteria:**
  - **Supported:** Retention of $\ge 85\%$ baseline AP under semantic perturbations with significant margin over chance prevalence $\pi_0$.
  - **Inconclusive:** Retention in $[70\%, 85\%)$ with overlapping confidence intervals against lexical baseline.
  - **Falsified:** Performance collapses to positive prevalence chance level ($\text{AP} \le \pi_0$) or converges to simple lexical baseline.

---

### Experiment EXP-04: Weak Evidence Attribution & Admin Confounder Control (Mapping: Exploratory RQ4, Axis A4)
- **Claim:** Coarse bag supervision via attention MIL enables instance attribution without learning benign admin tools as malicious.
- **Independent Variable:** Supervision regime (Stage A SSL + Stage B Attention MIL vs Stage A SSL-only vs Mean-pooling MIL).
- **Controlled Variables:** Bag size ($K \in [50, 500]$), Test splits (`SPL-LANL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over host-day authentication bags.
- **Primary Effect Size:** Absolute $\Delta \text{AP}$ on red-team instances and False Positive Rate on benign admin tools.
- **Tri-State Decision Criteria:**
  - **Supported:** Instance AP exceeds mean-pooling baseline by $\ge +0.10$ with admin false positive rate $< 3.0\%$.
  - **Inconclusive:** Instance AP delta in $(0, +0.10)$ or admin false positive rate in $[3.0\%, 15.0\%]$.
  - **Falsified:** False positive rate on benign admin tools $> 15\%$ or instance attribution does not exceed mean-pooling baseline.

---

### Experiment EXP-05: Operational Streaming Complexity & Bounded State Feasibility (Mapping: Canonical H4, Axis A5)
- **Claim:** Streaming extractor meets real-time SLOs: latency $\le 10\text{ms}$ (p95), peak memory $\le 500\text{MB/host}$, throughput $\ge 10,000\text{ events/s}$.
- **Independent Variable:** Ingestion stream rate ($10^2 \dots 10^5$ events/s), Active host count ($1 \dots 1000$).
- **Controlled Variables:** Fixed workstation hardware specification.
- **Evaluation Framework:** Conjunctive Intersection-Union Test (IUT) across 3 operational SLO targets.
- **Primary Effect Size:** Absolute p95 latency (ms), Peak RAM (MiB), Throughput (events/s).
- **Tri-State Decision Criteria:**
  - **Supported:** p95 latency $\le 5.0\text{ms}$, throughput $\ge 25,000\text{ events/s}$, peak RAM $\le 250\text{MB/host}$ (All 3 SLOs simultaneously satisfied at $\alpha=0.05$).
  - **Inconclusive:** p95 latency in $(5.0\text{ms}, 10.0\text{ms}]$ or throughput in $[10,000, 25,000)\text{ events/s}$.
  - **Falsified:** p95 extraction latency $> 10\text{ms}$ or peak RAM $> 500\text{MB/host}$ or throughput $< 10,000\text{ events/s}$ under nominal stream.

---

### Experiment EXP-06: Controlled Linkability & Utility–Privacy Pareto Frontier (Mapping: RQ5, H5, Axis A5)
- **Claim:** Controlled linkability establishes a Pareto-superior Utility–Privacy trade-off compared with raw identifiers and extreme anonymization.
- **Independent Variable:** Privacy regime and privacy budget $\epsilon \in \{0.1, 0.5, 1.0, 2.0, 5.0\}$.
- **Controlled Variables:** Downstream probe capacity, Test splits (`SPL-LANL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over user-day entity subgraphs.
- **Multiple Comparisons:** Holm-Bonferroni step-down testing across 4 adversary models.
- **Primary Effect Size:** Security AP vs Absolute Adversary Advantage Reduction $\Delta \text{Adv}$.
- **Tri-State Decision Criteria:**
  - **Supported:** Controlled linkability preserves $\ge 90\%$ utility while reducing ReID accuracy by $\ge 60\%$ and MIA advantage to $< 0.05$.
  - **Inconclusive:** Utility preservation in $[75\%, 90\%)$ or ReID reduction in $[40\%, 60\%)$.
  - **Falsified:** The empirical Pareto frontier is strictly dominated by raw identifiers or complete pseudonymization.
