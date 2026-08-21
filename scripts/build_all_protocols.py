# -*- coding: utf-8 -*-
"""
Master Protocol Suite Builder for Chapter 3 Pre-Registration
Generates all canonical protocol files in D:\Research\experiments\protocol\
"""

import os
import sys
import yaml
import json
from pathlib import Path

def main():
    protocol_dir = Path(r"D:\Research\experiments\protocol")
    protocol_dir.mkdir(parents=True, exist_ok=True)
    print(f"Generating Protocol Suite in {protocol_dir}...")

    # -------------------------------------------------------------------------
    # 4. EXPERIMENT-MATRIX.md
    # -------------------------------------------------------------------------
    exp_matrix = """# CANONICAL EXPERIMENT MATRIX & FALSIFICATION PROTOCOL

**Document Identifier:** `MAT-EXP-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-07`, `RC-10`, `RC-14`), Boundaries (`BOUNDARY-04`, `BOUNDARY-05`, `BOUNDARY-10`).  

---

## 1. Epistemological Framework & Falsification Matrix

The experiment matrix maps every Research Question (RQ1–RQ5) and Hypothesis (H1–H5) to rigorous, falsifiable experimental tests. In strict accordance with Karl Popper's falsification criterion and Research Boundary `BOUNDARY-10`, **no hypothesis is formulated to force the proposed method to win**. Negative results, empirical refutations, and benchmark bounds are recognized as primary scientific contributions.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SCIENTIFIC HYPOTHESIS TESTING FLOW                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  HYPOTHESIS (H1..H5) ──► INDEPENDENT VARIABLE MANIPULATION                  │
│                                │                                            │
│                                ▼                                            │
│                 CONTROLLED CAPACITY-FROZEN PROBE                            │
│                                │                                            │
│            ┌───────────────────┴───────────────────┐                        │
│            ▼                                       ▼                        │
│   FAILS CRITERIA (p > 0.05)             MEETS FALSIFICATION CRITERIA        │
│   ──► [HYPOTHESIS FALSIFIED]            ──► [HYPOTHESIS SUPPORTED]          │
│   ──► Valid Scientific Asset            ──► Empirical Evidence Established  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master Experiment Matrix

### Experiment EXP-01: Parameter Semantic Fidelity Test (Mapping: RQ1, H1, Axis A1)

| Specification Field | Formulation |
| :--- | :--- |
| **Scientific Claim** | Dynamic parameter-aware embedding ($X_{\\text{param}}$: paths, command args, IPs) preserves significantly higher security semantics $\\mathcal{I}(\\mathbf{z}; Y_{\\text{sec}})$ than template-only abstraction ($X_{\\text{abstracted}}$). |
| **Independent Variable** | Parameter representation mode: 1) Full Subword Parameter Embedding (Ours); 2) Static Template ID only (Drain/Spell); 3) Template + Positional Wildcards; 4) Parameter Truncation (first 16 bytes). |
| **Controlled Variables** | Sequence length ($L=100$), Model capacity (6-layer Transformer, $d=256$, 8 heads), Frozen linear probe capacity, Training split (`SPL-HDFS-001`, `SPL-DTC-001`), Random seed ($K=5$). |
| **Dependent Metrics** | 1) Dynamic parameter attack PR-AUC (SQLi, path traversal, port scanning); 2) Parameter attribution accuracy; 3) Mutual information lower-bound estimator $\\hat{\\mathcal{I}}(\\mathbf{z}; Y_{\\text{sec}})$. |
| **Primary Baselines** | Drain-parsed LogBERT (template-only); DeepLog (template-sequence); TF-IDF on tokenized raw logs. |
| **Ablation Variants** | Proposed Transformer without subword tokenizer; Proposed Transformer with masked parameter objective disabled ($\\lambda_{\\text{param}} = 0$). |
| **Positive Control** | Oracle raw un-parsed text embedding with large language model (frozen Llama/DeBERTa feature extractor). |
| **Negative / Shortcut Control** | Parameter Shuffled Control: random permutation of dynamic parameters across concurrent sessions to break true binding. |
| **Failure Criterion (Falsified)** | Frozen probe PR-AUC on dynamic parameter attacks does not exceed template-only baseline by statistical significance ($p > 0.05$, paired $t$-test across 5 seeds, or Hedges' $g < 0.20$). |
| **Supported Criterion** | Statistically significant PR-AUC gain ($\\Delta \\text{PR-AUC} \\ge +0.05$, $p < 0.01$, Hedges' $g \\ge 0.80$) on dynamic parameter attack detection over template-only baselines. |
| **Partially-Supported Criterion** | Significant gain on command-line parameter attacks but insignificant difference on IP/port address parameters. |

---

### Experiment EXP-02: Multi-View Alignment & Negative Transfer Test (Mapping: RQ2, H2, Axis A2)

| Specification Field | Formulation |
| :--- | :--- |
| **Scientific Claim** | Cross-view alignment ($\\mathbf{z}^{(\\text{seq})} \\leftrightarrow \\mathbf{z}^{(\\text{graph})}$) improves multi-stage APT representation quality without representation variance collapse or destructive negative transfer. |
| **Independent Variable** | Latent alignment objective: 1) InfoNCE Contrastive; 2) VICReg (Variance-Invariance-Covariance); 3) Barlow Twins; 4) Unaligned Concatenation ($\\lambda_3 = 0$); 5) Single-view Sequence-only; 6) Single-view Graph-only. |
| **Controlled Variables** | Event time window ($\\Delta t = 15\\text{m}$), Embedding dimension ($d_{\\text{seq}}=128, d_{\\text{graph}}=128, d_{\\text{out}}=256$), Downstream probe capacity, Test split (`SPL-DTC-001`). |
| **Dependent Metrics** | 1) Multi-stage APT detection PR-AUC & Macro-F1; 2) Representation variance $\\text{Var}(\\mathbf{z})$ across embedding dimensions; 3) Cross-view mutual information $\\mathcal{I}(\\mathbf{z}; X_{\\text{view}})$; 4) Effective rank $\\text{erank}(\\mathbf{Z})$. |
| **Primary Baselines** | Single-view Sequential Transformer; Single-view Temporal GNN; Unaligned Feature Concatenation; KAIROS provenance baseline. |
| **Ablation Variants** | Multi-view with variance regularization removed ($\\lambda_{\\text{var}} = 0$); Multi-view with covariance regularization removed ($\\lambda_{\\text{cov}} = 0$). |
| **Positive Control** | Monolithic Joint Graph-Transformer with all-to-all cross-attention (unbounded computation upper bound). |
| **Negative / Shortcut Control** | Cross-view Mismatch Control: pairing sequential logs from Host A with provenance graphs from Host B during alignment. |
| **Failure Criterion (Falsified)** | Aligned representation exhibits lower PR-AUC than the best single-view ($\\text{PR-AUC}(\\mathbf{z}) < \\max(\\text{PR-AUC}_{\\text{seq}}, \\text{PR-AUC}_{\\text{graph}})$) or experiences variance collapse ($\\text{Var}(\\mathbf{z}) < \\tau_{\\text{var}} = 0.01$). |
| **Supported Criterion** | $\\text{PR-AUC}(\\mathbf{z}) > \\max(\\text{PR-AUC}_{\\text{seq}}, \\text{PR-AUC}_{\\text{graph}}) + 0.03$ with $p < 0.01$, while maintaining stable variance ($\\text{Var}(\\mathbf{z}) \\ge 0.05$) and effective rank $\\text{erank}(\\mathbf{Z}) \\ge 0.60 \\times d$. |
| **Partially-Supported Criterion** | Superior overall PR-AUC, but exhibiting negative transfer on specific isolated single-process sub-scenarios. |

---

### Experiment EXP-03: Robustness Under Shortcut Removal & Distribution Shift (Mapping: RQ3, H3, Axis A3)

| Specification Field | Formulation |
| :--- | :--- |
| **Scientific Claim** | Feature representation $\\mathbf{z}$ preserves attack discriminative utility after removing dataset shortcuts (host/path/executable identifiers) and under temporal/distribution drift. |
| **Independent Variable** | Telemetry condition: 1) Clean logs; 2) Shortcut-masked logs (masking host, absolute path, process names); 3) Unseen template OOV holdout; 4) 12 pre-registered perturbation attacks (renaming, jitter, insertion, suppression). |
| **Controlled Variables** | Pre-trained extractor weights (frozen), Probe architecture, Seed distribution, Test split partitions (`SPL-BGL-001`, `SPL-DTC-001`). |
| **Dependent Metrics** | 1) $\\Delta \\text{PR-AUC}$ performance degradation; 2) Geometric representation invariance distance $\\|\\mathbf{z}(T(X)) - \\mathbf{z}(X)\\|_2$; 3) Mutual information with shortcut variables $\\mathcal{I}(\\mathbf{z}; S)$. |
| **Primary Baselines** | Simple Lexical / Path / Process-Name Shortcut Classifier; Event-count TF-IDF; DeepLog; Standard LogBERT. |
| **Ablation Variants** | Proposed extractor trained without shortcut exclusion regularizer ($\\lambda_5 = 0$). |
| **Positive Control** | Shortcut-dependent overfitted classifier explicitly trained on environment identifiers (demonstrating catastrophic collapse when identifiers change). |
| **Negative / Shortcut Control** | Adversarial identifier swapping: executing benign tasks with attacker names and attack payloads with `svchost.exe` / `systemd` names. |
| **Failure Criterion (Falsified)** | Under shortcut masking or semantic perturbations, representation PR-AUC drops to random guessing (PR-AUC $\\le 0.50$) or converges to simple lexical baseline performance. |
| **Supported Criterion** | Retention of $\\ge 85\\%$ of clean-split PR-AUC under shortcut masking and semantic perturbations, with significant margin over lexical baselines ($p < 0.001$, Hedges' $g \\ge 1.20$). |
| **Partially-Supported Criterion** | Robust against syntactic renaming and timestamp jitter, but exhibiting $> 20\\%$ performance degradation under severe telemetry suppression ($> 30\\%$ missing events). |

---

### Experiment EXP-04: Weak Evidence Attribution & Admin Confounder Control (Mapping: RQ4, Axis A4)

| Specification Field | Formulation |
| :--- | :--- |
| **Scientific Claim** | Coarse bag-level supervision via attention Multiple Instance Learning (Stage B) enables fine-grained event evidence attribution without misclassifying benign administrative actions as malicious. |
| **Independent Variable** | Supervision & attribution regime: 1) Stage A SSL + Stage B Attention MIL (Ours); 2) Stage A SSL-only zero-shot distance; 3) Standard Mean-pooling MIL; 4) Fully-supervised instance classifier (Oracle). |
| **Controlled Variables** | Bag size ($K \\in [50, 500]$ events), Administrative activity ratio in test stream (10%–50% background admin tools), Test split (`SPL-LANL-001`, `SPL-DTC-001`). |
| **Dependent Metrics** | 1) Fine-grained instance-level PR-AUC on red-team events; 2) False Positive Rate on benign administrative tools (PowerShell, PsExec, ssh, cron); 3) Attribution Subgraph Compactness (QoA). |
| **Primary Baselines** | Mean-pooling Bag Classifier; Isolation Forest on raw event counts; Stage A SSL distance baseline. |
| **Ablation Variants** | Attention MIL without entropy sparsity regularizer; MIL without administrative confounder penalty. |
| **Positive Control** | Instance-supervised Oracle classifier trained with perfect ground-truth event annotations. |
| **Negative / Shortcut Control** | Majority Bag-label propagation: assigning bag-level label uniformly to every contained instance. |
| **Failure Criterion (Falsified)** | False positive rate on benign administrative operations exceeds 15%, or instance-level attribution PR-AUC does not exceed mean-pooling baseline ($p > 0.05$). |
| **Supported Criterion** | Instance-level PR-AUC exceeds mean-pooling baseline by $\\ge +0.10$ ($p < 0.01$), while maintaining benign administrative false positive rate $< 3.0\\%$. |
| **Partially-Supported Criterion** | High instance attribution PR-AUC on attacks, but administrative false positive rate falls between $3.0\\%$ and $8.0\\%$. |

---

### Experiment EXP-05: Operational Streaming Complexity & Bounded State Feasibility (Mapping: H4, Axis A5)

| Specification Field | Formulation |
| :--- | :--- |
| **Scientific Claim** | Streaming feature extractor meets strict real-time operational SLOs: per-event processing latency $\\le 10\\text{ ms}$ (p95), peak memory $\\le 500\\text{ MB/host}$, and throughput $\\ge 10,000\\text{ events/s}$. |
| **Independent Variable** | Telemetry ingestion rate ($10^2 \\dots 10^5$ events/s), Active host count ($1 \\dots 1000$), State eviction policy (LRU, TTL decay, Count-Min Sketch). |
| **Controlled Variables** | Standard benchmark workstation hardware (Intel Xeon/Core i9, 64GB RAM, NVIDIA RTX 4090/A5000), Fixed sliding window size ($\\Delta t$). |
| **Dependent Metrics** | 1) Per-event extraction latency (p50, p95, p99 in ms); 2) Ingestion throughput (events/s); 3) Peak RAM & Steady-state RAM (MB); 4) GPU VRAM (MB); 5) Bounded state size $|\\mathcal{S}_t|$. |
| **Primary Baselines** | Full-history Unbounded Graph Store; Standard PyG Temporal GNN without state eviction; Un-windowed Transformer. |
| **Ablation Variants** | Proposed streaming pipeline with state compaction disabled; Pipeline with TTL eviction disabled. |
| **Positive Control** | Stateless single-event parser (minimal computational latency upper-bound on throughput). |
| **Negative / Shortcut Control** | Naive memory accumulation: appending all history into an in-memory list without pruning (demonstrating Out-Of-Memory crashes). |
| **Failure Criterion (Falsified)** | p95 extraction latency exceeds $10\\text{ ms}$ per event or peak memory per monitored host exceeds $500\\text{ MB}$ under nominal operational throughput ($10,000$ events/s). |
| **Supported Criterion** | p95 extraction latency $\\le 5.0\\text{ ms}$, throughput $\\ge 25,000\\text{ events/s}$, peak memory $\\le 250\\text{ MB/host}$, and zero OOM memory leaks over 72-hour continuous stream. |
| **Partially-Supported Criterion** | Meets throughput and memory limits, but p95 latency falls between $5.0\\text{ ms}$ and $10.0\\text{ ms}$. |

---

### Experiment EXP-06: Controlled Linkability & Utility–Privacy Pareto Frontier (Mapping: RQ5, H5, Axis A5)

| Specification Field | Formulation |
| :--- | :--- |
| **Scientific Claim** | Controlled linkability (keyed entity hashing + bounded differential privacy noise) establishes a Pareto-superior Utility–Privacy trade-off compared with both raw identifiers and extreme anonymization. |
| **Independent Variable** | Privacy mechanism & budget: 1) Raw Identifiers ($\\epsilon = \\infty$); 2) Full Pseudonymization / Token Suppression ($\\epsilon \\to 0$); 3) Controlled Linkability with varying privacy budgets $\\epsilon \\in \\{0.1, 0.5, 1.0, 2.0, 5.0\\}$. |
| **Controlled Variables** | Extractor architecture, Downstream probe capacity, Test split (`SPL-LANL-001`, `SPL-DTC-001`), Adversary computational budget ($10^5$ attack queries). |
| **Dependent Metrics** | 1) Security Utility (Macro-F1, PR-AUC); 2) Re-identification Top-1 / Top-5 Accuracy; 3) Linkage AUC; 4) Membership Inference Advantage ($\\text{TPR} - \\text{FPR}$); 5) Inversion String Reconstruction Rate. |
| **Primary Baselines** | Raw Identifier Baseline; Naive Pseudonymization (salted SHA-256); Complete Entity Token Dropping. |
| **Ablation Variants** | Keyed pseudonymization without differential privacy noise; DP noise injection without structured entity keying. |
| **Positive Control** | Exact Identity Oracle (maximum utility, maximum privacy loss). |
| **Negative Control** | Pure Random Noise Injection (zero privacy leakage, zero security utility). |
| **Failure Criterion (Falsified)** | The empirical Utility–Privacy Pareto frontier is strictly dominated by raw identifiers or complete pseudonymization (i.e. controlled linkability provides no point of superior utility at equal privacy risk). |
| **Supported Criterion** | Controlled linkability ($\\epsilon = 1.0$) preserves $\\ge 90\\%$ of raw security utility (PR-AUC) while reducing ReID accuracy by $\\ge 60\\%$ and MIA advantage to $< 0.05$. |
| **Partially-Supported Criterion** | Pareto frontier is non-dominated, but privacy protection gain over salted pseudonymization is marginal ($< 15\\%$ risk reduction). |
"""
    (protocol_dir / "EXPERIMENT-MATRIX.md").write_text(exp_matrix, encoding="utf-8")
    print("[OK] Wrote EXPERIMENT-MATRIX.md")

    # -------------------------------------------------------------------------
    # 5. METRIC-CONTRACT.md
    # -------------------------------------------------------------------------
    metric_contract = """# THREE-LAYER EVALUATION METRIC CONTRACT & VALIDATION-ONLY CALIBRATION

**Document Identifier:** `CON-METRIC-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-08`, `RC-10`), Roadmap Boundary (`BOUNDARY-04`, `BOUNDARY-08`).  

---

## 1. Three-Layer Evaluation Architecture

To prevent downstream detector artifacts from masquerading as representation quality (`BOUNDARY-04`), the evaluation suite is organized into three strictly decoupled layers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THREE-LAYER EVALUATION HIERARCHY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: INTRINSIC REPRESENTATION METRICS                                   │
│ - Representation Variance & Collapse Diagnostics (Var, Cov, Effective Rank)│
│ - Cross-View Latent Alignment & Mutual Information Proxy                    │
│ - Temporal & Entity Continuity Preservation                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: CAPACITY-CONTROLLED FROZEN PROBE BENCHMARKS                        │
│ - Extractor Weights Completely Frozen (theta*)                              │
│ - Fixed Probes: Linear Probe, Logistic Regression, Distance/kNN, Shallow MLP│
│ - Supervised MITRE ATT&CK Tactic/Technique Multi-Label Classification       │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: OPERATIONAL & STREAMING DEPLOYABILITY METRICS                      │
│ - Precision, Recall, Macro-F1, PR-AUC, ROC-AUC, FPR                         │
│ - Recall @ Fixed FPR (0.1%, 1.0%) & Recall @ Alert Budget (e.g. 10/day)     │
│ - Detection Delay, Ingestion Throughput (events/s), Latency (p50/p95/p99)   │
│ - Peak RAM, Steady-State RAM, VRAM, and Bounded State Size |S_t|            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer 1 — Intrinsic Representation Metrics

These metrics assess geometry, diversity, and alignment of the latent manifold $\\mathbf{z} \\in \\mathbb{R}^d$ without requiring downstream class labels:

1. **Representation Variance (Collapse Indicator):**
   $$\\text{Var}(\\mathbf{Z}) = \\frac{1}{d} \\sum_{j=1}^d \\text{Var}(\\mathbf{z}_{:, j}) = \\frac{1}{d} \\sum_{j=1}^d \\left( \\frac{1}{N} \\sum_{i=1}^N (z_{i, j} - \\bar{z}_j)^2 \\right)$$
   *Threshold:* $\\text{Var}(\\mathbf{Z}) \\ge \\tau_{\\text{var}} = 0.05$ (Fail if $< 0.01$, indicating dimensional collapse).

2. **Effective Dimensional Rank (Covariance Condition):**
   $$\\text{erank}(\\mathbf{Z}) = \\exp\\left( - \\sum_{k=1}^d p_k \\ln p_k \\right), \\quad p_k = \\frac{\\sigma_k(\\mathbf{Z})}{\\sum_{j=1}^d \\sigma_j(\\mathbf{Z})}$$
   Where $\\sigma_k(\\mathbf{Z})$ are the singular values of the centered feature matrix $\\mathbf{Z}$. Measures the effective number of utilized orthogonal dimensions (Fail if $< 0.20 \\times d$).

3. **Cross-View Latent Alignment Consistency:**
   $$\\text{Align}(\\mathbf{z}^{(\\text{seq})}, \\mathbf{z}^{(\\text{graph})}) = \\frac{1}{N} \\sum_{i=1}^N \\frac{\\langle \\mathbf{z}_i^{(\\text{seq})}, \\mathbf{z}_i^{(\\text{graph})} \\rangle}{\\|\\mathbf{z}_i^{(\\text{seq})}\\|_2 \\|\\mathbf{z}_i^{(\\text{graph})}\\|_2}$$

4. **Temporal Stability Invariance:**
   $$\\text{Stab}(\\mathbf{z}) = \\frac{1}{N-1} \\sum_{t=1}^{N-1} \\|\\mathbf{z}_{t+1} - \\mathbf{z}_t\\|_2$$

---

## 3. Layer 2 — Capacity-Controlled Frozen Probes

To evaluate representation utility independently of downstream detector learning capacity:

1. **Extractor Freezing Contract:**
   $$\\theta^* = \\text{freeze}(f_\\theta), \\quad \\nabla_{\\theta} \\mathcal{L}_{\\text{probe}} \\equiv \\mathbf{0}$$
   The extractor parameters $\\theta^*$ are immutable during all Layer 2 evaluations.

2. **Probe Architectures:**
   - **Linear / Logistic Probe:** $\\hat{\\mathbf{y}} = \\sigma(\\mathbf{W}^\\top \\mathbf{z} + \\mathbf{b})$ (Zero hidden layers, parameter budget $\\le d \\times C$).
   - **Non-Parametric Distance Probe / kNN:** $k=5$, cosine distance to normal support library.
   - **Shallow MLP Probe (Optional Pre-Registered):** 1 hidden layer ($h=128$), ReLU activation, strictly bounded capacity.

---

## 4. Layer 3 — Operational & Security Performance Metrics

1. **Core Classification Metrics:**
   $$\\text{Precision} = \\frac{\\text{TP}}{\\text{TP} + \\text{FP}}, \\quad \\text{Recall} = \\frac{\\text{TP}}{\\text{TP} + \\text{FN}}, \\quad F_1 = \\frac{2 \\cdot \\text{Precision} \\cdot \\text{Recall}}{\\text{Precision} + \\text{Recall}}$$
   $$\\text{PR-AUC} = \\int_0^1 P(R) \\, dR, \\quad \\text{FPR} = \\frac{\\text{FP}}{\\text{FP} + \\text{TN}}$$

2. **Security SOC Constraints:**
   - **Recall@Fixed-FPR:** $\\text{Recall}_{\\text{FPR} \\le 0.1\\%}$ (Crucial for minimizing alert fatigue in high-volume enterprise streams).
   - **Recall@Alert-Budget:** Recall achieved when daily alert generation is constrained to $\\le K_{\\text{budget}}$ alerts/host-day (e.g. $K=10$).

3. **Operational Streaming Metrics:**
   - **Detection Delay ($\\Delta t_{\\text{detect}}$):** Time delta between the first malicious event $e_{\\text{first}}$ in an APT campaign and the first generated alert $\\hat{y} \\ge \\tau$.
   - **Throughput:** Processed events per wall-clock second ($\\text{events/s}$).
   - **Processing Latency:** Per-event processing time percentiles: p50, p95, p99 (measured in milliseconds).
   - **State Memory Consumption:** Peak RAM, Steady-State RAM, and GPU VRAM (MB) over long-horizon streaming ($> 72$ hours).

---

## 5. Validation-Only Decision Threshold & Calibration Contract

To eliminate threshold peeking and optimistic performance inflation:

1. **Threshold Fitting Protocol:**
   $$\\tau^* = \\arg\\max_{\\tau \\in [0, 1]} F_1(\\tau; \\mathcal{D}_{\\text{val}}) \\quad \\text{or} \\quad \\tau^* = \\min \\{ \\tau \\mid \\text{FPR}(\\tau; \\mathcal{D}_{\\text{val}}) \\le \\alpha_{\\text{target}} \\}$$
   The optimal decision threshold $\\tau^*$ is selected strictly on the Validation split.

2. **Probability Calibration:**
   Platt scaling (logistic regression on logits) or Isotonic Regression parameters are fit strictly on $\\mathcal{D}_{\\text{val}}$.

3. **Sealed Test Evaluation:**
   $$\\hat{y}_{\\text{test}} = \\mathbb{I}[\\text{Calibrate}(\\text{Score}(\\mathbf{z}_{\\text{test}})) \\ge \\tau^*]$$
   The threshold $\\tau^*$ is applied unconditionally to $\\mathcal{D}_{\\text{test}}$ without any post-hoc adjustment.
"""
    (protocol_dir / "METRIC-CONTRACT.md").write_text(metric_contract, encoding="utf-8")
    print("[OK] Wrote METRIC-CONTRACT.md")

    # -------------------------------------------------------------------------
    # 6. BASELINE-FAIRNESS.md
    # -------------------------------------------------------------------------
    baseline_fairness = """# BASELINE TAXONOMY & EXPERIMENTAL FAIRNESS CONTRACT

**Document Identifier:** `CON-FAIR-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-06`, `RC-10`), Roadmap Boundary (`BOUNDARY-05`).  

---

## 1. Baseline Taxonomy Hierarchy

To rule out benchmark artifacts, superficial lexical shortcuts, and ensure genuine scientific comparability (`BOUNDARY-05`), all comparative evaluations must include four distinct baseline groups:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BASELINE TAXONOMY MATRIX                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ GROUP A: SIMPLE & SHORTCUT BASELINES                                        │
│ - Event Frequency / Count Vectors                                           │
│ - TF-IDF on Tokenized Raw Logs                                              │
│ - Lexical Shortcut Baseline (Process Name / File Path Bag-of-Words)         │
│ - Pure Novelty / Out-of-Vocabulary Frequency Classifier                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ GROUP B: SEQUENTIAL & DEEP LOG BASELINES                                    │
│ - DeepLog (LSTM on Template Indices, Du et al., ACM CCS 2017)               │
│ - LogBERT (BERT Masked Language Modeling on Logs, Guo et al., IJCNN 2021)   │
│ - Reproducible Parser-Free SSL Method (e.g. NeuralLog, Le & Zhang, ASE 2021)│
├─────────────────────────────────────────────────────────────────────────────┤
│ GROUP C: PROVENANCE GRAPH BASELINES (Compatible Granularity Only)           │
│ - KAIROS (Temporal Graph Anomaly Detection, Cheng et al., USENIX Sec 2021) │
│ - NODLINK (Node-level link prediction provenance baseline)                  │
│ - MAGIC / ORTHRUS (Graph representation baselines)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ GROUP D: SYSTEMATIC INTERNAL ABLATION SUITE                                 │
│ - Ablation 1: Sequence-Only Extractor (z_seq)                               │
│ - Ablation 2: Graph-Only Extractor (z_graph)                                │
│ - Ablation 3: Multi-View Concatenation without Alignment (lambda_3 = 0)     │
│ - Ablation 4: Multi-View without Dynamic Parameters (Template-Only)         │
│ - Ablation 5: Multi-View without Privacy Mechanism                          │
│ - Ablation 6: Multi-View without Attention MIL Adaptation (lambda_4 = 0)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Strict Fairness Contract

Every baseline model evaluated in Chapter 3 must strictly operate under identical experimental constraints:

| Fairness Dimension | Contract Requirement | Violation Criteria |
| :--- | :--- | :--- |
| **1. Data Partitions** | Exact same `split_id` and SHA-256 split manifest. | Baseline evaluated on random split while proposed model uses causal split. |
| **2. Available Information** | Exact same telemetry fields and historical window $\\mathcal{L}_{1:t}$. | Baseline denied dynamic parameters available to proposed model, or baseline given future lookahead. |
| **3. Downstream Probe** | Identical probe family, capacity, and regularization. | Proposed model evaluated with complex non-linear ensemble while baseline uses simple linear threshold. |
| **4. Test Sealing** | Evaluated exactly once on sealed Test split. | Re-tuning baseline on test split or peeking test ground truth. |
| **5. Hyperparameter Budget** | Comparable tuning budget on Validation split. | Proposed model tuned over 100 trials while baseline evaluated on default out-of-the-box settings. |
| **6. Computational Reporting** | Mandatory reporting of GPU-hours, trial counts, and parameter scale. | Hiding excessive compute requirements of proposed model. |

---

## 3. Baseline Tuning Budget Protocol

To enforce comparable tuning effort across all models:
1. **Search Space:** Define an explicit grid / Bayesian search space of exactly $N_{\\text{trials}} = 30$ configurations for each baseline on the Validation split.
2. **Early Stopping:** Uniform early stopping patience ($E=10$ epochs without validation loss improvement).
3. **Resource Accounting:** Record total wall-clock training time, peak VRAM, and GPU-hours for every baseline run.
"""
    (protocol_dir / "BASELINE-FAIRNESS.md").write_text(baseline_fairness, encoding="utf-8")
    print("[OK] Wrote BASELINE-FAIRNESS.md")

    # -------------------------------------------------------------------------
    # 7. ROBUSTNESS-PROTOCOL.md
    # -------------------------------------------------------------------------
    robustness_protocol = """# LOG ROBUSTNESS & ADVERSARIAL TELEMETRY PERTURBATION PROTOCOL

**Document Identifier:** `PROT-ROBUST-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-10`), Roadmap (`AXIS-A3`, `BOUNDARY-05`).  

---

## 1. Perturbation Principles & Semantic Preservation Invariant

To evaluate representation resilience against real-world evasion, log pipeline faults, and environment drift, the system defines 12 deterministic perturbation operators.

### Core Semantic Invariant:
$$\\text{Semantics}(T(X)) \\equiv \\text{Semantics}(X)$$
**Strict Rule:** No perturbation operator shall alter the ground-truth execution semantics of the underlying attack or benign activity. Perturbations simulate realistic adversary evasion tactics, log pipeline dropouts, and benign environment noise without altering actual execution outcomes.

---

## 2. The 12 Pre-Registered Perturbation Operators

| # | Perturbation Operator | Attack Budget / Parameter Scope | Semantic Preservation Condition | Deterministic Generator / Config |
| :--- | :--- | :--- | :--- | :--- |
| **P01** | **Executable Renaming** | Replace attack executable names with benign system names (e.g. `mimikatz.exe` $\\to$ `svchost.exe`). | Execution arguments and process parentage remain identical. | Seeded token mapping table. |
| **P02** | **Path Relocation** | Mutate file paths (e.g. `/tmp/payload` $\\to$ `/var/log/syslog.1`). | File operations target valid system directories. | Deterministic path substitution engine. |
| **P03** | **Benign Identifier Replacement** | Randomize user IDs (`U1001` $\\to$ `U9999`) and hostnames. | Identifier linkage within session preserved; global ID shifted. | Causal identity pseudonymizer. |
| **P04** | **Timestamp Jitter** | Add Gaussian jitter $\\Delta t \\sim \\mathcal{N}(0, \\sigma^2)$, $\\sigma \\in [0.1\\text{s}, 5.0\\text{s}]$ to timestamps. | Total event causal order strictly preserved ($t_i \\le t_{i+1}$). | Seeded noise injector. |
| **P05** | **Benign Event Insertion** | Interleave benign background log events (up to $50\\%$ noise ratio). | Benign events sampled from empirical $\\mathcal{D}_{\\text{train}}$ normal pool. | Poisson process event merger. |
| **P06** | **Telemetry Dropout / Deletion** | Randomly drop $\\rho_{\\text{drop}} \\in [5\\%, 30\\%]$ of telemetry events (packet loss). | Dropped events cannot include critical primary attack execution tokens. | Uniform Bernoulli mask with fixed seed. |
| **P07** | **Local Event Reordering** | Permute adjacent independent events occurring within $\\Delta t \\le 500\\text{ms}$. | Causal dependencies (e.g. `write` before `read`) cannot be inverted. | Windowed topological permuter. |
| **P08** | **Telemetry Suppression** | Suppress all telemetry from a specific child process branch. | Simulates auditd/Sysmon logging evasion without breaking parent stream. | Process subtree pruning mask. |
| **P09** | **Broken Entity Linkage** | Strip Parent Process ID (PPID) or network socket binding on 20% of events. | Event content preserved; structural provenance pointer set to $\\bot$. | Structural pointer nullifier. |
| **P10** | **Missing View Simulation** | Complete dropout of sequential view ($X_{\\text{seq}} = \\emptyset$) or graph view ($G = \\emptyset$). | Simulates collector outage for one logging modality. | Modality dropout switch. |
| **P11** | **Unseen Host / Entity Cold-Start** | Evaluate model on hosts/users never observed during training. | Telemetry conforms to standard OS schema. | Host holdout partition (`SPL-DTC-001`). |
| **P12** | **Mimicry Benign Tool Insertion** | Interleave realistic discovery commands (`whoami`, `dir`, `ping`, `systeminfo`) inside attack chain. | Standard MITRE ATT&CK discovery techniques executed by adversary. | Synthetic ATT&CK discovery sequence injector. |

---

## 3. Robustness Evaluation Metric & Success Criteria

For each perturbation $P_k$ at budget level $\\beta$, compute:
$$\\Delta \\text{PR-AUC}(P_k, \\beta) = \\text{PR-AUC}(\\text{Clean}) - \\text{PR-AUC}(P_k(\\beta))$$
$$\\text{Invariance}(P_k, \\beta) = \\frac{1}{N} \\sum_{i=1}^N \\|\\mathbf{z}(P_k(X_i)) - \\mathbf{z}(X_i)\\|_2$$

- **Robustness Pass:** $\\Delta \\text{PR-AUC} \\le 0.15$ across all $P_1 \\dots P_{12}$ at standard budget.
- **Robustness Falsified:** $\\Delta \\text{PR-AUC} > 0.40$ or performance collapses to random guess level under minor syntactic perturbations ($P_1, P_2, P_4$).
"""
    (protocol_dir / "ROBUSTNESS-PROTOCOL.md").write_text(robustness_protocol, encoding="utf-8")
    print("[OK] Wrote ROBUSTNESS-PROTOCOL.md")

    # -------------------------------------------------------------------------
    # 8. PRIVACY-PROTOCOL.md
    # -------------------------------------------------------------------------
    privacy_protocol = """# PRIVACY ATTACK PROTOCOL & UTILITY–PRIVACY PARETO FRONTIER

**Document Identifier:** `PROT-PRIV-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-10`), Roadmap Boundary (`BOUNDARY-06`), Axis (`AXIS-A5`).  

---

## 1. Core Privacy Invariant: Attack-Based Empirical Verification

In strict accordance with Research Boundary `BOUNDARY-06`:
> **Hard Invariant:** A log representation mechanism cannot be claimed as privacy-preserving without empirical leakage evaluation under realistic threat models. Theoretical pseudonymization, token hashing, and string masking frequently fail under linkage and inference attacks.

---

## 2. Four Pre-Registered Adversary Threat Models

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRIVACY ADVERSARY TAXONOMY                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. RE-IDENTIFICATION ADVERSARY (A_ReID)                                     │
│    Goal: Map anonymous feature vector z to true entity identity u in U.     │
│    Background Knowledge: Public/auxiliary behavioral log statistics.        │
│    Attack Metric: Top-1 & Top-5 Re-identification Accuracy.                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. LINKAGE ADVERSARY (A_Link)                                               │
│    Goal: Determine if two vectors z_1, z_2 originate from same entity u.    │
│    Background Knowledge: Cross-session timing and structural correlations.  │
│    Attack Metric: Linkage Verification ROC-AUC & True Positive Rate @ 1% FPR│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. MEMBERSHIP INFERENCE ADVERSARY (A_MIA)                                   │
│    Goal: Determine if target session L_target was in pretraining set D_train│
│    Background Knowledge: Shadow datasets and shadow extractors.             │
│    Attack Metric: MIA Advantage = TPR - FPR & Membership AUC.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. REPRESENTATION INVERSION ADVERSARY (A_Inv)                               │
│    Goal: Reconstruct raw sensitive parameter strings (IPs, paths, accounts) │
│    Background Knowledge: Generative decoder trained on representation z.    │
│    Attack Metric: Exact String Reconstruction Rate & Character Edit Distance│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Utility–Privacy Pareto Frontier Formulation

The privacy-security trade-off is formalized as a multi-objective optimization problem:

$$\\max_{\\mathbf{z}} \\quad \\left( \\mathcal{U}(\\mathbf{z}), \\; -\\mathcal{L}_{\\text{privacy}}(\\mathbf{z}) \\right)$$

Where:
- **Security Utility $\\mathcal{U}(\\mathbf{z})$:** Downstream Frozen Probe Macro-F1 / PR-AUC on MITRE ATT&CK attack detection.
- **Privacy Loss $\\mathcal{L}_{\\text{privacy}}(\\mathbf{z})$:** Aggregate empirical leakage score across the 4 adversary models:
  $$\\mathcal{L}_{\\text{privacy}}(\\mathbf{z}) = w_1 \\text{Acc}(\\mathcal{A}_{\\text{ReID}}) + w_2 \\text{AUC}(\\mathcal{A}_{\\text{Link}}) + w_3 \\text{Adv}(\\mathcal{A}_{\\text{MIA}}) + w_4 \\text{Rec}(\\mathcal{A}_{\\text{Inv}})$$

### Evaluated Privacy Regimes:
1. **Raw Baseline:** Exact un-anonymized identifiers ($\\epsilon = \\infty$).
2. **Naive Pseudonymization:** Static salted SHA-256 hashing of entity identifiers.
3. **Controlled Linkability (Ours):** Keyed session-bound hashing + Local Differential Privacy noise $\\epsilon \\in \\{0.1, 0.5, 1.0, 2.0, 5.0\\}$.
4. **Extreme Anonymization:** Complete entity token suppression / replacement with universal wildcard `[ENTITY]`.

### Falsification Test for Hypothesis H5:
Hypothesis H5 is **FALSIFIED** if the empirical Pareto frontier generated by Controlled Linkability is strictly dominated by either Raw Identifiers or Complete Anonymization across all tested operating points.
"""
    (protocol_dir / "PRIVACY-PROTOCOL.md").write_text(privacy_protocol, encoding="utf-8")
    print("[OK] Wrote PRIVACY-PROTOCOL.md")

    # -------------------------------------------------------------------------
    # 9. STATISTICAL-PLAN.md
    # -------------------------------------------------------------------------
    stat_plan = """# STATISTICAL ANALYSIS PLAN & MISUSE PREVENTION

**Document Identifier:** `PLAN-STAT-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-10`), Statistical Protocol (`docs/STATISTICAL-PROTOCOL.md`).  

---

## 1. Core Principles & Sample Unit Definition

1. **Mandatory Sample Unit:** The fundamental unit of statistical analysis is the **Independent Random Seed Run** ($K \\ge 5$) evaluated across standardized causal splits.
2. **Multi-Seed Distribution Reporting:** Cherry-picking single best runs is strictly prohibited. All reported tables must convey:
   $$\\text{Mean} \\pm \\text{Standard Deviation} \\quad \\text{and/or} \\quad \\text{Median } [\\text{IQR}]$$
3. **Pre-Registered Random Seeds:**
   $$\\mathcal{K}_{\\text{seeds}} = \\{42, \\; 1337, \\; 2024, \\; 7, \\; 999\\}$$

---

## 2. Hypothesis Testing Decision Matrix

| Comparison Structure | Normality Condition | Primary Statistical Test | Standardized Effect Size Metric |
| :--- | :--- | :--- | :--- |
| **Paired Seed Evaluations** ($K \\ge 5$) | Normal (Shapiro-Wilk $p \\ge 0.05$) | Paired Student's $t$-test | Hedges' $g$ (small-sample corrected) |
| **Paired Seed Evaluations** ($K \\ge 5$) | Non-Normal / Skewed ($p < 0.05$) | Wilcoxon Signed-Rank Test | Rank-Biserial Correlation $r_{\\text{rb}}$ |
| **Independent Split Partitions** | Normal ($p \\ge 0.05$) | Independent Two-Sample $t$-test | Cohen's $d$ / Hedges' $g$ |
| **Independent Split Partitions** | Non-Normal ($p < 0.05$) | Mann-Whitney $U$ Test | Rank-Biserial Correlation $r_{\\text{rb}}$ |

---

## 3. Mathematical Formulations for Effect Sizes & Bootstrap CIs

### Hedges' $g$ (Small-Sample Bias Corrected):
$$g = d \\cdot \\left(1 - \\frac{3}{4(n_1 + n_2) - 9}\\right), \\quad d = \\frac{\\bar{x}_1 - \\bar{x}_2}{s_{\\text{pooled}}}$$
$$s_{\\text{pooled}} = \\sqrt{\\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}$$

### 95% Non-Parametric Bootstrap Confidence Intervals:
- Resampling iterations: $B = 2,000$ iterations with replacement.
- Fixed bootstrap seed: $\\text{seed}_{\\text{boot}} = 10007$.
- Interval bounds: $[\\theta_{0.025}^*, \\; \\theta_{0.975}^*]$.

---

## 4. Multiple Comparisons Adjustment

When testing multiple sub-hypotheses simultaneously (e.g. across 12 perturbation operators or 5 MITRE ATT&CK tactics):
1. **Family-Wise Error Rate (FWER):** Bonferroni adjustment:
   $$\\alpha' = \\frac{\\alpha}{m}, \\quad \\alpha = 0.05$$
2. **False Discovery Rate (FDR):** Benjamini-Hochberg procedure when evaluating exploratory multi-class attribution metrics.

---

## 5. Statistical Misuse Guardrails

1. **Absence of Evidence $\\neq$ Evidence of Absence:** A finding of $p \\ge 0.05$ cannot be interpreted as proof that two feature representations are identical without formal Two One-Sided Tests (TOST) equivalence testing.
2. **Cherry-Picking Detection:** The automated auditor will trigger a fatal violation if a reported scalar $V_{\\text{rep}}$ in thesis text equals $\\max(V_{\\text{seeds}})$ while diverging from $\\bar{V}$.
"""
    (protocol_dir / "STATISTICAL-PLAN.md").write_text(stat_plan, encoding="utf-8")
    print("[OK] Wrote STATISTICAL-PLAN.md")

    # -------------------------------------------------------------------------
    # 10. RESULT-PROVENANCE-SCHEMA.md
    # -------------------------------------------------------------------------
    res_provenance = """# MACHINE-READABLE RESULT PROVENANCE SCHEMA

**Document Identifier:** `SCH-PROV-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-09`, `RC-10`, `RC-11`), Scientific Verification Architecture (`docs/SCIENTIFIC-VERIFICATION.md`).  

---

## 1. Result Provenance Firewall Contract

To permanently eradicate hallucinated experimental numbers:
> **Hard Rule:** Every number, metric, table cell, and plot coordinate appearing in Chapter 3 must be generated via code directly from a verified `result.json` artifact located in `experiments/runs/<RUN-ID>/`.

If an experiment has not yet been executed in the physical environment, all associated table entries and metrics must remain strictly formatted as:
`PENDING_EXECUTION`

---

## 2. Canonical JSON Schema for `result.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ExperimentRunResult",
  "type": "object",
  "required": [
    "run_id",
    "experiment_id",
    "rq_id",
    "hyp_id",
    "git_commit",
    "dataset_id",
    "dataset_version_sha256",
    "split_manifest_sha256",
    "extractor_config_sha256",
    "environment_manifest_sha256",
    "random_seed",
    "execution_mode",
    "status",
    "layer1_metrics",
    "layer2_metrics",
    "layer3_metrics",
    "provenance_signature"
  ],
  "properties": {
    "run_id": {"type": "string", "pattern": "^RUN-[0-9]{6}$"},
    "experiment_id": {"type": "string", "pattern": "^EXP-[0-9]{2}$"},
    "rq_id": {"type": "string", "pattern": "^RQ-[0-9]{6}$"},
    "hyp_id": {"type": "string", "pattern": "^HYP-[0-9]{6}$"},
    "git_commit": {"type": "string", "minLength": 7},
    "dataset_id": {"type": "string"},
    "dataset_version_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "split_manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "extractor_config_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "environment_manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "random_seed": {"type": "integer"},
    "execution_mode": {"type": "string", "enum": ["RESEARCH_DETERMINISTIC", "PERFORMANCE"]},
    "status": {"type": "string", "enum": ["COMPLETED", "FAILED", "PENDING_EXECUTION"]},
    "timestamps": {
      "type": "object",
      "properties": {
        "started_at": {"type": "string", "format": "date-time"},
        "finished_at": {"type": "string", "format": "date-time"},
        "duration_seconds": {"type": "number"}
      }
    },
    "layer1_metrics": {
      "type": "object",
      "properties": {
        "representation_variance": {"type": "number"},
        "effective_rank": {"type": "number"},
        "cross_view_alignment_cosine": {"type": "number"},
        "temporal_stability": {"type": "number"}
      }
    },
    "layer2_metrics": {
      "type": "object",
      "properties": {
        "linear_probe_macro_f1": {"type": "number"},
        "linear_probe_pr_auc": {"type": "number"},
        "knn_probe_pr_auc": {"type": "number"}
      }
    },
    "layer3_metrics": {
      "type": "object",
      "properties": {
        "precision": {"type": "number"},
        "recall": {"type": "number"},
        "f1_score": {"type": "number"},
        "pr_auc": {"type": "number"},
        "roc_auc": {"type": "number"},
        "fpr": {"type": "number"},
        "recall_at_01_fpr": {"type": "number"},
        "detection_delay_seconds": {"type": "number"},
        "throughput_events_per_sec": {"type": "number"},
        "p95_latency_ms": {"type": "number"},
        "peak_ram_mb": {"type": "number"},
        "peak_vram_mb": {"type": "number"}
      }
    },
    "provenance_signature": {"type": "string", "pattern": "^[a-f0-9]{64}$"}
  }
}
```
"""
    (protocol_dir / "RESULT-PROVENANCE-SCHEMA.md").write_text(res_provenance, encoding="utf-8")
    print("[OK] Wrote RESULT-PROVENANCE-SCHEMA.md")

    # -------------------------------------------------------------------------
    # 11. ENVIRONMENT-MANIFEST-SCHEMA.yaml
    # -------------------------------------------------------------------------
    env_manifest = """# REPRODUCIBILITY ENVIRONMENT MANIFEST SCHEMA
# Document Identifier: SCH-ENV-20260821-V1.0
# Protocol Version: 1.0.0

schema_version: "1.0.0"
execution_modes:
  RESEARCH_DETERMINISTIC:
    description: "Bit-exact reproducible execution mode. All random operations seeded; cuDNN deterministic flags enabled."
    torch_deterministic: true
    cublas_workspace_config: ":4096:8"
    benchmark_cudnn: false
  PERFORMANCE:
    description: "Operational throughput and latency benchmark mode. cuDNN benchmark enabled."
    torch_deterministic: false
    cublas_workspace_config: "default"
    benchmark_cudnn: true

environment_specification:
  hardware:
    cpu_model: "string (e.g. Intel(R) Core(TM) i9-14900K / Xeon Gold)"
    cpu_cores_physical: "integer"
    cpu_cores_logical: "integer"
    system_ram_gb: "number"
    gpu_model: "string (e.g. NVIDIA GeForce RTX 4090 / A5000)"
    gpu_count: "integer"
    gpu_vram_gb: "number"
    gpu_driver_version: "string"
  software:
    os_name: "string (e.g. Windows 11 Pro / Ubuntu 22.04 LTS via WSL2)"
    os_kernel_version: "string"
    python_version: "string (e.g. 3.12.3)"
    cuda_version: "string (e.g. 12.4)"
    cudnn_version: "string"
    frameworks:
      torch: "string (e.g. 2.4.0+cu124)"
      torch_geometric: "string (e.g. 2.5.3)"
      numpy: "string (e.g. 1.26.4)"
      scipy: "string (e.g. 1.13.1)"
      scikit_learn: "string (e.g. 1.5.1)"
      pandas: "string (e.g. 2.2.2)"
      networkx: "string (e.g. 3.3)"
      sympy: "string (e.g. 1.13.1)"
      transformers: "string (e.g. 4.44.0)"
"""
    (protocol_dir / "ENVIRONMENT-MANIFEST-SCHEMA.yaml").write_text(env_manifest, encoding="utf-8")
    print("[OK] Wrote ENVIRONMENT-MANIFEST-SCHEMA.yaml")

    # -------------------------------------------------------------------------
    # 12. generate_split_manifests.py
    # -------------------------------------------------------------------------
    split_gen_script = '''# -*- coding: utf-8 -*-
"""
Deterministic Anti-Leakage Split Generator
Computes causal-time partition boundaries and exports verified split manifests.
"""

import hashlib
import json
import sys
from pathlib import Path

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def generate_canonical_splits():
    manifests_dir = Path(r"D:\\Research\\datasets\\manifests")
    manifests_dir.mkdir(parents=True, exist_ok=True)

    splits = [
        {
            "split_id": "SPL-HDFS-001",
            "dataset_id": "DATA-HDFS-001",
            "dataset_name": "HDFS LogHub Benchmark",
            "version": "v1.0",
            "strategy": "STRICT_CAUSAL_TIME",
            "total_blocks": 575061,
            "train_ratio": 0.70,
            "val_ratio": 0.15,
            "test_ratio": 0.15,
            "seed": 42,
            "train_blocks": 402542,
            "val_blocks": 86259,
            "test_blocks": 86260,
            "oov_template_holdout_ratio": 0.10,
            "status": "LOCKED"
        },
        {
            "split_id": "SPL-BGL-001",
            "dataset_id": "DATA-BGL-001",
            "dataset_name": "BGL Supercomputer Log",
            "version": "v1.0",
            "strategy": "STRICT_CAUSAL_TIME",
            "total_events": 4747963,
            "temporal_span_days": 214.7,
            "train_days": [1, 150],
            "val_days": [151, 180],
            "test_days": [181, 215],
            "seed": 42,
            "status": "LOCKED"
        },
        {
            "split_id": "SPL-DTC-001",
            "dataset_id": "DATA-DTC-001",
            "dataset_name": "DARPA Transparent Computing E3/E5",
            "version": "v1.0",
            "strategy": "CAUSAL_SCENARIO_HOST_HOLDOUT",
            "e3_train_days": [1, 9],
            "e3_val_days": [10, 11],
            "e3_test_days": [12, 14],
            "holdout_target_hosts": ["victim-linux-02", "victim-win-01"],
            "seed": 42,
            "status": "LOCKED"
        },
        {
            "split_id": "SPL-LANL-001",
            "dataset_id": "DATA-LANL-001",
            "dataset_name": "LANL Cyber Security Data Set 2015",
            "version": "v1.0",
            "strategy": "STRICT_CAUSAL_TIME",
            "total_days": 89,
            "train_seconds": [1, 5184000],
            "val_seconds": [5184001, 6393600],
            "test_seconds": [6393601, 7776000],
            "seed": 42,
            "redteam_evaluation_scope": "TEST_WINDOW_ONLY",
            "status": "LOCKED"
        }
    ]

    for sp in splits:
        sp_bytes = json.dumps(sp, indent=2, sort_keys=True).encode("utf-8")
        sp["manifest_sha256"] = compute_sha256(sp_bytes)
        out_path = manifests_dir / f"{sp['split_id']}.json"
        out_path.write_text(json.dumps(sp, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[OK] Exported split manifest: {out_path.name} (SHA-256: {sp['manifest_sha256'][:16]}...)")

if __name__ == "__main__":
    generate_canonical_splits()
'''
    (protocol_dir / "generate_split_manifests.py").write_text(split_gen_script, encoding="utf-8")
    print("[OK] Wrote generate_split_manifests.py")

    print("\n========================================================")
    print("ALL PROTOCOL ARTIFACTS SUCCESSFULLY GENERATED IN D:\\Research\\experiments\\protocol\\")
    print("========================================================")

if __name__ == "__main__":
    main()
