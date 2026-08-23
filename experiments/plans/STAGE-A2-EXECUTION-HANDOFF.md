# CHAPTER 3 — STAGE A2 PRE-EXECUTION HANDOFF PLAN & RUNNER BLUEPRINT

**Document ID:** `HANDOFF-CH3-STAGE-A2-001`  
**Date:** 2026-08-23  
**Status:** `READY_FOR_STAGE_A2_RUNNER_IMPLEMENTATION`  
**Target Execution:** Real Stage A2 Dependency-Temporal Graph View Pretraining  

---

## 1. Execution Directives for Next Session

1. **Strict Invariant Maintenance:**
   - No Test split unsealing (`TEST_OPENED = false`, `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`).
   - Pure self-supervised graph learning ($L_{\text{graph}} = 1.0 \cdot L_{\text{rel}} + 1.0 \cdot L_{\text{node}} + 0.1 \cdot L_{\text{time}}$).
   - Zero label ingestion into data packages (`enforce_ssl_package_label_free`).
2. **Deterministic Resumption Guarantee:**
   - The Stage A2 trainer must implement full state serialization (`model`, `optimizer`, `scheduler`, `node_memory_states`, `4-RNG states`, `stream_iterator`, `negative_sampler_rng`).
   - Run the deterministic regression test before starting master training.
3. **Execution Matrix ($K=5$ Seeds per Dataset):**
   - **HDFS ($K=5$):** Seeds `{42, 1337, 2024, 7, 999}` $\to$ `experiments/runs/stage-a2/HDFS/seed-<SEED>/`
   - **BGL ($K=5$):** Seeds `{42, 1337, 2024, 7, 999}` $\to$ `experiments/runs/stage-a2/BGL/seed-<SEED>/`
4. **Acceptance Gates for Stage A2 Completion:**
   - 10 Run Manifests generated with `nan_loss_count = 0`, `inf_loss_count = 0`, `test_opened = false`.
   - Checkpoint SHA-256 hashes generated and recorded for every seed.
   - Deterministic resumption test passes with $\text{max divergence} < 10^{-6}$.
