# CHAPTER 3 — STAGE A2 PRE-EXECUTION DESIGN & HANDOFF PLAN

**Document ID:** `PLAN-CH3-STAGE-A2-001`  
**Date:** 2026-08-23  
**Status:** `DRAFT_DESIGN_ONLY (NO OPTIMIZER STEPS / NO TEST ACCESS)`  
**Scope:** Graph & Temporal View Self-Supervised Pretraining  

---

## 1. Scope & Inviolable Scientific Boundaries

1. **Zero Execution in this Phase:**
   - `ANY_OPTIMIZER_STEP = NO`
   - `ANY_MODEL_TRAINED = NO`
   - `TEST_SPLIT_ACCESSED = NO`
2. **Role of Stage A2:**
   - Pretraining the Chapter 2 Graph/Node/Temporal View Encoder on system provenance / entity interaction graphs.
   - Stage A2 operates strictly on the **Train and Validation splits** of system provenance datasets (e.g. DARPA TC / Prov-Bench / system entity logs).
   - Downstream anomaly labels and attack scenario labels are strictly prohibited from entering Stage A2 SSL data packages (`LabelLeakageError`).

---

## 2. Proposed Objective & Loss Formulation

Stage A2 evaluates self-supervised representation learning over dynamic temporal graphs:

$$L_{\text{graph}} = \lambda_{\text{edge}} \cdot L_{\text{edge\_pred}} + \lambda_{\text{node}} \cdot L_{\text{node\_mask}} + \lambda_{\text{temp}} \cdot L_{\text{time\_drift}}$$

### Objective Breakdown
1. **$L_{\text{edge\_pred}}$ (Temporal Link Prediction):**
   - Predicts destination node $u$ given source $v$ and event timestamp $t$, using cross-entropy with in-batch negative sampling or sampled negative destinations.
2. **$L_{\text{node\_mask}}$ (Masked Node Attribute Reconstruction):**
   - Privacy-safe node attribute representation $x_v^{\text{priv}}$.
   - Smooth L1 / MSE loss between predicted continuous representation and true unmasked $x_v^{\text{priv}}$.
3. **$L_{\text{time\_drift}}$ (Dynamic Edge Time Gap Prediction):**
   - Predicts inter-interaction delta $\Delta t_{uv}$ between consecutive edges on the same destination node.

---

## 3. Architecture Candidates

- **Primary Candidate:** `TemporalGraphViewEncoder` (Chapter 2 Dynamic Message Passing + Temporal Memory + Node Aggregator).
- **Core Parameters:**
  - Node embedding dimension: $d_{\text{node}} = 128$
  - Edge feature dimension: $d_{\text{edge}} = 64$
  - Message aggregation: Grouped by $(u, t)$ before destination update.
  - Memory update: GRU / Transformer cell with exact causal memory state propagation.

---

## 4. Leakage Risks & Firewall Contracts

1. **Temporal Boundary Enforcement:**
   - All graph events must be processed in strict monotonically non-decreasing timestamp order ($t_i \le t_{i+1}$).
   - $\max(t_{\text{Train}}) < \min(t_{\text{Val}}) < \min(t_{\text{Test}})$.
2. **Entity Leakage Safeguards:**
   - Cross-boundary node memory: Node state $h_v$ must be cleanly reset at split transitions (or evaluated under explicit inductive zero-memory initialization).
3. **Label Leakage Firewall:**
   - Same `enforce_ssl_package_label_free` decorator as Stage A1.

---

## 5. Preregistration Decisions Needed Prior to First Optimizer Step

Before any training script executes:
1. **Dataset Selection & Hash Materialization:** Exact raw dataset SHA-256 and manifest budgets.
2. **Exact Loss Weights Preregistration:** Values of $\lambda_{\text{edge}}, \lambda_{\text{node}}, \lambda_{\text{temp}}$.
3. **Seed Policy:** Exact 5 canonical seeds ($K=5$: `{42, 1337, 2024, 7, 999}`).
4. **Pre-Execution Lock Generation:** Create `STAGE-A2-PREEXECUTION-LOCK.json` with immutable hashes.
5. **Acceptance Criteria Definition:** Clear convergence metrics, deterministic resumption test, and zero-test-leakage assertions.
