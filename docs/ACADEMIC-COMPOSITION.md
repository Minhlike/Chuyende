# Academic Composition & Anti-Hallucination Architecture

## 1. Executive Summary

The Academic Composition Subsystem is the final stage of the Research Agent. It enforces a strict anti-hallucination policy where the Large Language Model and Academic Composer are strictly forbidden from writing scientific thesis paragraphs from raw parametric memory.

```mermaid
flowchart LR
    RN[ResearchNode] --> AB[ArgumentBundle]
    AB --> VCB[VerifiedClaimBundle]
    VCB --> RB[ResultBundle]
    RB --> DP[Discourse Plan]
    DP --> AC[Academic Composer]
    AC --> AHC[Anti-Hallucination Compiler]
    AHC --> DIR[Document IR]
    DIR --> AUD[Thesis Auditor]
    AUD --> DRAFT[Accepted Draft]
```

## 2. Epistemic Invariants & Gate Architecture

### 2.1 Writing Gate States
A node transitions through verified states:
- `NOT_READY`: Missing required canonical claims, sources, or argument bundles.
- `PROVISIONAL`: Allowed structured placeholders (`[[CITATION_REQUIRED]]`, `[[RESULT_PENDING]]`).
- `READY`: All evidentiary and reasoning preconditions satisfied.
- `BLOCKED`: Fatal/Critical reasoning issues or unverified empirical claims present.
- `DRAFTED`: Initial draft written to Document IR.
- `AUDITED`: Passed machine-level sentence audit.
- `APPROVED`: Passed human-in-the-loop review.

### 2.2 Sentence-Level Classification & Compilation
Every sentence is an explicit `SentenceRecord` classified by epistemic role:
- `SOURCE_FACT`: Verifiable factual statement from peer-reviewed literature.
- `SOURCE_CLAIM`: Interpretive or theoretical proposition from literature.
- `SYNTHESIS`: Comparison or integrative statement across multiple sources.
- `OUR_DESIGN`: Novel architectural or methodological formulation.
- `EXPERIMENT_RESULT`: Measured numerical finding from execution.
- `HYPOTHESIS`: Testable scientific proposition.
- `LIMITATION`: Bounded scope or threat to validity.
- `INTERPRETATION`: Scientific inference strictly separated from raw observation.

### 2.3 Anti-Hallucination Compilation States
- `PASS`: Grounded, verified, and bounded.
- `NEEDS_CITATION`: External claim without citation.
- `UNSUPPORTED`: Claim lacking empirical evidence.
- `OWNERSHIP_CONFLICT`: Laundering or theft between SOURCE and OURS.
- `NUMERICALLY_UNVERIFIED`: Numerical claim missing from registry.
- `EQUATION_UNVERIFIED`: Symbolic equation unverified by solver.
- `OVERGENERALIZED`: Unjustified causal inflation or novelty claims.
- `SCOPE_MISMATCH`: Domain conflation (e.g. HDFS log anomaly $\ne$ cyberattack).
- `REJECTED`: Invalid source or fabricated citation.

## 3. Specialized Writing Subsystems
- **Literature Synthesis**: Concept-grouped analysis with explicit preservation of scholarly disagreement.
- **Methodology Writer**: Mechanistic explanations, symbolic equations, explicit assumptions, and module interfaces.
- **Results Writer**: Protocol $O \to U \to I \to A \to L$ (Observation $\to$ Uncertainty $\to$ Interpretation $\to$ Alternatives $\to$ Limitations).
- **Discussion Writer**: Competing explanations, negative results preservation, and operational boundary checks.
- **Abstract & Conclusion**: Generated last strictly from audited empirical state.
