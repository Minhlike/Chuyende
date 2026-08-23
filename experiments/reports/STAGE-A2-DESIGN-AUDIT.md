# CHAPTER 3 — STAGE A2 SCIENTIFIC DESIGN AUDIT & RAW-TO-GRAPH GROUNDING REVIEW

**Document ID:** `AUDIT-CH3-STAGE-A2-001-V1.1`  
**Date:** 2026-08-23  
**Status:** `AUDITED & SEALED (AMENDED V1.1 PRE-EXECUTION)`  
**Scope:** Deep Architectural, Causal Leakage & Raw-Grounded Graph Semantics Audit  

---

## 1. Executive Summary of Protocol Amendment V1.1

Following post-preregistration independent review and prior to executing any optimizer step (`OPTIMIZER_STEPS = 0`, `MODELS_TRAINED = 0`, `TEST_OPENED = false`, `RESULTS_SEEN = NO`), the Stage A2 protocol was amended to V1.1 to resolve key scientific consistency gaps:

1. **Raw Log Grounding & BGL Ineligibility:**
   - **HDFS:** Fully eligible (`HDFS_GRAPH_ELIGIBILITY = YES`). Raw logs contain explicit multi-entity interactions linking DataBlocks, StorageNodes, Namesystem coordinators, and ExecutionThreads.
   - **BGL:** Ineligible for graph pretraining (`BGL_STAGE_A2_GRAPH_ELIGIBILITY = FAIL / INELIGIBLE`). Raw BGL logs represent localized single-node alert reports without extractable inter-entity destination nodes. To prevent fabricated interaction topology, BGL is excluded from Stage A2 Graph Pretraining.
2. **Removal of Unused Negative Destination Sampling:**
   - The canonical objective $L_{\text{graph}} = 1.0 \cdot L_{\text{rel}} + 1.0 \cdot L_{\text{node}} + 0.1 \cdot L_{\text{time}}$ computes relation classification $L_{\text{rel}}$ on known $(v, u)$ pairs.
   - Negative destination sampling was completely removed from the graph contract, pre-execution lock, and checkpoint state definitions, eliminating ambiguity.
3. **Fixed, Non-Learnable Node Reconstruction Target:**
   - $x_v^{\text{fixed\_priv}}$ is defined as a fixed 6-dimensional observable vector: 4-dim one-hot entity type + 2-dim log1p causal in/out degrees.
   - Zero learnable parameters, zero future statistics, zero raw private strings, zero downstream labels.
4. **Conservation & Exact Multi-Edge Policy:**
   - Exact conservation law enforced: $\text{raw\_scanned} = \text{materialized\_events} + \text{explicitly\_rejected\_events}$.
   - Multi-edge policy: `PRESERVE_ALL_TEMPORAL_EVENTS_FIFO_CAUSAL` with `max_node_history = 64`.

---

## 2. Adversarial Risk Audit Matrix (12 Invariant Categories)

### 2.1. Future-Edge Target Leakage
- **Risk:** Updating node memory states $h_v, h_u$ with event $e_t = (v, u, r, t, x_e)$ before evaluating the prediction loss.
- **Resolution:** Strict **Predict-Before-Update** semantics. At timestamp $t$, the auxiliary prediction heads compute $\hat{r} = g_{\text{rel}}(h_v(t-), h_u(t-), \phi(\Delta t))$ and $\hat{x}_v = g_{\text{node}}(h_v(t-))$ using node states strictly prior to $e_t$. The GRU memory update executes strictly *after* loss computation.
- **Contract:** `causality_invariants:predict_before_update = true`.

### 2.2. Future-Neighbor & Non-Causal Topology Leakage
- **Risk:** Constructing a global adjacency matrix across the entire timeline allows past events to aggregate messages from future neighbors.
- **Resolution:** Graph neighborhoods $\mathcal{N}(v, t)$ at time $t$ query only historical edges $E_{<t}$. Static whole-timeline graph construction is strictly prohibited.
- **Contract:** `future_neighbor_firewall = true`.

