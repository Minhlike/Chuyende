# CHAPTER 3 — STAGE A2 SCIENTIFIC DESIGN AUDIT & ADVERSARIAL REVIEW

**Document ID:** `AUDIT-CH3-STAGE-A2-001`  
**Date:** 2026-08-23  
**Status:** `AUDITED & SEALED (PRE-EXECUTION)`  
**Scope:** Deep Architectural & Causal Leakage Audit for Temporal Graph Self-Supervised Pretraining  

---

## 1. Adversarial Risk Audit Matrix (12 Invariant Categories)

### 1.1. Future-Edge Target Leakage
- **Risk:** During temporal link prediction / relation classification at event $e_t = (v, u, r, t, x_e)$, if node memory states $h_v, h_u$ are updated with $e_t$ before evaluating the prediction loss, the model trivially predicts the edge from its own newly updated state.
- **Evidence:** Standard static GNN frameworks and naive dynamic GNN loops frequently update memory states in the forward pass before computing loss.
- **Resolution:** Strict **Predict-Before-Update** semantics. At timestamp $t$, the auxiliary prediction heads compute $\hat{r} = g_{\text{rel}}(h_v(t-), h_u(t-), \phi(\Delta t))$ and $\hat{x}_v = g_{\text{node}}(h_v(t-))$ using the memory state $h(t-)$ strictly prior to incorporating $e_t$. The GRU memory update $h_v(t) = \text{GRU}(h_v(t-), \bar{m}_v(t))$ is executed strictly *after* loss computation.
- **Final Contract:** `SCHEMA-STAGE-A2-GRAPH-CONTRACT-V1:causality_invariants:predict_before_update = true`.

---

### 1.2. Future-Neighbor & Non-Causal Topology Leakage
- **Risk:** Constructing a global adjacency matrix across the entire timeline allows past events to aggregate messages from future neighbors.
- **Evidence:** Naive implementations of PyTorch Geometric `DataLoader` on temporal datasets construct static graphs over whole datasets.
- **Resolution:** **Temporal Neighborhood Firewall**. Graph neighborhoods $\mathcal{N}(v, t)$ at time $t$ query only historical edges $E_{<t}$. Neighborhood message passing occurs along causal incoming edges observed up to $t-$.
- **Final Contract:** Global static graph queries are strictly prohibited; dynamic memory updates maintain causal temporal adjacency.

---

### 1.3. Global Statistics & Graph Metric Contamination
- **Risk:** Computing graph-level statistics (e.g. PageRank, global degree, centrality, clustering coefficient) across the full dataset and feeding them as static node features leaks future activity patterns.
- **Evidence:** `Bilot2025SimplerIsBetter` and `Arp2022DosDonts` demonstrated that global degree in provenance datasets acts as a high-performing shortcut.
- **Resolution:** Only **causal dynamic degrees** ($d_{\text{in}}(v, t-), d_{\text{out}}(v, t-)$) computed on the fly from the causal stream are permitted. Global whole-dataset graph metrics are strictly banned.
- **Final Contract:** Dynamic attributes restricted to causal degree and local event properties (`STAGE-A2-GRAPH-CONTRACT.json`).

---

### 1.4. Split Contamination & Vocabulary Snooping
- **Risk:** Fitting node vocabularies, tokenizers, or normalization scalers on Validation or Test splits leaks entity sets and distribution boundaries.
- **Evidence:** `CTRL-LEAK-001` in Chapter 2 establishes strict unidirectional information flow ($\mathcal{D}_{\text{train}} \to \mathcal{D}_{\text{val}} \to \mathcal{D}_{\text{test}}$).
- **Resolution:** Node entity tables, relation vocabularies, and continuous feature scalers are fit **strictly and exclusively on the Train split**. Unseen nodes in Validation/Test receive the typed `<UNK_NODE>` fallback representation.
- **Final Contract:** `entity_vocabulary_scope:fit_split = "TRAIN_ONLY"`.

---

### 1.5. Entity Identity Shortcut & Privacy Inversion
- **Risk:** Using raw hostnames, raw usernames, or raw PIDs as direct target labels in self-supervised reconstruction allows the model to memorize static entity fingerprints rather than generalizable structural interaction patterns.
- **Evidence:** Chapter 2 (Mục 2.2.2) establishes the Controlled Linkability and Privacy Threat Model (`CTRL-PRIV-001`).
- **Resolution:** Reconstruction targets for $L_{\text{node}}$ are strictly $x_v^{\text{priv}}$ (normalized causal degree + entity type embedding). Raw PIDs, raw IP addresses, and raw usernames are strictly excluded from SSL reconstruction targets.
- **Final Contract:** `privacy_and_firewall:raw_identifiers_in_targets = "STRICTLY_PROHIBITED"`.

---

