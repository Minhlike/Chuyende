# ADR-0010: Scientific Verification Toolchain, Statistical Integrity & Reproducibility Hierarchy

## Status
**ACCEPTED**

## Date
2026-08-16

## Context
In doctoral and top-tier scientific research, hallucinated numbers, ungrounded mathematical equations, silent data leakage, and statistical misuse (such as reporting only best runs or omitting effect sizes) undermine scientific credibility. The LLM must not be used as an arithmetic calculator or authoritative source of numbers. Every equation, number, metric, statistical claim, table, and figure must trace directly to raw data, code, and deterministic verification tools.

## Decision
1. **Separation of LLM and Calculation:**
   - Established the **Hard Principle: LLM Is Not The Calculator**.
   - Built the modular `src/research_agent/verification/` subsystem containing symbolic solvers (SymPy), deterministic metric calculators (confusion matrices, PR-AUC), statistical engines (SciPy/NumPy), table builders, and figure generators.
2. **Deterministic Verification Pipeline:**
   - Implemented `ScientificVerificationPipeline` executing `VerificationRequest` tickets across `EQUATION_CHECK`, `NUMERICAL_CHECK`, `STATISTICAL_TEST`, `DATASET_VALIDATE`, `METRIC_RECOMPUTE`, `TABLE_BUILD`, `FIGURE_BUILD`, and `RESULT_REPRODUCE`.
3. **Anti-Leakage & Dataset Guardrails:**
   - Enforced temporal progression ($T_{train}^{\max} < T_{val}^{\min} \le T_{val}^{\max} < T_{test}^{\min}$) and entity/host holdout separation.
   - Enforced fitting preprocessing transformers only on `TRAIN_ONLY`.
4. **Statistical Protocol & Cherry-Picking Prevention:**
   - Enforced reporting multi-seed distributions ($\text{Mean} \pm \text{SD}$ / $\text{Median } [\text{IQR}]$) with the `BestRunCherryPickingGuard`.
   - Mandated pairing $p$-values with standardized effect sizes (Cohen's $d$, Hedges' $g$) and bootstrap confidence intervals.
5. **Deterministic Artifacts with Cryptographic Hashes:**
   - Implemented `TableBuilder` (CSV, Markdown, LaTeX with cell-level provenance and fairness audits).
   - Implemented `FigureBuilder` with mandatory companion `figure-data.csv` and metadata JSON.
6. **5-Tier Reproducibility Hierarchy:**
   - Structured reproducibility across Levels 1 (Hash Integrity) to 5 (End-to-End Retraining) with DAG invalidation cascading.
7. **Writing Firewall Gate for Prompt 7:**
   - Introduced `VerificationGateForWriting` that guards `ResultBundle` and `VerifiedClaimBundle` with `AllowedWordingStrength`.

## Consequences
- **Positive:** Zero fabricated numbers or equations can enter the thesis; all results are verifiable and reproducible across the 5 tiers.
- **Tradeoff:** Computation requires explicit execution of verification tickets and Python tool execution, biasing rigor over speed.
