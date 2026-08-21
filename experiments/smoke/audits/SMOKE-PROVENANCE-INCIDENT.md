# SMOKE PROVENANCE AUDIT INCIDENT REPORT

**Document ID:** `AUDIT-INC-SMOKE-20260822-01`  
**Timestamp:** 2026-08-22T02:35:00+07:00  
**Severity:** HIGH (Artifact Overwrite & Non-Hermetic Test Contamination)  
**Status:** RESOLVED  
**Branch:** `smoke/ch3-train-validation`

---

## 1. Incident Summary
During the initial smoke test execution for Chapter 3 validation, two distinct smoke runs were triggered in sequence:
1. **Manual Canonical Smoke Run (`SMOKE-1787339250`):**
   - Executed via `scripts/run_smoke.py`.
   - Configuration: 2 epochs, 8 optimizer steps, batch size 16, 64 training windows, 16 validation windows.
   - Result: All 7 individual losses finite ($L_{\text{MEP}}=3.3233$, $L_{\text{MPP}}=2.2319$, $L_{\text{time}}=0.1065$, $L_{\text{mask-node}}=1.9596$, $L_{\text{mask-edge}}=0.7570$, $L_{\text{time-gap}}=0.3100$, $L_{\text{VICReg}}=44.7155$), 0 unexpected zero-gradients, optimizer updated parameters.
2. **Automated Test Run (`SMOKE-1787339433`):**
   - Executed as part of `pytest tests/test_smoke_runner.py`.
   - Configuration: 1 epoch, 2 optimizer steps, batch size 8, 16 training windows, 8 validation windows.
   - Cause of Overwrite: `test_smoke_runner.py` instantiated `SmokeTestRunner` directly with the repository root `base_dir=Path('/mnt/d/Research')`, causing it to write its test output directly into the fixed files `experiments/smoke/SMOKE-RUN-MANIFEST.json` and `experiments/smoke/SMOKE-REPORT.md`.

---

## 2. Root Cause Analysis
- **Root Cause 1 (Fixed Path Collisions):** The original `SmokeTestRunner` wrote artifacts to static flat file paths (`experiments/smoke/SMOKE-RUN-MANIFEST.json`, `SMOKE-REPORT.md`) instead of isolated, immutable run directories.
- **Root Cause 2 (Non-Hermetic Unit Tests):** `tests/test_smoke_runner.py` executed against the live workspace rather than an isolated `tmp_path` fixture with synthetic smoke data.

---

## 3. Remediation Actions
1. **Immutable Run Subdirectories:**
   Refactored `SmokeTestRunner` to write all run artifacts to dedicated, immutable subdirectories:
   `experiments/smoke/runs/<SMOKE_RUN_ID>/`
   - `manifest.json`
   - `subset-manifest.json`
   - `train-log.jsonl`
   - `validation-log.jsonl`
   - `report.md`
   `experiments/smoke/LATEST.json` tracks the latest run ID without mutating historical run data.
2. **Hermetic Test Harness:**
   Refactored `tests/test_smoke_runner.py` to run exclusively inside pytest's isolated `tmp_path` using synthetic mock fixtures (`SYNTHETIC_TEST_ONLY`), guaranteeing that test runs never touch the live workspace or overwrite canonical smoke artifacts.
3. **Artifact Integrity Verification:**
   Added a regression test asserting that canonical smoke run files in `experiments/smoke/runs/` maintain identical SHA-256 checksums before and after full `pytest` execution.