### 2.3. Global Statistics & Graph Metric Contamination
- **Risk:** Computing graph-level statistics (PageRank, global degree) across the full dataset and feeding them as static node features.
- **Resolution:** Only causal dynamic degrees ($d_{\text{in}}(v, t-), d_{\text{out}}(v, t-)$) computed on the fly are permitted. Continuous scalers are fit strictly on Train.
- **Contract:** Continuous degree scalers fit on `TRAIN_ONLY`.

### 2.4. Split Contamination & Vocabulary Snooping
- **Risk:** Fitting node vocabularies or tokenizers on Validation or Test splits.
- **Resolution:** Node entity tables and relation vocabularies are fit **strictly on the Train split**. Unseen nodes in Validation receive the typed `<UNK_NODE>` fallback representation.
- **Contract:** `entity_vocabulary_scope:fit_split = "TRAIN_ONLY"`.

### 2.5. Entity Identity Shortcut & Privacy Inversion
- **Risk:** Using raw hostnames, usernames, or PIDs as target labels.
- **Resolution:** Reconstruction targets for $L_{\text{node}}$ are strictly $x_v^{\text{fixed\_priv}}$ (fixed one-hot type + causal degree). Raw PIDs, raw IP addresses, and raw usernames are strictly excluded from SSL reconstruction targets.
- **Contract:** `privacy_and_firewall:raw_identifiers_in_targets = "STRICTLY_PROHIBITED"`.

### 2.6. Negative Sampling Discrepancy Resolution
- **Risk:** Keeping negative sampling in contracts when the canonical objective does not use link prediction loss.
- **Resolution:** Negative destination sampling is completely removed from all contracts, schemas, and checkpoint definitions.
- **Contract:** `negative_sampling:status = "REMOVED_NO_LINK_PRED_LOSS"`.

### 2.7. Temporal Batching & Window Boundary Leakage
- **Risk:** Shuffling temporal graph batches across time destroys the monotonicity of time and violates causal memory updates.
- **Resolution:** Batches are processed in **strict chronological order** within contiguous temporal windows.
- **Contract:** `temporal_ordering_policy = "STRICT_CHRONOLOGICAL_STREAM"`.

### 2.8. Hidden Label Leakage in Graph Attributes
- **Risk:** Ingesting ground-truth security flags into edge or node attribute vectors during SSL pretraining.
- **Resolution:** The data package builder enforces `LabelLeakageError` on any graph edge/node containing `label`, `is_anomaly`, `attack`, or `alert`.
- **Contract:** `privacy_and_firewall:downstream_labels_in_ssl = "STRICTLY_PROHIBITED"`.

### 2.9. Test Topology & Graph Structure Sealing
- **Risk:** Accessing Test graph nodes to build static graph structures or semi-supervised transductive representations.
- **Resolution:** **Absolute Inductive Test Sealing**. The Test split graph is completely sealed. Zero nodes, zero edges, and zero graph features are accessed or materialized during Stage A2.
- **Contract:** `TEST_OPENED = false`, `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`.

### 2.10. Invalid Transductive Assumptions
- **Risk:** Assuming all testing entities were observed during training.
- **Resolution:** Inductive architecture design with typed fallback embeddings ($e_{\text{type}}(v)$) and zero-memory initialization for cold-start entities.
- **Contract:** `unseen_node_policy = "TYPED_UNK_NODE_ONLY"`.

### 2.11. Equal-Timestamp Nondeterminism
- **Risk:** Multiple log events sharing identical timestamps causing non-deterministic ordering.
- **Resolution:** Deterministic tie-breaking key: `(event_timestamp_utc, raw_line_index)`.
- **Contract:** `timestamp_tie_breaking:canonical_sort_key = ["event_timestamp_utc", "raw_line_index"]`.

### 2.12. Split Boundary Node Memory Contamination
- **Risk:** Ambiguity between warm-starting Validation memory from Train vs. resetting node states.
- **Resolution:** **Single Canonical Policy Locked**: `INDUCTIVE_SPLIT_RESET_ZERO_MEMORY`. At the start of Validation, all node dynamic memory states are reset to $h_{\text{init}} = \mathbf{0}$, ensuring complete inductive isolation and exact reproducibility.
- **Contract:** `split_memory_boundary_policy:canonical_policy = "INDUCTIVE_SPLIT_RESET_ZERO_MEMORY"`.
