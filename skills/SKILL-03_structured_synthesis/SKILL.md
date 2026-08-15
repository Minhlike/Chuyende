---
name: structured_literature_synthesis
id: SKILL-03
category: SYNTHESIS
version: 1.0.0
inputs:
  - topic: string
  - claims: list[Claim]
  - sources: list[Source]
  - roadmap_node: Optional[string]
outputs:
  - structured_synthesis: StructuredSynthesis
---

# SKILL-03: Structured Literature Synthesis

## 1. Objective
Synthesize literature across a topic or roadmap section organized by issues, mechanisms, consensus, and disagreements, avoiding sequential paper-by-paper enumeration.

## 2. Invariants
- `SYNTH-01`: Grouping must be thematic/mechanistic, not per-author summary lists.
- `SYNTH-02`: Must explicitly articulate divergence causes and research implications.
