# CHAPTER 3 — STAGE A2 PRE-REGISTRATION PROTOCOL & SPECIFICATION (AMENDMENT V1.1)

**Document Identifier:** `REG-CH3-STAGE-A2-20260823-V1.1`  
**Registration Date:** 2026-08-23  
**Status:** **FROZEN & LOCKED PRE-EXECUTION (AMENDED V1.1)**  
**Execution Branch:** `train/ch3-stage-a2-preregistration`  
**Base Frozen Commit:** `9a707025ed5899c524962558732218ff48e8b212` (Tagged: `ch3-stage-a1-final`)  
**Previous Preregistration Commit:** `7b0feb788bf242456ab801e062caf6b1f06b8474`  
**Amendment Justification:** Pre-execution audit resolved raw-to-graph grounding consistency, designated HDFS as the authorized dataset for Stage A2 graph pretraining, excluded BGL due to absence of inter-entity interaction destinations in raw logs, removed unused negative destination sampling from $L_{\text{graph}}$, and fixed the node reconstruction target $x_v^{\text{fixed\_priv}}$ to a non-learnable 6-dimensional observable vector.  

---

## 1. Executive Scientific Scope & Boundaries

Stage A2 executes real self-supervised pretraining for the Chapter 2 Temporal Graph View Encoder (`TemporalGraphViewEncoder`) on the causal event-entity temporal graph derived from HDFS logs.

### Inviolable Pre-Execution Boundaries:
1. **Zero Pre-Execution Optimizer Steps:** At the time of locking, `STAGE_A2_OPTIMIZER_STEPS = 0`, `STAGE_A2_MODELS_TRAINED = 0`.
2. **Zero Test Split Access:** The Test split is strictly sealed (`TEST_OPENED = false`, `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`).
3. **Pure Self-Supervision:** Zero downstream anomaly labels, attack types, or security alerts are loaded or exposed to the model (`enforce_ssl_package_label_free`).
4. **Dataset Eligibility Audit:**
   - **HDFS:** `AUTHORIZED` — Causal event-entity temporal graph derived from raw HDFS block interactions.
   - **BGL:** `INELIGIBLE` — Single-node localized alert telemetry without extractable inter-entity destination nodes.
   - **DARPA TC E3 & LANL:** `PENDING_ACQUISITION` — Reserved for post-acquisition execution.

---

## 2. Dataset Selection & Causal Partition Registry

| Dataset | Split ID | Raw Checksum (SHA-256) | Train Specification | Validation Specification | Test Specification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HDFS** | `SPL-HDFS-001` | `6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169` | Earliest 70% causal block sessions (35,000 sessions) | Next 15% causal block sessions (7,500 sessions) | Final 15% causal block sessions (Sealed, 0 features) | **AUTHORIZED FOR STAGE A2** |
| **BGL** | `SPL-BGL-001` | `0a58be959cef101bbe5c053e60bd8a49673e9c942b164f4d969bb109e99fce95` | Days 1..150 | Days 151..180 | Days 181..215 (Sealed) | **INELIGIBLE FOR GRAPH SSL** |
| **DARPA TC E3** | `SPL-DTC-001` | `PENDING_ACQUISITION` | `PENDING_RAW_CDM18_ALIGNMENT` | `PENDING_RAW_CDM18_ALIGNMENT` | Sealed | `PENDING_ACQUISITION` |
| **LANL Cyber 1**| `SPL-LANL-001` | `PENDING_ACQUISITION` | `PENDING_ACQUISITION` | `PENDING_ACQUISITION` | Sealed | `PENDING_ACQUISITION` |

---

## 3. Model Architecture Specification (`TemporalGraphViewEncoder`)

The architecture strictly implements Chapter 2 (Mục 2.3.2):
- **Base Architecture Family:** Typed Temporal Message Passing Graph Neural Network with Dynamic Memory Cell (`TemporalGraphViewEncoder`).
- **Memory Cell:** Gated Recurrent Unit (`nn.GRUCell`) maintaining persistent dynamic node states $h_v(t) \in \mathbb{R}^{d_{\text{node}}}$.
- **Node State Dimension ($d_{\text{node}}$):** 128
- **Edge Feature Dimension ($d_{\text{edge}}$):** 64
- **Message Dimension ($d_{\text{msg}}$):** 128
- **Temporal Attention Heads ($H$):** 4 ($\text{head\_dim} = 32$)
- **Time Projection ($\phi(\Delta t)$):** Harmonic / Sinusoidal continuous log-time projection ($\mathbb{R}^{32}$)
- **Relation Embedding ($e_{\text{rel}}$):** Learnable embedding table over typed relations ($d_{\text{rel}} = 32$)
- **Node Type Embedding ($e_{\text{type}}$):** Learnable embedding table over entity types ($d_{\text{type}} = 32$)
- **Dropout:** 0.10
- **Normalization:** LayerNorm applied after message aggregation and before auxiliary projection heads.

