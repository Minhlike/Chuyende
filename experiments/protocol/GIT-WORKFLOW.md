# GIT WORKFLOW & REPOSITORY GOVERNANCE POLICY

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
