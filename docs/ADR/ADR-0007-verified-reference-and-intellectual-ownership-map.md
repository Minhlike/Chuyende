# ADR-0007: Verified Reference Map, Intellectual Ownership Taxonomy & Citation Firewall

## Status
ACCEPTED

## Date
2026-08-16

## Context
A rigorous computer science dissertation requires clear, unyielding boundaries between external literature findings (`SOURCE`, `BASELINE`), adapted methodologies (`ADAPTED`), and novel scientific contributions (`OURS`). Without strict provenance and citation gating:
1. LLM agents may hallucinate literature claims or inflate baseline capabilities.
2. Inventions might be claimed where prior art already established the technique, or conversely, our novel designs could be misattributed to referenced papers.
3. Unverified preprints or flawed evaluation benchmarks might leak into core argumentation without proper methodological qualification.

## Decisions

1. **Four-Class Intellectual Ownership Taxonomy (RC-06):**
   - `SOURCE`: Unaltered facts, definitions, or methods originating in cited literature.
   - `ADAPTED`: External methodologies modified, extended, or recontextualized.
   - `OURS`: Original scientific formulations, contracts, architectures, and hypotheses.
   - `BASELINE`: External methods implemented strictly for comparative evaluation.

2. **Bibliographic Quality & Verification States:**
   - Quality Tiers: `PRIMARY_STANDARD`, `PEER_REVIEWED_TOP_VENUE`, `PEER_REVIEWED`, `OFFICIAL_DATASET`, `INSTITUTIONAL_REPORT`, `PREPRINT`, `SOFTWARE_ARTIFACT`, `SECONDARY_SURVEY`.
   - Verification Lifecycle: `DISCOVERED` $\to$ `METADATA_VERIFIED` $\to$ `CONTENT_VERIFIED` $\to$ `INGESTED` $\to$ `SUPERSEDED` / `RETRACTED`.

3. **Citation Firewall (Section 10):**
   - Downstream generation tools are prohibited from inserting bibliographic citations into prose unless:
     a) Source exists in the registry.
     b) Bibliographic metadata is verified against official records.
     c) Explicit claim-evidence linkage is established.
     d) Precise locator (section, page, table) is registered.
     e) Support type is explicitly declared (`DIRECT_SUPPORT`, `PARTIAL_SUPPORT`, `BACKGROUND`, `MOTIVATION`, `CONTRADICTION`, `METHOD_SOURCE`, `DATASET_SOURCE`, `BASELINE_SOURCE`).

4. **Candidate Contribution Novelty Lifecycle (Section 17):**
   - Candidate contributions (`CAND-01` through `CAND-15`) are tracked in `CONTRIBUTION-REGISTRY.yaml`.
   - Initial state is `CANDIDATE` / `PRIOR_ART_SEARCHED`. No automatic transition to `NOVEL` is permitted without evidence-backed differential analysis.

5. **Epistemic Invariant Enforcement (Section 41):**
   - The system strictly enforces invariants preventing the conflation of general prior art (e.g. VICReg collapse regularization, MIL formulations, or log parsing parameter loss) with our security-specific mechanisms (e.g. cross-view log/provenance alignment, session-to-event MIL mapping, or Preserve/Invariant/Exclude contracts).

## Consequences
- **Positive:** Guarantees airtight defensibility during dissertation examination; eliminates fabricated citations; prevents overclaiming and novelty inflation.
- **Negative:** Requires thorough upfront metadata extraction and locator recording for all ingested literature.
