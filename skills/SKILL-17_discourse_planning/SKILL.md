---
name: rhetorical_discourse_planning
id: SKILL-17
category: DISCOURSE
version: 1.0.0
inputs:
  - roadmap_node: string
  - preferred_pattern: Optional[string]
outputs:
  - discourse_plan: DiscoursePlan
---

# SKILL-17: Rhetorical Discourse Planning

## 1. Objective
Plan non-rigid rhetorical argumentation sequences across 10 diverse argument patterns, preventing repetitive template-attractor collapse across chapter sections.

## 2. Invariants
- `DISC-01`: No 3 consecutive sections may use identical argument patterns.
