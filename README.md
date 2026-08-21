# Log Feature Representation Research Engineering System

**Project Title:** *Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công*  
**Subject:** Feature representation vector / manifold $\mathbf{z} \in \mathbb{R}^d$  
**Core Abstraction:** $f_\theta : \mathcal{L}_{1:t} \to \mathbf{z}_t$  
**Master Document:** [`Chuyên đề chuyên sâu.docx`](file:///D:/Research/Chuyên%20đề%20chuyên%20sâu.docx)  
**Master DOCX SHA-256:** `07cdd037868ffbca135498d077bdef291c6e5638b619d41b60175d80cac80463`  

---

## 1. Research Scope & Invariants

This repository hosts the canonical codebase, formal specifications, and experimental protocols for the PhD-level research study on multi-view, privacy-aware log feature representation.

### Foundational Invariants (Research Constitution):
1. **Raw Evidence $\to$ Verified Knowledge $\to$ Explicit Reasoning $\to$ Defensible Claims $\to$ Academic Prose** (`RC-01`–`RC-18`).
2. **No Fabricated Sources (`RC-01`) & No Fabricated Numbers (`RC-02`):** Zero tolerance for hallucinated literature or un-grounded empirical metrics.
3. **Extractor–Detector Boundary (`BOUNDARY-04`):** The research object is strictly the representation extractor $f_\theta$, evaluated via capacity-controlled frozen probes on sealed test data.
4. **Causal Time Partitions (`CTRL-LEAK-001`):** Strict time-arrow splitting ($	ext{Train} < 	ext{Val} < 	ext{Test}$). Preprocessors fit on Train only; hyperparameters and thresholds tuned on Validation only; Test split sealed.

---

## 2. Thesis Structure & Current State

| Chapter | Topic | Status | Cryptographic Checksum (`DOCX_CANONICAL_CONTENT_HASH_V1`) |
| :--- | :--- | :--- | :--- |
| **Chapter 1** | Overview & Security Semantic Preservation Challenges | **FROZEN** | `b7912883570e369e765c7a6daa7fc626db570c8b53050e976d4f652a2dc7e16e` |
| **Chapter 2** | Proposed Multi-View Privacy-Aware Representation | **FROZEN** | `e91bbc47de218d037d5dec3192b6ba59fda4e3c7423e51c34aea898d3db25a01` |
| **Chapter 3** | Experiments, Evaluation & Applications | **PRE-REGISTRATION LOCKED** | *All experiments in `PLANNED` state (Zero Test Snooping)* |

---

## 3. Directory Layout

```text
D:\Research\
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
