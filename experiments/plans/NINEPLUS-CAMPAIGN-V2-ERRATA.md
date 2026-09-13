# NINEPLUS CAMPAIGN V2 — ERRATA & TERMINOLOGY CLARIFICATION

**Document ID:** `ERRATA-NINEPLUS-CAMPAIGN-V2`  
**Date:** 2026-09-13  
**Workspace:** `D:\Research`  
**Repository:** `Minhlike/Chuyende`  
**Branch:** `fix/thesis-apply-edits`  
**Authoritative Plan Reference:** `experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V2.json`  
**Review Reference:** `experiments/plans/NINEPLUS-PHASE0-REVIEW-V2.md`

---

## 1. Authoritative V2 Git Commit SHA Correction

In the narrative text of `experiments/plans/NINEPLUS-PHASE0-REVIEW-V2.md`, an anticipatory narrative SHA (`0df87c2b512e0fa540ce8a49c66e2c3fe58dcda1`) was printed prior to final Git tree object sealing.

The official, bitwise-verified Git commit SHA for the V2 preregistration in the remote repository is:
```text
AUTHORITATIVE_V2_COMMIT = 0df87c2c35ad23c45ab64b994e26d65a0688c1c0
```
All future provenance references to the V2 preregistration must cite `0df87c2c35ad23c45ab64b994e26d65a0688c1c0`.

---

## 2. Terminology Clarification: Decoupling Provenance from Causality

In accordance with ATTT Warranted-Derivation Scientific Writing Skill v4.0 (Rule 2: *"Không coi correlation, temporal order, graph dependency hoặc attention weight là causal effect"*), all instances of informal causal language in campaign documentation are strictly disambiguated:

1. **Graph Relations:**
   - **Deprecated Term:** *"causal graph relations"*
   - **Corrected Scientific Term:** **"temporal provenance / execution-dependency relations"**
   - **Warrant:** The edges in the constructed graph represent observed chronological execution dependencies and system event ordering recorded in log streams. They do not reflect counterfactual interventions or structural causal models (SCMs).
2. **Temporal Split:**
   - **Deprecated Term:** *"causal temporal split"*
   - **Corrected Scientific Term:** **"chronological no-lookahead temporal split"**
   - **Warrant:** The partition divides sessions strictly along the chronological time axis to prevent future-to-past information leakage (Arp et al. [2]). It preserves temporal ordering, which is a necessary condition for realistic evaluation, but does not identify causal mechanisms.
3. **Explicit Invariant:**
   $$\text{Temporal / Provenance Dependency} \neq \text{Causal Effect}$$
   No interventional or counterfactual causal claim is made regarding system behavior or graph topology.

---

## 3. H2 Non-Inferiority Margin Qualification

The H2 decision rule establishes a non-inferiority tolerance:
$$\Delta AP = AP(z_{mv}) - AP(z_{single}) \ge -0.02$$

- **Epistemological Classification:** **`AUTHOR_DEFINED_A_PRIORI_PRACTICAL_MARGIN`**
- **Qualification:** The threshold $\epsilon = -0.02$ is an a priori, study-specific practical engineering margin selected by the authors to permit multi-modal representations that preserve overall performance within a tight tolerance band while acquiring cross-modal synergy. It is **NOT** a universal benchmark constant, an established regulatory standard, or a literature-proven threshold.

---

## 4. Statistical Hierarchy: Disambiguating Model vs. Data Uncertainty

To prevent pseudoreplication across all subsequent analyses:

1. **Level 1 (Model-Level Replication — Primary Inferential Unit):**
   - The three confirmatory seeds (Seeds 42, 7, 999) constitute three independent model training instances.
   - All primary conclusions must report individual seed outcomes ($AP_{42}, AP_7, AP_{999}$), their arithmetic mean, and sample standard deviation ($N=3$).
2. **Level 2 (Data-Level Uncertainty — Nested Resampling):**
   - Paired cluster bootstrap ($B=2000$, seed `10007`) resamples independent session/block clusters within each evaluation split.
   - It quantifies finite-sample data sampling variability for a specific trained model checkpoint.
   - **Strict Rule:** Cluster bootstrap **MUST NEVER** substitute for training seed replication. Conclusions cannot treat resampled test clusters as independent model training instances.
