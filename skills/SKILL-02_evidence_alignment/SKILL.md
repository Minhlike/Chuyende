---
name: evidence_alignment_and_gap_detection
id: SKILL-02
category: EVIDENCE_EVALUATION
version: 1.0.0
inputs:
  - claim: Claim
  - evidences: list[Evidence]
outputs:
  - alignments: list[EvidenceAlignmentResult]
  - evidence_gap: Optional[EvidenceGap]
---

# SKILL-02: Evidence Alignment & Gap Detection

## 1. Objective
Evaluate whether empirical evidence units directly support, partially support, qualify, or contradict a target claim. Generate typed `EvidenceGap` entities when claims lack sufficient empirical backing.

## 2. Invariants
- `EVD-ALIGN-01`: Evidence strength and semantic entailment must be evaluated independently of retrieval score.
- `EVD-ALIGN-02`: If all linked evidences are partial/qualified, an `EvidenceGap` must be generated.
