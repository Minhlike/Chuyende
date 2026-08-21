# BASELINE TAXONOMY & EXPERIMENTAL FAIRNESS CONTRACT

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
| **2. Available Information** | Exact same telemetry fields and historical window $\mathcal{L}_{1:t}$. | Baseline denied dynamic parameters available to proposed model, or baseline given future lookahead. |
| **3. Downstream Probe** | Identical probe family, capacity, and regularization. | Proposed model evaluated with complex non-linear ensemble while baseline uses simple linear threshold. |
| **4. Test Sealing** | Evaluated exactly once on sealed Test split. | Re-tuning baseline on test split or peeking test ground truth. |
| **5. Hyperparameter Budget** | Comparable tuning budget on Validation split. | Proposed model tuned over 100 trials while baseline evaluated on default out-of-the-box settings. |
| **6. Computational Reporting** | Mandatory reporting of GPU-hours, trial counts, and parameter scale. | Hiding excessive compute requirements of proposed model. |

---

## 3. Baseline Tuning Budget Protocol

To enforce comparable tuning effort across all models:
1. **Search Space:** Define an explicit grid / Bayesian search space of exactly $N_{\text{trials}} = 30$ configurations for each baseline on the Validation split.
2. **Early Stopping:** Uniform early stopping patience ($E=10$ epochs without validation loss improvement).
3. **Resource Accounting:** Record total wall-clock training time, peak VRAM, and GPU-hours for every baseline run.
