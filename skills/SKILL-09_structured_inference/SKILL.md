---
name: structured_research_inference
id: SKILL-09
category: INFERENCE
version: 1.0.0
inputs:
  - premises: list[string]
  - evidence_ids: list[string]
  - assumption_ids: list[string]
  - conclusion: string
  - reasoning_type: string
outputs:
  - inference: InferenceRecord
  - issues: list[ReasoningIssue]
---

# SKILL-09: Structured Research Inference

## 1. Objective
Formulate structured inferences (Premises $\to$ Evidence $\to$ Assumptions $\to$ Conclusion) while strictly enforcing the scope guard: `conclusion_scope ⊆ justified_scope`.

## 2. Invariants
- `INF-SCOPE-01`: Candidate conclusion must not generalize beyond premise datasets or experimental bounds.
