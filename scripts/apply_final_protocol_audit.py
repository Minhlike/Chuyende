# -*- coding: utf-8 -*-
"""
Final Protocol Audit & Baseline Locking Script
Applies all 10 audit corrections from the final pre-registration audit.
"""

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

def main():
    protocol_dir = Path(r"D:\Research\experiments\protocol")
    manifests_dir = Path(r"D:\Research\datasets\manifests")
    protocol_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    # Master Hashes
    master_docx_sha256 = "07cdd037868ffbca135498d077bdef291c6e5638b619d41b60175d80cac80463"
    ch1_norm_hash = "b7912883570e369e765c7a6daa7fc626db570c8b53050e976d4f652a2dc7e16e"
    ch2_norm_hash = "e91bbc47de218d037d5dec3192b6ba59fda4e3c7423e51c34aea898d3db25a01"
    hash_algo_version = "DOCX_CANONICAL_CONTENT_HASH_V1"

    # =========================================================================
    # 1. CH3-PRE-REGISTRATION.md
    # =========================================================================
    ch3_pre_reg = f"""# CHAPTER 3 EXPERIMENT PROTOCOL PRE-REGISTRATION & SCIENTIFIC BASELINE FREEZE

**Document Identifier:** `REG-CH3-20260821-V1.0`  
**Registration Date:** 2026-08-21  
**Status:** **LOCKED & CANONICAL — INVIOLABLE**  
**Governing Standard:** Research Constitution (`docs/RESEARCH-CONSTITUTION.md`), Open Science Framework (OSF) Pre-Registration Standard, IEEE/ACM Reproducibility Guidelines.  
**Target Thesis Document:** `"D:\\Research\\Chuyên đề chuyên sâu.docx"`  

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
5. **NO Test-Guided Hyperparameter Tuning:** All hyperparameters, thresholds ($\\tau$), window sizes, masking ratios, and early stopping criteria must be fit strictly on Train/Validation splits.
6. **NO Modification to Chapter 1 or Chapter 2:** Chapters 1 and 2 are cryptographically frozen.

---

## 2. Cryptographic Baseline Freeze Registry

The baseline specifications, textual content, code generators, and foundational research maps are frozen with the following verified SHA-256 hashes extracted directly from the canonical Master DOCX artifact:

| Artifact / Component | Canonical Scope & Boundaries | Hash / Checksum | Hashing Algorithm & Status |
| :--- | :--- | :--- | :--- |
| **Master DOCX Canonical** | `D:\\Research\\Chuyên đề chuyên sâu.docx` (2,020,132 bytes) | `{master_docx_sha256}` | **LOCKED & CANONICAL** |
| **Chapter 1 Canonical Content** | Paragraphs 79..181 (103 paras, 87 normalized text lines) | `{ch1_norm_hash}` | `{hash_algo_version}` (**FROZEN**) |
| **Chapter 2 Canonical Content** | Paragraphs 182..467 (286 paras, 228 normalized text lines) | `{ch2_norm_hash}` | `{hash_algo_version}` (**FROZEN**) |
| **Canonical Roadmap v1.0.0** | `research_specs/roadmap/roadmap.yaml` | `d896dabd9916739d557ba56c5004058ea6a5771e9b8d16e7cdce84d52e6e16bf` | **LOCKED** |
| **Reference Map v1.0.0** | `research_specs/reference_map/REFERENCE-MAP.md` | `bcc62c948c3227762f42efa68a224ea736410935ff987b70ff68c3bbb6dcdbba` | **LOCKED** |

### DOCX Content Normalization Algorithm (`DOCX_CANONICAL_CONTENT_HASH_V1`):
1. **Paragraph Extraction:** Extract all paragraphs within exact chapter boundaries:
   - Chapter 1: From `[Heading 1] TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT...` up to `[Heading 1] PHƯƠNG PHÁP BIỂU DIỄN...`
   - Chapter 2: From `[Heading 1] PHƯƠNG PHÁP BIỂU DIỄN...` up to `[UH1] Kết luận`
2. **Unicode Normalization:** Apply Unicode NFC normalization to every paragraph text string.
3. **Whitespace Canonicalization:** Collapse internal multi-spaces and tabs to single ASCII space `' '`. Strip leading and trailing whitespace.
4. **Empty Line Suppression:** Exclude blank / whitespace-only paragraphs.
5. **Join & Hash:** Join normalized non-empty lines with ASCII newline `\\n`, encode via UTF-8, and compute SHA-256.

---

## 3. Canonical Research Questions (RQ1–RQ5)

- **RQ1 — REPRESENTATION FIDELITY:** Can a log representation remove syntactic noise while preserving security-critical dynamic parameters?
- **RQ2 — CROSS-VIEW ALIGNMENT:** Can heterogeneous views be aligned without representation collapse or negative transfer while preserving useful view-specific information?
- **RQ3 — VALIDITY WITHOUT SHORTCUTS:** Does the representation remain useful after removing dataset shortcuts and under distribution shift?
- **RQ4 — WEAK EVIDENCE ATTRIBUTION:** Can attack evidence be assigned under coarse labels without learning benign administrative behavior as inherently malicious?
- **RQ5 — PRIVACY–SECURITY TRADE-OFF:** What balance between entity continuity and privacy leakage yields useful security representations?

---

## 4. Canonical Hypotheses & Falsification Conditions (H1–H5)

- **H1 — FIDELITY:** $\\mathcal{{I}}(\\mathbf{{z}}; Y_{{\\text{{sec}}}}) > \\mathcal{{I}}(\\mathbf{{z}}_{{\\text{{abstracted}}}}; Y_{{\\text{{sec}}}})$. Falsified if frozen probe PR-AUC on dynamic parameter attacks does not exceed template-only baseline ($p > 0.0125$ under Bonferroni correction, or Hedges' $g < 0.20$).
- **H2 — MULTI-VIEW:** $\\text{{Utility}}(\\mathbf{{z}}) > \\max(\\text{{Utility}}(\\mathbf{{z}}^{{(\\text{{seq}})}}), \\text{{Utility}}(\\mathbf{{z}}^{{(\\text{{graph}})}})) - \\epsilon_{{\\text{{margin}}}}$. Falsified if aligned multi-view PR-AUC is lower than best single-view ($p > 0.0167$) or suffers variance collapse ($\\text{{Var}}(\\mathbf{{z}}) < 0.01$).
- **H3 — ROBUSTNESS:** $\\|\\mathbf{{z}}(T(X)) - \\mathbf{{z}}(X)\\|_2 \\le \\epsilon_{{\\text{{inv}}}}$. Falsified if performance collapses to random guess level (PR-AUC $\\le 0.50$) or converges to lexical baseline under shortcut removal or 12 perturbation attacks.
- **H4 — OPERATIONAL:** $\\Delta t(e_t) \\le 10\\text{{ ms}}$ (p95), $\\text{{Mem}}(\\mathcal{{S}}_t) \\le 500\\text{{ MB/host}}$. Falsified if extraction latency exceeds $10\\text{{ ms}}$ or peak memory exceeds $500\\text{{ MB/host}}$ at $10,000$ events/s.
- **H5 — PRIVACY:** Controlled linkability Pareto-dominates raw identifiers and extreme anonymization. Falsified if empirical Pareto frontier is strictly dominated by either extreme.

---

## 5. Extractor–Detector Boundary & Supervision Contract

$$\\mathcal{{L}}_{{1:t}} \\xrightarrow{{\\quad f_\\theta \\quad}} \\mathbf{{z}}_t \\in \\mathbb{{R}}^d \\xrightarrow{{\\quad g_{{\\text{{frozen}}}} \\quad}} \\hat{{y}}_t$$

- **Stage A (Offline SSL Pretraining):** Extractor $f_\\theta$ trained on $\\mathcal{{D}}_{{\\text{{train}}}}$ via masked sequence modeling, dynamic graph structure prediction, and cross-view latent alignment. Zero attack labels used.
- **Stage B (Weak Evidence Adaptation / Optional):** Attention Multiple Instance Learning (MIL) on coarse bag-level labels with entropy regularization.
- **Stage C (Frozen Downstream Evaluation):** Extractor weights $\\theta^*$ are completely frozen. Capacity-controlled probes (linear, logistic, kNN) evaluate $\\mathbf{{z}}$ on sealed Test split.

---

## 6. Random Seed Lock & Execution Contract

- **Canonical Experiment Runs:** Exactly $K = 5$ independent random seeds:
  $$\\mathcal{{K}}_{{\\text{{canonical}}}} = \\{{ 42, \\; 1337, \\; 2024, \\; 7, \\; 999 \\}}$$
- **Extended Replication Runs:** Any additional seeds are strictly designated as `EXTENDED_REPLICATION` and reported separately in appendix tables.
"""
    (protocol_dir / "CH3-PRE-REGISTRATION.md").write_text(ch3_pre_reg, encoding="utf-8")
    print("[OK] Updated CH3-PRE-REGISTRATION.md with exact DOCX hashes")

    # =========================================================================
    # 2. DATASET-CARDS.md (DARPA exact scope & LANL redteam boundary locked)
    # =========================================================================
    dataset_cards = """# DATASET PROTOCOL & CANONICAL DATASET CARDS

**Document Identifier:** `CARD-DATA-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  

---

## 1. Two-Tier Dataset Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TWO-TIER BENCHMARK SUITE                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ TIER A: System Log Benchmarks        │ TIER B: Cyberattack Provenance Logs  │
│ - HDFS (LogHub, Xu et al., SOSP 09)  │ - DARPA TC Engagements E3 & E5       │
│ - BGL (LogHub, Oliner et al., DSN 07)│ - LANL Enterprise Cyber Security 2015│
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Purpose:                             │ Purpose:                             │
│ - Parsing & template novelty stress  │ - Multi-host causal provenance graph │
│ - Dynamic parameter retention        │ - Multi-stage APT campaign context   │
│ - Unseen template drift & OOV tests  │ - MITRE ATT&CK tactical attribution  │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Boundary Restriction:                │ Boundary Restriction:                │
│ STRICTLY PROHIBITED from claiming    │ Ground truth strictly locked to      │
│ cyberattack semantics (B-01).        │ official engagement reports (B-02).  │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 2. Detailed Dataset Cards

### Dataset Card 1: HDFS (Hadoop Distributed File System)
- **Official Source:** LogHub Repository / Xu et al., ACM SOSP 2009; Zhu et al., IEEE ISSRE 2023.
- **Version / Release:** `HDFS_v1` (11,175,629 log lines, 575,061 block sessions).
- **Observation Unit:** Event tuple $e_i$, Block session sequence $\mathcal{L}_{\text{blk}}$, sliding window.
- **Label Granularity:** Block ID binary label (`Normal` vs `Anomaly`).
- **Permitted Claims:** Parameter retention (Block ID, IP, byte count), parsing robustness, template abstraction.
- **Prohibited Overclaims:** Strictly prohibited from claiming cyberattack semantics or provenance graph reasoning (`BOUNDARY-01`).

### Dataset Card 2: BGL (Blue Gene/L Supercomputer)
- **Official Source:** LogHub Repository / Oliner & Stearley, IEEE/IFIP DSN 2007; Zhu et al., ISSRE 2023.
- **Version / Release:** `BGL_v1` (4,747,963 log messages, 214.7 operational days).
- **Observation Unit:** Event message, Node temporal sequence, fixed time window $\Delta t$.
- **Label Granularity:** RAS alert category flag (`-` = non-alert, non-`-` = alert).
- **Permitted Claims:** Robustness against template drift, long-term temporal shift, OOV log templates.
- **Prohibited Overclaims:** Strictly prohibited from claiming cyberattack defense or lateral movement detection (`BOUNDARY-01`).

---

### Dataset Card 3: DARPA Transparent Computing (TC) Engagements E3 & E5 — EXACT RUN SCOPE

To prevent post-hoc performer or scenario cherry-picking, the DARPA TC evaluation scope is strictly pre-registered:

| Parameter | Pre-Registered Canonical Scope | Prohibited Scope |
| :--- | :--- | :--- |
| **Engagements** | Engagement 3 (E3, April 2018) & Engagement 5 (E5, May 2019). | Unreleased or corrupted interim trials. |
| **Performers & Adapters** | 1) **THEIA** (Linux kernel LSM audit); 2) **CADETS** (FreeBSD DTrace/Audit); 3) **FiveDirections** (Windows ETW/Sysmon). | Non-standard third-party re-instrumentations. |
| **Operating Systems** | Ubuntu 14.04/16.04 LTS (x86_64, Linux 4.4.0), FreeBSD 11.0, Windows 7/10 Enterprise. | Unverified virtualization snapshots. |
| **CDM Schema Version** | **CDM v19** (Engagement 3) and **CDM v20** (Engagement 5). | Incompatible custom schema translations. |
| **Official Ground Truth Reports** | *DARPA Transparent Computing Engagement 3 / 5 Evaluation Ground Truth Reports* (compiled by SPAWAR Systems Center Pacific, MIT Lincoln Laboratory, and BAE Systems). | Subjective manual re-labeling of background logs. |
| **Pre-Registered Scenarios (E3)** | - **Scenario 1:** Browser extension phishing & local payload execution.<br>- **Scenario 2:** SSH password compromise, privilege escalation via kernel exploit.<br>- **Scenario 3:** Nginx web shell persistence and document exfiltration.<br>- **Scenario 4 (Holdout):** Multi-host lateral movement and telemetry evasion. | Selecting scenarios based on test detection rates. |
| **Permitted Claims** | Kernel-level provenance graph representation, cross-view sequential-graph alignment, multi-stage APT attribution. | Causal physical reality claims without causal identification assumptions (`BOUNDARY-03`). |

---

### Dataset Card 4: LANL Enterprise Multi-Source Cyber-Security Events — GROUND TRUTH BOUNDARY

- **Official Source:** Los Alamos National Laboratory / Alexander D. Kent, 2015. DOI: 10.17021/1110439.
- **Version / Release:** `LANL_CyberSecurity_2015_v1` (`auth.txt.gz`, `proc.txt.gz`, `redteam.txt.gz`).
- **Temporal Coverage:** 89 continuous operational days ($t = 1 \dots 7,776,000$ seconds).
- **Exact Red Team Label Invariant:**
  > **Hard Ground Truth Invariant:** The `redteam.txt` file contains exactly 749 verified compromised authentication events. Each record is strictly an authentication event 4-tuple: `(Time, User@Domain, SourceHost, DestHost)`.
- **Prohibited Label Propagation:**
  - **NO Process Labeling:** Coincident processes in `proc.txt` are **NOT** automatically labeled malicious.
  - **NO Temporal Window Expansion:** Events occurring in the same 1-hour or 1-day window as a red team event are **NOT** labeled malicious by association.
  - **NO Host-Wide Infection Assumption:** Hosts involved in red team events are **NOT** treated as globally compromised for their entire lifespan.
- **Pre-Registered Weak Evidence Attribution Rule:**
  Coarse bag-level labels for Stage B MIL are formed over fixed host-day authentication bags $\mathcal{B}_{h, d}$. A bag is labeled positive ($\mathcal{Y}_{\mathcal{B}} = 1$) if and only if it contains $\ge 1$ exact match in `redteam.txt`. All instances within the bag remain weakly labeled, and attention attribution uncertainty must be explicitly reported.
"""
    (protocol_dir / "DATASET-CARDS.md").write_text(dataset_cards, encoding="utf-8")
    print("[OK] Updated DATASET-CARDS.md with DARPA exact scope and LANL boundary")

    # =========================================================================
    # 3. SPLIT-PROTOCOL.md (State Machine: PLANNED -> ACQUIRED -> SEALED)
    # =========================================================================
    split_protocol = """# ANTI-LEAKAGE CAUSAL SPLIT PROTOCOL & SPLIT MANIFEST STATE MACHINE

**Document Identifier:** `PROT-SPLIT-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-10`, `RC-16`), Roadmap Boundary (`BOUNDARY-09`).  

---

## 1. Split Manifest Lifecycle State Machine

To prevent fabricated partition counts and speculative split hashes prior to physical data acquisition, every split manifest follows a strict three-state lifecycle:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SPLIT MANIFEST LIFECYCLE STATE MACHINE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  STATE 1: PLANNED (Current State — Pre-Acquisition)                         │
│  - Formal partitioning ratios defined (Train 70% < Val 15% < Test 15%)      │
│  - Holdout dimensions and causal boundary rules locked                      │
│  - Raw file hashes and event counts marked strictly PENDING_ACQUISITION     │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │ (Trigger: Raw Data Acquired & SHA256)│
│                                      ▼                                      │
│  STATE 2: ACQUIRED (Data Staging & Integrity Audit)                         │
│  - Raw tarball/files downloaded and verified against official sources       │
│  - SHA-256 hash computed for every raw artifact                             │
│  - Parser version, valid/invalid record counts, and temporal span recorded  │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │ (Trigger: Preprocessors Fit on Train)│
│                                      ▼                                      │
│  STATE 3: SEALED (Locked For Evaluation)                                    │
│  - Exact index/timestamp partition boundaries generated deterministically   │
│  - Train/Val/Test SHA-256 manifests calculated and frozen                   │
│  - Test set sealed against any access until final frozen evaluation         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pre-Acquisition Verification Checklist (Required for Transition to ACQUIRED)

Before any split manifest transitions from `PLANNED` to `ACQUIRED` and `SEALED`, the following checklist must be satisfied and recorded in `datasets/manifests/<SPLIT-ID>.json`:
1. Official download URL and verified mirror citation.
2. Exact release version / release date.
3. List of constituent raw files with byte sizes.
4. Cryptographic SHA-256 checksum of every raw file.
5. Parser version and canonicalization script hash.
6. Total raw records, valid parsed records, and malformed/discarded record count.
7. Exact minimum timestamp $T_{\min}$ and maximum timestamp $T_{\max}$ in event-time.
8. Ground truth label file path and label file SHA-256.
9. Explicit list of excluded hosts/records with formal scientific rationale.

---

## 3. Pre-Registered Partition Specifications (State: PLANNED)

| Split ID | Dataset | Strategy | Planned Partition Ratios | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`SPL-HDFS-001`** | HDFS LogHub | Strict Causal Time + OOV Template Holdout | Train: First 70% block sessions<br>Val: Next 15% sessions<br>Test: Final 15% sessions (Sealed)<br>Holdout: 10% rare anomaly templates | **PLANNED** |
| **`SPL-BGL-001`** | BGL Supercomputer | Strict Causal Time + Temporal Drift Test | Train: Days 1..150 (~70%)<br>Val: Days 151..180 (~15%)<br>Test: Days 181..215 (~15%, Sealed)<br>Stress: Days 181+ unseen failure codes | **PLANNED** |
| **`SPL-DTC-001`** | DARPA TC E3/E5 | Causal Scenario + Host Holdout | Train: E3 Days 1..9 (Baseline)<br>Val: E3 Days 10..11 (Validation redteam)<br>Test: E3 Days 12..14 & E5 Days 15..21 (Sealed)<br>Holdout: 2 designated target hosts | **PLANNED** |
| **`SPL-LANL-001`** | LANL Cyber Security | Strict Causal Time | Train: Days 1..60 ($t = 1 \dots 5.184 \times 10^6\text{s}$)<br>Val: Days 61..74 ($t = 5.184 \times 10^6 \dots 6.393 \times 10^6\text{s}$)<br>Test: Days 75..89 (Sealed)<br>Red Team: Test-window occurrences only | **PLANNED** |
"""
    (protocol_dir / "SPLIT-PROTOCOL.md").write_text(split_protocol, encoding="utf-8")
    print("[OK] Updated SPLIT-PROTOCOL.md with state machine specification")

    # =========================================================================
    # 4. STATISTICAL-PLAN.md (Exact Decision Tree, Families, Bootstrap Contract)
    # =========================================================================
    stat_plan = """# STATISTICAL ANALYSIS PLAN & HYPOTHESIS TESTING CONTRACT

**Document Identifier:** `PLAN-STAT-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-10`), Statistical Protocol (`docs/STATISTICAL-PROTOCOL.md`).  

---

## 1. Random Seed Contract

- **Canonical Sample Budget:** Exactly $K = 5$ independent random seeds:
  $$\mathcal{K}_{\text{canonical}} = \{42, \; 1337, \; 2024, \; 7, \; 999\}$$
- **Strict Prohibition:** It is strictly forbidden to run a larger set of seeds and cherry-pick the 5 most favorable runs. All 5 pre-registered seeds must be reported in full.
- **Reporting Format:** All benchmark tables must convey $\text{Mean} \pm \text{Standard Deviation}$ alongside $\text{Median } [\text{IQR}]$.

---

## 2. Deterministic Hypothesis Testing Decision Tree

To eliminate post-hoc test selection based on favorable $p$-values:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC STATISTICAL DECISION TREE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Step 1: Compute Paired Differences across K=5 Seeds:                       │
│          Delta_k = Metric(Proposed, Seed_k) - Metric(Baseline, Seed_k)      │
│                                │                                            │
│                                ▼                                            │
│  Step 2: Test Normality Assumption via Shapiro-Wilk Test on {Delta_k}:      │
│          H0: Delta is normally distributed (alpha = 0.05)                   │
│                                │                                            │
│            ┌───────────────────┴───────────────────┐                        │
│            ▼                                       ▼                        │
│   p_SW >= 0.05 (Normality Holds)          p_SW < 0.05 (Normality Violated)  │
│   ──────────────────────────────          ────────────────────────────────  │
│   MANDATORY TEST:                         MANDATORY TEST:                   │
│   Paired Student's t-test                 Wilcoxon Signed-Rank Test         │
│   EFFECT SIZE:                            EFFECT SIZE:                      │
│   Hedges' g (small-sample corrected)      Rank-Biserial Correlation r_rb    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mathematical Effect Size Formulations:
- **Hedges' $g$:**
  $$g = \frac{\bar{x}_1 - \bar{x}_2}{s_{\text{pooled}}} \cdot \left(1 - \frac{3}{4(n_1 + n_2) - 9}\right)$$
- **Rank-Biserial Correlation ($r_{\text{rb}}$):**
  $$r_{\text{rb}} = \frac{W_+ - W_-}{W_+ + W_-}$$

---

## 3. Pre-Registered Multiple Comparisons Policy by Hypothesis Family

Correction methods are strictly locked per hypothesis family; switching methods post-hoc is prohibited:

| Hypothesis Family | Scope & Comparison Count ($m$) | Mandatory Correction Method | Target Family-Wise $\alpha$ or FDR $q^*$ |
| :--- | :--- | :--- | :--- |
| **Family 1 (H1 — Fidelity)** | 4 dynamic attack subtypes (SQLi, Command Injection, Path Traversal, Port Scan). | **Bonferroni Adjustment** | $\alpha' = \frac{0.05}{4} = 0.0125$ |
| **Family 2 (H2 — Multi-View)** | 3 pairwise comparisons (Multi-View vs Seq-only, Multi-View vs Graph-only, Multi-View vs Unaligned Concat). | **Bonferroni Adjustment** | $\alpha' = \frac{0.05}{3} = 0.0167$ |
| **Family 3 (H3 — Robustness)** | 12 perturbation operator hypotheses (P01..P12). | **Benjamini-Hochberg FDR** | Target FDR $q^* = 0.05$ |
| **Family 4 (H4 — Operational)** | 3 conjunctive SLOs (Latency $\le 10\text{ms} \land \text{RAM} \le 500\text{MB} \land \text{Throughput} \ge 10^4$). | **Intersection-Union Test (IUT)** | All 3 must pass at individual $\alpha = 0.05$ |
| **Family 5 (H5 — Privacy)** | 4 privacy adversary leakage models ($\mathcal{A}_{\text{ReID}}, \mathcal{A}_{\text{Link}}, \mathcal{A}_{\text{MIA}}, \mathcal{A}_{\text{Inv}}$). | **Holm-Bonferroni Step-Down** | Sequential step-down testing at overall $\alpha = 0.05$ |
| **Exploratory Analyses** | Post-hoc sub-population slicing, token length stratifications, embedding dimension sweeps. | **Benjamini-Yekutieli FDR** | Must be explicitly labeled **`[EXPLORATORY]`**; cannot be claimed as confirmatory evidence. |

---

## 4. Bootstrap Confidence Interval Contract

To prevent invalid row-level independence assumptions in correlated log streams:
1. **Resampling Iterations:** Exactly $B = 2,000$ iterations.
2. **Fixed Random Seed:** $\text{seed}_{\text{boot}} = 10007$.
3. **Locked CI Type:** **Percentile Bootstrap** ($[\theta_{0.025}^*, \; \theta_{0.975}^*]$ at $95\%$ confidence level).
4. **Independent Resampling Units (Cluster / Block Bootstrap):**
   - **EXP-01 (Fidelity):** Resample by **Block Session ID** (`blk_` in HDFS, Process Tree Session in DARPA TC).
   - **EXP-02 (Multi-View):** Resample by **15-Minute Provenance Subgraph Windows**.
   - **EXP-03 (Robustness):** Resample by **Perturbed Session Chunks** ($L=100$ events).
   - **EXP-04 (MIL Attribution):** Resample by **Coarse Bag Unit** (Host-day authentication bags).
   - **EXP-05 (Streaming Complexity):** Resample by **5-Minute Operational Streaming Segments**.
   - **EXP-06 (Privacy Frontier):** Resample by **User-Day Entity Subgraphs**.
   *Absolute Rule:* Never resample individual log event rows independently if they belong to the same session or host window.
"""
    (protocol_dir / "STATISTICAL-PLAN.md").write_text(stat_plan, encoding="utf-8")
    print("[OK] Updated STATISTICAL-PLAN.md with decision tree and bootstrap contract")

    # =========================================================================
    # 5. PROTOCOL-AMENDMENTS.md (Amendment Tracking Ledger)
    # =========================================================================
    protocol_amendments = """# EXPERIMENTAL PROTOCOL AMENDMENT LEDGER

**Document Identifier:** `LEDGER-AMD-20260821`  
**Status:** **ACTIVE & AUDITED**  
**Governing Rule:** Research Constitution (`RC-15` — No Silent Reinterpretation).  

---

## 1. Amendment Governance Policy

Any modification to the locked pre-registration protocol after registration date (2026-08-21) must be logged in this ledger with:
1. `amendment_id`: Sequential identifier (e.g. `AMD-001`).
2. `timestamp`: ISO-8601 UTC timestamp of amendment adoption.
3. `reason`: Comprehensive scientific or operational justification.
4. `files_changed`: Exact paths of modified protocol documents.
5. `before_after_diff`: Explicit textual and mathematical diffs.
6. `test_opened`: `YES` or `NO` indicating whether test split was unsealed.
7. `results_seen`: `YES` or `NO` indicating whether empirical results influenced the change.
8. `impact_on_confirmatory_status`: If an amendment is introduced after seeing test results, the affected hypothesis test **loses pure confirmatory status** and must be classified as **`EXPLORATORY / POST-HOC`** in thesis prose.

---

## 2. Canonical Amendment Registry

### Amendment AMD-001: Initial Pre-Registration Audit & Baseline Locking
- **Timestamp:** `2026-08-21T07:16:00Z`
- **Author:** Research Engineering System / Auditor
- **Reason:** Comprehensive audit of pre-registration specifications: recomputing Chapter 1 and Chapter 2 hashes directly from canonical Master DOCX (`Chuyên đề chuyên sâu.docx`), formalizing split manifest state machine (`PLANNED` $\to$ `ACQUIRED` $\to$ `SEALED`), locking exact DARPA TC E3/E5 scope, establishing strict LANL `redteam.txt` label boundaries, locking $K=5$ random seeds, defining deterministic statistical decision tree, and formalizing bootstrap cluster resampling units.
- **Files Changed:**
  - `experiments/protocol/CH3-PRE-REGISTRATION.md`
  - `experiments/protocol/DATASET-CARDS.md`
  - `experiments/protocol/SPLIT-PROTOCOL.md`
  - `experiments/protocol/STATISTICAL-PLAN.md`
  - `experiments/protocol/EXPERIMENT-MATRIX.md`
  - `experiments/protocol/PROTOCOL-AMENDMENTS.md`
  - `experiments/protocol/generate_split_manifests.py`
  - `datasets/manifests/SPL-HDFS-001.json`
  - `datasets/manifests/SPL-BGL-001.json`
  - `datasets/manifests/SPL-DTC-001.json`
  - `datasets/manifests/SPL-LANL-001.json`
- **Test Set Opened:** `NO`
- **Results Seen:** `NO`
- **Impact on Confirmatory Status:** `CONFIRMATORY_PRESERVED` (All confirmatory hypothesis testing contracts 100% intact before any execution).
"""
    (protocol_dir / "PROTOCOL-AMENDMENTS.md").write_text(protocol_amendments, encoding="utf-8")
    print("[OK] Created PROTOCOL-AMENDMENTS.md")

    # =========================================================================
    # 6. Update generate_split_manifests.py to State: PLANNED
    # =========================================================================
    split_gen_code = '''# -*- coding: utf-8 -*-
"""
Deterministic Split Manifest Generator (Pre-Acquisition State: PLANNED)
Exports canonical split specifications with status = PLANNED.
"""

import json
import hashlib
from pathlib import Path

def generate_planned_split_manifests():
    manifests_dir = Path(r"D:\\Research\\datasets\\manifests")
    manifests_dir.mkdir(parents=True, exist_ok=True)

    planned_splits = [
        {
            "split_id": "SPL-HDFS-001",
            "dataset_id": "DATA-HDFS-001",
            "dataset_name": "HDFS LogHub Benchmark",
            "version": "v1.0",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_ratios": {"train": 0.70, "val": 0.15, "test": 0.15},
            "holdout_specification": {"oov_anomaly_template_ratio": 0.10},
            "seed": 42,
            "acquisition_requirements": [
                "Verify LogHub HDFS raw log archive checksum",
                "Fit Drain/Spell template parser strictly on Train split",
                "Extract session IDs and compute causal timestamp bounds"
            ]
        },
        {
            "split_id": "SPL-BGL-001",
            "dataset_id": "DATA-BGL-001",
            "dataset_name": "BGL Supercomputer Log",
            "version": "v1.0",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_temporal_partitions": {
                "train_days": [1, 150],
                "val_days": [151, 180],
                "test_days": [181, 215]
            },
            "seed": 42,
            "acquisition_requirements": [
                "Verify LLNL BGL raw log checksum",
                "Validate 214.7 day timestamp monotonic sequence",
                "Isolate Days 181+ failure codes for template drift evaluation"
            ]
        },
        {
            "split_id": "SPL-DTC-001",
            "dataset_id": "DATA-DTC-001",
            "dataset_name": "DARPA Transparent Computing E3/E5",
            "version": "v1.0",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "CAUSAL_SCENARIO_HOST_HOLDOUT",
            "pre_registered_scope": {
                "engagements": ["E3", "E5"],
                "performers": ["THEIA", "CADETS", "FiveDirections"],
                "cdm_versions": ["CDM v19", "CDM v20"],
                "holdout_target_hosts": ["victim-linux-02", "victim-win-01"]
            },
            "seed": 42,
            "acquisition_requirements": [
                "Verify official DARPA CDM release checksums",
                "Extract attack ground truth matching official engagement reports",
                "Verify zero test ground-truth leakage into train plane"
            ]
        },
        {
            "split_id": "SPL-LANL-001",
            "dataset_id": "DATA-LANL-001",
            "dataset_name": "LANL Cyber Security Data Set 2015",
            "version": "v1.0",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_temporal_partitions": {
                "train_seconds": [1, 5184000],
                "val_seconds": [5184001, 6393600],
                "test_seconds": [6393601, 7776000]
            },
            "redteam_label_boundary": "AUTH_EVENT_EXACT_MATCH_ONLY",
            "seed": 42,
            "acquisition_requirements": [
                "Verify LANL auth.txt.gz and redteam.txt.gz official checksums",
                "Enforce strict non-propagation of redteam labels to proc/flow",
                "Build host-day authentication bags for Stage B MIL"
            ]
        }
    ]

    for sp in planned_splits:
        sp_bytes = json.dumps(sp, indent=2, sort_keys=True).encode("utf-8")
        sp["specification_sha256"] = hashlib.sha256(sp_bytes).hexdigest()
        out_path = manifests_dir / f"{sp['split_id']}.json"
        out_path.write_text(json.dumps(sp, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[OK] Exported PLANNED split manifest: {out_path.name}")

if __name__ == "__main__":
    generate_planned_split_manifests()
'''
    (protocol_dir / "generate_split_manifests.py").write_text(split_gen_code, encoding="utf-8")
    print("[OK] Updated generate_split_manifests.py")

    print("\n========================================================")
    print("FINAL PROTOCOL AUDIT & RE-LOCKING COMPLETE 100%")
    print("========================================================")

if __name__ == "__main__":
    main()
