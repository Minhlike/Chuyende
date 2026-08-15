# ADR-0009: Scientific Reasoning, Argumentation & Research Skills Architecture

- **Status:** Accepted
- **Date:** 2026-08-16
- **Context:** Prompt 5/7 of the Autonomous Research Agent Architecture
- **Authors:** Principal Research AI Engineer, Scientific Reasoning Architect, Critical Research Reviewer

---

## 1. Context and Problem Statement

A primary vulnerability of LLM-based autonomous research agents is "hallucinatory writing" and superficial essay generation. LLMs frequently conflate observational correlations with causal effects, ignore empirical contradictions in literature, fail to test alternate confounders (model capacity, dataset shortcuts, data leakage), overclaim novelty, and collapse into repetitive, uniform rhetorical styles.

Furthermore, internal "chain-of-thought" generation is ephemeral, non-canonical, and un-auditable as scientific evidence.

To guarantee rigorous, defensible scientific outputs before thesis composition, the Research Agent requires a dedicated **Scientific Reasoning Engine** that produces explicit, auditable reasoning artifacts and enforces strict methodological guards.

---

## 2. Decision Drivers

1. **Reason != Write:** The reasoning engine must construct defensible research structures (Claims, Evidences, Inferences, Falsifications, Graphs) rather than unstructured chapter prose.
2. **Explicit Reasoning Artifacts:** All reasoning steps must be materialized as typed Pydantic models stored in SQLite and queryable via hybrid retrieval.
3. **Strict Epistemic Guards:** Automated auditors must enforce:
   - `DEPENDS_ON != CAUSES` in host audit graphs.
   - `ANOMALY_NOT_ATTACK` (supercomputer crash logs != cyberattack telemetry).
   - `UNUSUAL_NOT_MALICIOUS` (admin tools != attack without contextual role).
   - `REPRESENTATION_NOT_DETECTOR` (probe complexity isolation).
   - `PSEUDONYMIZATION_NOT_PRIVACY` (membership inference vulnerability).
   - `OURS != NOVEL` (explicit prior art differentiation).
   - `conclusion_scope ⊆ justified_scope` (scope containment).
4. **Anti-HARKing & Negative Result Preservation:** Negative results and failed experiments must transition hypotheses to `CONTESTED` or `FALSIFIED`, never quietly omitted or post-hoc rationalized.
5. **Procedural Skill System:** 18 canonical research skills must be versioned, callable, and validated.
6. **Prompt 6 Handoff Interface:** Formal `VerificationRequest` objects must be generated for mathematical and statistical validation.

---

## 3. Considered Options

- **Option A (Unstructured Chain-of-Thought):** Rely on model internal reasoning steps stored in scratchpads or hidden prompt context.
- **Option B (Heuristic Rule Engine):** Pure hardcoded validation rules without structured argument graph modeling or discourse planning.
- **Option C (Unified Explicit Scientific Reasoning Engine & M4 Argument Graph):** A multi-layer architecture with 16 reasoning modes, typed explicit artifacts (`AtomicClaimCandidate`, `EvidenceGap`, `AssumptionRecord`, `AlternativeExplanation`, `CounterargumentRecord`, `FalsificationPlan`, `InferenceRecord`, `ArgumentBundle`), 18 procedural skills, and automated methodological auditors.

---

## 4. Decision Outcome

**Chosen Option:** **Option C (Unified Explicit Scientific Reasoning Engine & M4 Argument Graph)**.

### Architectural Structure:
1. **Core Schemas (`schemas/reasoning.py`):** Typed models for explicit reasoning artifacts, argument graph elements, and verification requests.
2. **Database Integration (`storage/db.py`, `storage/repository.py`):** Relational tables for `argument_bundles`, `evidence_gaps`, `assumptions`, `verification_requests`, `reasoning_issues`, `argument_nodes`, and `argument_edges`.
3. **Modular Reasoning Engines (`reasoning/`):**
   - `ClaimExtractor` (atomic proposition decomposition & scope extraction).
   - `EvidenceAlignmentEngine` (entailment & gap detection).
   - `LiteratureSynthesisEngine` (issue-organized structured synthesis).
   - `ContradictionAnalyzer` (10-point multi-dimensional conflict diagnosis).
   - `AssumptionAuditor` (implicit assumption challenge & fragility testing).
   - `AlternativeExplanationsEngine` (8 canonical confounders & negative controls).
   - `CounterargumentBuilder` (steelman `OUR_COUNTERARGUMENT` generation).
   - `FalsificationPlanner` (falsification conditions & discriminating tests).
   - `InferenceEngine` (structured inference & scope containment).
   - `CausalityAuditor` (causal inflation & graph causality guards).
   - `LeakageAuditor` (12-point leakage checklist).
   - `ShortcutAuditor` (10-point dataset shortcut checklist).
   - `ValidityAuditor` (4-factor validity audit).
   - `SecurityGuards` (security and privacy overclaim guards).
   - `HypothesisEvaluator` (H1..H5 epistemic evaluation).
   - `ContributionDifferentiator` (prior art novelty differentiation).
   - `ArgumentGraphEngine` (M4 DAG construction & cycle detection).
   - `DiscoursePlanner` (10 non-rigid argument patterns & template attractor audit).
   - `ResearchActionPrioritizer` (information-gain priority ranking).
   - `ArgumentBundleBuilder` (packaging & multi-criteria readiness gate).
4. **Research Skills System (`skills/` & `src/research_agent/skills/`):**
   - Registry and runner for the 18 canonical research skills.
5. **CLI Integration (`src/research_agent/cli.py`):**
   - `research-agent reason [rq|claim|synthesize|contradictions|assumptions|falsify|critique|contribution|build-bundle|validate]`
   - `research-agent skills [list|show|validate|run]`

---

## 5. Consequences

### Positive:
- Mathematical and operational grounding of all assertions before thesis chapter writing.
- Elimination of LLM "essay writing" hallucinations.
- Preservation of negative results and active literature contradictions.
- Deterministic, auditable M4 Argument Graph exportable to Mermaid and Graphviz DOT.
- Seamless hand-off to Prompt 6 via typed `VerificationRequest` interface.

### Negative / Trade-offs:
- Increased schema and validation complexity.
- Requires explicit evidence locators and negative controls for all claims before readiness gate can pass to `READY`.

---

## 6. References & Invariants
- `RESEARCH-CONSTITUTION.md` (RC-01..RC-15)
- `ROADMAP-ARCHITECTURE.md` (RQ1..RQ5, H1..H5, Axes A1..A5)
- `REFERENCE-MAP-ARCHITECTURE.md` (Verified Reference Map & Citation Firewall)
- `MEMORY-ARCHITECTURE.md` (Persistent Research Memory & Hybrid Retrieval)
- `REASONING-ARCHITECTURE.md` (Complete reasoning specification)
