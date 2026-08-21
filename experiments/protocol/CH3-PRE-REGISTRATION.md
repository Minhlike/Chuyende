# CHAPTER 3 EXPERIMENT PROTOCOL PRE-REGISTRATION & SCIENTIFIC BASELINE FREEZE

**Document Identifier:** `REG-CH3-20260821-V1.0`  
**Registration Date:** 2026-08-21  
**Status:** **LOCKED & CANONICAL — INVIOLABLE**  
**Governing Standard:** Research Constitution (`docs/RESEARCH-CONSTITUTION.md`), Open Science Framework (OSF) Pre-Registration Standard, IEEE/ACM Reproducibility Guidelines.  
**Target Thesis Document:** `"D:\Research\Chuyên đề chuyên sâu.docx"`  

---

## 1. Executive Scientific Scope & Invariant Non-Negotiables

This document formally records and freezes the complete experimental protocol for Chapter 3 (*Thực nghiệm, Đánh giá và Ứng dụng*) of the thesis:  
**"Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công"**  
prior to executing any official experiment runs, training neural models, acquiring full raw datasets, or accessing sealed test evaluation sets.

### Absolute Negative Invariants (Constitutional Prohibitions):
1. **NO Chapter 3 Results Generation:** No empirical numbers, scores, metrics, or performance tables shall be written into Chapter 3 prose before verified execution (`RC-02`).
2. **NO Model Training on Unregistered Protocols:** Extractor and baseline training must strictly adhere to pre-registered configurations.
3. **NO Test Set Snooping / Peeking:** Evaluation on Test splits remains strictly sealed until final frozen evaluation.
4. **NO Synthetic / Hallucinated Data Generation:** All metrics must trace to deterministic machine-readable run logs (`RC-02`).
5. **NO Test-Guided Hyperparameter Tuning:** All hyperparameters, thresholds ($\tau$), window sizes, masking ratios, and early stopping criteria must be fit strictly on Train/Validation splits.
6. **NO Modification to Chapter 1 or Chapter 2:** Chapters 1 and 2 are cryptographically frozen.

---

## 2. Cryptographic Baseline Freeze Registry

The baseline specifications, textual content, code generators, and foundational research maps are frozen with the following verified SHA-256 hashes extracted directly from the canonical Master DOCX artifact:

| Artifact / Component | Canonical Scope & Boundaries | Hash / Checksum | Hashing Algorithm & Status |
| :--- | :--- | :--- | :--- |
| **Master DOCX Canonical** | `D:\Research\Chuyên đề chuyên sâu.docx` (2,020,132 bytes) | `07cdd037868ffbca135498d077bdef291c6e5638b619d41b60175d80cac80463` | **LOCKED & CANONICAL** |
| **Chapter 1 Canonical Content** | Paragraphs 79..181 (103 paras, 87 normalized text lines) | `b7912883570e369e765c7a6daa7fc626db570c8b53050e976d4f652a2dc7e16e` | `DOCX_CANONICAL_CONTENT_HASH_V1` (**FROZEN**) |
| **Chapter 2 Canonical Content** | Paragraphs 182..467 (286 paras, 228 normalized text lines) | `e91bbc47de218d037d5dec3192b6ba59fda4e3c7423e51c34aea898d3db25a01` | `DOCX_CANONICAL_CONTENT_HASH_V1` (**FROZEN**) |
| **Canonical Roadmap v1.0.0** | `research_specs/roadmap/roadmap.yaml` | `d896dabd9916739d557ba56c5004058ea6a5771e9b8d16e7cdce84d52e6e16bf` | **LOCKED** |
| **Reference Map v1.0.0** | `research_specs/reference_map/REFERENCE-MAP.md` | `bcc62c948c3227762f42efa68a224ea736410935ff987b70ff68c3bbb6dcdbba` | **LOCKED** |

### DOCX Content Normalization Algorithm (`DOCX_CANONICAL_CONTENT_HASH_V1`):
1. **Paragraph Extraction:** Extract all paragraphs within exact chapter boundaries:
   - Chapter 1: From `[Heading 1] TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT...` up to `[Heading 1] PHƯƠNG PHÁP BIỂU DIỄN...`
   - Chapter 2: From `[Heading 1] PHƯƠNG PHÁP BIỂU DIỄN...` up to `[UH1] Kết luận`
2. **Unicode Normalization:** Apply Unicode NFC normalization to every paragraph text string.
3. **Whitespace Canonicalization:** Collapse internal multi-spaces and tabs to single ASCII space `' '`. Strip leading and trailing whitespace.
4. **Empty Line Suppression:** Exclude blank / whitespace-only paragraphs.
5. **Join & Hash:** Join normalized non-empty lines with ASCII newline `\n`, encode via UTF-8, and compute SHA-256.

---

## 3. Canonical Research Questions (RQ1–RQ5)

