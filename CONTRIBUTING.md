# CONTRIBUTING & SCIENTIFIC GOVERNANCE GUIDELINES

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
