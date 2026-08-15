# Thesis Auditor & Defensibility Invariant Engine

## 1. Executive Summary

The Thesis Auditor performs continuous multi-dimensional verification across 18 audit categories, validating epistemological defensibility, statistical rigor, ownership isolation, and structural variety.

## 2. The 18 Audit Categories

| Category | Invariant Checked | Blocking Severity |
| :--- | :--- | :--- |
| `CLAIMS` | Grounding in empirical data or literature | CRITICAL |
| `CITATIONS` | Propositional entailment & Firewall authorization | CRITICAL |
| `OWNERSHIP` | Strict SOURCE vs OURS attribution | CRITICAL |
| `LOGIC` | Sound deduction & avoidance of non sequiturs | HIGH |
| `NUMBERS` | Direct traceability to `NumericalClaim` registry | CRITICAL |
| `STATISTICS` | Effect sizes, p-values, multiple testing bounds | CRITICAL |
| `EQUATIONS` | Symbolic solver verification & symbol scoping | CRITICAL |
| `TABLES` | Companion CSV data & SHA-256 provenance | CRITICAL |
| `FIGURES` | Operating point data & render hashes | CRITICAL |
| `ARGUMENTATION` | Competing explanations & counterargument handling | HIGH |
| `VALIDITY` | Construct, internal, external, and statistical validity | HIGH |
| `REPRODUCIBILITY` | 5-tier reproducibility verification | CRITICAL |
| `TERMINOLOGY` | Consistent entity and metric naming | MEDIUM |
| `STRUCTURE` | Discourse plan adherence & logical flow | MEDIUM |
| `STYLE` | Restrained academic tone & hedging accuracy | LOW |
| `REPETITION` | Template-attractor & syntactic monotony audit | MEDIUM |
| `CONTRIBUTIONS` | Differentiated novelty across CAND-01..15 | CRITICAL |
| `RQ_H_COVERAGE` | Exhaustive answering of RQ1..5 and H1..5 | CRITICAL |

## 3. The 10 Defensibility Questions (DQ-01..DQ-10)

1. **DQ-01 (What is Learned):** What information is retained in vector $z$ versus discarded?
2. **DQ-02 (Mechanistic Basis):** Why should the architecture work beyond baseline architectures?
3. **DQ-03 (Parsimony):** Could a simpler linear baseline achieve identical performance?
4. **DQ-04 (Leakage):** Could the recorded score be caused by temporal or pipeline leakage?
5. **DQ-05 (Distribution Shift):** Does the performance hold across temporal and environmental drift?
6. **DQ-06 (Privacy Evaluation):** Was the representation evaluated against reconstruction attacks?
7. **DQ-07 (Probe Testing):** Does linear probing confirm feature disentanglement?
8. **DQ-08 (Operational Overhead):** What is the latency and memory footprint per million events?
9. **DQ-09 (Failure Modes):** What evasion campaigns or anomalous structures defeat the model?
10. **DQ-10 (Reproducibility):** Can an external auditor reproduce the numerical claims end-to-end?
