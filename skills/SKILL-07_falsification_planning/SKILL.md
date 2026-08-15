---
name: falsification_negative_control_design
id: SKILL-07
category: EXPERIMENT_DESIGN
version: 1.0.0
inputs:
  - hypothesis_id: string
  - hypothesis_statement: string
outputs:
  - falsification_plan: FalsificationPlan
---

# SKILL-07: Falsification Protocol & Negative Control Design

## 1. Objective
Design empirical falsification conditions, negative controls, and discriminating experiments that could reject or narrow the scope of H1..H5.

## 2. Invariants
- `FALS-01`: Falsification plans must define expected empirical outcomes if true vs if false.
- `FALS-02`: Negative controls must isolate candidate shortcuts (e.g. identifier masking, campaign holdouts).
