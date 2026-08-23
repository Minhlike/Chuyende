# CHAPTER 3 — STAGE A2 PRE-EXECUTION HANDOFF PLAN & RUNNER BLUEPRINT (AMENDMENT V1.3)

**Document ID:** `HANDOFF-CH3-STAGE-A2-001-V1.3`  
**Date:** 2026-08-23  
**Status:** `READY_FOR_STAGE_A2_RUNNER_IMPLEMENTATION`  
**Target Execution:** Real Stage A2 Temporal Graph View Pretraining on HDFS  

---

## 1. Execution Directives for Next Session

1. **Strict Invariant Maintenance:**
   - No Test split unsealing (`TEST_OPENED = false`, `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`, `TEST_GRAPH_EVENTS_MATERIALIZED = 0`, `TEST_RELATION_PARSE_COUNT = 0`).
   - Pure self-supervised graph learning ($L_{\text{graph}} = 1.0 \cdot L_{\text{rel}} + 1.0 \cdot L_{\text{node}} + 0.1 \cdot L_{\text{time}}$).
   - Zero label ingestion into data packages (`enforce_ssl_package_label_free`).
2. **Authorized Dataset Scope & Execution Budget:**
   - **HDFS ($K=5$ Seeds: `{42, 1337, 2024, 7, 999}`):** Grounded in causal event-entity graph stream materialized via `HDFSSplitAuthority` under `SPL-HDFS-001`.
   - **Execution Budget:** Exactly 35,000 Train sessions (586,577 graph events) and 7,500 Val sessions (119,531 graph events) as locked in `HDFS-EXECUTION-MEMBERSHIP.json`.
   - **BGL:** Excluded from Stage A2 graph pretraining (`INELIGIBLE`).
3. **Architecture & Target-Leakage Firewalls:**
   - Architecture: `TemporalGraphViewEncoder` (GRUCell, $d_{\text{node}}=128, d_{\text{edge}}=64, d_{\text{msg}}=128, H=4, \text{dropout}=0.10$).
   - Relation Masking: Classification head receives $[h_v(t-) \parallel h_u(t-) \parallel \phi(\Delta t)]$; true relation embedding withheld until post-loss memory update.
   - Node Masking: Reconstruction head predicts $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$ strictly from $h_v(t-)$.
   - Temporal Gap: $\log(1 + \Delta t_{uv})$ with millisecond resolution and boundary reset on Validation transition.
4. **Deterministic Resumption & Checkpoint State:**
   - Checkpoint occurs strictly at optimizer-step boundaries (`CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY = true`).
   - Serializes all 14 mandatory state elements: `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict`, `node_memory_states`, `node_last_interaction_timestamps`, `node_causal_in_degrees`, `node_causal_out_degrees`, `node_temporal_history_buffers`, `rng_states_4tuple`, `stream_iterator_state`, `masking_rng_state`, `early_stopping_state`, `global_step`, `current_epoch`.
   - Resumption regression test must pass with $\text{max divergence} < 10^{-6}$ prior to master execution.
5. **Experimental Source Manifest Generation:**
   - Each run directory (`experiments/runs/stage-a2/HDFS/seed-<SEED>/`) must output `EXPERIMENTAL-SOURCE.json` conforming to `EXPERIMENTAL-SOURCE-SCHEMA.json`.
