# -*- coding: utf-8 -*-
"""
Master Protocol Correction & Repository Governance Builder
Applies all 20 requirements of the pre-registration correction and git baseline gate.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

def main():
    root_dir = Path(r"D:\Research")
    protocol_dir = root_dir / "experiments" / "protocol"
    manifests_dir = root_dir / "datasets" / "manifests"
    github_dir = root_dir / ".github"

    protocol_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    github_dir.mkdir(parents=True, exist_ok=True)

    master_docx_sha256 = "07cdd037868ffbca135498d077bdef291c6e5638b619d41b60175d80cac80463"
    ch1_norm_hash = "b7912883570e369e765c7a6daa7fc626db570c8b53050e976d4f652a2dc7e16e"
    ch2_norm_hash = "e91bbc47de218d037d5dec3192b6ba59fda4e3c7423e51c34aea898d3db25a01"
    hash_algo_version = "DOCX_CANONICAL_CONTENT_HASH_V1"

    # =========================================================================
    # 1. .gitignore
    # =========================================================================
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.env.*
!.env.example
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
node_modules/

# Testing & Coverage
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# IDE & Editors
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
desktop.ini

# Secrets, keys & credentials
secrets/**
credentials*
*.key
*.pem
*.log

# Raw Datasets & Binary Caches (RC-16)
datasets/raw/**
!datasets/raw/.gitkeep
datasets/processed/**
!datasets/processed/.gitkeep
datasets/cache/**

# Experiments Runs, Checkpoints & Scratch Caches (RC-10)
experiments/runs/**
!experiments/runs/.gitkeep
experiments/checkpoints/**
experiments/cache/**

# SQLite binary databases (Disposable runtime indexes RC-17)
*.db
*.sqlite
*.sqlite3
runtime/db/*
!runtime/db/.gitkeep

# Word COM Automation temporary & debug files
*.tmp
mso*.tmp
~$*.docx
*.backup.docx
*.pre_*.docx
tmp*.docx
test_canvas.*
test_clean_eqs*
test_omath*
test_lists.docx
test_repair_tgn.docx
test_single_eq.docx
test_superscripts.*
test_current_word.pdf
clean_tgn_buildup.docx
test_ps.txt

# Rendered PDF & PNG Visual Debug Dumps (disposable derived artifacts)
pdf_closure_pages/
pdf_closure_pages2/
pdf_hotfix_pages/
pdf_pages/
current_audit_pages/
final_rendered_pages/
runtime/qa_*
visual_check_*.png
fig_page_*.png
lo_build/
"""
    (root_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")
    print("[OK] Wrote comprehensive .gitignore")

    # =========================================================================
    # 2. README.md
    # =========================================================================
    readme_content = f"""# Log Feature Representation Research Engineering System

**Project Title:** *Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công*  
**Subject:** Feature representation vector / manifold $\\mathbf{{z}} \\in \\mathbb{{R}}^d$  
**Core Abstraction:** $f_\\theta : \\mathcal{{L}}_{{1:t}} \\to \\mathbf{{z}}_t$  
**Master Document:** [`Chuyên đề chuyên sâu.docx`](file:///D:/Research/Chuyên%20đề%20chuyên%20sâu.docx)  
**Master DOCX SHA-256:** `{master_docx_sha256}`  

---

## 1. Research Scope & Invariants

This repository hosts the canonical codebase, formal specifications, and experimental protocols for the PhD-level research study on multi-view, privacy-aware log feature representation.

### Foundational Invariants (Research Constitution):
1. **Raw Evidence $\\to$ Verified Knowledge $\\to$ Explicit Reasoning $\\to$ Defensible Claims $\\to$ Academic Prose** (`RC-01`–`RC-18`).
2. **No Fabricated Sources (`RC-01`) & No Fabricated Numbers (`RC-02`):** Zero tolerance for hallucinated literature or un-grounded empirical metrics.
3. **Extractor–Detector Boundary (`BOUNDARY-04`):** The research object is strictly the representation extractor $f_\\theta$, evaluated via capacity-controlled frozen probes on sealed test data.
4. **Causal Time Partitions (`CTRL-LEAK-001`):** Strict time-arrow splitting ($\text{{Train}} < \text{{Val}} < \text{{Test}}$). Preprocessors fit on Train only; hyperparameters and thresholds tuned on Validation only; Test split sealed.

---

## 2. Thesis Structure & Current State

| Chapter | Topic | Status | Cryptographic Checksum (`{hash_algo_version}`) |
| :--- | :--- | :--- | :--- |
| **Chapter 1** | Overview & Security Semantic Preservation Challenges | **FROZEN** | `{ch1_norm_hash}` |
| **Chapter 2** | Proposed Multi-View Privacy-Aware Representation | **FROZEN** | `{ch2_norm_hash}` |
| **Chapter 3** | Experiments, Evaluation & Applications | **PRE-REGISTRATION LOCKED** | *All experiments in `PLANNED` state (Zero Test Snooping)* |

---

## 3. Directory Layout

```text
D:\\Research\\
├── research_specs/          # Canonical specifications (Roadmap, Reference Map, Claims)
├── docs/                   # System architecture documents and Constitution
├── experiments/
│   ├── protocol/           # Pre-registration protocols, matrices, and statistical plans
│   ├── configs/            # Extractor and baseline model configurations
│   ├── manifests/          # Execution manifests
│   └── runs/               # Deterministic machine-readable execution logs (run_id)
├── datasets/
│   └── manifests/          # Split manifests (SPL-HDFS-001, SPL-BGL-001, etc.)
├── src/research_agent/     # Core Python research engineering engine
├── scripts/                # Deterministic compilation, auditing and hashing scripts
└── tests/                  # Pytest verification suites (invariants, statistics, reasoning)
```

---

## 4. Reproducibility & Governance Rules

- **Protocol-First Execution:** No official neural training or test evaluation is permitted without a pre-registered protocol.
- **Git Branching Policy:** All scientific, methodological, and experimental changes must occur on dedicated branches (`protocol/*`, `data/*`, `experiment/*`, `feat/*`) and pass verification gates before merging into `main`.
"""
    (root_dir / "README.md").write_text(readme_content, encoding="utf-8")
    print("[OK] Wrote README.md")

    # =========================================================================
    # 3. CONTRIBUTING.md
    # =========================================================================
    contributing_content = """# CONTRIBUTING & SCIENTIFIC GOVERNANCE GUIDELINES

## 1. Branch Policy

The `main` branch represents the **verified, gate-passed research baseline**. Direct commits to `main` are strictly prohibited for any substantive scientific modifications.

### Mandatory Branch Taxonomy:
- `protocol/<name>`: Pre-registration protocols, experiment matrices, metric contracts.
- `env/<name>`: Software environment, CUDA/PyTorch configurations.
- `data/<name>`: Dataset acquisition, parser scripts, split manifest generators.
- `feat/<name>`: Feature extractor architecture, representation mechanisms.
- `experiment/<exp-id>`: Experiment execution pipelines (e.g. `experiment/exp-01-fidelity`).
- `thesis/<section>`: Thesis composition and manuscript updates.
- `fix/<name>`: Bug fixes in supporting tooling.
- `audit/<name>`: Invariant checks, hash audits, and gate verifications.

---

## 2. Commit Message Standards

All commits must be atomic and follow conventional semantic prefixes:
- `protocol:` Modifications to pre-registration files and experimental contracts.
- `docs:` Documentation and architecture updates.
- `data:` Dataset schemas, manifest generators, parser implementations.
- `feat:` Core extractor or downstream probe implementations.
- `fix:` Tooling bug fixes.
- `test:` Unit tests and verification assertions.
- `experiment:` Experiment pipeline scripts and configuration definitions.
- `thesis:` Thesis drafting and typesetting scripts.
- `audit:` Invariant auditing, cryptographic hashing, and gate checks.

---

## 3. Pre-Merge Verification Gates

A branch may only be merged into `main` after:
1. `python scripts/verify_invariants.py` passes 100%.
2. All pytest test suites in `tests/` pass.
3. Frozen Chapter 1 and Chapter 2 hashes remain unchanged.
4. No secrets, raw large datasets, or temporary debug files are staged.
"""
    (root_dir / "CONTRIBUTING.md").write_text(contributing_content, encoding="utf-8")
    print("[OK] Wrote CONTRIBUTING.md")

    # =========================================================================
    # 4. CHANGELOG.md
    # =========================================================================
    changelog_content = """# CHANGELOG & RESEARCH AUDIT TRAIL

## [1.0.0] - 2026-08-21
### Added
- Pre-registration protocol suite in `experiments/protocol/` (`CH3-PRE-REGISTRATION.md`, `DATASET-CARDS.md`, `SPLIT-PROTOCOL.md`, `EXPERIMENT-MATRIX.md`, `METRIC-CONTRACT.md`, `BASELINE-FAIRNESS.md`, `ROBUSTNESS-PROTOCOL.md`, `PRIVACY-PROTOCOL.md`, `STATISTICAL-PLAN.md`, `RESULT-PROVENANCE-SCHEMA.md`, `ENVIRONMENT-MANIFEST-SCHEMA.yaml`, `GIT-WORKFLOW.md`, `REPOSITORY-STATE.md`, `PROTOCOL-AMENDMENTS.md`).
- Master DOCX canonical content hash extraction tool (`scripts/compute_docx_chapter_hashes.py`).
- Causal split manifest state machine (`PLANNED` -> `ACQUIRED` -> `SEALED`) and manifest generator.
- Repository governance files (`.gitignore`, `README.md`, `CONTRIBUTING.md`, `.github/pull_request_template.md`).

### Fixed
- Fixed DARPA TC Schema specification: Engagement 3 uses `CDM18` (corrected from CDM19); Engagement 5 uses `CDM20`.
- Explicitly separated DARPA TC Official Performer Universe (CADETS, ClearScope, FiveDirections, THEIA, TRACE) from Our Pre-Registered Experimental Subset (THEIA, CADETS, FiveDirections).
- Corrected LANL `redteam.txt` record count to `PENDING_VERIFICATION` prior to physical dataset acquisition.
- Removed sample-size underpowered Shapiro-Wilk decision gate for $K=5$ seeds; established Paired Cluster Bootstrap as the primary confirmatory inference method.
- Established rigorous cluster resampling unit audit for EXP-01 through EXP-06 with non-overlap and temporal leakage rules.
- Formalized effect-size hierarchy with absolute difference as primary metric.
"""
    (root_dir / "CHANGELOG.md").write_text(changelog_content, encoding="utf-8")
    print("[OK] Wrote CHANGELOG.md")

    # =========================================================================
    # 5. .github/pull_request_template.md
    # =========================================================================
    pr_template = """## Summary of Changes

### Scope of Pull Request:
- [ ] `protocol`: Experimental protocol or pre-registration amendment
- [ ] `data`: Dataset processing, parser, or split manifest
- [ ] `feat`: Model architecture or extractor implementation
- [ ] `experiment`: Experiment runner or configuration
- [ ] `thesis`: Academic composition or typesetting
- [ ] `audit`: Invariant verification or hash audit

### Verification Checklist:
- [ ] `python scripts/verify_invariants.py` passed with 0 violations.
- [ ] `pytest tests/` passed 100%.
- [ ] Frozen Chapter 1 & Chapter 2 hashes verified identical to baseline.
- [ ] No un-acquired raw dataset files or binary databases staged.
- [ ] No secrets, keys, or private tokens committed.
- [ ] If protocol modified, corresponding `PROTOCOL-AMENDMENTS.md` entry logged.
"""
    (github_dir / "pull_request_template.md").write_text(pr_template, encoding="utf-8")
    print("[OK] Wrote .github/pull_request_template.md")

    # =========================================================================
    # 6. DATASET-CARDS.md (DARPA CDM18/CDM20 & LANL Pending Count)
    # =========================================================================
    dataset_cards_content = """# DATASET PROTOCOL & CANONICAL DATASET CARDS

**Document Identifier:** `CARD-DATA-20260821-V1.1`  
**Protocol Version:** 1.1.0  
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
- **Version / Release:** `HDFS_v1` (LogHub release).
- **Acquisition State:** `PLANNED` (Record counts and raw checksums to be verified upon acquisition).
- **Observation Unit:** Event tuple $e_i$, Block session sequence $\mathcal{L}_{\text{blk}}$, sliding window.
- **Label Granularity:** Block ID binary label (`Normal` vs `Anomaly`).
- **Permitted Claims:** Parameter retention (Block ID, IP, byte count), parsing robustness, template abstraction.
- **Prohibited Overclaims:** Strictly prohibited from claiming cyberattack semantics or provenance graph reasoning (`BOUNDARY-01`).

---

### Dataset Card 2: BGL (Blue Gene/L Supercomputer)
- **Official Source:** LogHub Repository / Oliner & Stearley, IEEE/IFIP DSN 2007; Zhu et al., ISSRE 2023.
- **Version / Release:** `BGL_v1` (Lawrence Livermore National Laboratory release).
- **Acquisition State:** `PLANNED`.
- **Observation Unit:** Event message, Node temporal sequence, fixed time window $\Delta t$.
- **Label Granularity:** RAS alert category flag (`-` = non-alert, non-`-` = alert).
- **Permitted Claims:** Robustness against template drift, long-term temporal shift, OOV log templates.
- **Prohibited Overclaims:** Strictly prohibited from claiming cyberattack defense or lateral movement detection (`BOUNDARY-01`).

---

### Dataset Card 3: DARPA Transparent Computing (TC) Engagements E3 & E5

| Parameter | Official Release Specification | Our Pre-Registered Experimental Subset |
| :--- | :--- | :--- |
| **Engagements** | Engagement 3 (E3, April 2018) & Engagement 5 (E5, May 2019). | E3 and E5 official releases. |
| **Performer Universe** | **E3:** CADETS, ClearScope, FiveDirections, THEIA, TRACE.<br>**E5:** CADETS, ClearScope, FiveDirections, MARPLE, THEIA, TRACE. | **Selected Subset:**<br>1) **THEIA** (Linux LSM kernel audit);<br>2) **CADETS** (FreeBSD DTrace/Audit);<br>3) **FiveDirections** (Windows Sysmon/ETW). |
| **Subset Selection Rationale** | Diverse instrumentation paradigms across multiple OS kernels. | Pre-registered prior to test evaluation to provide multi-platform OS diversity with stable process-socket bindings. |
| **Schema Versions** | **E3: CDM18** (Common Data Model release 18).<br>**E5: CDM20** (Common Data Model release 20). | Strictly **CDM18** for E3 and **CDM20** for E5 (CDM19 count = 0). |
| **Ground Truth Reports** | *DARPA Transparent Computing Engagement 3 / 5 Evaluation Ground Truth Reports* (SPAWAR / MIT Lincoln Laboratory / BAE Systems). | Ground truth event mapping status: `PENDING_ARTIFACT_PARSE`. |
| **Acquisition State** | `PLANNED` | `PLANNED` |
| **Permitted Claims** | Kernel-level provenance graph representation, cross-view sequential-graph alignment, multi-stage APT attribution. | Evaluated with capacity-controlled frozen probes. |
| **Prohibited Overclaims** | Causal physical reality claims without explicit causal identification assumptions (`BOUNDARY-03`). | Arbitrary post-hoc performer selection. |

---

### Dataset Card 4: LANL Enterprise Multi-Source Cyber-Security Events

- **Official Source:** Los Alamos National Laboratory / Alexander D. Kent, 2015. DOI: 10.17021/1110439.
- **Version / Release:** `LANL_CyberSecurity_2015_v1` (`auth.txt.gz`, `proc.txt.gz`, `flows.txt.gz`, `redteam.txt.gz`).
- **Acquisition State:** `PLANNED`.
- **Red Team Record Count:** `PENDING_VERIFICATION` (Exact valid record count and file checksum verified upon physical archive acquisition).
- **Exact Red Team Label Invariant:**
  > **Hard Invariant:** The `redteam.txt` file contains known compromised authentication events only. Each entry is strictly an authentication 4-tuple: `(Time, User@Domain, SourceHost, DestHost)`.
- **Prohibited Label Propagation:**
  - Strictly **NO** propagation to `proc.txt` (processes are not automatically labeled malicious).
  - Strictly **NO** propagation to `flows.txt` or DNS telemetry.
  - Strictly **NO** expansion to arbitrary temporal windows, whole hosts, or whole user sessions without pre-registered uncertainty modeling.
- **Pre-Registered Weak Evidence Attribution Rule:**
  Coarse bag labels for Stage B MIL are formed over fixed host-day authentication bags $\mathcal{B}_{h, d}$. A bag is positive ($\mathcal{Y}_{\mathcal{B}} = 1$) if and only if it contains $\ge 1$ exact match in `redteam.txt`. All instances within the bag remain weakly labeled, and attention attribution uncertainty is reported.
"""
    (protocol_dir / "DATASET-CARDS.md").write_text(dataset_cards_content, encoding="utf-8")
    print("[OK] Updated DATASET-CARDS.md (CDM18/CDM20 & Pending Count)")

    # =========================================================================
    # 7. STATISTICAL-PLAN.md (Paired Cluster Bootstrap, Unit Audit, Effect Sizes)
    # =========================================================================
    stat_plan_content = """# STATISTICAL ANALYSIS PLAN & HYPOTHESIS TESTING CONTRACT

**Document Identifier:** `PLAN-STAT-20260821-V1.1`  
**Protocol Version:** 1.1.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-10`), Statistical Protocol (`docs/STATISTICAL-PROTOCOL.md`).  

---

## 1. Canonical Random Seed Stability Contract

- **Training Stability Runs:** Exactly $K = 5$ independent random seeds:
  $$\mathcal{K}_{\text{canonical}} = \{42, \; 1337, \; 2024, \; 7, \; 999\}$$
- **Role of $K=5$:** Evaluates stochastic training stability, parameter initialization sensitivity, and variance dispersion (reported as $\text{Mean} \pm \text{Standard Deviation}$ alongside individual-run dispersion).
- **Inferential Scope:** The $K=5$ seeds do **NOT** serve as the inferential sampling population for hypothesis testing.
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
│  6. Confirmatory Decision:                                                  │
│     H_supported if CI_95 lower bound > Delta_threshold                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Cluster Resampling Unit Audit (EXP-01..EXP-06)

To prevent severe optimistic bias caused by treating dependent log events as independent samples, every experiment defines a strict cluster resampling unit:

| Exp ID | Hypothesis | Cluster Resampling Unit | Non-Overlap Rule | Entity Leakage Rule | Temporal Boundary Rule | Independence Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-01** | **H1 (Fidelity)** | **Block Session ID / Process Execution Tree** | Each `blk_` ID or process tree is a disjoint cluster. | Parameters from one session cannot leak into another. | Bounded by session termination timestamp. | `PROVISIONAL` (Verified at acquisition) |
| **EXP-02** | **H2 (Multi-View)** | **15-Minute Provenance Subgraph Window** | Non-overlapping consecutive 15-min time chunks. | Edges crossing time chunk boundaries are handled via causal state snapshots. | Event-time watermark strictly enforced. | `PROVISIONAL` |
| **EXP-03** | **H3 (Robustness)** | **Perturbed Telemetry Session Chunk** ($L=100$) | Independent session chunks partitioned before perturbation. | Perturbation operators applied strictly within cluster. | No inter-chunk event reordering. | `PROVISIONAL` |
| **EXP-04** | **H4 (MIL Attribution)** | **Host-Day Authentication Bag** $\mathcal{B}_{h, d}$ | Disjoint host-day units ($h \in \mathcal{H}, d \in \mathcal{D}$). | User authentications across different days treated as distinct bags. | Daily 00:00:00–23:59:59 UTC boundary. | `PROVISIONAL` |
| **EXP-05** | **H4 (Streaming SLO)** | **5-Minute Operational Streaming Segment** | Consecutive non-overlapping 5-minute operational stream segments. | Memory state measured independently per segment. | Segment boundaries strictly ordered in causal time. | `PROVISIONAL` |
| **EXP-06** | **H5 (Privacy)** | **User-Day Entity Subgraph** | Disjoint user-day interaction clusters. | Linkage adversary evaluated across disjoint session pairs. | Session rotation boundary enforced. | `PROVISIONAL` |

*Invariant:* Event rows within the same cluster are never resampled independently.

---

## 5. Effect-Size Specification Contract

Effect sizes are defined hierarchically based on metric characteristics:

| Metric Category | Target Metrics | Primary Effect Size | Secondary Effect Size |
| :--- | :--- | :--- | :--- |
| **Detection Performance** | PR-AUC, Macro-F1, Recall@0.1% FPR | **Absolute $\Delta$** ($\Delta = \text{Score}_{\text{proposed}} - \text{Score}_{\text{baseline}}$) | Relative $\Delta$ percentage ($\frac{\Delta}{\text{Score}_{\text{base}}} \times 100\%$) |
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
| **Family 4 (H4 — Operational)** | 3 conjunctive SLO targets (Latency $\le 10\text{ms} \land \text{RAM} \le 500\text{MB} \land \text{Throughput} \ge 10^4$). | **Intersection-Union Test (IUT)** | Strict conjunctive compliance (all must pass at $\alpha = 0.05$, no $p$-value hunting). |
| **Family 5 (H5 — Privacy)** | 4 adversary leakage models ($\mathcal{A}_{\text{ReID}}, \mathcal{A}_{\text{Link}}, \mathcal{A}_{\text{MIA}}, \mathcal{A}_{\text{Inv}}$). | **Holm-Bonferroni Step-Down** | Sequential step-down testing across 4 adversary models. |
| **Exploratory Analyses** | Sub-population slicing, parameter sweeps, post-hoc ablation. | **Benjamini-Yekutieli FDR** | Must be explicitly labeled **`[EXPLORATORY]`**. |
"""
    (protocol_dir / "STATISTICAL-PLAN.md").write_text(stat_plan_content, encoding="utf-8")
    print("[OK] Updated STATISTICAL-PLAN.md (Paired Cluster Bootstrap & Unit Audit)")

    # =========================================================================
    # 8. EXPERIMENT-MATRIX.md
    # =========================================================================
    exp_matrix_content = """# CANONICAL EXPERIMENT MATRIX & FALSIFICATION PROTOCOL

**Document Identifier:** `MAT-EXP-20260821-V1.1`  
**Protocol Version:** 1.1.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-07`, `RC-10`, `RC-14`), Boundaries (`BOUNDARY-04`, `BOUNDARY-05`, `BOUNDARY-10`).  

---

## 1. Master Experiment Matrix

### Experiment EXP-01: Parameter Semantic Fidelity Test (Mapping: RQ1, H1, Axis A1)
- **Claim:** Parameter-aware representation ($X_{\\text{param}}$) preserves significantly higher security semantics than template-only abstraction.
- **Independent Variable:** Parameter representation mode (Full Subword Parameter Embedding vs Template-only vs Template+Wildcard).
- **Controlled Variables:** Sequence length ($L=100$), Model capacity (6-layer Transformer, $d=256$), Frozen linear probe capacity, Training split (`SPL-HDFS-001`, `SPL-DTC-001`), Canonical seeds ($K=5$).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$, seed 10007) over Block Session clusters.
- **Primary Effect Size:** Absolute $\\Delta \\text{PR-AUC}$.
- **Multiple Comparisons:** Bonferroni adjustment across 4 attack subtypes ($\\alpha' = 0.0125$).
- **Failure Criterion (Falsified):** 95% Bootstrap CI of $\\Delta \\text{PR-AUC}$ includes 0 ($p > 0.0125$).
- **Supported Criterion:** $\\Delta \\text{PR-AUC} \\ge +0.05$ with lower 95% CI bound $> 0$.

---

### Experiment EXP-02: Multi-View Alignment & Negative Transfer Test (Mapping: RQ2, H2, Axis A2)
- **Claim:** Controlled cross-view alignment ($\\mathbf{z}^{(\\text{seq})} \\leftrightarrow \\mathbf{z}^{(\\text{graph})}$) improves representation quality without variance collapse or negative transfer.
- **Independent Variable:** Alignment mechanism (InfoNCE vs VICReg vs Barlow Twins vs Unaligned Concat vs Single-view components).
- **Controlled Variables:** Event window ($\Delta t=15\\text{m}$), Feature dimension ($d=256$), Frozen probe capacity, Test split (`SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over 15-minute provenance subgraph windows.
- **Primary Effect Size:** Absolute $\\Delta \\text{PR-AUC}$ and Dimensional Variance $\\text{Var}(\\mathbf{z})$.
- **Multiple Comparisons:** Bonferroni adjustment across 3 component comparisons ($\\alpha' = 0.0167$).
- **Failure Criterion (Falsified):** $\\text{PR-AUC}(\\mathbf{z}_{\\text{mv}}) < \\max(\\text{PR-AUC}_{\\text{seq}}, \\text{PR-AUC}_{\\text{graph}})$ or $\\text{Var}(\\mathbf{z}) < 0.01$.
- **Supported Criterion:** $\\Delta \\text{PR-AUC} \\ge +0.03$ over best single-view with $\\text{Var}(\\mathbf{z}) \\ge 0.05$.

---

### Experiment EXP-03: Robustness Under Shortcut Removal & Distribution Shift (Mapping: RQ3, H3, Axis A3)
- **Claim:** Feature representation preserves discriminative utility after removing dataset shortcuts and under 12 perturbation attacks.
- **Independent Variable:** Telemetry condition (Clean vs Shortcut-masked vs OOV Template Holdout vs 12 Perturbations P01..P12).
- **Controlled Variables:** Pre-trained frozen extractor weights, Downstream probe capacity, Test splits (`SPL-BGL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over session chunks.
- **Primary Effect Size:** Absolute performance retention $\\text{PR-AUC}_{\\text{perturbed}} / \\text{PR-AUC}_{\\text{clean}}$ and geometric invariance distance $\\|\\mathbf{z}(T(X)) - \\mathbf{z}(X)\\|_2$.
- **Multiple Comparisons:** Benjamini-Hochberg FDR at $q^* = 0.05$ across 12 perturbations.
- **Failure Criterion (Falsified):** Performance collapses to random guessing (PR-AUC $\\le 0.50$) or converges to simple lexical baseline.
- **Supported Criterion:** Retention of $\\ge 85\\%$ baseline PR-AUC under semantic perturbations with significant margin over lexical baselines.

---

### Experiment EXP-04: Weak Evidence Attribution & Admin Confounder Control (Mapping: RQ4, Axis A4)
- **Claim:** Coarse bag supervision via attention MIL enables instance attribution without learning benign admin tools as malicious.
- **Independent Variable:** Supervision regime (Stage A SSL + Stage B Attention MIL vs Stage A SSL-only vs Mean-pooling MIL).
- **Controlled Variables:** Bag size ($K \\in [50, 500]$), Test splits (`SPL-LANL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over host-day authentication bags.
- **Primary Effect Size:** Absolute $\\Delta \\text{PR-AUC}$ on red-team instances and False Positive Rate on benign admin tools.
- **Failure Criterion (Falsified):** False positive rate on benign admin tools $> 15\\%$ or instance attribution does not exceed mean-pooling baseline.
- **Supported Criterion:** Instance PR-AUC exceeds mean-pooling by $\\ge +0.10$ with admin false positive rate $< 3.0\\%$.

---

### Experiment EXP-05: Operational Streaming Complexity & Bounded State Feasibility (Mapping: H4, Axis A5)
- **Claim:** Streaming extractor meets real-time SLOs: latency $\\le 10\\text{ms}$ (p95), peak memory $\\le 500\\text{MB/host}$, throughput $\\ge 10,000\\text{ events/s}$.
- **Independent Variable:** Ingestion stream rate ($10^2 \\dots 10^5$ events/s), Active host count ($1 \\dots 1000$).
- **Controlled Variables:** Fixed workstation hardware specification.
- **Evaluation Framework:** Conjunctive Intersection-Union Test (IUT) across SLO targets.
- **Primary Effect Size:** Absolute p95 latency (ms), Peak RAM (MiB), Throughput (events/s).
- **Failure Criterion (Falsified):** p95 extraction latency $> 10\\text{ms}$ or peak RAM $> 500\\text{MB/host}$ under nominal throughput.
- **Supported Criterion:** p95 latency $\\le 5.0\\text{ms}$, throughput $\\ge 25,000\\text{ events/s}$, peak RAM $\\le 250\\text{MB/host}$.

---

### Experiment EXP-06: Controlled Linkability & Utility–Privacy Pareto Frontier (Mapping: RQ5, H5, Axis A5)
- **Claim:** Controlled linkability establishes a Pareto-superior Utility–Privacy trade-off compared with raw identifiers and extreme anonymization.
- **Independent Variable:** Privacy regime and privacy budget $\\epsilon \\in \\{0.1, 0.5, 1.0, 2.0, 5.0\\}$.
- **Controlled Variables:** Downstream probe capacity, Test splits (`SPL-LANL-001`, `SPL-DTC-001`).
- **Primary Statistical Test:** Paired Cluster Bootstrap ($B=2000$) over user-day entity subgraphs.
- **Multiple Comparisons:** Holm-Bonferroni step-down testing across 4 adversary models.
- **Primary Effect Size:** Security PR-AUC vs Absolute Adversary Advantage Reduction $\\Delta \\text{Adv}$.
- **Failure Criterion (Falsified):** The empirical Pareto frontier is strictly dominated by raw identifiers or complete pseudonymization.
- **Supported Criterion:** Controlled linkability preserves $\\ge 90\\%$ utility while reducing ReID accuracy by $\\ge 60\\%$ and MIA advantage to $< 0.05$.
"""
    (protocol_dir / "EXPERIMENT-MATRIX.md").write_text(exp_matrix_content, encoding="utf-8")
    print("[OK] Updated EXPERIMENT-MATRIX.md")

    # =========================================================================
    # 9. PROTOCOL-AMENDMENTS.md (Adding AMD-002)
    # =========================================================================
    amendments_content = """# EXPERIMENTAL PROTOCOL AMENDMENT LEDGER

**Document Identifier:** `LEDGER-AMD-20260821`  
**Status:** **ACTIVE & AUDITED**  
**Governing Rule:** Research Constitution (`RC-15` — No Silent Reinterpretation).  

---

## 1. Amendment Governance Policy

Any modification to the locked pre-registration protocol after registration date (2026-08-21) must be logged in this ledger with:
1. `amendment_id`: Sequential identifier (e.g. `AMD-001`, `AMD-002`).
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
- **Reason:** Recomputed Chapter 1 and Chapter 2 hashes directly from canonical Master DOCX (`Chuyên đề chuyên sâu.docx`), formalized split manifest state machine (`PLANNED` $\to$ `ACQUIRED` $\to$ `SEALED`), and registered initial protocol suite.
- **Files Changed:** `experiments/protocol/*.md`
- **Test Set Opened:** `NO`
- **Results Seen:** `NO`
- **Impact on Confirmatory Status:** `CONFIRMATORY_PRESERVED`.

---

### Amendment AMD-002: DARPA TC Schema Correction, LANL Boundary & Statistical Protocol Hardening
- **Timestamp:** `2026-08-21T07:26:00Z`
- **Author:** Research Engineering System / Auditor
- **Reason:** Comprehensive audit corrections:
  1. Corrected DARPA TC Engagement 3 schema from CDM19 to official **CDM18**; confirmed Engagement 5 as **CDM20**.
  2. Disambiguated DARPA TC Official Performer Universe (CADETS, ClearScope, FiveDirections, THEIA, TRACE) from Our Pre-Registered Experimental Subset (THEIA, CADETS, FiveDirections).
  3. Formatted LANL `redteam.txt` record count as `PENDING_VERIFICATION` prior to physical dataset acquisition.
  4. Removed underpowered Shapiro-Wilk normality decision gate on $K=5$ seed differences; established **Paired Cluster Bootstrap** ($B=2000$, seed 10007) as primary confirmatory inference method.
  5. Established Cluster Resampling Unit Audit for EXP-01 through EXP-06 with non-overlap and temporal leakage rules.
  6. Formatted effect sizes with absolute difference as primary metric.
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
- **Impact on Confirmatory Status:** `CONFIRMATORY_PRESERVED`.
"""
    (protocol_dir / "PROTOCOL-AMENDMENTS.md").write_text(amendments_content, encoding="utf-8")
    print("[OK] Updated PROTOCOL-AMENDMENTS.md with AMD-002")

    # =========================================================================
    # 10. GIT-WORKFLOW.md & REPOSITORY-STATE.md
    # =========================================================================
    git_workflow_content = """# GIT WORKFLOW & REPOSITORY GOVERNANCE POLICY

**Document Identifier:** `POL-GIT-20260821`  
**Status:** **CANONICAL & INVIOLABLE**  

---

## 1. Branching Policy & Protection Semantics

The `main` branch represents the **gate-verified research baseline**.
- **No Direct Push to Main:** Substantive modifications (hypotheses, protocols, model architectures, dataset splits, statistics, evaluation code, or thesis claims) must NEVER be committed directly to `main`.
- **Allowed Direct Pushes to Main:** Minor typos, non-scientific documentation maintenance, `.gitignore` tweaks, and automated status logging — provided all verification checks pass.

### Branch Naming Conventions:
- `protocol/<short-name>`
- `env/<short-name>`
- `data/<short-name>`
- `feature/<short-name>`
- `experiment/<exp-id>`
- `thesis/<section>`
- `audit/<short-name>`
- `fix/<short-name>`

---

## 2. Commit Policy & Message Syntax

All commits must be atomic and categorized using typed prefixes:
- `protocol:` | `docs:` | `data:` | `feat:` | `fix:` | `test:` | `experiment:` | `thesis:` | `audit:`

---

## 3. Pre-Merge Gate & Data Exclusion Invariants

Before any branch merge into `main`:
1. `python scripts/verify_invariants.py` must pass with 0 errors.
2. Frozen Chapter 1 & Chapter 2 hashes must match canonical baseline.
3. No raw datasets (`datasets/raw/**`), binary caches (`*.db`), or debug dumps (`*.tmp`, `*.png`) may be committed.
4. No API keys, tokens, or environment credentials may be committed.
"""
    (protocol_dir / "GIT-WORKFLOW.md").write_text(git_workflow_content, encoding="utf-8")
    print("[OK] Wrote GIT-WORKFLOW.md")

    repo_state_content = f"""# CANONICAL REPOSITORY STATE LEDGER

**Current Milestone:** `CH3-PRE-REGISTRATION-GATE`  
**Last Updated:** `2026-08-21T07:26:00Z`  
**Master DOCX SHA-256:** `{master_docx_sha256}`  
**Chapter 1 Frozen Hash:** `{ch1_norm_hash}` (`{hash_algo_version}`)  
**Chapter 2 Frozen Hash:** `{ch2_norm_hash}` (`{hash_algo_version}`)  
**Test Set State:** `SEALED` (Zero Test Access)  
**Experiment State:** `PLANNED` (Zero Synthetic / Hallucinated Metrics)  
**Remote URL:** `https://github.com/Minhlike/Chuyende.git`  
"""
    (protocol_dir / "REPOSITORY-STATE.md").write_text(repo_state_content, encoding="utf-8")
    print("[OK] Wrote REPOSITORY-STATE.md")

    # =========================================================================
    # 11. generate_split_manifests.py (CDM18/CDM20 & Pending Count)
    # =========================================================================
    split_gen_code = '''# -*- coding: utf-8 -*-
"""
Deterministic Split Manifest Generator (Pre-Acquisition State: PLANNED)
Version: 1.1.0 (CDM18 for E3, CDM20 for E5, Pending LANL Verification)
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
            "version": "v1.1",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "CAUSAL_SCENARIO_HOST_HOLDOUT",
            "official_schemas": {
                "engagement_3": "CDM18",
                "engagement_5": "CDM20"
            },
            "official_performer_universe": [
                "CADETS", "ClearScope", "FiveDirections", "MARPLE", "THEIA", "TRACE"
            ],
            "pre_registered_experimental_subset": [
                "THEIA", "CADETS", "FiveDirections"
            ],
            "ground_truth_mapping_status": "PENDING_ARTIFACT_PARSE",
            "seed": 42,
            "acquisition_requirements": [
                "Verify official DARPA CDM18 (E3) and CDM20 (E5) checksums",
                "Extract attack ground truth matching official engagement reports",
                "Verify zero test ground-truth leakage into train plane"
            ]
        },
        {
            "split_id": "SPL-LANL-001",
            "dataset_id": "DATA-LANL-001",
            "dataset_name": "LANL Cyber Security Data Set 2015",
            "version": "v1.1",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_temporal_partitions": {
                "train_seconds": [1, 5184000],
                "val_seconds": [5184001, 6393600],
                "test_seconds": [6393601, 7776000]
            },
            "redteam_record_count": "PENDING_VERIFICATION",
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
    print("[OK] Wrote updated generate_split_manifests.py")

    print("\n========================================================")
    print("ALL PROTOCOL & GOVERNANCE FILES SUCCESSFULLY GENERATED")
    print("========================================================")

if __name__ == "__main__":
    main()
