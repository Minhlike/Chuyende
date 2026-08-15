---
name: hypothesis_and_rq_epistemic_evaluation
id: SKILL-14
category: EVALUATION
version: 1.0.0
inputs:
  - hypothesis_code: string
  - evidence_ids: list[string]
  - contradiction_ids: list[string]
outputs:
  - evaluation_result: HypothesisEvaluationResult
---

# SKILL-14: Hypothesis & RQ Epistemic Evaluation

## 1. Objective
Calculate grounded `EpistemicStatus` for hypotheses (H1..H5) and research questions (RQ1..RQ5), strictly preserving negative results without post-hoc hypothesis rescue.

## 2. Invariants
- `EPIST-01`: Failed or contradictory runs must transition hypotheses to `CONTESTED` or `FALSIFIED`, never quietly omitted.
