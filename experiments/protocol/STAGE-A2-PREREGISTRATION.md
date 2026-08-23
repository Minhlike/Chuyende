# CHAPTER 3 — STAGE A2 PRE-REGISTRATION PROTOCOL (AMENDED V1.3)

**Protocol Document ID:** `PREREG-CH3-STAGE-A2-V1.3`  
**Registration Status:** `SEALED & FROZEN (AMENDED V1.3 PRE-EXECUTION)`  
**Effective Date:** 2026-08-23  
**Target Execution:** Real Stage A2 Dependency-Temporal Graph Pretraining on HDFS  
**Base Frozen Commit:** `9a707025ed5899c524962558732218ff48e8b212` (Tagged: `ch3-stage-a1-final`)  

---

## 1. Scope, Dataset Authorization & Execution Budget

1. **Authorized Dataset Scope:**
   - **HDFS ($K=5$ Canonical Seeds: `{42, 1337, 2024, 7, 999}`):** Authorized for Stage A2 graph pretraining. Bound directly to `SPL-HDFS-001`.
   - **BGL:** Ineligible for Stage A2 graph pretraining (`INELIGIBLE`).
2. **Execution Scope Disambiguation:**
   - **Eligible Population:** 357,133 Train sessions (7,447,591 raw records / 5,998,764 graph events) and 50,204 Val sessions (825,616 raw records / 735,091 graph events).
   - **Authorized Execution Budget Subset:** 35,000 Train sessions (826,241 raw records / 586,577 graph events) and 7,500 Val sessions (142,114 raw records / 119,531 graph events), selected deterministically by earliest chronological session start time `(session_start_time, block_id)`.
   - Deterministic membership locked in `experiments/evidence/stage-a2/preexecution/HDFS-EXECUTION-MEMBERSHIP.json`.
3. **Execution State Lock:**
   - `REAL_STAGE_A2_OPTIMIZER_STEPS = 0`
   - `REAL_STAGE_A2_MODELS_TRAINED = 0`
   - `STAGE_A2_TEST_OPENED = false`
   - `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`, `TEST_GRAPH_EVENTS_MATERIALIZED = 0`, `TEST_RELATION_PARSE_COUNT = 0`.

---

## 2. Multi-Task Self-Supervised Objectives & Target Masking Semantics

The composite graph self-supervised loss is formulated as:
$$\mathcal{L}_{\text{graph}} = 1.0 \cdot \mathcal{L}_{\text{rel}} + 1.0 \cdot \mathcal{L}_{\text{node}} + 0.1 \cdot \mathcal{L}_{\text{time}}$$

### 2.1 Masked Edge Relation Prediction ($\mathcal{L}_{\text{rel}}$)
- Evaluated on masked edge events ($p = 0.15$).
- **Target-Leakage Firewall:** When relation $r$ of event $e_t = (v, u, r, t, x_e)$ is masked, the prediction input is strictly $[h_v(t-) \parallel h_u(t-) \parallel \phi(\Delta t_{uv})]$. The true relation embedding $e_{\text{rel}}(r)$ is strictly withheld from the relation classification head and applied only during post-loss memory update.

### 2.2 Masked Node Feature Reconstruction ($\mathcal{L}_{\text{node}}$)
- Target: $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$ (4-dim one-hot type + $\log(1 + d_{\text{in}}(v, t-))$ + $\log(1 + d_{\text{out}}(v, t-))$).
- **Target-Leakage Firewall:** Predicted strictly from node hidden state $h_v(t-)$. Target attributes are never passed into or concatenated with the reconstruction head input.

### 2.3 Continuous Temporal Gap Prediction ($\mathcal{L}_{\text{time}}$)
- Target: $\log(1 + \Delta t_{uv})$ where $\Delta t_{uv} = t_{\text{curr}} - t_{\text{last\_interaction}}(v, u)$ in seconds with millisecond resolution.
- Reset to 0.0 upon split boundary transition (`INDUCTIVE_SPLIT_RESET_ZERO_MEMORY`).

---

## 3. Checkpoint Boundary Policy & Mutable State Contract

1. **Boundary Policy:** `CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY = true` (`gradient_accumulation_position = 0`, `pending_gradients = NONE`).
2. **Mandatory Checkpoint State Tuple:**
   - `model_state_dict`
   - `optimizer_state_dict`
   - `scheduler_state_dict`
   - `node_memory_states`
   - `node_last_interaction_timestamps`
   - `node_causal_in_degrees`
   - `node_causal_out_degrees`
   - `node_temporal_history_buffers`
   - `rng_states_4tuple`
   - `stream_iterator_state`
   - `masking_rng_state`
   - `early_stopping_state`
   - `global_step`
   - `current_epoch`

---

## 4. Experimental Source Contract Binding

All empirical results produced by Stage A2 must comply with `experiments/evidence/EXPERIMENTAL-SOURCE-CONTRACT.md` and generate an `EXPERIMENTAL-SOURCE.json` conforming to `experiments/evidence/EXPERIMENTAL-SOURCE-SCHEMA.json`.
