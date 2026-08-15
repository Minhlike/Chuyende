# SKL-000002: Experiment Execution & Negative Result Logging Protocol (v1.0)

## Purpose
Enforces reproducibility, cryptographic provenance, and immutable negative result logging for all computational benchmark runs.

## Preconditions
1. Dataset split manifest exists and has valid SHA-256 hash.
2. Random seed is explicitly specified.
3. Target hypothesis (`H1`..`H5`) and roadmap node are declared.

## Invariants
1. Invariant 4: No experiment result may be persisted without a unique `run_id`.
2. Invariant 8: Failed runs (OOM, timeout, divergence) must be persisted with `is_failure = True`.
3. Negative Controls: Must be executed prior to or alongside proposed architectures.

## Checklist
- [ ] Record environment hardware spec and Python dependencies.
- [ ] Save output metrics and artifact hashes.
- [ ] If execution fails, create `EpisodeRecord` with `failure_reason` and derive `LessonLearned`.
