# Stage A2 Five-Seed Forensic Provenance Reconciliation Report

**Audit Date:** 2026-09-10  
**Branch:** `fix/stage-a2-forensic-reconciliation`  
**Base Commit:** `585223e3deba67665c92bdd0cfb9fc71c8420b2f`  
**Auditor:** Senior Research Reproducibility Engineer + Scientific Auditor + DOCX Engineer  

---

## 1. Executive Summary & Seed Classification

| Seed | Classification | Status | Epochs | Steps | Best Epoch | Best Val Loss | Final Train Loss | Execution Commit | Provenance Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seed 7** | `CANONICAL_WITH_DOCUMENTED_AMENDMENT` | COMPLETED | 12 | 6,876 | 12 | `0.550259` | `0.160910` | `e4d53b82...` | Verified in Git & Remote |
| **Seed 999** | `CANONICAL_WITH_DOCUMENTED_AMENDMENT` | COMPLETED | 12 | 6,876 | 12 | `0.609500` | `0.159004` | `e4d53b82...` | Verified in Git & Remote |
| **Seed 42** | `CANONICAL_WITH_DOCUMENTED_AMENDMENT` | EARLY_STOPPED | 4 | 2,292 | 1 | `6.081352` | `0.308279` | `33269cbe...` | Verified in Git & Remote |
| **Seed 1337** | `NONCANONICAL` | INCOMPLETE/HALTED | 12 | 6,876 | 10 | `0.917827` | `0.184784` | `33269cbe...` | Scheduler mismatch (20 vs 12), missing manifest/metrics |
| **Seed 2024** | `NONCANONICAL` | COMPLETED_FLAWED | 12 | 6,876 | 12 | `0.553257` | `0.167085` | `e4d53b82...` / `00ce524e` | Phantom commit in completion record, retroactive authorization |

- **Canonical Seeds (3/5):** Seed 7, Seed 999, Seed 42.
- **Noncanonical Seeds (2/5):** Seed 1337, Seed 2024.

---

## 2. Statistical Aggregates

### Canonical Converged Subset (Seeds 7, 999 — $N=2$):
- **Mean Best Val Loss:** $\frac{0.550259 + 0.609500}{2} = 0.579880$
- **Std Best Val Loss (sample):** $0.041890$
- **Mean Final Train Loss:** $\frac{0.160910 + 0.159004}{2} = 0.159957$
- **Mean Final Val Loss:** $0.579880$

### All Canonical Seeds (Seeds 7, 999, 42 — $N=3$):
- **Mean Best Val Loss:** $\frac{0.550259 + 0.609500 + 6.081352}{3} = 2.413704$
- **Std Best Val Loss (sample):** $3.176319$
- **Mean Final Train Loss:** $\frac{0.160910 + 0.159004 + 0.308279}{3} = 0.209398$

---

## 3. Invariants & Security
- **Test Set Opened:** `false` (0 test reads).
- **New Optimizer Steps:** `0`.
- **Hardware & Environment Lock:** SHA-256 `81d3ca4865a95c75cc2345695091265f948ad58e705865a3f8f780a9bf09f362` preserved.