---

## 4. Multi-Task Self-Supervised Loss Formulation

$$L_{\text{graph}} = \lambda_{\text{rel}} \cdot L_{\text{rel}} + \lambda_{\text{node}} \cdot L_{\text{node}} + \lambda_{\text{time}} \cdot L_{\text{time}}$$

Where:
1. **$L_{\text{rel}}$ (Masked Edge Relation Prediction):**
   $$\mathcal{L}_{\text{rel}} = -\frac{1}{|\mathcal{E}_{\text{mask}}|} \sum_{e=(v,u,r) \in \mathcal{E}_{\text{mask}}} \log P(r \mid h_v(t-), h_u(t-), \phi(\Delta t_{uv}))$$
   - 15% Bernoulli masking on active edges.
   - Categorical cross-entropy over relation vocabulary ($|\mathcal{R}| = 8$).
   - Evaluated strictly using node states $h(t-)$ BEFORE memory update.
2. **$L_{\text{node}}$ (Masked Node Attribute Reconstruction):**
   $$\mathcal{L}_{\text{node}} = \frac{1}{|\mathcal{V}_{\text{mask}}|} \sum_{v \in \mathcal{V}_{\text{mask}}} \| g_{\text{node}}(h_v(t-)) - x_v^{\text{fixed\_priv}} \|_2^2$$
   - 15% Bernoulli masking on active entity nodes.
   - Mean Squared Error between predicted continuous vector and true non-learnable feature $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$ (4-dim fixed one-hot type + 2-dim log1p causal in/out degrees).
3. **$L_{\text{time}}$ (Relative Temporal Gap Prediction):**
   $$\mathcal{L}_{\text{time}} = \frac{1}{|\mathcal{E}_t|} \sum_{e=(v,u) \in \mathcal{E}_t} \text{Smooth}_{L1}\left( g_{\text{time}}(h_v(t-), h_u(t-)) - \log(1 + \Delta t_{uv}) \right)$$
   - Smooth L1 loss ($\beta = 1.0$) between predicted log-gap and ground-truth inter-event time difference.

**Canonical Loss Weights:**
$$\lambda_{\text{rel}} = 1.0, \quad \lambda_{\text{node}} = 1.0, \quad \lambda_{\text{time}} = 0.1$$

---

## 5. Optimization & Execution Regime

- **Optimizer:** `AdamW` (learning rate $\eta = 5.0 \times 10^{-4}$, weight decay $\lambda = 0.01$, $\beta = (0.9, 0.98), \epsilon = 10^{-8}$)
- **Batching:** `temporal_window_size = 256` events per micro-step, `gradient_accumulation_steps = 4` (effective batch = 1,024 events/step)
- **Learning Rate Schedule:** Linear Warmup for first 5% of optimizer steps followed by Cosine Decay to $\eta_{\min} = 1.0 \times 10^{-5}$
- **Gradient Clipping:** Maximum gradient norm $= 1.0$
- **Validation Cadence:** Once per completed epoch on full Validation split.
- **Early Stopping:** Patience $= 3$ completed epochs on Validation $L_{\text{graph}}$.
- **Canonical Random Seeds ($K=5$):**
  $$\mathcal{K}_{\text{canonical}} = \{ 42, \; 1337, \; 2024, \; 7, \; 999 \}$$

---

## 6. Deterministic Resumption & Checkpoint Contract

All checkpoints (`best_val_loss.pt`, `checkpoint_last.pt`) must atomically serialize:
1. Model state dict (`model_state_dict`)
2. Optimizer state dict (`optimizer_state_dict`)
3. Scheduler state dict (`scheduler_state_dict`)
4. Node memory states (`node_memory_states`)
5. Full 4-state RNG tuple: Python, NumPy, PyTorch CPU, PyTorch CUDA
6. Stream iterator state (`stream_iterator_state`)
7. Global step and epoch counters

**Acceptance Criteria for Checkpoint Resumption:**
$$\text{Max Parameter Divergence between Continuous Run and Resumed Run} < 1.0 \times 10^{-6} \quad (\text{Target: } 0.0)$$