- **RQ1 — REPRESENTATION FIDELITY:** Can a log representation remove syntactic noise while preserving security-critical dynamic parameters?
- **RQ2 — CROSS-VIEW ALIGNMENT:** Can heterogeneous views be aligned without representation collapse or negative transfer while preserving useful view-specific information?
- **RQ3 — VALIDITY WITHOUT SHORTCUTS:** Does the representation remain useful after removing dataset shortcuts and under distribution shift?
- **RQ4 — WEAK EVIDENCE ATTRIBUTION:** Can attack evidence be assigned under coarse labels without learning benign administrative behavior as inherently malicious?
- **RQ5 — PRIVACY–SECURITY TRADE-OFF:** What balance between entity continuity and privacy leakage yields useful security representations?

---

## 4. Canonical Hypotheses & Falsification Conditions (H1–H5)

- **H1 — FIDELITY:** $\mathcal{I}(\mathbf{z}; Y_{\text{sec}}) > \mathcal{I}(\mathbf{z}_{\text{abstracted}}; Y_{\text{sec}})$. Supported if frozen probe AP on dynamic parameter attacks satisfies $\Delta \text{AP} \ge +0.05$ with lower 95% bootstrap CI bound $> 0$ ($p < 0.0125$). Inconclusive if 95% CI overlaps $0$. Falsified if point estimate $\Delta \text{AP} \le 0$ with upper 95% CI bound $\le 0$.
- **H2 — MULTI-VIEW:** $\text{Utility}(\mathbf{z}) > \max(\text{Utility}(\mathbf{z}^{(\text{seq})}), \text{Utility}(\mathbf{z}^{(\text{graph})})) - \epsilon_{\text{margin}}$. Supported if aligned multi-view AP satisfies $\Delta \text{AP} \ge +0.03$ over best single-view with $\text{Var}(\mathbf{z}) \ge 0.05$ and lower 95% bootstrap CI bound $> 0$ ($p < 0.0167$). Inconclusive if 95% CI overlaps $0$ or $\text{Var}(\mathbf{z}) \in [0.01, 0.05)$. Falsified if $\text{AP}(\mathbf{z}_{\text{mv}}) < \max(\text{AP}_{\text{seq}}, \text{AP}_{\text{graph}})$ with upper 95% CI bound $\le 0$, or dimensional collapse $\text{Var}(\mathbf{z}) < 0.01$.
- **H3 — ROBUSTNESS:** $\|\mathbf{z}(T(X)) - \mathbf{z}(X)\|_2 \le \epsilon_{\text{inv}}$. Supported if $\ge 85\%$ baseline AP is retained under semantic perturbations. Inconclusive if retention in $[70\%, 85\%)$ with overlapping CI against lexical baseline. Falsified if performance collapses to sample positive prevalence chance level ($\text{AP} \le \pi_0$) or converges to simple lexical baseline.
- **H4 — OPERATIONAL:** $\Delta t(e_t) \le 10\text{ ms}$ (p95), $\text{Mem}(\mathcal{S}_t) \le 500\text{ MB/host}$. Supported if p95 latency $\le 5.0\text{ms}$, throughput $\ge 25,000\text{ events/s}$, and peak RAM $\le 250\text{MB/host}$. Inconclusive if p95 latency in $(5.0\text{ms}, 10.0\text{ms}]$ or throughput in $[10,000, 25,000)\text{ events/s}$. Falsified if extraction latency $> 10\text{ ms}$ or peak RAM $> 500\text{ MB/host}$ or throughput $< 10,000\text{ events/s}$.
- **H5 — PRIVACY:** Controlled linkability Pareto-dominates raw identifiers and extreme anonymization. Supported if $\ge 90\%$ utility is preserved while reducing ReID accuracy by $\ge 60\%$ and MIA advantage to $< 0.05$. Inconclusive if utility retention in $[75\%, 90\%)$ or ReID reduction in $[40\%, 60\%)$. Falsified if empirical Pareto frontier is strictly dominated by either extreme.

---

## 5. Extractor–Detector Boundary & Supervision Contract

$$\mathcal{L}_{1:t} \xrightarrow{\quad f_\theta \quad} \mathbf{z}_t \in \mathbb{R}^d \xrightarrow{\quad g_{\text{frozen}} \quad} \hat{y}_t$$

- **Stage A (Offline SSL Pretraining):** Extractor $f_\theta$ trained on $\mathcal{D}_{\text{train}}$ via masked sequence modeling, dynamic graph structure prediction, and cross-view latent alignment. Zero attack labels used.
- **Stage B (Weak Evidence Adaptation / Optional):** Attention Multiple Instance Learning (MIL) on coarse bag-level labels with entropy regularization.
- **Stage C (Frozen Downstream Evaluation):** Extractor weights $\theta^*$ are completely frozen. Capacity-controlled probes (linear, logistic, kNN) evaluate $\mathbf{z}$ on sealed Test split.

---

## 6. Random Seed Lock & Execution Contract

- **Canonical Experiment Runs:** Exactly $K = 5$ independent random seeds:
  $$\mathcal{K}_{\text{canonical}} = \{ 42, \; 1337, \; 2024, \; 7, \; 999 \}$$
- **Extended Replication Runs:** Any additional seeds are strictly designated as `EXTENDED_REPLICATION` and reported separately in appendix tables.