### 1.6. Negative Sampling Contamination
- **Risk:** Sampling negative destinations from the entire dataset vocabulary allows the sampler to draw entities that only exist in future unobserved time windows.
- **Evidence:** Naive uniform negative sampling over $\mathcal{V}_{\text{global}}$ draws future nodes as negatives for past events, artificially inflating link prediction difficulty while leaking future vocabulary.
- **Resolution:** **Causal Negative Sampling**. The negative candidate pool at time $t$ is strictly restricted to entities causally observed prior to $t$ in the training timeline ($\mathcal{V}_{\le t} \cap \mathcal{V}_{\text{train}}$). True positive destination $u$ and existing active neighbors are excluded. The negative sampler uses an explicit deterministic RNG seeded with `(seed, global_step)`.
- **Final Contract:** `negative_sampling:algorithm = "CAUSAL_UNIFORM_SAMPLED_HISTORICAL_DESTINATION"`.

---

### 1.7. Temporal Batching & Window Boundary Leakage
- **Risk:** Shuffling temporal graph batches across time destroys the monotonicity of time and violates the causal memory update contract.
- **Evidence:** Random shuffling of temporal graph batches causes backwards time jumps where $t_{i+1} < t_i$.
- **Resolution:** Batches are processed in **strict chronological order** within contiguous temporal windows. Gradient accumulation preserves monotonic timeline progression.
- **Final Contract:** `temporal_ordering_policy = "STRICT_CHRONOLOGICAL_STREAM"`.

---

### 1.8. Hidden Label Leakage in Graph Attributes
- **Risk:** Ingesting ground-truth security flags (e.g. `anomaly_label`, `attack_type`, `redteam_tag`) into edge or node attribute vectors during SSL pretraining.
- **Evidence:** `enforce_ssl_package_label_free` decorator in `research_agent.experiments.data.data_contract`.
- **Resolution:** The data package builder enforces `LabelLeakageError` on any graph edge/node containing `label`, `is_anomaly`, `attack`, or `alert`.
- **Final Contract:** `privacy_and_firewall:downstream_labels_in_ssl = "STRICTLY_PROHIBITED"`.

---

### 1.9. Test Topology & Graph Structure Sealing
- **Risk:** Accessing Test graph nodes to build static graph structures or semi-supervised transductive representations before Stage C.
- **Evidence:** In transductive GNNs, Test graph edges are often included in the message-passing graph with masked labels.
- **Resolution:** **Absolute Inductive Test Sealing**. The Test split graph is completely sealed. Zero nodes, zero edges, and zero graph features are accessed or materialized during Stage A2.
- **Final Contract:** `TEST_OPENED = false`, `TEST_FEATURE_READ_COUNT = 0`, `TEST_LABEL_READ_COUNT = 0`, `TEST_METRIC_COUNT = 0`.

---

### 1.10. Invalid Transductive Assumptions
- **Risk:** Assuming all testing entities were observed during training, failing when encountering new processes, ephemeral sockets, or cold-start hosts.
- **Evidence:** Real-world enterprise environments exhibit high entity turnover ($> 30\%$ new PIDs/sockets per day).
- **Resolution:** Inductive architecture design with typed fallback embeddings ($e_{\text{type}}(v) + W_{\text{hash}} \cdot \text{hash}(v)$) and zero-memory initialization for cold-start entities.
- **Final Contract:** Model evaluates purely inductively without assuming static transductive node sets.

---

### 1.11. Equal-Timestamp Nondeterminism
- **Risk:** When multiple audit log events share the exact same microsecond timestamp, random sorting causes non-deterministic training trajectories.
- **Evidence:** High-throughput logging produces dozens of events sharing identical millisecond timestamps.
- **Resolution:** Deterministic tie-breaking key: `(event_timestamp_utc, raw_line_index)`. Events with identical timestamps are causally ordered by their physical order of logging.
- **Final Contract:** `timestamp_tie_breaking:canonical_sort_key = ["event_timestamp_utc", "raw_line_index"]`.

---

### 1.12. Split Boundary Node Memory Contamination
- **Risk:** Ambiguity between warm-starting Validation memory from Train vs. resetting node states, leading to unreproducible Validation metrics.
- **Evidence:** Draft plan listed both options without selecting a single canonical rule.
- **Resolution:** **Single Canonical Policy Locked**: `INDUCTIVE_SPLIT_RESET_ZERO_MEMORY`. At the start of Validation, all node dynamic memory states are reset to $h_{\text{init}} = \mathbf{0}$. Each validation batch/window operates within its own causal temporal context, guaranteeing exact, leak-free reproducibility.
- **Final Contract:** `split_memory_boundary_policy:canonical_policy = "INDUCTIVE_SPLIT_RESET_ZERO_MEMORY"`.

---

## 2. Synthesis & Final Pre-Execution Verdict

All 12 potential leakage channels have been formally addressed, resolved, and bound to machine-verifiable constraints in `STAGE-A2-GRAPH-CONTRACT.json` and `STAGE-A2-PREEXECUTION-LOCK.json`.
