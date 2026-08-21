# CANONICAL EXPERIMENT MATRIX & FALSIFICATION PROTOCOL

**Document Identifier:** `MAT-EXP-20260821-V1.1`  
**Protocol Version:** 1.1.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-07`, `RC-10`, `RC-14`), Boundaries (`BOUNDARY-04`, `BOUNDARY-05`, `BOUNDARY-10`).  

---

## 1. Master Experiment Matrix

### Experiment EXP-01: Parameter Semantic Fidelity Test (Mapping: RQ1, H1, Axis A1)
- **Claim:** Parameter-aware representation ($X_{\text{param}}$) preserves significantly higher security semantics than template-only abstraction.
- **Independent Variable:** Parameter representation mode (Full Subword Parameter Embedding vs Template-only vs Template+Wildcard).
- **Controlled Variables:** Sequence length ($L=100$), Model capacity (6-layer Transformer, $d=256$), Frozen linear probe capacity, Training split (`SPL-HDFS-001`, `SPL-DTC-001`), Canonical seeds ($K=5$).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over Block Session clusters.
- **Primary Effect Size:** Absolute $\Delta \text{PR-AUC}$.
- **Multiple Comparisons:** Bonferroni adjustment across 4 attack subtypes ($\alpha' = 0.0125$).
- **Failure Criterion (Falsified):** 95% Bootstrap CI of $\Delta \text{PR-AUC}$ includes 0 ($p > 0.0125$).
- **Supported Criterion:** $\Delta \text{PR-AUC} \ge +0.05$ with lower 95% CI bound $> 0$.

---

### Experiment EXP-02: Multi-View Alignment & Negative Transfer Test (Mapping: RQ2, H2, Axis A2)
- **Claim:** Controlled cross-view alignment ($\mathbf{z}^{(\text{seq})} \leftrightarrow \mathbf{z}^{(\text{graph})}$) improves representation quality without variance collapse or negative transfer.
- **Independent Variable:** Alignment mechanism (InfoNCE vs VICReg vs Barlow Twins vs Unaligned Concat vs Single-view components).
- **Controlled Variables:** Event window ($\Delta t=15\text{m}$), Feature dimension ($d=256$), Frozen probe capacity, Test split (`SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over 15-minute provenance subgraph windows.
- **Primary Effect Size:** Absolute $\Delta \text{PR-AUC}$ and Dimensional Variance $\text{Var}(\mathbf{z})$.
- **Multiple Comparisons:** Bonferroni adjustment across 3 component comparisons ($\alpha' = 0.0167$).
- **Failure Criterion (Falsified):** $\text{PR-AUC}(\mathbf{z}_{\text{mv}}) < \max(\text{PR-AUC}_{\text{seq}}, \text{PR-AUC}_{\text{graph}})$ or $\text{Var}(\mathbf{z}) < 0.01$.
- **Supported Criterion:** $\Delta \text{PR-AUC} \ge +0.03$ over best single-view with $\text{Var}(\mathbf{z}) \ge 0.05$.

---

### Experiment EXP-03: Robustness Under Shortcut Removal & Distribution Shift (Mapping: RQ3, H3, Axis A3)
- **Claim:** Feature representation preserves discriminative utility after removing dataset shortcuts and under 12 perturbation attacks.
- **Independent Variable:** Telemetry condition (Clean vs Shortcut-masked vs OOV Template Holdout vs 12 Perturbations P01..P12).
- **Controlled Variables:** Pre-trained frozen extractor weights, Downstream probe capacity, Test splits (`SPL-BGL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over session chunks.
- **Primary Effect Size:** Absolute performance retention $\text{PR-AUC}_{\text{perturbed}} / \text{PR-AUC}_{\text{clean}}$ and geometric invariance distance $\|\mathbf{z}(T(X)) - \mathbf{z}(X)\|_2$.
- **Multiple Comparisons:** Benjamini-Hochberg FDR at $q^* = 0.05$ across 12 perturbations.
- **Failure Criterion (Falsified):** Performance collapses to random guessing (PR-AUC $\le 0.50$) or converges to simple lexical baseline.
- **Supported Criterion:** Retention of $\ge 85\%$ baseline PR-AUC under semantic perturbations with significant margin over lexical baselines.

---

### Experiment EXP-04: Weak Evidence Attribution & Admin Confounder Control (Mapping: RQ4, Axis A4)
- **Claim:** Coarse bag supervision via attention MIL enables instance attribution without learning benign admin tools as malicious.
- **Independent Variable:** Supervision regime (Stage A SSL + Stage B Attention MIL vs Stage A SSL-only vs Mean-pooling MIL).
- **Controlled Variables:** Bag size ($K \in [50, 500]$), Test splits (`SPL-LANL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over host-day authentication bags.
- **Primary Effect Size:** Absolute $\Delta \text{PR-AUC}$ on red-team instances and False Positive Rate on benign admin tools.
- **Failure Criterion (Falsified):** False positive rate on benign admin tools $> 15\%$ or instance attribution does not exceed mean-pooling baseline.
- **Supported Criterion:** Instance PR-AUC exceeds mean-pooling by $\ge +0.10$ with admin false positive rate $< 3.0\%$.

---

### Experiment EXP-05: Operational Streaming Complexity & Bounded State Feasibility (Mapping: H4, Axis A5)
- **Claim:** Streaming extractor meets real-time SLOs: latency $\le 10\text{ms}$ (p95), peak memory $\le 500\text{MB/host}$, throughput $\ge 10,000\text{ events/s}$.
- **Independent Variable:** Ingestion stream rate ($10^2 \dots 10^5$ events/s), Active host count ($1 \dots 1000$).
- **Controlled Variables:** Fixed workstation hardware specification.
- **Evaluation Framework:** Conjunctive Intersection-Union Test (IUT) across SLO targets.
- **Primary Effect Size:** Absolute p95 latency (ms), Peak RAM (MiB), Throughput (events/s).
- **Failure Criterion (Falsified):** p95 extraction latency $> 10\text{ms}$ or peak RAM $> 500\text{MB/host}$ under nominal throughput.
- **Supported Criterion:** p95 latency $\le 5.0\text{ms}$, throughput $\ge 25,000\text{ events/s}$, peak RAM $\le 250\text{MB/host}$.

---

### Experiment EXP-06: Controlled Linkability & Utility–Privacy Pareto Frontier (Mapping: RQ5, H5, Axis A5)
- **Claim:** Controlled linkability establishes a Pareto-superior Utility–Privacy trade-off compared with raw identifiers and extreme anonymization.
- **Independent Variable:** Privacy regime and privacy budget $\epsilon \in \{0.1, 0.5, 1.0, 2.0, 5.0\}$.
- **Controlled Variables:** Downstream probe capacity, Test splits (`SPL-LANL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over user-day entity subgraphs.
- **Multiple Comparisons:** Holm-Bonferroni step-down testing across 4 adversary models.
- **Primary Effect Size:** Security PR-AUC vs Absolute Adversary Advantage Reduction $\Delta \text{Adv}$.
- **Failure Criterion (Falsified):** The empirical Pareto frontier is strictly dominated by raw identifiers or complete pseudonymization.
- **Supported Criterion:** Controlled linkability preserves $\ge 90\%$ utility while reducing ReID accuracy by $\ge 60\%$ and MIA advantage to $< 0.05$.
