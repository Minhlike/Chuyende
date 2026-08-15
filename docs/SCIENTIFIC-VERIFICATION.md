# Scientific Verification Architecture & Computation Toolchain

## 1. Constitutional Hard Principle: LLM Is Not The Calculator

In accordance with the **Research Constitution** (`docs/RESEARCH-CONSTITUTION.md`, `RC-08`, `RC-09`, `RC-10`, `RC-14`, `RC-16`, `RC-18`):

> **Hard Invariant:** The LLM is strictly prohibited from serving as the authoritative source or calculator for mathematical equations, arithmetic operations, statistical hypothesis test results, p-values, confidence intervals, effect sizes, confusion matrices, aggregate metrics, table values, figure coordinates, or dataset transformations.

All numerical, mathematical, and empirical artifacts must be computed deterministically via code, logged to the provenance store, hashed with SHA-256, and verified prior to thesis prose composition.

---

## 2. Verification Pipeline Architecture

The **Scientific Verification Pipeline** coordinates deterministic execution of `VerificationRequest` tickets dispatched by the Reasoning Engine (`Prompt 5`):

```mermaid
graph TD
    VRQ[VerificationRequest (Prompt 5)] --> Router{Request Type Router}
    Router -->|EQUATION_CHECK| SymEngine[SymPy Symbolic Engine & Scope Registry]
    Router -->|DATASET_VALIDATE| DataVal[DataValidator & AntiLeakageSplitValidator]
    Router -->|METRIC_RECOMPUTE| MetricEng[MetricRecomputationEngine (CM, PR-AUC, Latency)]
    Router -->|STATISTICAL_TEST| StatEng[HypothesisTestingEngine & EffectSizeEngine]
    Router -->|TABLE_BUILD| TblBuilder[TableBuilder (CSV/MD/LaTeX + Fairness Audit)]
    Router -->|FIGURE_BUILD| FigBuilder[FigureBuilder (Plot + Companion CSV + Meta)]
    Router -->|RESULT_REPRODUCE| ReproRunner[ReproductionRunner (Level 1..5)]
    
    SymEngine --> Result[VerificationResult]
    DataVal --> Result
    MetricEng --> Result
    StatEng --> Result
    TblBuilder --> Result
    FigBuilder --> Result
    ReproRunner --> Result
    
    Result --> Store[(Research Repository & DB)]
    Result --> Guard[VerificationGateForWriting]
    Guard --> Bundle[ResultBundle & VerifiedClaimBundle]
```

### Verification Request Lifecycle
$$\text{REQUESTED} \longrightarrow \text{VALIDATING} \longrightarrow \text{READY} \longrightarrow \text{RUNNING} \longrightarrow \text{PASS} \, / \, \text{FAIL} \, / \, \text{INCONCLUSIVE} \, / \, \text{BLOCKED}$$

---

## 3. Symbolic Mathematical Verification

The symbolic verification layer (`src/research_agent/verification/equations/`) uses **SymPy** for algebraic analysis:
- **Algebraic Equivalence:** Simplifies symbolic differences $f(x) - g(x) = 0$ alongside randomized domain sampling.
- **Calculus Derivatives:** Symbolically differentiates functions and verifies claimed derivative expressions $\frac{\partial \mathcal{L}}{\partial \theta}$.
- **Domain Sanity:** Audits expressions for division by zero (denominators $\to 0$), logarithms with non-positive arguments ($\log(x), x \le 0$), and square roots.
- **Tensor Shape Compatibility:** Checks ML matrix and vector alignment (e.g. $\mathbf{z}_{seq} \in \mathbb{R}^d$ and $\mathbf{z}_{graph} \in \mathbb{R}^d$).
- **Loss Composition Audit:** Audits multi-term objectives $\mathcal{L} = \sum \lambda_i \mathcal{L}_i$, verifying scalar outputs, $\lambda_i \ge 0$, and constituent provenance.

---

## 4. Dataset Lineage & Anti-Leakage Guardrails

The dataset verification layer (`src/research_agent/verification/datasets/`) guarantees:
1. **Raw Immutability:** Raw data files are never overwritten or deleted.
2. **Deterministic Profiling:** Generates `DataProfile` containing total events, entities, label distributions, missing rates, and SHA-256 profile hash.
3. **Anti-Leakage Protocols:**
   - **Temporal Strictness:** $T_{train}^{\max} < T_{val}^{\min} \le T_{val}^{\max} < T_{test}^{\min}$.
   - **Entity / Host Holdout:** $\text{Hosts}_{train} \cap \text{Hosts}_{test} = \emptyset$.
   - **Preprocessing Split Fit:** Verifies that scalers, parsers, and vocabularies are fitted exclusively on `TRAIN_ONLY`.

---

## 5. 5-Tier Reproducibility Hierarchy

| Tier | Name | Target Invariant | Verification Tool |
| :--- | :--- | :--- | :--- |
| **Level 1** | Integrity | File bit-level SHA-256 consistency | `ReproductionRunner.verify_level_1_integrity` |
| **Level 2** | Metric Recomputation | Exact numerical match from raw predictions | `ReproductionRunner.verify_level_2_metrics` |
| **Level 3** | Statistical Reproduction | Regrowth of CIs, tables, figures from metric logs | `TableBuilder` / `FigureBuilder` |
| **Level 4** | Inference Rerun | Rerun fixed model checkpoints on test split | Model evaluation runner with seed lock |
| **Level 5** | End-to-End Retraining | Full pipeline reproduction from raw data | End-to-end retraining script |

---

## 6. Prompt 7 Handoff Contract: Verified Bundles

Before any empirical claim or experimental section is written by the Chapter Composer in Prompt 7, it must be packaged into:
1. **`ResultBundle`:** Contains machine-computed metrics, statistical hypothesis test results ($p$-value, effect size, 95% bootstrap CI), table IDs, figure IDs, dataset version hashes, and explicit limitations.
2. **`VerifiedClaimBundle`:** Binds normalized claims to verified numerical quantities, mathematical equations, and an **`AllowedWordingStrength`** (`DESCRIPTIVE_ONLY`, `ASSOCIATIONAL`, `COMPARATIVE`, `SUPPORTIVE`, `STRONG_SUPPORT`).
