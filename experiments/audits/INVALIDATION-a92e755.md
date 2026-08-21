# Formal Audit & Invalidation Record: Commit a92e755

> **Audit Identifier:** `AUDIT-INV-a92e755`  
> **Invalidated Commit:** `a92e755c7c3409e419d055e7488a42f6ab4b23ac`  
> **Classification:** `INVALID_CONFIRMATORY_RESULT` | `PILOT_ONLY` | `DO_NOT_USE_IN_THESIS`  
> **Authority:** Chapter 3 Confirmatory Protocol & Pre-Registration Gate  
> **Status:** `QUARANTINED` (Zero empirical metrics from `a92e755` may be cited or used in the thesis)

---

## 1. Summary of Invalidation Reasons

Commit `a92e755` produced provisional experiment outputs that violated fundamental scientific pre-registration rules, hypothesis definitions, and data governance boundaries:

1. **Synthetic Data Violation (DARPA TC E3):**
   - Executed a synthetic subgraph generator (`process_darpa_e3_synthetic_subgraphs`) instead of parsing authentic DARPA TC Engagement 3 CDM18 raw topic streams.
   - Prematurely marked manifest `SPL-DTC-001.json` as `SEALED` despite `raw_dataset_acquired = false`.

2. **Hypothesis Identity Corruption (H1–H5 Redefinition):**
   - **H1:** Redefined canonical *Parameter Semantic Fidelity* (Template vs Security-Aware Parameterized representations) into an unauthorized *Label Scarcity Probe* experiment.
   - **H2:** Redefined canonical *Multi-View Alignment* (Sequence-only vs Graph-only vs Multi-View unaligned vs Multi-View aligned with VICReg anti-collapse) into a generic *Concept Drift* evaluation.
   - **H3:** Redefined canonical *Robustness / Shortcut Invariance* (Perturbations P01–P12) into a *Multiple Instance Learning (MIL) Weak Attribution* experiment.
   - **H4:** Replaced raw hardware benchmark harness with hard-coded literal latency measurements.
   - **H5:** Replaced canonical *Controlled Linkability / Utility–Privacy Frontier* with a theoretical *PAC-Bayesian generalization error gap* calculation.

3. **Fabricated Attribution Ground Truth:**
   - Heuristically assumed that the last 3 events of every anomaly sequence were the root-cause anomalous events (`gt_anom_indices = set(range(valid_len - 3, valid_len))`), fabricating instance-level ground truth where none existed.

4. **Statistical Protocol Violation:**
   - Bootstrapped scalar seed-level arrays across 5 runs instead of resampling independent evaluation clusters with identical paired cluster indices.
   - Used $B = 10,000$ and arbitrary seeds instead of the pre-registered $B = 2,000$ with bootstrap seed `10007`.
   - Omitted required multiple testing corrections (H1/H2 Bonferroni, H3 Benjamini-Hochberg FDR, H5 Holm-Bonferroni, H4 Conjunctive SLO).

5. **Incomplete Chapter 2 Architectural Implementation:**
   - The multi-view framework was executed without a Temporal Graph Neural Network (TGNN), without the multi-view correspondence contract, without VICReg anti-collapse loss, and without privacy-preserving tokenization variants.

6. **Non-Causal Split on HDFS:**
   - Performed random stratified sampling across blocks instead of the pre-registered causal temporal / holdout protocol.

---

## 2. Quarantine Actions & Governance Rules

- All artifacts from `a92e755` (`experiments/results/EXPERIMENT_RESULTS_LOCK.json`, `EXPERIMENT_SUMMARY_REPORT.md`) are quarantined as exploratory pilot artifacts only.
- Branch `exp/ch3-pipeline-execution` shall **NEVER** be merged into `main`.
- All confirmatory experiment states are reset to `PENDING`.
- No model training or Test set opening is permitted until the complete Chapter 2 multi-view extractor and exact H1–H5 test contracts are implemented and audited.
