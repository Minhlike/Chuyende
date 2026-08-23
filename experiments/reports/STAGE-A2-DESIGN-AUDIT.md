# CHAPTER 3 — STAGE A2 SCIENTIFIC DESIGN AUDIT & RAW-TO-GRAPH GROUNDING REVIEW (AMENDED V1.3)

**Document ID:** `AUDIT-CH3-STAGE-A2-001-V1.3`  
**Date:** 2026-08-23  
**Status:** `AUDITED & SEALED (AMENDED V1.3 PRE-EXECUTION)`  
**Scope:** Deep Architectural, Causal Leakage, Split Authority Binding, Target Masking & Execution Scope Audit  

---

## 1. Executive Summary of Protocol Amendment V1.3

Prior to executing any Stage A2 optimizer step (`REAL_STAGE_A2_OPTIMIZER_STEPS = 0`, `REAL_STAGE_A2_MODELS_TRAINED = 0`, `TEST_OPENED = false`), the Stage A2 protocol was amended to V1.3:

1. **Execution Scope Disambiguation:**
   - Clearly separated Full Eligible Population (357,133 Train / 50,204 Val) from the Authorized Execution Budget (35,000 Train / 7,500 Val).
   - Produced both `HDFS-GRAPH-MATERIALIZATION-AUDIT.json` (population) and `HDFS-EXECUTION-SUBSET-AUDIT.json` (execution budget).
   - Materialized deterministic session membership in `HDFS-EXECUTION-MEMBERSHIP.json`.
2. **Target-Leakage Masking Formalism:**
   - For $L_{\text{rel}}$, true relation embedding is withheld from the classification head until post-loss memory update.
   - For $L_{\text{node}}$, reconstruction predicts $x_v^{\text{fixed\_priv}}$ strictly from $h_v(t-)$ without target attribute pass-through.
3. **Atomic Optimizer-Boundary Checkpointing:**
   - Enforced `CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY = true` with complete serialization of all 14 execution state elements.
4. **Experimental Source Contract:**
   - Bound all empirical claims to machine-readable source manifests (`EXPERIMENTAL-SOURCE-CONTRACT.md`).

---

## 2. Invariant & Boundary Verification Matrix

| Invariant Category | Specification in V1.3 | Verification Method |
| :--- | :--- | :--- |
| **Split Authority** | `HDFSSplitAuthority` (SPL-HDFS-001) | Shared class import in adapter and graph builder |
| **Execution Budget** | 35,000 Train / 7,500 Val sessions | Deterministic chronological selection |
| **Split Disjointness** | $\text{Train} \cap \text{Val} = \emptyset, \text{Train} \cap \text{Test} = \emptyset, \text{Val} \cap \text{Test} = \emptyset$ | Set intersection assertions |
| **Purged Sessions** | Purged T$\to$V $\cap$ Train = $\emptyset$, Purged V$\to$T $\cap$ Val = $\emptyset$ | Automated set disjointness gate |
| **Timestamp Fidelity** | Millisecond UTC epoch: `base_epoch + ms/1000.0` | Parity test vs canonical adapter ($\Delta t = 0.0$) |
| **Relation Masking** | Prediction input $[h_v(t-) \parallel h_u(t-) \parallel \phi(\Delta t)]$ without $e_{\text{rel}}(r)$ | Unit regression test |
| **Node Masking** | Prediction from $h_v(t-)$ without $x_v^{\text{fixed\_priv}}$ target pass-through | Unit regression test |
| **Checkpoint Boundary** | Checkpoint at optimizer step boundaries only | Complete 14-element state tuple check |
| **Graph Conservation** | $\text{eligible\_records} = \text{materialized} + \text{rejected}$ | Full Population & Execution Subset audits |
| **Source Provenance** | Machine-readable `EXPERIMENTAL-SOURCE.json` required | Schema validation test |
