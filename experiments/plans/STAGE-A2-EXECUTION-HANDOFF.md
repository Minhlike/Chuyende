# CHAPTER 3 — STAGE A2 PRE-EXECUTION HANDOFF PLAN & RUNNER BLUEPRINT (AMENDMENT V1.2)

**Document ID:** `HANDOFF-CH3-STAGE-A2-001-V1.2`  
**Date:** 2026-08-23  
**Status:** `READY_FOR_STAGE_A2_RUNNER_IMPLEMENTATION`  
**Target Execution:** Real Stage A2 Temporal Graph View Pretraining on HDFS  

---

## 1. Execution Directives for Next Session

1. **Strict Invariant Maintenance:**
   - No Test split unsealing (`TEST_OPENED = false`, `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`, `TEST_GRAPH_EVENTS_MATERIALIZED = 0`, `TEST_RELATION_PARSE_COUNT = 0`).
   - Pure self-supervised graph learning ($L_{\text{graph}} = 1.0 \cdot L_{\text{rel}} + 1.0 \cdot L_{\text{node}} + 0.1 \cdot L_{\text{time}}$).
   - Zero label ingestion into data packages (`enforce_ssl_package_label_free`).
2. **Authorized Dataset Scope & Split Authority:**
   - **HDFS ($K=5$ Seeds: `{42, 1337, 2024, 7, 999}`):** Grounded in causal event-entity graph stream materialized via `HDFSSplitAuthority` under `SPL-HDFS-001`.
   - **BGL:** Excluded from Stage A2 graph pretraining (`INELIGIBLE`).
3. **Model & Target Grounding:**
   - Architecture: `TemporalGraphViewEncoder` (GRUCell, $d_{\text{node}}=128, d_{\text{edge}}=64, d_{\text{msg}}=128, H=4, \text{dropout}=0.10$).
   - Temporal Gap: $\log(1 + \Delta t_{uv})$ with millisecond resolution and boundary reset on Validation transition.
   - Node Target ($L_{\text{node}}$): $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$ (4-dim one-hot type + $\log(1 + d_{\text{in}}(v, t-))$ + $\log(1 + d_{\text{out}}(v, t-))$).
4. **Deterministic Resumption Guarantee:**
   - The Stage A2 trainer must serialize: `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict`, `node_memory_states`, `node_last_interaction_timestamps`, `4-RNG states`, `stream_iterator_state`, and `global_step`.
   - Resumption regression test must pass with $\text{max divergence} < 10^{-6}$ prior to master execution.
