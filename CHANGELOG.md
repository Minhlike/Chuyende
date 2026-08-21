# CHANGELOG & RESEARCH AUDIT TRAIL

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
