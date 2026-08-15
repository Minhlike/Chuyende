# SYSTEM ARCHITECTURE
**Project:** Log Feature Extraction Research Engineering System  
**Subject:** *Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công*  
**Central Focus:** Feature representation vector / manifold \( \mathbf{z} \in \mathbb{R}^d \)  
**Version:** 1.0.0-bootstrap  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Executive Summary & Architectural Philosophy

The Research Engineering System is a local-first, verifiable, and audit-compliant scientific research system. Its core objective is to support the doctoral/master-level thesis research on log data feature extraction for attack detection.

### 1.1 Non-Negotiable Core Principle
```text
RAW EVIDENCE ──► VERIFIED KNOWLEDGE ──► EXPLICIT REASONING ──► DEFENSIBLE CLAIM ──► ACADEMIC PROSE
```

### 1.2 Clear Research Boundary
The central research subject is the **feature representation** \( \mathbf{z} = f_\theta(x) \) extracted from heterogeneous, multi-source log records \( x \) under constraints of adversarial evasion, distribution shifts, provenance tracking, privacy preservation, and label noise (e.g., Multiple Instance Learning). The system is **NOT** a turnkey intrusion detection appliance; it is a scientific testbed and evidence graph for evaluating representations.

---

## 2. Layered Architecture

The system is organized into decoupled architectural tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LEVEL 5: SYNTHESIS & AUDIT                        │
│   • Chapter Composer (Stubs)              • Thesis Auditor (Stubs)          │
│   • Citation & Ownership Formatter        • Invariant Gatekeeper            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        LEVEL 4: RESEARCH MEMORY (M0–M5)                     │
│   • M0: Working Memory                    • M3: Episodic Research Memory    │
│   • M1: Source Canonical Memory           • M4: Argument Graph Memory       │
│   • M2: Semantic Claims & Concepts        • M5: Procedural Protocols/Skills │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LEVEL 3: EXPERIMENT & ARTIFACT LINEAGE                   │
│   • Dataset & Split Registry              • Experiment Run Manifests        │
│   • Equation Registry (LaTeX/Symbols)     • Table & Figure Hash Lineage     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LEVEL 2: EPISTEMIC & KNOWLEDGE LEDGER                    │
│   • Claim Ledger (Types, Status, Owners)  • Evidence Ledger (Locators)      │
│   • Argument Graph (13 Edge Types)        • Contradiction Records           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                  LEVEL 1: CANONICAL STORAGE & FILE PERSISTENCE              │
│   • SQLite Relational Database (Canonical Tables)                           │
│   • Filesystem Immutable Tree (YAML / JSON / Markdown Artifacts)            │
│   • SHA-256 Checksum Engine                                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LEVEL 0: INFRASTRUCTURE & PATH GUARDS                    │
│   • PathGuard (Strict D:\Research boundary isolation)                       │
│   • Untrusted Document Isolator (Data != System Instruction)                │
│   • Deterministic ID Generator (SRC-, CLM-, EVD-, ARG-, EQ-, EXP-, etc.)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Epistemic Model & Canonical Schemas

### 3.1 Claim & Evidence Architecture
Scientific assertions are never raw strings. Every claim is an atomic entity:
- **Identifier:** Deterministic string (`CLM-000001`).
- **Claim Types:** `SOURCE_FACT`, `SOURCE_CLAIM`, `SYNTHESIS`, `OUR_INFERENCE`, `OUR_DESIGN`, `EXPERIMENT_RESULT`, `HYPOTHESIS`.
- **Intellectual Ownership:** `SOURCE`, `ADAPTED`, `OURS`, `BASELINE`.
- **Epistemic Status:** `UNVERIFIED`, `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTESTED`, `FALSIFIED`, `SUPERSEDED`.
- **Relational Proof Trace:** Explicit link to one or more `EVD-xxxxxx` entities or `RUN-xxxxxx` experiment runs.

