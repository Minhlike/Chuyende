---
name: alternative_explanations_confounders
id: SKILL-06
category: METHODOLOGY
version: 1.0.0
inputs:
  - claim_id: string
  - claim_statement: string
outputs:
  - alternatives: list[AlternativeExplanation]
---

# SKILL-06: Alternative Explanations & Confounders

## 1. Objective
Generate 8 canonical competing explanations (capacity, leakage, shortcuts, tuning, stochastic variation) for reported performance improvements and link each to a negative control or discriminating test.

## 2. Invariants
- `ALT-01`: Every performance claim must be accompanied by plausible confounder explanations before acceptance as proven.
