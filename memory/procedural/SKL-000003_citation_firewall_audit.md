# SKL-000003: Citation Firewall Audit Protocol (v1.0)

## Purpose
Procedure to audit draft thesis sections and papers to ensure no unverified sources or unlinked citations are used.

## Preconditions
1. Source Registry and Evidence Store are populated.
2. Citation Firewall rule table is initialized.

## Invariants
1. Block any citation that lacks verified metadata, locator, and claim-evidence link.
2. Flag preprints and surveys with appropriate epistemic qualifiers.

## Checklist
- [ ] Run `research-agent refs firewall` to identify blocked citations.
- [ ] Ensure all claims cited as `SOURCE_FACT` have verified evidence.
- [ ] Verify that candidate novelties `CAND-01`..`CAND-15` cite prior art only as `BACKGROUND` or `MOTIVATION`.
