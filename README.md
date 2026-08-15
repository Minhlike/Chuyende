# Log Feature Extraction Research Engineering System

**Subject:** *Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công*  
**Central Research Object:** Feature representation vector / manifold \( \mathbf{z} \in \mathbb{R}^d \)  
**Workspace Root:** `D:\Research`  
**Status:** Bootstrap Complete (Prompt 1/7)

---

## 1. Overview & Core Philosophy

This repository contains the canonical foundation of the **Research Engineering System** built to support scientific research on log data feature extraction for attack detection.

Unlike standard conversational chatbots or ungrounded generative systems, this platform enforces a strict epistemic and cryptographic pipeline:
```text
RAW EVIDENCE ──► VERIFIED KNOWLEDGE ──► EXPLICIT REASONING ──► DEFENSIBLE CLAIM ──► ACADEMIC PROSE
```

The system strictly bans fabricated literature, hallucinated numbers, ungrounded equations, and unverified data generation.

---

## 2. Research Constitution

The system's laws are codified in [`docs/RESEARCH-CONSTITUTION.md`](file:///D:/Research/docs/RESEARCH-CONSTITUTION.md):
- **RC-01:** No Fabricated Source (All citations bound to physical `SRC-xxxxxx` entities).
- **RC-02:** No Fabricated Number (Numerical assertions must have `Source` or `Computation` provenance).
- **RC-03:** Prose is not knowledge (Only typed, structured entities form canonical knowledge).
- **RC-04:** Claim Atomicity (Stable IDs e.g. `CLM-000001`).
- **RC-05:** Claim Type Taxonomy (`SOURCE_FACT`, `SOURCE_CLAIM`, `SYNTHESIS`, `OUR_INFERENCE`, `OUR_DESIGN`, `EXPERIMENT_RESULT`, `HYPOTHESIS`).
- **RC-06:** Intellectual Ownership (`SOURCE`, `ADAPTED`, `OURS`, `BASELINE`).
- **RC-07:** Epistemic Status Matrix (`UNVERIFIED`, `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTESTED`, `FALSIFIED`, `SUPERSEDED`).
- **RC-08:** Equation Provenance & Symbol Scoping (`SOURCE_EQUATION`, `DERIVED_EQUATION`, `PROPOSED_EQUATION`).
- **RC-09:** Data, Table & Figure Provenance (`Raw Data -> Transformation -> Derived Data -> Visual`).
- **RC-10:** Experiment Reproducibility Contract (Seeds, config, split hash, git commit, runtime environment).
- **RC-11:** Retrieval \(\neq\) Evidence.
- **RC-12:** Synthesis \(\neq\) Source Quotation.
- **RC-13:** Preservation of Contradictions (`ContradictionRecord` entities).
- **RC-14:** Preservation of Negative Results (Failed `ExperimentRun` records are preserved).
- **RC-15:** No Silent Reinterpretation (Roadmap and ownership specifications are immutable without explicit `DecisionRecord`).
- **RC-16:** Primary Artifact Immutability.
- **RC-17:** Disposability of Derived Indexes (Embeddings, BM25, and runtime caches are discardable and rebuildable).
- **RC-18:** Visibility of Failures (No swallowed exceptions or dummy success states).

---

## 3. Directory Layout

```text
D:\Research
├── README.md                              # This file
├── pyproject.toml                         # Packaging and dependencies
├── .gitignore                             # Ignore cache, logs, and venvs
├── .env.example                           # Environment configuration template
│
├── docs\
│   ├── RESEARCH-CONSTITUTION.md           # Supreme research laws
│   ├── ARCHITECTURE.md                    # System architecture & memory models
│   └── ADR\                               # Architectural Decision Records (ADR-0001..ADR-0005)
│
├── research_specs\
│   ├── roadmap\                           # Versioned roadmap specifications (Prompt 2)
│   └── reference_map\                     # Versioned reference maps (Prompt 3)
│
├── sources\                               # Primary literature & verified bibtex
├── datasets\                              # Raw & processed log datasets with split manifests
├── experiments\                           # Experiment configs, runs, and metric logs
├── artifacts\                             # LaTeX equations, markdown tables, SVG figures
├── memory\                                # Long-term memory (procedural skills & snapshots)
│
├── src\
│   └── research_agent\
│       ├── config.py                      # Workspace config & centralized path resolver
│       ├── core\                          # Invariants, enums, guards, IDs, hash
│       ├── schemas\                       # Strict Pydantic models for all entities
│       ├── storage\                       # SQLite relational schema & repository
│       ├── interfaces\                    # Ingestion and management contracts
│       ├── stubs\                         # Explicit NOT_IMPLEMENTED future modules
│       └── logging.py                     # Structured JSON/Console logger
│
├── tests\                                 # Pytest suite for critical invariants
├── scripts\                               # Database init, maintenance, and invariant verification
└── runtime\                               # Relational DB, disposable cache, and logs
```

---

## 4. Quickstart & Verification

### 4.1 Prerequisites
- Python 3.12+ (Installed at `C:\Users\Acer\AppData\Local\Programs\Python\Python312` or system PATH).

### 4.2 Initialize Database & Canonical Schemas
```powershell
python scripts/init_db.py
```

### 4.3 Run Test Suite
```powershell
python -m pytest tests/ -v
```

### 4.4 Verify Canonical Invariants
```powershell
python scripts/verify_invariants.py
```

### 4.5 Purge Derived Indexes & Caches (Disaster Recovery Demo)
```powershell
python scripts/clean_derived_indexes.py
```

---

## 5. Handoff Contract for Prompt 2

Prompt 2 will supply the complete **Research Roadmap Specification** (3 chapters, RQ1–RQ5, H1–H5, Representation Contracts).
The system is ready to ingest this specification via:
- Schema: [`research_agent.schemas.roadmap.ResearchRoadmap`](file:///D:/Research/src/research_agent/schemas/roadmap.py)
- Ingestion Service: [`research_agent.interfaces.roadmap_ingestion.RoadmapIngestionService`](file:///D:/Research/src/research_agent/interfaces/roadmap_ingestion.py)
- Storage Destination: `D:\Research\research_specs\roadmap\` and relational SQLite `roadmaps`, `roadmap_nodes`, `research_questions`, and `hypotheses` tables.