### 3.2 Argument Graph
The argument graph captures logical relationships between claims and evidence nodes using 13 canonical edge types:
1. `SUPPORTS`: Direct empirical or deductive validation.
2. `CONTRADICTS`: Empirical divergence or logical incompatibility.
3. `QUALIFIES`: Narrowing operational boundary conditions or assumptions.
4. `DEPENDS_ON`: Upstream prerequisite knowledge or theorem.
5. `ASSUMES`: Explicit baseline assumption.
6. `DERIVED_FROM`: Mathematical or empirical derivation.
7. `GENERALIZES`: Extension of finding to higher-dimensional domain.
8. `SPECIALIZES`: Instantiation of abstract theory to log domain.
9. `FALSIFIES`: Experimental or theoretical refutation.
10. `REPLICATES`: Independent replication confirming prior finding.
11. `FAILS_TO_REPLICATE`: Independent replication failing to match prior metric.
12. `MOTIVATES`: Empirical problem prompting new representation design.
13. `COMPARES_WITH`: Direct head-to-head benchmark evaluation.

### 3.3 Equation Registry & Symbol Scoping
Equations are classified as `SOURCE_EQUATION`, `DERIVED_EQUATION`, or `PROPOSED_EQUATION`.
To prevent semantic collision:
- Every symbol (e.g., \( \alpha, \lambda, \mathbf{z} \)) within an equation is tied to an explicit `SymbolDefinition` with dimension, domain, and contextual meaning.
- Two equations using the same letter do not inherit the same semantics unless explicitly linked to the same canonical symbol definition.

### 3.4 Data, Table & Figure Provenance
Figures and tables are derived artifacts with cryptographic lineage:
```text
Raw Dataset (SHA-256) ──► Transformation Script (Git Hash) ──► Experiment Run ──► Output Artifact (SHA-256)
```
No visual artifact can be registered without its parent dataset and run provenance.

---

## 4. Multi-Tier Long-Term Memory Hierarchy

The system structures persistent research memory into six tiers:

| Tier | Name | Storage Subsystem | Mutability | Role |
| :--- | :--- | :--- | :--- | :--- |
| **M0** | Working Memory | Session / Runtime | Volatile | Active reasoning context, scratchpad, transient step states. |
| **M1** | Source Memory | Filesystem + SQLite | Immutable once ingested | Original papers, PDFs, datasets, bibtex metadata, source versions. |
| **M2** | Semantic Memory | SQLite + JSON | Versioned Canonical | Atomic claims, definitions, verified conceptual models, taxonomy. |
| **M3** | Episodic Memory | SQLite + Markdown | Append-only | Experiment history, audit logs, trial attempts, failure analyses. |
| **M4** | Argument Memory | SQLite Relational Graph | Dynamic Graph | Claim-evidence graph, contradiction records, epistemic states. |
| **M5** | Procedural Memory | Markdown Protocols | Versioned Canonical | Research skills, execution protocols, invariant checklists, rubrics. |

> [!IMPORTANT]
> Vector embeddings, BM25 indices, and graph caches are **Derived Index Artifacts**. If `runtime/indexes` or `runtime/cache` is wiped, the system reconstructs all indices deterministically from M1–M5 canonical stores.

---

## 5. Stable Identifier Strategy

All entities utilize typed, monotonic, padded human-readable identifiers:

| Prefix | Entity | Example |
| :--- | :--- | :--- |
| `PRJ-` | Research Project | `PRJ-000001` |
| `ROD-` | Research Roadmap | `ROD-000001` |
| `NOD-` | Research Roadmap Node | `NOD-000001` |
| `RQ-` | Research Question | `RQ-000001` |
| `HYP-` | Hypothesis | `HYP-000001` |
| `SRC-` | Source Record | `SRC-000001` |
| `SRA-` | Source Artifact | `SRA-000001` |
| `EVD-` | Evidence Item | `EVD-000001` |
| `CLM-` | Atomic Claim | `CLM-000001` |
| `ARG-` | Argument Node | `ARG-000001` |
| `ARE-` | Argument Edge | `ARE-000001` |
| `EQ-` | Equation Record | `EQ-000001` |
| `SYM-` | Symbol Definition | `SYM-000001` |
| `DATA-` | Dataset Record | `DATA-000001` |
| `DSV-` | Dataset Version | `DSV-000001` |
| `EXP-` | Experiment Specification | `EXP-000001` |
| `RUN-` | Experiment Run | `RUN-000001` |
| `TBL-` | Table Artifact | `TBL-000001` |
| `FIG-` | Figure Artifact | `FIG-000001` |
| `DEC-` | Architectural / Research Decision | `DEC-000001` |
| `CTR-` | Contradiction Record | `CTR-000001` |
| `MEM-` | Memory Record | `MEM-000001` |
| `SKL-` | Procedural Skill Record | `SKL-000001` |
| `VRF-` | Verification Audit Record | `VRF-000001` |

