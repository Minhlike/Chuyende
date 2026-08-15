---
name: steelman_counterargument_generation
id: SKILL-08
category: DIALECTIC
version: 1.0.0
inputs:
  - claim_id: string
  - claim_statement: string
outputs:
  - counterargument: CounterargumentRecord
---

# SKILL-08: Steelman Counterargument Generation

## 1. Objective
Construct the strongest plausible objections and counter-theses against research inferences, labeling self-generated objections as `OUR_COUNTERARGUMENT`.

## 2. Invariants
- `STEEL-01`: Counterarguments must address core architectural/operational vulnerabilities rather than trivial strawmen.
