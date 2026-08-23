# CHAPTER 3 — STAGE A2 SCIENTIFIC DESIGN AUDIT & RAW-TO-GRAPH GROUNDING REVIEW (AMENDED V1.2)

**Document ID:** `AUDIT-CH3-STAGE-A2-001-V1.2`  
**Date:** 2026-08-23  
**Status:** `AUDITED & SEALED (AMENDED V1.2 PRE-EXECUTION)`  
**Scope:** Deep Architectural, Causal Leakage, Split Authority Binding & Millisecond Temporal Fidelity Audit  

---

## 1. Executive Summary of Protocol Amendment V1.2

Prior to executing any Stage A2 optimizer step (`OPTIMIZER_STEPS = 0`, `MODELS_TRAINED = 0`, `TEST_OPENED = false`, `RESULTS_SEEN = NO`), the Stage A2 protocol was amended to V1.2 to eliminate subtle experimental drift and bind the graph construction pipeline directly to empirical raw invariants:

1. **Binding to Single Canonical Split Authority (`HDFSSplitAuthority`):**
   - Eliminated arbitrary line-offset partitioning.
   - Graph materialization strictly uses the shared `HDFSSplitAuthority` (SPL-HDFS-001) where Train (357,133 eligible / 35,000 selected sessions), Val (50,204 eligible / 7,500 selected sessions), and Test (86,261 sealed sessions) are partitioned causally by `(session_start_time, block_id)`.
   - Verified strict boundary ordering: $\max(\text{Train end}) < \min(\text{Val start}) < \max(\text{Val end}) < \min(\text{Test start})$.
   - Boundary purges (45,406 T$\to$V crossing sessions; 36,057 V$\to$T crossing sessions) are strictly excluded from both Train and Validation graph materialization.
2. **Restoration of Millisecond Temporal Fidelity:**
   - HDFS raw header field 3 (`ms_str`) is parsed into fractional seconds (`ms / 1000.0`).
   - Exact parity verified between `HDFSRealDataAdapter` and `HDFSGraphBuilder` ($\Delta t = 0.0$).
   - Canonical sort key: `(event_timestamp_utc_exact, raw_line_index)`.
3. **Re-Audited Relation Direction & Component Constraints:**
   - Audited all 8 canonical relations against raw Train records.
   - Added component constraints (`dfs.DataNode$DataXceiver`, `dfs.DataNode$PacketResponder`, `dfs.FSNamesystem`).
   - Renamed Relation 2 to `TRANSMITS_BLOCK` (`StorageNode (src) -> DataBlock (with block size)`).
4. **Deterministic Temporal Gap ($\Delta t$) & Causal Node Target ($x_v^{\text{fixed\_priv}}$):**
   - $\Delta t_{uv} = t_{\text{curr}} - t_{\text{last\_interaction}}(v, u)$ in continuous seconds.
   - $x_v^{\text{fixed\_priv}} \in \mathbb{R}^6$: 4-dim one-hot type + $\log(1 + d_{\text{in}}(v, t-))$ + $\log(1 + d_{\text{out}}(v, t-))$.
   - Zero learnable parameters, zero future statistics, zero downstream labels.

---

## 2. Invariant & Boundary Verification Matrix

| Invariant Category | Specification in V1.2 | Verification Method |
| :--- | :--- | :--- |
| **Split Authority** | `HDFSSplitAuthority` (SPL-HDFS-001) | Shared class import in adapter and graph builder |
| **Split Disjointness** | $\text{Train} \cap \text{Val} = \emptyset, \text{Train} \cap \text{Test} = \emptyset, \text{Val} \cap \text{Test} = \emptyset$ | Set intersection unit assertions |
| **Purged Sessions** | Purged T$\to$V $\cap$ Train = $\emptyset$, Purged V$\to$T $\cap$ Val = $\emptyset$ | Automated set disjointness gate |
| **Timestamp Fidelity** | Millisecond UTC epoch: `base_epoch + ms/1000.0` | Parity test vs canonical adapter ($\Delta t = 0.0$) |
| **Test Firewall** | Zero Test graph nodes, edges, relations, features | `TestSetSealedError` fail-closed exception |
| **Predict-Before-Update** | Auxiliary losses ($L_{\text{rel}}, L_{\text{node}}, L_{\text{time}}$) evaluate on $h(t-)$ | `STAGE-A2-GRAPH-CONTRACT.json` |
| **Graph Conservation** | $\text{eligible\_records} = \text{materialized} + \text{rejected}$ | Full Train/Val streaming audit |