---

## 6. Directory Layout & Physical Mapping

```text
D:\Research
├── README.md                              # Root project manual
├── pyproject.toml                         # Python package specification
├── .gitignore                             # Ignore cache, venv, secrets, logs
├── .env.example                           # Configuration environment template
├── docs\
│   ├── RESEARCH-CONSTITUTION.md           # Supreme research invariants (RC-01..RC-18)
│   ├── ARCHITECTURE.md                    # This document
│   └── ADR\                               # Architecture Decision Records
│       ├── ADR-0001-local-first-hybrid-persistence.md
│       ├── ADR-0002-deterministic-stable-identifiers.md
│       ├── ADR-0003-epistemic-status-and-contradiction-preservation.md
│       ├── ADR-0004-derived-indexes-disposability.md
│       └── ADR-0005-path-containment-and-untrusted-content-isolation.md
├── research_specs\
│   ├── roadmap\                           # Versioned roadmap specifications (Prompt 2)
│   └── reference_map\                     # Versioned reference maps (Prompt 3)
├── sources\
│   ├── original\                          # Immutable primary source files (PDF, bibtex)
│   ├── metadata\                          # Extracted verified metadata
│   └── manifests\                         # Checksum and verification manifests
├── datasets\
│   ├── raw\                               # Unprocessed raw log datasets (immutable)
│   ├── processed\                         # Deterministically processed log splits
│   └── manifests\                         # Split manifests and hash registries
├── experiments\
│   ├── configs\                           # Reproducible YAML experiment configs
│   ├── runs\                              # Run execution records, seeds, metrics
│   └── manifests\                         # Experiment ledger manifests
├── artifacts\
│   ├── equations\                         # LaTeX equation definitions and proofs
│   ├── tables\                            # Generated markdown / LaTeX tables
│   └── figures\                           # Generated visual artifacts (SVG, PNG)
├── memory\
│   ├── procedural\                        # M5 Procedural skills and checklists
│   └── snapshots\                         # M2/M4 semantic state snapshots
├── src\
│   └── research_agent\
│       ├── __init__.py                    # Top-level package init
│       ├── config.py                      # Centralized configuration & path resolver
│       ├── core\                          # Invariants, enums, guards, IDs, hash
│       ├── schemas\                       # Strict Pydantic models for all entities
│       ├── storage\                       # SQLite relational schema & repository
│       ├── interfaces\                    # Ingestion and management contracts
│       ├── stubs\                         # Explicit NOT_IMPLEMENTED future modules
│       └── logging.py                     # Structured JSON/Console logger
├── tests\
│   ├── conftest.py                        # Pytest fixtures and isolated DB setup
│   ├── test_invariants.py                 # Tests for Constitution Invariants (TEST 1..8)
│   ├── test_guards.py                     # Path and workspace security tests (TEST 10)
│   ├── test_persistence.py                # Database and index rebuild tests (TEST 9)
│   └── test_stubs.py                      # Subsystem stub behavior verification
├── scripts\
│   ├── init_db.py                         # Database initialization script
│   ├── verify_invariants.py               # Automated integrity check utility
│   └── clean_derived_indexes.py           # Index disposal and recovery script
└── runtime\
    ├── db\                                # SQLite canonical database (research.db)
    ├── cache\                             # Discardable runtime cache
    ├── indexes\                           # Discardable vector/BM25 derived indices
    └── logs\                              # Execution logs
```

---

## 7. Security & Integrity Guardrails

1. **PathGuard:** All file reading, writing, and deletion operations validate target paths through `PathGuard.resolve_and_verify(path)`. Any path pointing outside `D:\Research` triggers immediate `SecurityPathViolationError`.
2. **Untrusted Content as Data:** Ingested papers, text excerpts, and logs are parsed purely as data payloads. They are never evaluated or passed into control-flow interpreters without sanitization.
3. **No Phantom Implementations:** Future subsystems (Symbolic Math Verifiers, Automated Chapter Composers, Statistical Hypothesis Auditors) explicitly raise `NotImplementedError` rather than returning mock success.
